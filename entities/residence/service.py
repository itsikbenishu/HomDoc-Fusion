from sqlmodel import Session
from entities.home_doc.service import HomeDocService
from entities.residence.models import ResidenceResponse, ResidenceSpecsAttributes
from entities.home_doc.models import HomeDocs, HomeDocsDimensions
from entities.utils.decorators import singleton
from typing import Dict, Any, List, Optional
from sqlalchemy.exc import NoResultFound


@singleton
class ResidenceService(HomeDocService):
    def __init__(self, repo):
        super().__init__(repo)

    def get_by_id(self, item_id: int, session: Session) -> ResidenceResponse:
        try:
            home_doc, specs, dimensions = self.repo.get_by_id(item_id, session)
            
            return ResidenceResponse.from_models(home_doc, specs, dimensions)
        except NoResultFound:
            raise ValueError(f"Residence with id {item_id} not found")

    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[ResidenceResponse]:
        results = self.repo.get(session, query_params)
        
        return [ResidenceResponse.from_models(*result) for result in results]

    def create(self, data: Dict[str, Any], session: Session) -> ResidenceResponse:
        try:
            home_doc = HomeDocs(**{
                field_name: field_value 
                for field_name, field_value in data.items() 
                if field_name in HomeDocs.model_fields
            })
            
            specs = ResidenceSpecsAttributes(**{
                field_name: field_value 
                for field_name, field_value in data.items() 
                if field_name in ResidenceSpecsAttributes.model_fields 
                and field_name not in ['id', 'home_doc_id']
            })
            
            dimensions = HomeDocsDimensions(**{
                field_name: field_value 
                for field_name, field_value in data.items() 
                if field_name in HomeDocsDimensions.model_fields 
                and field_name not in ['id', 'home_doc_id']
            })

            created_doc = self.repo.create(home_doc, specs, dimensions, session)
            
            return ResidenceResponse.from_models(*created_doc)
            
        except ValueError as e:
            session.rollback()
            raise ValueError(str(e))
        except Exception as e:
            session.rollback()
            raise Exception(f"Error creating residence record: {str(e)}")

    def update(self, item_id: int, data: Dict[str, Any], session: Session) -> ResidenceResponse:
        try:
            home_doc, specs, dimensions = self.repo.get_by_id(item_id, session)
            
            home_doc_fields = set(home_doc.model_fields) - {'id'}
            for field_name, field_value in data.items():
                if field_name in home_doc_fields:
                    setattr(home_doc, field_name, field_value)
            
            specs_fields = set(specs.model_fields) - {'id', 'home_doc_id'}
            for field_name, field_value in data.items():
                if field_name in specs_fields:
                    setattr(specs, field_name, field_value)
                    
            dimensions_fields = set(dimensions.model_fields) - {'id', 'home_doc_id'}
            for field_name, field_value in data.items():
                if field_name in dimensions_fields:
                    setattr(dimensions, field_name, field_value)
            
            updated_doc = self.repo.update(home_doc, specs, dimensions, session)

            return ResidenceResponse.from_models(*updated_doc)
            
        except Exception as e:
            session.rollback()
            raise Exception(f"Error updating residence record: {str(e)}")

