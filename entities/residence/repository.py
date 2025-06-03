from sqlmodel import Session, select
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.exc import NoResultFound
from entities.home_doc.repository import HomeDocRepository
from entities.home_doc.models import HomeDocs, HomeDocsDimensions
from entities.residence.models import ResidenceSpecsAttributes
from entities.utils.decorators import singleton
from entities.utils.multi_table_features import MultiTableFeatures

@singleton
class ResidenceRepository(HomeDocRepository):
    def __init__(self):
        super().__init__()

    def get_by_id(self, item_id: int, session: Session) -> Tuple[HomeDocs, ResidenceSpecsAttributes, HomeDocsDimensions]:
        statement = (
            select(HomeDocs, ResidenceSpecsAttributes, HomeDocsDimensions)
            .outerjoin(ResidenceSpecsAttributes)
            .outerjoin(HomeDocsDimensions)
            .where(HomeDocs.id == item_id)
        )
        
        result = session.exec(statement).first()
        if not result:
            raise NoResultFound(f"Residence with id {item_id} not found")
            
        return result

    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[Tuple[HomeDocs, ResidenceSpecsAttributes, HomeDocsDimensions]]:        
        base_statement = (
            select(HomeDocs, ResidenceSpecsAttributes, HomeDocsDimensions)
            .outerjoin(ResidenceSpecsAttributes)
            .outerjoin(HomeDocsDimensions)
        )

        models = [HomeDocs, ResidenceSpecsAttributes, HomeDocsDimensions]
        features = MultiTableFeatures(base_statement, models, HomeDocs, query_params)

        statement = features.filter()
        statement = features.sort()
        statement = features.paginate()
                
        results = session.exec(statement).all()
        
        return results

    def create(self, home_doc: HomeDocs, specs: ResidenceSpecsAttributes, dimensions: HomeDocsDimensions, session: Session) -> Tuple[HomeDocs, ResidenceSpecsAttributes, HomeDocsDimensions]:
        created_doc = self._create_home_doc(home_doc, session)
        specs.home_doc_id = created_doc.id
        dimensions.home_doc_id = created_doc.id
        
        created_specs = self._create_specs(specs, session)
        created_dimensions = self._create_dimensions(dimensions, session)
        
        return created_doc, created_specs, created_dimensions

    def update(self, home_doc: HomeDocs, specs: ResidenceSpecsAttributes, dimensions: HomeDocsDimensions, session: Session) -> Tuple[HomeDocs, ResidenceSpecsAttributes, HomeDocsDimensions]:
        session.add(home_doc)
        session.add(specs)
        session.add(dimensions)
        session.flush()
        session.refresh(home_doc)
        session.refresh(specs)
        session.refresh(dimensions)
        
        return home_doc, specs, dimensions

    def _create_home_doc(self, home_doc: HomeDocs, session: Session) -> HomeDocs:
        session.add(home_doc)
        session.flush()
        session.refresh(home_doc)

        return home_doc

    def _create_specs(self, specs: ResidenceSpecsAttributes, session: Session) -> ResidenceSpecsAttributes:
        session.add(specs)
        session.commit()
        session.refresh(specs)

        return specs

    def _update_home_doc(self, home_doc: HomeDocs, session: Session) -> HomeDocs:
        session.add(home_doc)
        session.flush()
        session.refresh(home_doc)

        return home_doc

    def _update_specs(self, specs: ResidenceSpecsAttributes, session: Session) -> ResidenceSpecsAttributes:
        session.add(specs)
        session.commit()
        session.refresh(specs)

        return specs

    def _create_dimensions(self, dimensions: HomeDocsDimensions, session: Session) -> HomeDocsDimensions:
        session.add(dimensions)
        session.flush()
        session.refresh(dimensions)

        return dimensions

    def _update_dimensions(self, dimensions: HomeDocsDimensions, session: Session) -> HomeDocsDimensions:
        session.add(dimensions)
        session.flush()
        session.refresh(dimensions)
        
        return dimensions


