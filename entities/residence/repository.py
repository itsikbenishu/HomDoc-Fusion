from sqlmodel import Session,select
from typing import List, Optional, Dict, Any
from entities.abstracts.expanded_entity_repository import ExpandedEntityRepository
from entities.abstracts.expanded_entity_repository import RelationshipConfig, RelationshipType, LoadStrategy
from entities.home_doc.models import HomeDoc, HomeDocDimensions
from entities.residence.models import ResidenceSpecsAttributes, Listing, ListingHistory, ListingContact
from entities.utils.multi_table_features import MultiTableFeatures
from entities.common.enums import HomeDocTypeEnum
from entities.utils.decorators import singleton

@singleton
class ResidenceRepository(ExpandedEntityRepository[HomeDoc]):
    def __init__(self):
        relationships = [
            RelationshipConfig(
                model=ResidenceSpecsAttributes,
                relationship_type=RelationshipType.ONE_TO_ONE,
                load_strategy=LoadStrategy.JOINED,
                relationship_field="specs"
            ),
            RelationshipConfig(
                model=HomeDocDimensions,
                relationship_type=RelationshipType.ONE_TO_ONE,
                load_strategy=LoadStrategy.JOINED,
                relationship_field="dimensions"
            ),
            RelationshipConfig(
                model=HomeDoc,
                relationship_type=RelationshipType.ONE_TO_MANY,
                load_strategy=LoadStrategy.SELECT_IN,
                relationship_field="children"
            ),
            RelationshipConfig(
                model=Listing,
                relationship_type=RelationshipType.ONE_TO_ONE,
                load_strategy=LoadStrategy.JOINED,
                relationship_field="listing"
            ),
            RelationshipConfig(
                model=ListingHistory,
                relationship_type=RelationshipType.ONE_TO_MANY,
                load_strategy=LoadStrategy.SELECT_IN,
                relationship_field="listing_history" 
            ),
            RelationshipConfig(
                model=ListingContact,
                relationship_type=RelationshipType.MANY_TO_ONE,
                load_strategy=LoadStrategy.JOINED,
                relationship_field="listing_agent"
            ),
            RelationshipConfig(
                model=ListingContact,
                relationship_type=RelationshipType.MANY_TO_ONE,
                load_strategy=LoadStrategy.JOINED,
                relationship_field="listing_office"
            ),
        ]
        self.types = [HomeDocTypeEnum.PROPERTY, 
                           HomeDocTypeEnum.FLOOR, 
                           HomeDocTypeEnum.APARTMENT, 
                           HomeDocTypeEnum.ROOM]
        super().__init__(HomeDoc, relationships)

    def get_by_id(self, item_id: int, session: Session) -> HomeDoc:
        residence_filter =HomeDoc.type.in_(self.types)
        statement = self._base_query.where(self.primary_model.id == item_id, residence_filter)
        result = session.exec(statement).one_or_none()
        return result

    def get(self, session: Session, query_params: Optional[Dict[str, Any]] = None) -> List[HomeDoc]:
        all_models = [self.primary_model] + self.get_related_models()
        features = MultiTableFeatures(
            self._base_query, 
            all_models, 
            self.primary_model, 
            date_fields=["createdAt", "updatedAt"],
            query_params=query_params
        )
        statement = features.filter()
        statement = features.sort() 
        statement = features.paginate()

        return session.exec(statement).all()

    def create(self, data: Dict[str, Any], session: Session) -> HomeDoc:
        if 'listing_agent' in data:
            agent = self._create_or_get_many_to_one_relationship(
                session,
                ListingContact,
                data['listing_agent'],
                unique_fields=["name", "phone", "email"]
            )

        if 'listing_office' in data:
            office = self._create_or_get_many_to_one_relationship(
                session,
                ListingContact,
                data['listing_office'],
                unique_fields=["name", "phone", "email"]
            )

        home_doc = HomeDoc(**{
            field_name: field_value 
            for field_name, field_value in data.items() 
            if field_name in HomeDoc.model_fields 
            and field_name not in ['id', 'listing_agent_id', 'listing_office_id']
        })
        home_doc.listing_agent_id = agent.id if agent else None
        home_doc.listing_office_id = office.id if office else None

        specs = self._create_one_to_one_relationship(ResidenceSpecsAttributes,
                                                     data,
                                                     excluded_fields=['id', 'home_doc_id'])        
        dimensions = self._create_one_to_one_relationship(HomeDocDimensions,
                                                     data,
                                                     excluded_fields=['id', 'home_doc_id'])
        listings = self._create_one_to_one_relationship(Listing,
                                                     data,
                                                     excluded_fields=['id', 'home_doc_id'])

        listings_history = self._create_one_to_many_relationship(ListingHistory,
                                                     data.get('listing_history', []),
                                                     excluded_fields=['id', 'residence_id'])
        
        session.add(home_doc)
        session.flush()  
        specs.home_doc_id = home_doc.id
        dimensions.home_doc_id = home_doc.id
        listings.residence_id = home_doc.id
        for listing_history in listings_history:
            listing_history.residence_id = home_doc.id

        session.add(specs)
        session.add(dimensions)
        session.add(listings)
        session.add_all(listings_history)
        session.commit()

        return self.get_by_id(home_doc.id, session)



    def update(self, item_id: int, data: Dict[str, Any], session: Session) -> HomeDoc:
        home_doc = self.get_by_id(item_id, session)

        home_doc_fields = set(HomeDoc.model_fields) - {'id'}
        for field_name, field_value in data.items():
            if field_name in home_doc_fields:
                setattr(home_doc, field_name, field_value)


        self._update_one_to_one_relationship(home_doc.specs, data, {'id', 'home_doc_id'})
        self._update_one_to_one_relationship(home_doc.dimensions, data, {'id', 'home_doc_id'})
        self._update_one_to_one_relationship(home_doc.listing, data, {'id', 'residence_id'})
        
        self._update_many_to_one_relationship(
            primary_instance=home_doc,
            relationship_field="listing_agent",
            related_model_class=ListingContact,
            data=data.get("listing_agent", {}),
            excluded_fields={"id"},
            session=session,
            relationship_attr_name="listing_agent",
        )
        self._update_many_to_one_relationship(
            primary_instance=home_doc,
            relationship_field="listing_office",
            related_model_class=ListingContact,
            data=data.get("listing_office", {}),
            excluded_fields={"id"},
            session=session,
            relationship_attr_name="listing_office",
        )
        
        self._update_one_to_many_relationship(
            primary_instance=home_doc,
            relationship_field="history",
            related_model_class=ListingHistory,
            data=data.get("history", []),
            excluded_fields={"id", "residence_id"},
        )

        session.commit()
        return home_doc

    def delete(self, item_id: int, session: Session) -> None:
        residence_filter = HomeDoc.type.in_(self.types)
        statement = select(self.primary_model).where(self.primary_model.id == item_id, residence_filter)
        result = session.exec(statement).one_or_none()
        if result:
            session.delete(result)
            session.commit()