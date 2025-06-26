from sqlmodel import Session, select
from entities.abstracts.single_entity_repository import SingleEntityRepository
from entities.home_doc.models import HomeDoc
from entities.utils.decorators import singleton
from entities.utils.single_table_features import SingleTableFeatures
from typing import List, Optional, Dict, Any

@singleton
class HomeDocRepository(SingleEntityRepository[HomeDoc]):
    def __init__(self):
        super().__init__()  

    def get_by_id(self, item_id: int, session: Session) -> HomeDoc:
        statement = select(HomeDoc).where(HomeDoc.id == item_id)
        results = session.exec(statement)
        home_doc = results.first()
        return home_doc
    
    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[HomeDoc] | List[Dict[str, Any]]:
        features = SingleTableFeatures(HomeDoc, ["createdAt", "updatedAt"], query_params)
        statement = features.fields_selection().filter().sort().paginate()

        if features.selected_columns:
            results = session.exec(statement).all()
            print(results)
            not_has_tuples_result = len(features.selected_columns) == 1
            if not_has_tuples_result:
                alias = features.selected_columns[0]._label 
                result_list = [{alias: r} for r in results]
            else:
                aliases = [col._label for col in features.selected_columns]
                result_list = [dict(zip(aliases, row)) for row in results]
        else:
            result_list = session.exec(statement).all()

        return result_list

    def create(self, data: HomeDoc, session: Session) -> HomeDoc:
        session.add(data)
        session.commit()
        session.refresh(data)

        return data

    def update(self, home_doc: HomeDoc, session: Session) -> HomeDoc:
        session.add(home_doc)
        session.commit()
        session.refresh(home_doc)

        return home_doc

    def delete(self, item_id: int, session: Session) -> None:
        statement = select(HomeDoc).where(HomeDoc.id == item_id)
        results = session.exec(statement)
        home_doc = results.one_or_none()
        if home_doc:
            session.delete(home_doc)
            session.commit()

    def get_ids_by_external_ids(self, external_ids: List[str], session: Session) -> Dict[str, int]:
        statement = select(HomeDoc.id, HomeDoc.external_id).where(HomeDoc.external_id.in_(external_ids))
        results = session.exec(statement)

        return {result.external_id: result.id for result in results}