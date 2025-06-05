from sqlmodel import Session, select
from entities.abstracts.repository import Repository
from entities.home_doc.models import HomeDocs
from entities.utils.decorators import singleton
from entities.utils.single_table_features import SingleTableFeatures
from typing import List, Optional, Dict, Any

@singleton
class HomeDocRepository(Repository):
    def __init__(self):
        super().__init__()  

    def get_by_id(self, item_id: int, session: Session) -> HomeDocs:
        statement = select(HomeDocs).where(HomeDocs.id == item_id)
        results = session.exec(statement)
        home_doc = results.one()
        return home_doc
    
    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[HomeDocs]:
        features = SingleTableFeatures(HomeDocs, query_params)
        statement = features.filter().sort().paginate()
        results = session.exec(statement)
        result_list = list(results)
        
        return result_list

    def create(self, data: HomeDocs, session: Session) -> HomeDocs:
        session.add(data)
        session.commit()
        session.refresh(data)

        return data

    def update(self, home_doc: HomeDocs, session: Session) -> HomeDocs:
        session.add(home_doc)
        session.commit()
        session.refresh(home_doc)

        return home_doc

    def delete(self, item_id: int, session: Session) -> None:
        statement = select(HomeDocs).where(HomeDocs.id == item_id)
        results = session.exec(statement)
        home_doc = results.one()
        session.delete(home_doc)
        session.commit()

    def get_ids_by_external_ids(self, external_ids: List[str], session: Session) -> Dict[str, int]:
        statement = select(HomeDocs.id, HomeDocs.external_id).where(HomeDocs.external_id.in_(external_ids))
        results = session.exec(statement)

        return {result.external_id: result.id for result in results}