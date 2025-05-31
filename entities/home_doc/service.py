from sqlmodel import Session
from entities.abstracts.service import Service
from entities.utils.decorators import singleton


@singleton
class HomeDocService(Service):
    def __init__(self, repo):
        super().__init__()
        self.repo = repo

    def get_by_id(self, item_id: int, session: Session):
        return self.repo.get_by_id(item_id, session)

    def get(self, session: Session):
        return self.repo.get(session)

    def create(self, data, session: Session):
        return self.repo.create(data, session)

    def update(self, item_id: int, data, session: Session):
        return self.repo.update(item_id, data, session)

    def delete(self, item_id: int, session: Session):
        return self.repo.delete(item_id, session)
