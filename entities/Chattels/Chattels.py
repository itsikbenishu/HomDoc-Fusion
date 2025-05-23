from dataclasses import dataclass
from entities.HomeDoc import HomeDoc

@dataclass
class Chattels(HomeDoc):
    colors: str
    quantity: str
    weight: str

    def get_by_id(self, item_id):
        return self.repo.get_by_id(item_id)

    def get(self):
        return self.repo.get()

    def create(self, data):
        return self.repo.create(data)

    def update(self, item_id, data):
        return self.repo.update(item_id, data)

    def delete(self, item_id):
        return self.repo.delete(item_id)
