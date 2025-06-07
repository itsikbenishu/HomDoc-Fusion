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

    def get_by_id(self, item_id: int, session: Session) -> ResidenceResponse:
        try:
            home_doc = self.repo.get_by_id(item_id, session)
            return self._to_response(home_doc)
        except NoResultFound:
            raise ValueError(f"Residence with id {item_id} not found")

    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[ResidenceResponse]:
        query_params["category[$NOTLIKE]"] = "ROOM\\_"
        query_params["category[$wildcard]"] = "end"
        results = self.repo.get(session, query_params)

        return [self._to_response(home_doc) for home_doc in results]

    def create(self, data: Dict[str, Any], session: Session) -> ResidenceResponse:
        self._validate_category(data)
        home_doc = self.repo.create(data, session)
        return self._to_response(home_doc)

    def update(self, item_id: int, data: Dict[str, Any], session: Session) -> ResidenceResponse:
        self._validate_category(data)
        home_doc = self.repo.update(item_id, data, session)
        return self._to_response(home_doc)

    def delete(self, item_id: int, session: Session) -> None:
        try:
            return self.repo.delete(item_id, session)
        except NoResultFound:
            raise ValueError(f"HomeDoc with id {item_id} not found")
        except Exception as e:
            session.rollback()
            raise Exception(f"Error deleting HomeDoc: {str(e)}")


    def _to_response(self, home_doc: HomeDocs) -> ResidenceResponse:
        specs = getattr(home_doc, 'specs', None)
        dimensions = getattr(home_doc, 'dimensions', None)
        
        return ResidenceResponse.from_models(home_doc, specs, dimensions)
    
    def _validate_category(self, data: Dict[str, Any]) -> None:
        category = data.get("category")
        if category and category.startswith("ROOM_"):
            raise ValueError(f"Category '{category}' creation/update is forbidden for residence.")
