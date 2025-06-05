# entities/abstracts/multi_entity_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from sqlmodel import Session, SQLModel, select


PrimaryModelType = TypeVar("PrimaryModelType", bound=SQLModel)

class ExpandedEntityRepository(ABC, Generic[PrimaryModelType]):
    def __init__(self, primary_model: type[PrimaryModelType], related_models: List[type[SQLModel]] ):
        self.primary_model = primary_model
        self.related_models = related_models

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
        statement = select(self.primary_model).where(self.primary_model.id == item_id)
        results = session.exec(statement)
        home_doc = results.one()
        session.delete(home_doc)
        session.commit()
