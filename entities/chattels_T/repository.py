from entities.abstracts_T.repository_T import Repository
from utils.decorators import singleton


@singleton
class ChattelsRepository(Repository):
    def __init__(self):
        super().__init__()  

    def get_by_id(self, item_id):
        return {}
    
    def get(self):
        return {}

    def create(self, data):
        return {}

    def update(self, item_id, data):
        return {}


    def delete(self, item_id):
        return {}
