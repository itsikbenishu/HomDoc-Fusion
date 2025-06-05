from sqlmodel import Session
from typing import List, Dict, Any, Optional
from entities.abstracts.service import Service
from entities.utils.decorators import singleton
from entities.home_doc.models import HomeDocs
from sqlalchemy.exc import NoResultFound
from entities.home_doc.repository import HomeDocRepository

@singleton
class HomeDocService(Service[HomeDocs]):
    def __init__(self, repo: HomeDocRepository):
        super().__init__()
        self.repo = repo

    def get_by_id(self, item_id: int, session: Session) -> HomeDocs:
        return self.repo.get_by_id(item_id, session)

    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[HomeDocs]:
        return self.repo.get(session, query_params)

    def create(self, data: Dict[str, Any], session: Session) -> HomeDocs:
        try:
            home_doc = HomeDocs(**data)
            return self.repo.create(home_doc, session)
        except Exception as e:
            session.rollback()
            raise Exception(f"Error creating HomeDoc: {str(e)}")

    def update(self, item_id: int, data: Dict[str, Any], session: Session) -> HomeDocs:
        try:
            home_doc = self.repo.get_by_id(item_id, session)
            if not home_doc:
                raise ValueError(f"HomeDoc with id {item_id} not found")
            
            for field_name, value in data.items():
                if hasattr(home_doc, field_name):
                    setattr(home_doc, field_name, value)

            return self.repo.update(home_doc, session)
        except NoResultFound:
            raise ValueError(f"HomeDoc with id {item_id} not found")
        except Exception as e:
            session.rollback()
            raise Exception(f"Error updating HomeDoc: {str(e)}")

    def delete(self, item_id: int, session: Session) -> None:
        try:
            return self.repo.delete(item_id, session)
        except NoResultFound:
            raise ValueError(f"HomeDoc with id {item_id} not found")
        except Exception as e:
            session.rollback()
            raise Exception(f"Error deleting HomeDoc: {str(e)}")
