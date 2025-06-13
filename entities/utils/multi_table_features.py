from typing import List, Type, Dict, Any, Optional
from sqlalchemy.sql import Select
from sqlalchemy import desc, asc
import re
from entities.utils.single_table_features import SingleTableFeatures

class MultiTableFeatures:
    def __init__(
        self,
        base_statement: Select,
        models: List[Type],
        main_model: Type,
        date_fields: Optional[List[str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ):
        self.models = models
        self.main_model = main_model
        self.date_fields = date_fields or []
        self.query_params = query_params or {}
        self.single_table_features = SingleTableFeatures(self.main_model, self.query_params)

        self.filter_ops = self.single_table_features.filter_ops
        self.operators = self.single_table_features.operators

        self.columns_with_aliases = self._build_columns_with_aliases(base_statement)

        fields_str = self.query_params.get("fields")
        if fields_str:
            field_names = [f.strip() for f in fields_str.split(",")]
            columns = []
            for field_name in field_names:
                column_label = self._get_column(field_name)
                if column_label is not None:
                    columns.append(column_label)
            self.statement = Select(*columns).select_from(base_statement.froms[0]) if columns else base_statement
        else:
            self.statement = base_statement

    def _build_columns_with_aliases(self, statement: Select) -> Dict[str, Any]:
        columns = {}
        for model in self.models:
            model_name = model.__name__
            for field_name, field_info in model.model_fields.items():
                alias = getattr(field_info, "alias", None) or field_name

                metadata = getattr(field_info, "metadata", [])
                metadata_dict = dict(metadata)
                column_name = metadata_dict.get("name", field_name)

                # חיפוש בעמודות של השאילתא - statement.get_final_froms()
                for from_ in statement.get_final_froms():
                    if hasattr(from_, "c") and column_name in from_.c:
                        col = from_.c[column_name]
                        key_alias = f"{model_name}.{alias}"
                        key_field = f"{model_name}.{field_name}"
                        columns[key_alias] = col.label(key_alias)
                        columns[key_field] = col.label(key_alias)
                        break

        return columns

    def build(self) -> Select:
        return self.statement

    def _find_model_for_field(self, field_name: str) -> Optional[Type]:
        """
        מוצא את המודל שבו נמצא השדה או האליאס, גם אם השדה כולל שם מודל (model.field)
        """
        # אם השדה מגיע בצורה "ModelName.field", נפרק את זה:
        if "." in field_name:
            model_name, simple_field_name = field_name.split(".", 1)
            for model in self.models:
                if model.__name__ == model_name:
                    return model
            return None

        # אחרת מחפשים לפי alias או שם שדה בכל המודלים
        for model in self.models:
            for field_name_in_model, field_info in model.model_fields.items():
                alias = getattr(field_info, "alias", None) or field_name_in_model
                if alias == field_name or field_name_in_model == field_name:
                    return model
        return None

    def _get_column(self, field_name: str):
        """
        מחזיר את העמודה עם label לפי השם או האליאס, תומך ב-"ModelName.field" או רק "field"
        """
        print(f"Looking for column: {field_name}")
        print(f"Looking for column: {self.columns_with_aliases}")

        if "." in field_name:
            # חיפוש ישיר במפתחות המלאים
            if field_name in self.columns_with_aliases:
                return self.columns_with_aliases[field_name]
            else:
                # אם אין, אפשר לנסות גם בלי שם מודל, אם קיים שם שדה בלבד
                _, simple_field = field_name.split(".", 1)
                # חיפוש לפי שדה בלבד - מחזיר את הראשון שמצאנו במודל כלשהו (פחות מדויק)
                for key, col in self.columns_with_aliases.items():
                    if key.endswith(f".{simple_field}"):
                        return col
                return None
        else:
            # אם אין שם מודל, מנסים למצוא עמודה לפי alias בכל המודלים
            # אם יש כמה מודלים עם אותו alias, נחזיר את הראשון (לא מושלם, מומלץ להעביר תמיד שם מודל)
            for key, col in self.columns_with_aliases.items():
                if key.endswith(f".{field_name}"):
                    return col
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
            if not match:
                continue
            field_name = match.group(1)
            operator = match.group(2) if match.group(2) else "eq"

            if operator in ["date", "wildcard"]:
                continue

            target_model = self._find_model_for_field(field_name)
            if not target_model:
                continue

            column_to_filter = self._get_column(field_name)
            if column_to_filter is None:
                print(f"Warning: Could not find column for filtering field '{field_name}'")
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

                column = self._get_column(field_name)
                if column is not None:
                    order_by_clauses.append(desc(column) if is_desc else asc(column))
                else:
                    print(f"Warning: Could not find sort column for field '{field_name}'")

            if order_by_clauses:
                self.statement = self.statement.order_by(*order_by_clauses)
        else:
            # מיון ברירת מחדל לפי created_at יורד
            default_col = self.columns_with_aliases.get(f"{self.main_model.__name__}.createdAt") \
                        or getattr(self.main_model, "created_at", None)
            if default_col is not None:
                self.statement = self.statement.order_by(desc(default_col))

        return self.statement

    def paginate(self) -> Select:
        paginated = self.single_table_features.paginate()
        self.statement = self.statement.limit(paginated._limit_clause).offset(paginated._offset_clause)
        return self.statement
