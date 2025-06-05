from sqlmodel import Session
from entities.abstracts.expanded_entity_repository import ExpandedEntityRepository
from entities.utils.decorators import singleton
from entities.home_doc.models import HomeDocs

@singleton
class ChattelsRepository(ExpandedEntityRepository[HomeDocs]):
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
