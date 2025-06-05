from abc import ABC, abstractmethod
from sqlmodel import Session, SQLModel
from typing import Optional, Dict, Any, TypeVar, Generic, List

ModelType = TypeVar("ModelType", bound=SQLModel)

class SingleEntityRepository(ABC, Generic[ModelType]):
    def __init__(self):
        pass

    @abstractmethod
    def get_by_id(self, item_id: int, session: Session) -> ModelType:
        pass

    @abstractmethod
    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[ModelType]:
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
