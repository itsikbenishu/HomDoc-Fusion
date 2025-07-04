from fastapi import status 
from typing import Dict, Any, Optional, Type, List
from sqlmodel import select
from sqlalchemy import desc, asc
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.sqltypes import Integer, Float, DateTime, Numeric
from dateutil.parser import parse
from fastapi import HTTPException
import re
from entities.utils.filter_operations import FilterOperators


class SingleTableFeatures:
    def __init__(
        self,
        model: Type,
        date_fields: Optional[List[str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        default_sort_field: str = "createdAt"
    ):
        DEFAULT_LIMIT = 25
        MAX_LIMIT = 100
        DEFAULT_TIMEZONE_STR = "Asia/Jerusalem"

        self.model = model
        self.query_params = query_params or {}
        self.date_fields = date_fields or []
        self.default_sort_field = default_sort_field

        self.page = int(self.query_params.get("page", 1))
        requested_limit = int(self.query_params.get("limit", DEFAULT_LIMIT))
        self.limit = min(requested_limit, MAX_LIMIT)

        tz_str = self.query_params.get("tz", DEFAULT_TIMEZONE_STR)
        self.filter_ops = FilterOperators(tz_str)
        self.operators = self.filter_ops.operators

        self.alias_to_attr = {
            field_info.alias or name: name
            for name, field_info in self.model.model_fields.items()
        }

        self.selected_columns = []
        self.statement = select(self.model)

    def _get_column(self, field_name: str) -> str:
        attr_name = self.alias_to_attr.get(field_name)

        if attr_name and hasattr(self.model, attr_name):
            return attr_name

        if hasattr(self.model, field_name):
            return field_name

        available_fields = list(self.alias_to_attr.keys())
        similar_fields = [f for f in available_fields if field_name.lower() in f.lower()]
       
        error_msg = f"Field '{field_name}' not valid column."
        if similar_fields:
            error_msg += f" Did you mean: {', '.join(similar_fields[:3])}?"
        else:
            error_msg += f" You can use one of these: {available_fields}"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

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

    def fields_selection(self) -> "SingleTableFeatures":
        fields_str = self.query_params.get("fields")
        if not fields_str:
            return self

        field_names = [field.strip() for field in fields_str.split(",")]
        for alias in field_names:
            attr_name = self._get_column(alias) 
            col = getattr(self.model, attr_name)
            self.selected_columns.append(col.label(alias))
        
        if self.selected_columns:
            self.statement = select(*self.selected_columns)
        return self

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

            attr_name = self._get_column(field_name)
            field = getattr(self.model, attr_name)

            if operator in ["date", "wildcard"]:
                continue

            is_date = attr_name in self.date_fields
            wildcard_position = query_params.get(f"{field_name}[$wildcard]", "both")

            if is_date:
                filter_clause = self.filter_ops.handle_date_filter(field, str(param_value), operator)
            elif operator.upper() in ["LIKE", "ILIKE"]:
                filter_clause = self.operators[operator.upper()](field, param_value, wildcard_position)
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

                attr_name = self._get_column(field_name)
                column = getattr(self.model, attr_name)
                order_by_clauses.append(desc(column) if is_desc else asc(column))

            if order_by_clauses:
                self.statement = self.statement.order_by(*order_by_clauses)
        else:
            default_sort_attr = self._get_column(self.default_sort_field)
            self.statement = self.statement.order_by(desc(getattr(self.model, default_sort_attr)))

        return self

    def paginate(self) -> ColumnElement:
        offset = (self.page - 1) * self.limit
        self.statement = self.statement.offset(offset).limit(self.limit)
        return self.statement
