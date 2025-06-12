from typing import List, Type, Dict, Any, Optional, Set, Callable
from sqlalchemy.sql import Select
from sqlalchemy import desc, asc
import re
from entities.utils.single_table_features import SingleTableFeatures

class MultiTableFeatures:
    def __init__(self, base_statement: Select, models: List[Type], main_model: Type, date_fields: Optional[List[str]] = None, query_params: Optional[Dict[str, Any]] = None):
        self.models = models
        self.main_model = main_model
        self.date_fields = date_fields or []
        self.query_params = query_params or {}
        self.single_table_features = SingleTableFeatures(self.main_model, self.query_params)

        self.filter_ops = self.single_table_features.filter_ops
        self.operators = self.single_table_features.operators

        fields_str = self.query_params.get("fields")
        if fields_str:
            field_names = [f.strip() for f in fields_str.split(",")]
            columns = []
            for field_name in field_names:
                for model in self.models:
                    if hasattr(model, field_name):
                        columns.append(getattr(model, field_name))
                        break

            if columns:
                self.statement = Select(*columns).select_from(base_statement.froms[0])
            else:
                self.statement = base_statement
        else:
            self.statement = base_statement


    def build(self) -> Select:
        return self.statement

    def _get_actual_field_name(self, model: Type, name: str) -> Optional[str]:
        for field_name, field_info in model.model_fields.items():
            if field_info.alias == name:
                return field_name
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
            match = re.match(r'^(.*?)(?:\[\$([a-zA-Z0-9_]+)\])?$', param_name)
            if match:
                field_name = match.group(1)
                operator = match.group(2) if match.group(2) else "eq"
            else:
                continue

            if operator in ["date", "wildcard"]:
                continue

            target_model = self._find_model_for_field(field_name)
            if target_model: 
                actual_name = self._get_actual_field_name(target_model, field_name)
                column_to_filter = None
                if actual_name and hasattr(target_model, actual_name):
                    column_to_filter = getattr(target_model, actual_name) 
                
                if column_to_filter is None:
                    print(f"Warning: Could not find column for filtering field '{field_name}' on model '{target_model.__name__}'")
                    continue 
                    
                is_date = field_name in self.date_fields
                wildcard_position = query_params.get(f"{field_name}[$wildcard]", "both")

                filter_clause = None
                if is_date:
                    filter_clause = self.filter_ops.handle_date_filter(column_to_filter, str(param_value), operator)
                elif operator.upper() in ["LIKE", "ILIKE", "NOT_LIKE", "NOT_ILIKE"]:
                    filter_clause = self.operators[operator.upper()](column_to_filter, param_value, wildcard_position)
                else:
                    filter_func = self.operators.get(operator, self.operators["eq"])
                    filter_clause = filter_func(column_to_filter, param_value)

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
                    column = None 
                    
                    if actual_name and hasattr(target_model, actual_name):
                        column = getattr(target_model, actual_name) 
                            
                    if column is not None:
                        order_by_clauses.append(desc(column) if is_desc else asc(column))
                    else:
                        print(f"Warning: Could not find sort column for field '{field_name}' on model '{target_model.__name__}'")
                
            if order_by_clauses:
                self.statement = self.statement.order_by(*order_by_clauses)
        else:
            self.statement = self.statement.order_by(desc(self.main_model.created_at))

        return self.statement

    def paginate(self) -> Select:
        paginated = self.single_table_features.paginate()
        self.statement = self.statement.limit(paginated._limit_clause).offset(paginated._offset_clause)
        
        return self.statement