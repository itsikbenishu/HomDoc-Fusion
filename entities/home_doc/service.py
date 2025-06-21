from sqlmodel import Session
from typing import List, Dict, Any, Optional
from entities.abstracts.service import Service
from entities.utils.decorators import singleton
from entities.home_doc.models import HomeDoc
from sqlalchemy.exc import NoResultFound
from entities.home_doc.repository import HomeDocRepository
from entities.home_doc.dtos import HomeDocCreate, HomeDocUpdate

@singleton
class HomeDocService(Service[HomeDoc, HomeDocRepository, HomeDocCreate, HomeDocUpdate]):
    def __init__(self, repo: HomeDocRepository):
        super().__init__(repo)

    def get_by_id(self, item_id: int, session: Session) -> HomeDoc:
        return self.repo.get_by_id(item_id, session)

    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[HomeDoc] | List[Dict[str, Any]]:
        return self.repo.get(session, query_params)

    def create(self, data: HomeDocCreate, session: Session) -> HomeDoc:
        try:
            self._validate_entity(data)
            home_doc_dict = data.model_dump(exclude_unset=True)
            home_doc = HomeDoc(**home_doc_dict)
            return self.repo.create(home_doc, session)
        except Exception as e:
            session.rollback()
            raise Exception(f"Error creating HomeDoc: {str(e)}")

    def update(self, item_id: int, data: HomeDocUpdate, session: Session) -> HomeDoc:
        try:
            self._validate_entity(data)
            home_doc = self.repo.get_by_id(item_id, session)
            if not home_doc:
                raise ValueError(f"HomeDoc with id {item_id} not found")
            
            home_doc_dict = data.model_dump(exclude_unset=True)
            for field_name, value in home_doc_dict.items():
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

    def _validate_entity(self, data: Dict[str, Any]) -> None:
        if data.get("type") != "PROPERTY":
            raise ValueError(f"Type '{data.get('type')}' is forbidden for entity' maybe it's a sub entity.")

    def _validate_sub_entity(self, data: Dict[str, Any]) -> None:
        if data.get("father_id") and data.get("father_interior_entity_key") and data.get("type") == "PROPERTY":
            raise ValueError(f"Father id and father interior entity key are forbidden for property.")
        if not data.get("father_id") and data.get("type") != "PROPERTY":
            raise ValueError(f"Father id is required.")
        if data.get("type") == "PROPERTY":
            raise ValueError(f"Type {data.get('type')} is forbidden for sub entity.")
