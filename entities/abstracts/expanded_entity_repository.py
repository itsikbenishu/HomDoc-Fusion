from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic, Type, Set
from sqlmodel import Session, SQLModel, select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.selectable import Select
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

        for rel_config in self.relationships:
            field = getattr(self.primary_model, rel_config.relationship_field)

            if rel_config.load_strategy == LoadStrategy.JOINED:
                query = query.options(joinedload(field))
            elif rel_config.load_strategy == LoadStrategy.SELECT_IN:
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
