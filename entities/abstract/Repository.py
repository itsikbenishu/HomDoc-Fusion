from abc import ABC, abstractmethod

class Repository(ABC):
    def __init__(self, DB):
        self.DB = DB

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
