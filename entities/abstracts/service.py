from abc import ABC, abstractmethod
from sqlmodel import Session
from typing import Optional, Dict, Any, TypeVar, Generic, List, Union
from entities.utils.decorators import singleton
from entities.abstracts.repository import Repository


ResponseType = TypeVar("ResponseType")  
RepoType = TypeVar("RepoType", bound=Repository)

@singleton
class Service(Generic[ResponseType], ABC):
    def __init__(self, repo: RepoType):
        self.repo = repo

    @abstractmethod
    def get_by_id(self, item_id: int, session: Session) -> ResponseType:
        pass

    @abstractmethod
    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[ResponseType]:
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any], session: Session) -> ResponseType:
        pass

    @abstractmethod
    def update(self, item_id: int, data: Dict[str, Any], session: Session) -> ResponseType:
        pass

    @abstractmethod
    def delete(self, item_id: int, session: Session) -> Union[bool, None]:
        pass
