from typing import Dict, Any, Optional, Type, Callable, List
from sqlmodel import select
from sqlalchemy import desc, asc
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.sqltypes import Integer, Float, DateTime, Numeric
from dateutil.parser import parse
import re
from entities.utils.filter_operations import FilterOperators

class SingleTableFeatures:    
    def __init__(self, model: Type, date_fields: Optional[List[str]] = None, query_params: Optional[Dict[str, Any]] = None):
        DEFAULT_LIMIT = 25
        MAX_LIMIT = 100
        DEFAULT_TIMEZONE_STR = "Asia/Jerusalem"

        self.model = model
        self.query_params = query_params or {}
        self.date_fields = date_fields or []
        
        self.page = int(self.query_params.get("page", 1))
        requested_limit = int(self.query_params.get("limit", DEFAULT_LIMIT))
        self.limit = min(requested_limit, MAX_LIMIT)

        tz_str = self.query_params.get("tz", DEFAULT_TIMEZONE_STR)
        self.filter_ops = FilterOperators(tz_str)
        self.operators = self.filter_ops.operators

        fields_str = self.query_params.get("fields")
        self.selected_columns = []

        if fields_str:
            field_names = [field.strip() for field in fields_str.split(",")]

            alias_to_attr = {
                field_info.alias or name: name
                for name, field_info in self.model.model_fields.items()
            }

            for alias in field_names:
                attr_name = alias_to_attr.get(alias)
                if attr_name and hasattr(self.model, attr_name):
                    col = getattr(self.model, attr_name)
                    self.selected_columns.append(col.label(alias))

        if self.selected_columns:
            self.statement = select(*self.selected_columns)
        else:
            self.statement = select(self.model)


    def _convert_value(self, column, value: str):
        try:
            col_type = getattr(column.type, "__class__", None)
            if col_type in [Integer]:
                return int(value)
            if col_type in [Float, Numeric]:
                return float(value)
            if col_type in [DateTime]:
                return parse(value)
            return value
        except Exception as e:
            print(f"Warning: failed to convert '{value}' for column {column} - {e}")
            return value


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

            is_date = field_name in self.date_fields
            wildcard_position  = query_params.get(f"{field_name}[$wildcard]", "both")

            if is_date:
                filter_clause = self.filter_ops.handle_date_filter(field, str(param_value), operator)
            elif operator.upper() in ["LIKE", "ILIKE"]:
                filter_clause = self.operators[operator.upper()](field, param_value, wildcard_position )
            else:
                filter_func = self.operators.get(operator, self.operators["eq"])
                converted_value = self._convert_value(field, param_value)
                filter_clause = filter_func(field, converted_value)

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
    