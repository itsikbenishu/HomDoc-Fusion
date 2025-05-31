from abc import ABC,abstractmethod
from entities.utils.decorators import singleton


@singleton
class Service(ABC):
    def __init__(self):
        self.repo = None

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
