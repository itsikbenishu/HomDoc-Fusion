from abc import ABC, abstractmethod
from sqlmodel import Session

class Repository(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_by_id(self, item_id: int, session: Session):
        pass

    @abstractmethod
    def get(self, session: Session):
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
