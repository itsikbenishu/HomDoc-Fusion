from typing import List, Type, Dict, Any, Optional
from sqlalchemy.sql import Select, ColumnElement
from sqlalchemy.orm import class_mapper
from sqlalchemy import desc, asc
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

    def _build_field_maps(self) -> None:
        """
        Creates maps from field names (short and qualified) to their SQLAlchemy Column objects and parent models.
        Short names are allowed only for the main model and ONE_TO_ONE relationships.
        MANY_TO_ONE only gets qualified mapping using relationship_field.
        ONE_TO_MANY is excluded completely.
        """
        self.field_to_column_map: Dict[str, ColumnElement] = {}
        self.field_to_model_map: Dict[str, Type] = {}
        self.relationship_field_to_model_map: Dict[str, Type] = {}
        short_name_collisions: set = set()

        relevant_models = [self.main_model]
        for rel in self.relationships:
            if rel.relationship_type in [RelationshipType.ONE_TO_ONE, RelationshipType.MANY_TO_ONE]:
                relevant_models.append(rel.model)

        for model in relevant_models:
            model_name = model.__name__
            print(f"==={model_name}===")

            try:
                mapper = class_mapper(model)
                for column in mapper.columns:
                    short_field_name = column.key

                    # qualified name depends on relationship type
                    if model == self.main_model:
                        qualified_field_name = f"{model_name}.{short_field_name}"

                    else:
                        rel = next((r for r in self.relationships if r.model == model), None)
                        if not rel:
                            continue

                        if rel.relationship_type == RelationshipType.MANY_TO_ONE:
                            qualified_field_name = f"{rel.relationship_field}.{short_field_name}"
                            # map to support MANY_TO_ONE prefix access like listing_agent.name
                            self.relationship_field_to_model_map[rel.relationship_field] = model

                        elif rel.relationship_type == RelationshipType.ONE_TO_ONE:
                            qualified_field_name = f"{model_name}.{short_field_name}"
                        else:
                            # skip ONE_TO_MANY
                            continue

                    # always add qualified name
                    self.field_to_column_map[qualified_field_name] = column
                    self.field_to_model_map[qualified_field_name] = model

                    # add short names only for main model and ONE_TO_ONE
                    if model == self.main_model or (rel and rel.relationship_type == RelationshipType.ONE_TO_ONE):
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
    
    def _get_column(self, field_name: str) -> Optional[ColumnElement]:
        column = self.field_to_column_map.get(field_name)
        if isinstance(column, ColumnElement):
            return column

        print(f"Warning: Field '{field_name}' is not a valid SQLAlchemy column.")
        return None

    def _find_model_for_field(self, field_name: str) -> Optional[Type]:
        """Finds the model for a field name using the pre-built map (O(1) lookup)."""
        model = self.field_to_model_map.get(field_name)
        if model is None:
            print(f"Warning: Could not find a model for field '{field_name}'.")
        return model
        
    def fields_selection(self) -> "MultiTableFeatures":
        """
        Applies field selection based on the 'fields' query parameter.
        This modifies the existing statement's columns instead of replacing it,
        preserving JOINs and other essential clauses.
        """
        fields_str = self.query_params.get("fields")
        if not fields_str:
            return self

        selected_columns = []
        field_names = [f.strip() for f in fields_str.split(",")]
        
        for field_name in field_names:
            column = self._get_column(field_name)
            if column is not None:
                selected_columns.append(column.label(field_name.replace('.', '_')))

        if selected_columns:
            self.statement = self.statement.with_only_columns(*selected_columns)
        
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
            if column_to_filter is None:
                continue
            
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
                if column is not None:
                    order_by_clauses.append(desc(column) if is_desc else asc(column))
        else:
            default_sort_field = f"{self.main_model.__name__}.createdAt"
            column = self._get_column(default_sort_field)
            if column is not None:
                order_by_clauses.append(desc(column))
        
        if order_by_clauses:
            self.statement = self.statement.order_by(*order_by_clauses)
        
        return self

    def paginate(self) -> "MultiTableFeatures":
        """Applies LIMIT and OFFSET for pagination."""
        # This reuses the logic from SingleTableFeatures but applies it to the current statement
        paginated_statement = self.single_table_features.paginate()
        self.statement = self.statement.limit(paginated_statement._limit_clause).offset(paginated_statement._offset_clause)
        return self
    