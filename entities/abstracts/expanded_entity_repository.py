from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic, Type, Set
from sqlmodel import Session, SQLModel, select, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import joinedload, selectinload, aliased
from sqlalchemy.sql.selectable import Select
from collections import defaultdict
from entities.abstracts.repository import Repository

class RelationshipType(Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"

class LoadStrategy(Enum):
    JOINED = "joined"
    SELECT_IN = "selectin"

@dataclass
class RelationshipConfig:
    model: Type[SQLModel]
    relationship_type: RelationshipType
    load_strategy: LoadStrategy
    relationship_field: str
    join_for_filter_or_sort: bool = False

PrimaryModelType = TypeVar("PrimaryModelType", bound=SQLModel)

class ExpandedEntityRepository(Repository, Generic[PrimaryModelType], ABC):
    primary_model: Type[PrimaryModelType]
    relationships: List[RelationshipConfig]
    _base_query: Select

    def __init__(self, primary_model: Type[PrimaryModelType], relationships: List[RelationshipConfig]) -> None:
        self.primary_model = primary_model
        self.relationships = relationships
        self._base_query = self._build_base_query()

    def _build_base_query(self) -> Select:
        query = select(self.primary_model)
        model_usage_count = defaultdict(int)
        alias_map = {}

        for rel_config in self.relationships:
            model_key = rel_config.model.__name__
            model_usage_count[model_key] += 1

        for rel_config in self.relationships:
            field_name = rel_config.relationship_field
            model_cls = rel_config.model
            model_key = model_cls.__name__

            # יצירת מפתח ייחודי עבור alias
            alias_key = f"{model_key}_{field_name}"
            
            alias_instance = None
            if model_usage_count[model_key] > 1:
                if alias_key not in alias_map:
                    # יצירת alias עם שם ייחודי מפורש
                    alias_instance = aliased(model_cls, name=alias_key)
                    alias_map[alias_key] = alias_instance
                else:
                    alias_instance = alias_map[alias_key]

            # בדיקת קיום השדה
            try:
                field = getattr(self.primary_model, field_name)
            except AttributeError:
                raise Exception(f"Field '{field_name}' does not exist on {self.primary_model.__name__}")

            # החלטה: JOIN לפילטרים או loading strategy (לא שניהם עם aliases!)
            if rel_config.join_for_filter_or_sort and alias_instance:
                # עם aliases - נעדיף JOIN לפילטרים על פני loading
                query = query.join(field.of_type(alias_instance), isouter=True)
            elif rel_config.join_for_filter_or_sort and not alias_instance:
                # בלי aliases - אפשר גם JOIN וגם loading
                query = query.join(field, isouter=True)
                
                # הוסף loading strategy
                if rel_config.load_strategy == LoadStrategy.JOINED:
                    query = query.options(joinedload(field))
                elif rel_config.load_strategy == LoadStrategy.SELECT_IN:
                    query = query.options(selectinload(field))
            else:
                # רק loading strategy (בלי JOIN לפילטרים)
                if rel_config.load_strategy == LoadStrategy.JOINED:
                    if alias_instance:
                        query = query.options(joinedload(field.of_type(alias_instance)))
                    else:
                        query = query.options(joinedload(field))
                elif rel_config.load_strategy == LoadStrategy.SELECT_IN:
                    if alias_instance:
                        query = query.options(selectinload(field.of_type(alias_instance)))
                    else:
                        query = query.options(selectinload(field))

        return query

    @abstractmethod
    def get_by_id(self, item_id: int, session: Session) -> PrimaryModelType:
        pass

    @abstractmethod
    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[PrimaryModelType]:
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any], session: Session) -> PrimaryModelType:
        pass

    def _create_one_to_one_relationship(
        self,
        model: Type[SQLModel],
        data: dict,
        excluded_fields: list[str]
    ) -> SQLModel:
        new_instance = model(**{
            field_name: field_value 
            for field_name, field_value in data.items() 
            if field_name in model.model_fields 
            and field_name not in excluded_fields
        })
        return new_instance

    def _create_one_to_many_relationship(
        self,
        model: Type[SQLModel],
        data: dict,
        excluded_fields: list[str]
    ) -> SQLModel:
        new_instances = [self._create_one_to_one_relationship(model, item, excluded_fields) 
                         for item in data]
        return new_instances


    def _create_or_get_many_to_one_relationship(
        self,
        session: Session,
        model: Type[SQLModel],
        data: dict,
        unique_fields: list[str]
    ) -> SQLModel:
        create_or_update = insert(model).values(**data).on_conflict_do_nothing(
            index_elements=unique_fields
        ).returning(model.id)

        result = session.exec(create_or_update).first()

        if result:
            return session.get(model, result[0])

        filters = [getattr(model, f) == data[f] for f in unique_fields]
        return session.exec(select(model).where(and_(*filters))).first()
    
    @abstractmethod
    def update(self, item_id: int, data: Dict[str, Any], session: Session) -> PrimaryModelType:
        pass

    def _update_one_to_one_relationship(self, 
                                        relationship_instance: SQLModel, 
                                        data: Dict[str, Any], 
                                        excluded_fields: Set[str]) -> None:
        if relationship_instance:
            fields = set(relationship_instance.model_fields) - excluded_fields
            for field_name, field_value in data.items():
                if field_name in fields:
                    setattr(relationship_instance, field_name, field_value)
    
    def _update_one_to_many_relationship(
        self,
        primary_instance: SQLModel,
        relationship_field: str,
        related_model_class: Type[SQLModel],
        data: List[Dict[str, Any]],
        excluded_fields: Set[str],
        foreign_key_field: str
    ) -> None:
        children = getattr(primary_instance, relationship_field, None)
        if children is None:
            raise ValueError(f"Relationship field '{relationship_field}' not found or not loaded.")

        parent_id_field = foreign_key_field
        children.clear()
        
        for child_data in data:
            new_child = related_model_class(**{
                field_name: field_value
                for field_name, field_value in child_data.items()
                if field_name not in excluded_fields
            })
            setattr(new_child, parent_id_field, primary_instance.id)
            children.append(new_child)

    def _update_many_to_one_relationship(
        self,
        primary_instance: SQLModel,
        relationship_field: str,
        related_model_class: Type[SQLModel],
        data: Dict[str, Any],
        excluded_fields: Set[str],
        session: Session
    ) -> None:
        if not data:
            return

        if "id" in data:
            existing = session.get(related_model_class, data["id"])
            if existing:
                setattr(primary_instance, relationship_field, existing)
                return

        relationship_instance = getattr(primary_instance, relationship_field, None)

        if relationship_instance:
            fields = set(related_model_class.model_fields) - excluded_fields
            for field_name, field_value in data.items():
                if field_name in fields:
                    setattr(relationship_instance, field_name, field_value)
        else:
            new_instance = related_model_class(**{
                field_name: field_value
                for field_name, field_value in data.items()
                if field_name in related_model_class.model_fields and field_name not in excluded_fields
            })
            session.add(new_instance)
            session.flush()
            setattr(primary_instance, relationship_field, new_instance)

    @abstractmethod
    def delete(self, item_id: int, session: Session) -> None:
        pass
    
    def get_related_models(self) -> List[Type[SQLModel]]:
        return [rel.model for rel in self.relationships]
