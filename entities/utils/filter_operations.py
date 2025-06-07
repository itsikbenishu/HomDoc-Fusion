from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.sql.elements import ColumnElement
from typing import Any

class FilterOperators:
    def __init__(self, timezone_str: str = "Asia/Jerusalem"):
        try:
            self.tz = ZoneInfo(timezone_str)
        except Exception:
            self.tz = ZoneInfo("UTC") 

        self.operators = {
            "eq": lambda field, value: field == value,
            "ne": lambda field, value: field != value,
            "gt": lambda field, value: field > value,
            "lt": lambda field, value: field < value,
            "gte": lambda field, value: field >= value,
            "lte": lambda field, value: field <= value,
            "in": lambda field, value: field.in_(self._handle_in_filter(field, value)),
            "not_in": lambda field, value: field.notin_(self._handle_in_filter(field, value)),
            "LIKE": lambda field, value, wildcard_position="both": self._handle_like_filter(field, str(value), False, wildcard_position),
            "ILIKE": lambda field, value, wildcard_position="both": self._handle_like_filter(field, str(value), True, wildcard_position),
            "NOT_LIKE": lambda field, value, wildcard_position="both": ~self._handle_like_filter(field, str(value), False, wildcard_position),
            "NOT_ILIKE": lambda field, value, wildcard_position="both": ~self._handle_like_filter(field, str(value), True, wildcard_position),
        }

    def handle_date_filter(self, field: ColumnElement, value: str, operator: str) -> ColumnElement:
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

    def _handle_in_filter(self, column: ColumnElement, value: Any) -> Any:
        try:
            python_type = column.type.python_type
        except AttributeError:
            return value

        try:
            if isinstance(value, list):
                return [python_type(v) for v in value]
            if isinstance(value, str) and ',' in value:
                return [python_type(v.strip()) for v in value.split(',')]
            return python_type(value)
        except Exception:
            return value

    def _handle_like_filter(self, field: ColumnElement, value: str, is_ilike: bool, wildcard_position: str = "both") -> ColumnElement:
        if "%" not in value:
            if wildcard_position == "start":
                value = f"%{value}"
            elif wildcard_position == "end":
                value = f"{value}%"
            elif wildcard_position == "both":
                value = f"%{value}%"
        return field.ilike(value) if is_ilike else field.like(value)
