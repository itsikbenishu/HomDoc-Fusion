from abc import ABC, abstractmethod
from sqlmodel import Session, SQLModel
from typing import Optional, Dict, Any, TypeVar, Generic, List
from entities.abstracts.repository import Repository

ModelType = TypeVar("ModelType", bound=SQLModel)

class SingleEntityRepository(Repository, Generic[ModelType]):
    def __init__(self):
        pass

    @abstractmethod
    def get_by_id(self, item_id: int, session: Session) -> ModelType:
        pass

    @abstractmethod
    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[ModelType] | List[Dict[str, Any]]:
        pass

    @abstractmethod
    def create(self, data: ModelType, session: Session) -> ModelType:
        pass

    @abstractmethod
    def update(self, data: ModelType, session: Session) -> ModelType:
        pass

    @abstractmethod
    def delete(self, item_id: int, session: Session) -> None:
        pass
