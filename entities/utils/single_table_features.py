from typing import Dict, Any, Optional, Type, Callable
from sqlmodel import select
from sqlalchemy import desc, asc
from sqlalchemy.sql.elements import ColumnElement
from datetime import datetime
from zoneinfo import ZoneInfo
import re

class SingleTableFeatures:    
    def __init__(self, model: Type, query_params: Optional[Dict[str, Any]] = None):
        DEFAULT_LIMIT = 25
        MAX_LIMIT = 100
        DEFAULT_TIMEZONE_STR = "Asia/Jerusalem"

        self.model = model
        self.query_params = query_params or {}
        self.statement = select(model)

        self.page = int(self.query_params.get("page", 1))
        requested_limit = int(self.query_params.get("limit", DEFAULT_LIMIT))
        self.limit = min(requested_limit, MAX_LIMIT)

        tz_str = self.query_params.get("tz", DEFAULT_TIMEZONE_STR)
        try:
            self.tz = ZoneInfo(tz_str)
        except Exception:
            self.tz = ZoneInfo("UTC") 

        self.operators: Dict[str, Callable] = {
            "eq": lambda field, value: field == value,
            "ne": lambda field, value: field != value,
            "gt": lambda field, value: field > value,
            "lt": lambda field, value: field < value,
            "gte": lambda field, value: field >= value,
            "lte": lambda field, value: field <= value,
            "in": lambda field, value: field.in_(value.split(",") if isinstance(value, str) else value),
            "LIKE": lambda field, value, wildcard_position="both": self._handle_like_filter(field, str(value), False, wildcard_position),
            "ILIKE": lambda field, value, wildcard_position="both": self._handle_like_filter(field, str(value), True, wildcard_position)
        }

    def _handle_date_filter(self, field: ColumnElement, value: str, operator: str) -> ColumnElement:
        value = value.replace('T', ' ')

        try:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                dt = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid datetime format: {value}")

        dt_local = dt.replace(tzinfo=self.tz)
        dt_utc = dt_local.astimezone(ZoneInfo("UTC"))

        if operator == "eq":
            start_of_day = datetime.combine(dt.date(), datetime.min.time()).replace(tzinfo=self.tz).astimezone(ZoneInfo("UTC"))
            end_of_day = datetime.combine(dt.date(), datetime.max.time()).replace(tzinfo=self.tz).astimezone(ZoneInfo("UTC"))
            return field.between(start_of_day, end_of_day)

        filter_func = self.operators.get(operator, self.operators["eq"])

        return filter_func(field, dt_utc)

    def _handle_like_filter(self, field: ColumnElement, value: str, is_ilike: bool, wildcard_position: str = "both") -> ColumnElement:
        if not "%" in value:
            if wildcard_position  == "start":
                value = f"%{value}"
            elif wildcard_position  == "end":
                value = f"{value}%"
            elif wildcard_position  == "both":
                value = f"%{value}%"
        
        return field.ilike(value) if is_ilike else field.like(value)

    def filter(self) -> 'SingleTableFeatures':
        if not self.query_params:
            return self

        excluded_fields = ["page", "sort", "limit", "fields", "tz"]
        query_params = {
            param_name: param_value 
            for param_name, param_value in self.query_params.items() 
            if param_name not in excluded_fields
        }

        for param_name, param_value in query_params.items():
            match = re.match(r'^(.+)\[\$(.+)]$', param_name)
            if match:
                field_name, operator = match.groups()
            else:
                field_name, operator = param_name, "eq"

            if not hasattr(self.model, field_name):
                continue

            field = getattr(self.model, field_name)
            
            if operator in ["date", "wildcard"]:
                continue

            is_date = query_params.get(f"{field_name}[$date]") == "true"
            wildcard_position  = query_params.get(f"{field_name}[$wildcard]", "both")

            if is_date:
                filter_clause = self._handle_date_filter(field, str(param_value), operator)
            elif operator.upper() in ["LIKE", "ILIKE"]:
                filter_clause = self.operators[operator.upper()](field, param_value, wildcard_position )
            else:
                filter_func = self.operators.get(operator, self.operators["eq"])
                filter_clause = filter_func(field, param_value)

            if filter_clause is not None:
                self.statement = self.statement.where(filter_clause)

        return self

    def sort(self) -> 'SingleTableFeatures':
        if "sort" in self.query_params:
            sort_fields = self.query_params["sort"].split(",")
            order_by_clauses = []
            
            for sort_field in sort_fields:
                is_desc = sort_field.startswith("-")
                field_name = sort_field[1:] if is_desc else sort_field
                
                if hasattr(self.model, field_name):
                    column = getattr(self.model, field_name)
                    order_by_clauses.append(desc(column) if is_desc else asc(column))
            
            if order_by_clauses:
                self.statement = self.statement.order_by(*order_by_clauses)
        else:
            self.statement = self.statement.order_by(desc(self.model.created_at))

        return self

    def paginate(self) -> ColumnElement:
        offset = (self.page - 1) * self.limit
        self.statement = self.statement.offset(offset).limit(self.limit)

        return self.statement 