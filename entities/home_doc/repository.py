from sqlmodel import Session, select
from entities.abstracts.repository import Repository
from entities.home_doc.models import HomeDocs
from entities.utils.decorators import singleton

@singleton
class HomeDocRepository(Repository):
    def __init__(self):
        super().__init__()  

    def get_by_id(self, item_id: int, session: Session):
        statement = select(HomeDocs).where(HomeDocs.id == item_id)
        results = session.exec(statement)
        home_doc = results.one()
        print("home_doc:", home_doc)

        return home_doc
    
    def get(self, session: Session):
        return {}

    def create(self, data, session: Session):
        return {}

    def update(self, item_id: int, data, session: Session):
        return {}


    def delete(self, item_id: int, session: Session):
        return {}
