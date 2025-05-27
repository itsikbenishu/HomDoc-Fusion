from entities.Abstracts.Controller import Controller
from utils.decorators import singleton


@singleton
class ctrl(Controller):
    def __init__(self, repo):
        super().__init__()  
        self.repo = repo

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
