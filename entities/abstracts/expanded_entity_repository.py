from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
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

    def delete(self, item_id: int, session: Session) -> None:
        pass
    
    def get_related_models(self) -> List[Type[SQLModel]]:
        return [rel.model for rel in self.relationships]
