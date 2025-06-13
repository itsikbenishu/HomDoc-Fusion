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

            alias_instance = None
            if model_usage_count[model_key] > 1:
                if field_name not in alias_map:
                    alias_map[field_name] = aliased(model_cls)
                alias_instance = alias_map[field_name]

            try:
                field = getattr(self.primary_model, field_name)
            except AttributeError:
                raise Exception(f"Field '{field_name}' does not exist on {self.primary_model.__name__}")

            if rel_config.join_for_filter_or_sort:
                if alias_instance:
                    query = query.join(field.of_type(alias_instance), isouter=True)
                else:
                    query = query.join(field, isouter=True)

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
                                        excluded_fields: Set[str],
                                        session: Session) -> None:
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
        excluded_fields: Set[str]
    ) -> None:
        children = getattr(primary_instance, relationship_field, None)
        if children is None:
            raise ValueError(f"Relationship field '{relationship_field}' not found or not loaded.")

        existing_children = {child.id: child for child in children if child.id is not None}
        incoming_children = {item['id']: item for item in data if 'id' in item}

        for child_id, child_data in incoming_children.items():
            if child_id in existing_children:
                for field_name, field_value in child_data.items():
                    if field_name not in excluded_fields and hasattr(existing_children[child_id], field_name):
                        setattr(existing_children[child_id], field_name, field_value)

        for child_data in data:
            if 'id' not in child_data:
                new_child = related_model_class(**{
                    field_name: field_value
                    for field_name, field_value in child_data.items()
                    if field_name not in excluded_fields
                })
                children.append(new_child)

        for child_id in list(existing_children.keys()):
            if child_id not in incoming_children:
                children.remove(existing_children[child_id])

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
