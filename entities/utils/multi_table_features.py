from typing import List, Type, Dict, Any, Optional, Set, Callable
from sqlalchemy.sql import Select
from sqlalchemy import desc, asc
from sqlalchemy.sql.elements import ColumnElement
from datetime import datetime
from zoneinfo import ZoneInfo
import re
from entities.utils.single_table_features import SingleTableFeatures
from entities.utils.filter_operations import FilterOperators


class MultiTableFeatures:
    def __init__(self, base_statement: Select, models: List[Type], main_model: Type, query_params: Optional[Dict[str, Any]] = None):
        self.models = models
        self.main_model = main_model
        self.statement = base_statement
        self.query_params = query_params or {}
        self.single_table_features = SingleTableFeatures(self.main_model, self.query_params)

        self.filter_ops = self.single_table_features.filter_ops
        self.operators = self.single_table_features.operators

    def build(self) -> Select:
        return self.statement

    def _get_actual_field_name(self, model: Type, name: str) -> Optional[str]:
        for field in model.__fields__.values():
            if field.alias == name:
                return field.name
        if hasattr(model, name):
            return name
        return None

    def _find_model_for_field(self, field_name: str) -> Optional[Type]:
        for model in self.models:
            actual_name = self._get_actual_field_name(model, field_name)
            if actual_name and hasattr(model, actual_name):
                return model
        return None

    def filter(self) -> Select:
        if not self.query_params:
            return self.statement

        excluded_fields = {"page", "sort", "limit", "fields", "tz"}
        
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

            if operator in ["date", "wildcard"]:
                continue

            target_model = self._find_model_for_field(field_name)
            if target_model:  # הסרנו את הבדיקה המיותרת
                actual_name = self._get_actual_field_name(target_model, field_name)
                if actual_name and hasattr(target_model, actual_name):
                    column = getattr(target_model, actual_name)

                    is_date = query_params.get(f"{field_name}[$date]") == "true"
                    wildcard_position = query_params.get(f"{field_name}[$wildcard]", "both")

                    if is_date:
                        filter_clause = self.filter_ops.handle_date_filter(column, str(param_value), operator)
                    elif operator.upper() in ["LIKE", "ILIKE"]:
                        filter_clause = self.operators[operator.upper()](column, param_value, wildcard_position)
                    else:
                        filter_func = self.operators.get(operator, self.operators["eq"])
                        filter_clause = filter_func(column, param_value)

                    if filter_clause is not None:
                        self.statement = self.statement.where(filter_clause)

        return self.statement

    def sort(self) -> Select:
        if "sort" in self.query_params:
            sort_fields = self.query_params["sort"].split(",")
            order_by_clauses = []
            
            for sort_field in sort_fields:
                is_desc = sort_field.startswith("-")
                field_name = sort_field[1:] if is_desc else sort_field
                    
                target_model = self._find_model_for_field(field_name)
                if target_model:
                    actual_name = self._get_actual_field_name(target_model, field_name)
                    if actual_name and hasattr(target_model, actual_name):
                        column = getattr(target_model, actual_name)
                        order_by_clauses.append(desc(column) if is_desc else asc(column))
                
            if order_by_clauses:
                self.statement = self.statement.order_by(*order_by_clauses)
        else:
            self.statement = self.statement.order_by(desc(self.main_model.created_at))

        return self.statement

    def paginate(self) -> Select:
        paginated = self.single_table_features.paginate()
        self.statement = self.statement.limit(paginated._limit_clause).offset(paginated._offset_clause)
        
        return self.statement

