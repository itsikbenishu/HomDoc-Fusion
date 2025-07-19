from sqlmodel import Session
from entities.home_doc.repository import HomeDocRepository
from entities.residence.dtos import ResidenceCreate, ListingContactCreate, ListingHistoryCreate, ResidenceUpdate, ListingContactUpdate, ListingHistoryUpdate
from entities.common.enums import HomeDocTypeEnum, HomeDocCategoriesEnum, ListingStatusEnum
from fusion.rental_listing.transformation import PropertyListing
from pipeline.operation import Operation
from db.session import engine

class FusionOper(Operation):
    def __init__(self):
        super().__init__()

    def run(self, input):
        home_doc_repo = HomeDocRepository.get_instance()

        with Session(engine) as session:
            try:
                property_listings = input
                external_ids = []
                rooms_numbers_by_external_ids = {}
  
                for propertyListing in property_listings:
                    external_ids.append(propertyListing.rentcastId)
                    rooms_numbers_by_external_ids[propertyListing.rentcastId] = {
                        "bedrooms": propertyListing.bedrooms,
                        "bathrooms": propertyListing.bathrooms
                    }

                ids_by_external_ids = home_doc_repo.get_ids_by_external_ids(
                    external_ids,
                    session
                )
                print("ids_by_external_ids:", ids_by_external_ids)
                output = []

                for propertyListing in property_listings:
                    if propertyListing.rentcastId in ids_by_external_ids:
                        residence_id = ids_by_external_ids[propertyListing.rentcastId]
                        output.append((residence_id, self.property_listing_to_update_residence(propertyListing)))
                    else:
                        output.append((None, self.property_listing_to_create_residence(propertyListing)))
                
                self.set_context_value("rooms_numbers_by_external_ids", rooms_numbers_by_external_ids)
                
                print("rooms_numbers_by_external_ids:", rooms_numbers_by_external_ids)
                print("property_listings:", property_listings)
                print("residence:", output)

                return output
            except Exception as e:
                print(f"error: {str(e)}")
                raise

    def property_listing_to_create_residence(self, property_listing: PropertyListing) -> ResidenceCreate:
        return ResidenceCreate(
            external_id=property_listing.rentcastId,
            interior_entity_key=property_listing.interiorEntityKey,
            category=HomeDocCategoriesEnum.ONE_STORY_HOUSE,  
            type=HomeDocTypeEnum.PROPERTY, 
            description=None, 
            extra_data=[],
            area=property_listing.area,
            sub_entities_quantity=None,
            construction_year=property_listing.constructionYear,
            length=None,
            width=None,
            price=property_listing.price,
            hoa_fee=property_listing.hoa.fee if property_listing.hoa else None,
            bedrooms=property_listing.bedrooms,
            bathrooms=property_listing.bathrooms,
            listing_status=property_listing.status or ListingStatusEnum.inactive,
            listing_agent=ListingContactCreate(
                name=property_listing.listingAgent.name if property_listing.listingAgent else None,
                phone=property_listing.listingAgent.phone if property_listing.listingAgent else None,
                email=property_listing.listingAgent.email if property_listing.listingAgent else None,
                website=property_listing.listingAgent.website if property_listing.listingAgent else None,
            ) if property_listing.listingAgent else None,
            listing_office=ListingContactCreate(
                name=property_listing.listingOffice.name if property_listing.listingOffice else None,
                phone=property_listing.listingOffice.phone if property_listing.listingOffice else None,
                email=property_listing.listingOffice.email if property_listing.listingOffice else None,
                website=property_listing.listingOffice.website if property_listing.listingOffice else None,
            ) if property_listing.listingOffice else None,
            listing_history=[
                ListingHistoryCreate(
                    event=item.event,
                    price=item.price,
                    listing_type=item.listingType,
                    listed_date=item.listedDate,
                    removed_date=item.removedDate,
                    days_on_market=item.daysOnMarket
                ) for item in property_listing.history.values()
            ] if property_listing.history else []
        )

    def property_listing_to_update_residence(self, property_listing: PropertyListing) -> ResidenceUpdate:
        return ResidenceUpdate(
            external_id=property_listing.rentcastId,
            description=None, 
            extra_data=[],
            area=property_listing.area,
            sub_entities_quantity=None,
            construction_year=property_listing.constructionYear,
            length=None,
            width=None,
            price=property_listing.price,
            hoa_fee=property_listing.hoa.fee if property_listing.hoa else None,
            bedrooms=property_listing.bedrooms,
            bathrooms=property_listing.bathrooms,
            listing_status=property_listing.status or ListingStatusEnum.inactive,
            listing_agent=ListingContactUpdate(
                name=property_listing.listingAgent.name if property_listing.listingAgent else None,
                phone=property_listing.listingAgent.phone if property_listing.listingAgent else None,
                email=property_listing.listingAgent.email if property_listing.listingAgent else None,
                website=property_listing.listingAgent.website if property_listing.listingAgent else None,
            ) if property_listing.listingAgent else None,
            listing_office=ListingContactUpdate(
                name=property_listing.listingOffice.name if property_listing.listingOffice else None,
                phone=property_listing.listingOffice.phone if property_listing.listingOffice else None,
                email=property_listing.listingOffice.email if property_listing.listingOffice else None,
                website=property_listing.listingOffice.website if property_listing.listingOffice else None,
            ) if property_listing.listingOffice else None,
            listing_history=[
                ListingHistoryUpdate(
                    event=item.event,
                    price=item.price,
                    listing_type=item.listingType,
                    listed_date=item.listedDate,
                    removed_date=item.removedDate,
                    days_on_market=item.daysOnMarket
                ) for item in property_listing.history.values()
            ] if property_listing.history else []
        )
