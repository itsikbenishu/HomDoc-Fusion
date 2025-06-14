from sqlmodel import Session
from entities.utils.decorators import singleton
from typing import Dict, Any, List, Optional
from entities.abstracts.service import Service
from entities.residence.dtos import ResidenceResponse, ResidenceCreate, ResidenceUpdate
from entities.residence.repository import ResidenceRepository
from entities.common.enums import HomeDocTypeEnum
from entities.home_doc.models import HomeDoc

@singleton
class ResidenceService(Service[ResidenceResponse, ResidenceRepository, ResidenceCreate, ResidenceUpdate]):
    def __init__(self, repo: ResidenceRepository):
        super().__init__(repo)
        self.types = [HomeDocTypeEnum.PROPERTY,
                       HomeDocTypeEnum.FLOOR,
                       HomeDocTypeEnum.APARTMENT, 
                       HomeDocTypeEnum.ROOM]

    def get_by_id(self, item_id: int, session: Session) -> Optional[ResidenceResponse]:
        home_doc = self.repo.get_by_id(item_id, session)
        if not home_doc:
            return None
        return self._to_response(home_doc)

    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> Optional[List[ResidenceResponse]]:
        if query_params is None:
            query_params = {}
        query_params["type[$in]"] = self.types
        
        results = self.repo.get(session, query_params)
        if not results:
            return None
        return [self._to_response(home_doc) for home_doc in results]

    def create(self, data: ResidenceCreate, session: Session) -> ResidenceResponse:
        try:
            residence_dict = data.model_dump(exclude_unset=True)
            self._validate_entity(residence_dict)
            
            home_doc = self.repo.create(residence_dict, session)
            return self._to_response(home_doc)
        except ValueError:
            raise
        except Exception as e:
            session.rollback()
            raise Exception(f"Error creating residence: {str(e)}")

    def update(self, item_id: int, data: ResidenceUpdate, session: Session) -> ResidenceResponse:
        try:
            # המרת ResidenceUpdate ל-dict
            residence_dict = data.model_dump(exclude_unset=True)
            self._validate_entity(residence_dict)
            
            home_doc = self.repo.update(item_id, residence_dict, session)
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

    def _to_response(self, home_doc: HomeDoc) -> ResidenceResponse:
        specs = getattr(home_doc, 'specs', None)
        dimensions = getattr(home_doc, 'dimensions', None)
        listing = getattr(home_doc, 'listing', None)
        listing_agent = getattr(home_doc, 'listing_agent', None)
        listing_office = getattr(home_doc, 'listing_office', None)
        listing_history = getattr(home_doc, 'listing_history', None)

        return ResidenceResponse.from_models(home_doc=home_doc, 
                                             specs=specs, 
                                             dimensions=dimensions,
                                             listing=listing, 
                                             listing_agent=listing_agent, 
                                             listing_office=listing_office,
                                             listing_history=listing_history)
    
    def _validate_entity(self, data: Dict[str, Any]) -> None:
        category = data.get("category")
        type = data.get("type")
        if category and category.startswith("ROOM_"):
            raise ValueError(f"Category '{category}' is forbidden for residence. it's maybe a chattels entity")
        if type and type != "PROPERTY":
            raise ValueError(f"Type '{type}' is forbidden for entity' maybe it's a sub entity.")

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