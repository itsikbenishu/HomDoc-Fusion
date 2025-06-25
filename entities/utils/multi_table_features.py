from typing import List, Type, Dict, Any, Optional
from sqlalchemy.sql import Select, ColumnElement
from sqlalchemy.orm import class_mapper
from sqlalchemy import desc, asc, select
from fastapi import HTTPException
import re
from entities.utils.single_table_features import SingleTableFeatures
from entities.abstracts.expanded_entity_repository import RelationshipConfig, RelationshipType

class MultiTableFeatures:
    def __init__(
        self,
        base_statement: Select,
        models: List[Type],
        main_model: Type,
        relationships: List[RelationshipConfig],
        date_fields: Optional[List[str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ):
        self.base_statement = base_statement
        self.statement = base_statement
        self.models = models
        self.main_model = main_model
        self.relationships = relationships
        self.date_fields = date_fields or []
        self.query_params = query_params or {}
        
        self.single_table_features = SingleTableFeatures(self.main_model, self.query_params)
        self.filter_ops = self.single_table_features.filter_ops
        self.operators = self.single_table_features.operators

        self._build_field_maps()

    def _snake_to_camel(self, snake_str: str) -> str:
        components = snake_str.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])

    def _build_field_maps(self) -> None:
        self.field_to_column_map: Dict[str, ColumnElement] = {}
        self.field_to_model_map: Dict[str, Type] = {}
        self.relationship_field_to_model_map: Dict[str, Type] = {}
        short_name_collisions: set = set()

        model = self.main_model
        model_name = model.__name__
        print(f"==={model_name}===")

        try:
            mapper = class_mapper(model)
            for column in mapper.columns:
                short_field_name = column.key
                qualified_field_name = f"{model_name}.{short_field_name}"

                if short_field_name in self.field_to_column_map:
                    if short_field_name not in short_name_collisions:
                        print(
                            f"Warning: Field name '{short_field_name}' is ambiguous. "
                            f"Use qualified name (e.g., {qualified_field_name})."
                        )
                        del self.field_to_column_map[short_field_name]
                        del self.field_to_model_map[short_field_name]
                        short_name_collisions.add(short_field_name)
                else:
                    self.field_to_column_map[short_field_name] = column
                    self.field_to_model_map[short_field_name] = model

        except Exception as e:
            print(f"Error inspecting model {model_name}: {e}")

        for rel in self.relationships:
            if rel.relationship_type == RelationshipType.ONE_TO_MANY:
                continue
                
            model = rel.model
            model_name = model.__name__
            print(f"==={model_name} ({rel.relationship_field})===")

            try:
                mapper = class_mapper(model)
                for column in mapper.columns:
                    short_field_name = column.key

                    if rel.relationship_type == RelationshipType.MANY_TO_ONE:
                        camel_case_field = self._snake_to_camel(rel.relationship_field)
                        qualified_field_name = f"{camel_case_field}.{short_field_name}"
                        self.relationship_field_to_model_map[camel_case_field] = model

                    elif rel.relationship_type == RelationshipType.ONE_TO_ONE:
                        qualified_field_name = f"{model_name}.{short_field_name}"

                    if rel.relationship_type != RelationshipType.ONE_TO_ONE:
                        self.field_to_column_map[qualified_field_name] = column
                        self.field_to_model_map[qualified_field_name] = model

                    if rel.relationship_type == RelationshipType.ONE_TO_ONE:
                        if short_field_name in self.field_to_column_map:
                            if short_field_name not in short_name_collisions:
                                print(
                                    f"Warning: Field name '{short_field_name}' is ambiguous. "
                                    f"Use qualified name (e.g., {qualified_field_name})."
                                )
                                del self.field_to_column_map[short_field_name]
                                del self.field_to_model_map[short_field_name]
                                short_name_collisions.add(short_field_name)
                        else:
                            self.field_to_column_map[short_field_name] = column
                            self.field_to_model_map[short_field_name] = model

            except Exception as e:
                print(f"Error inspecting model {model_name} ({rel.relationship_field}): {e}")

    def _get_column(self, field_name: str) -> Optional[ColumnElement]:
        column = self.field_to_column_map.get(field_name)
        if isinstance(column, ColumnElement):
            return column

        print(f"Field '{field_name}' is not a valid SQLAlchemy column.")
        
        available_fields = list(self.field_to_column_map.keys())
        similar_fields = [f for f in available_fields if field_name.lower() in f.lower()]
        error_msg = f"Field '{field_name}' not valid column."
        if similar_fields:
            error_msg += f" Did you mean: {', '.join(similar_fields[:3])}?"
        else:
            error_msg += f" You can use one of these: {available_fields}"
        raise HTTPException(status_code=400, detail=error_msg)

    def _find_model_for_field(self, field_name: str) -> Optional[Type]:
        model = self.field_to_model_map.get(field_name)
        if model is None:
            print(f"Warning: Could not find a model for field '{field_name}'.")
        return model
        
    def fields_selection(self) -> "MultiTableFeatures":
        fields_str = self.query_params.get("fields")
        if not fields_str:
            return self

        selected_columns = []
        field_names = [f.strip() for f in fields_str.split(",")]
        
        for field_name in field_names:
            column = self._get_column(field_name)
            selected_columns.append(column.label(field_name.replace('.', '_')))


        if selected_columns:
            self.statement = select(*selected_columns)

            if hasattr(self.base_statement, 'froms') and self.base_statement.froms:
                for from_clause in self.base_statement.froms:
                    self.statement = self.statement.select_from(from_clause)
            
            if hasattr(self.base_statement, 'whereclause') and self.base_statement.whereclause is not None:
                self.statement = self.statement.where(self.base_statement.whereclause)
        
        return self


    def filter(self) -> "MultiTableFeatures":
        excluded_params = {"page", "sort", "limit", "fields", "tz"}
        
        query_params_to_filter = {
            k: v for k, v in self.query_params.items() if k not in excluded_params
        }

        for param_name, param_value in query_params_to_filter.items():
            match = re.match(r'^(.*?)(?:\[\$([a-zA-Z0-9_]+)\])?$', param_name)
            if not match:
                continue
            
            field_name, operator = match.groups()
            operator = operator or "eq"

            if operator in ["date", "wildcard"]:
                continue

            column_to_filter = self._get_column(field_name)
            
            is_date = field_name in self.date_fields
            
            filter_clause = None
            
            if is_date:
                filter_clause = self.filter_ops.handle_date_filter(column_to_filter, str(param_value), operator)
            elif operator.upper() in ["LIKE", "ILIKE", "NOT_LIKE", "NOT_ILIKE"]:
                wildcard_pos = self.query_params.get(f"{field_name}[$wildcard]", "both")
                filter_clause = self.operators[operator.upper()](column_to_filter, param_value, wildcard_pos)
            else:
                filter_func = self.operators.get(operator, self.operators["eq"])
                converted_value = self.single_table_features._convert_value(column_to_filter, param_value)
                filter_clause = filter_func(column_to_filter, converted_value)

            if filter_clause is not None:
                self.statement = self.statement.where(filter_clause)

        return self

    def sort(self) -> "MultiTableFeatures":
        sort_param = self.query_params.get("sort")
        order_by_clauses = []

        if sort_param:
            sort_fields = sort_param.split(",")
            for field in sort_fields:
                is_desc = field.startswith("-")
                field_name = field[1:] if is_desc else field
                
                column = self._get_column(field_name)
                order_by_clauses.append(desc(column) if is_desc else asc(column))
        else:
            default_sort_field = self.single_table_features.default_sort_field
            column = self._get_column(default_sort_field)
            order_by_clauses.append(desc(column))
        
        if order_by_clauses:
            self.statement = self.statement.order_by(*order_by_clauses)
        
        return self

    def paginate(self) -> "MultiTableFeatures":
        paginated_statement = self.single_table_features.paginate()
        self.statement = self.statement.limit(paginated_statement._limit_clause).offset(paginated_statement._offset_clause)
        return self
    