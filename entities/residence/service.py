from sqlmodel import Session
from entities.abstracts.service import Service
from entities.residence.models import ResidenceResponse
from entities.residence.repository import ResidenceRepository
from entities.home_doc.models import HomeDocs
from entities.utils.decorators import singleton
from typing import Dict, Any, List, Optional
from sqlalchemy.exc import NoResultFound

@singleton
class ResidenceService(Service[ResidenceResponse, ResidenceRepository]):
    def __init__(self, repo: ResidenceRepository):
        super().__init__(repo)

    def get_by_id(self, item_id: int, session: Session) -> Optional[ResidenceResponse]:
        home_doc = self.repo.get_by_id(item_id, session)
        if not home_doc:
            return None
        return self._to_response(home_doc)

    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> Optional[List[ResidenceResponse]]:
        if query_params is None:
            query_params = {}
        query_params["category[$NOTLIKE]"] = "ROOM\\_"
        query_params["category[$wildcard]"] = "end"
        
        results = self.repo.get(session, query_params)
        if not results:
            return None
        return [self._to_response(home_doc) for home_doc in results]

    def create(self, data: Dict[str, Any], session: Session) -> ResidenceResponse:
        try:
            self._validate_entity(data)
            home_doc = self.repo.create(data, session)
            return self._to_response(home_doc)
        except ValueError:
            raise
        except Exception as e:
            session.rollback()
            raise Exception(f"Error creating residence: {str(e)}")

    def update(self, item_id: int, data: Dict[str, Any], session: Session) -> ResidenceResponse:
        try:
            self._validate_entity(data)
            home_doc = self.repo.update(item_id, data, session)
            if not home_doc:
                raise ValueError(f"Residence with id {item_id} not found")
            return self._to_response(home_doc)
        except ValueError:
            raise
        except Exception as e:
            session.rollback()
            raise Exception(f"Error updating residence with id {item_id}: {str(e)}")

    def delete(self, item_id: int, session: Session) -> None:
        try:
            self.repo.delete(item_id, session)
        except Exception as e:
            session.rollback()
            raise Exception(f"Error deleting residence with id {item_id}: {str(e)}")

    def _to_response(self, home_doc: HomeDocs) -> ResidenceResponse:
        specs = getattr(home_doc, 'specs', None)
        dimensions = getattr(home_doc, 'dimensions', None)
        
        return ResidenceResponse.from_models(home_doc, specs, dimensions)
    
    def _validate_entity(self, data: Dict[str, Any]) -> None:
        category = data.get("category")
        if category and category.startswith("ROOM_"):
            raise ValueError(f"Category '{category}' is forbidden for residence. it's maybe a chattels entity")
        if data.get("type") != "PROPERTY":
            raise ValueError(f"Type '{data.get('type')}' is forbidden for entity' maybe it's a sub entity.")

    def _validate_sub_entity(self, data: Dict[str, Any]) -> None:
        category = data.get("category")
        if category and category.startswith("ROOM_"):
            raise ValueError(f"Category '{category}' is forbidden for residence. it's maybe a chattels entity")
        if data.get("father_id") and data.get("father_interior_entity_key") and data.get("type") == "PROPERTY":
            raise ValueError(f"Father id and father interior entity key are forbidden for property.")
        if not data.get("father_id") and data.get("type") != "PROPERTY":
            raise ValueError(f"Father id is required.")
        if data.get("type") == "PROPERTY":
            raise ValueError(f"Type {data.get('type')} is forbidden for sub entity.")