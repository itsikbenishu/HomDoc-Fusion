from sqlmodel import Session
from entities.abstracts.repository import Repository
from entities.utils.decorators import singleton

@singleton
class ChattelsRepository(Repository):
    def __init__(self):
        super().__init__()

    def get_by_id(self, item_id: int, session: Session):
        return {}

    def get(self, session: Session):
        return {}

    def create(self, data, session: Session):
        return {}

    def update(self, item_id: int, data, session: Session):
        return {}

    def delete(self, item_id: int, session: Session):
        return {}
