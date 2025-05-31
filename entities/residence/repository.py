from sqlmodel import Session
from entities.home_doc.repository import HomeDocRepository
from entities.utils.decorators import singleton

@singleton
class ResidenceRepository(HomeDocRepository):
    def __init__(self):
        super().__init__()

    def get_by_id(self, item_id: int, session: Session):
        homedoc = super().get_by_id(item_id, session)
        return homedoc

    def get(self, session: Session):
        return {}

    def create(self, data, session: Session):
        return {}

    def update(self, item_id: int, data, session: Session):
        return {}

    def delete(self, item_id: int, session: Session):
        return {}
