from abc import ABC,abstractmethod
from .Repository import Repository

class Controller(ABC):
    def __init__(self, repo):
        pass

    @abstractmethod
    def get_by_id(self, item_id):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def create(self, data):
        pass

    @abstractmethod
    def update(self, item_id, data):
        pass

    @abstractmethod
    def delete(self, item_id):
        pass
