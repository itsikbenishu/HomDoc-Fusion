from abc import ABC,abstractmethod
from sqlmodel import Session
from typing import Optional, Dict, Any
from entities.utils.decorators import singleton

@singleton
class Service(ABC):
    def __init__(self):
        self.repo = None

    @abstractmethod
    def get_by_id(self, item_id: int, session: Session):
        pass

    @abstractmethod
    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None):
        pass

    @abstractmethod
    def create(self, data, session: Session):
        pass

    @abstractmethod
    def update(self, item_id: int, data, session: Session):
        pass

    @abstractmethod
    def delete(self, item_id: int, session: Session):
        pass
