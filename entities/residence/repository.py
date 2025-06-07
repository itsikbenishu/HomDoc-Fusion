from sqlmodel import Session,select, not_
from typing import List, Optional, Dict, Any
from entities.abstracts.expanded_entity_repository import ExpandedEntityRepository
from entities.abstracts.expanded_entity_repository import RelationshipConfig, RelationshipType, LoadStrategy
from entities.home_doc.models import HomeDocs, HomeDocsDimensions
from entities.residence.models import ResidenceSpecsAttributes
from entities.utils.multi_table_features import MultiTableFeatures
from entities.utils.decorators import singleton

@singleton
class ResidenceRepository(ExpandedEntityRepository[HomeDocs]):
    def __init__(self):
        relationships = [
            RelationshipConfig(
                model=ResidenceSpecsAttributes,
                relationship_type=RelationshipType.ONE_TO_ONE,
                load_strategy=LoadStrategy.JOINED,
                relationship_field="specs"
            ),
            RelationshipConfig(
                model=HomeDocsDimensions,
                relationship_type=RelationshipType.ONE_TO_ONE,
                load_strategy=LoadStrategy.JOINED,
                relationship_field="dimensions"
            ),
            RelationshipConfig(
                model=HomeDocs,
                relationship_type=RelationshipType.ONE_TO_MANY,
                load_strategy=LoadStrategy.SELECT_IN,
                relationship_field="children"
            ),
        ]
        super().__init__(HomeDocs, relationships)

    def get_by_id(self, item_id: int, session: Session) -> HomeDocs:
        residence_filter = not_(HomeDocs.category.like("ROOM\\_%"))
        statement = self._base_query.where(self.primary_model.id == item_id, residence_filter)
        result = session.exec(statement).one_or_none()

        return result

    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[HomeDocs]:
        all_models = [self.primary_model] + self.get_related_models()
        features = MultiTableFeatures(
            self._base_query, 
            all_models, 
            self.primary_model, 
            query_params
        )
        statement = features.filter()
        statement = features.sort() 
        statement = features.paginate()

        return session.exec(statement).all()

    def create(self, data: Dict[str, Any], session: Session) -> HomeDocs:
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
        
        session.add(home_doc)
        session.flush()  
        specs.home_doc_id = home_doc.id
        dimensions.home_doc_id = home_doc.id

        session.add(specs)
        session.add(dimensions)
        session.commit()

        return self.get_by_id(home_doc.id, session)

    def update(self, item_id: int, data: Dict[str, Any], session: Session) -> HomeDocs:
        try:
            home_doc = self.get_by_id(item_id, session)
            
            home_doc_fields = set(HomeDocs.model_fields) - {'id'}
            for field_name, field_value in data.items():
                if field_name in home_doc_fields:
                    setattr(home_doc, field_name, field_value)
            
            if hasattr(home_doc, 'specs') and home_doc.specs:
                specs_fields = set(ResidenceSpecsAttributes.model_fields) - {'id', 'home_doc_id'}
                for field_name, field_value in data.items():
                    if field_name in specs_fields:
                        setattr(home_doc.specs, field_name, field_value)
            
            if hasattr(home_doc, 'dimensions') and home_doc.dimensions:
                dimensions_fields = set(HomeDocsDimensions.model_fields) - {'id', 'home_doc_id'}
                for field_name, field_value in data.items():
                    if field_name in dimensions_fields:
                        setattr(home_doc.dimensions, field_name, field_value)

            session.commit()
            return home_doc
            
        except Exception as e:
            session.rollback()
            raise Exception(f"Error updating residence: {str(e)}")

    def delete(self, item_id: int, session: Session) -> None:
        residence_filter = not_(HomeDocs.category.like("ROOM\\_%"))
        statement = select(self.primary_model).where(self.primary_model.id == item_id, residence_filter)
        result = session.exec(statement).one_or_none()
        if result:
            session.delete(result)
            session.commit()
