from sqlmodel import Session
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from entities.residence.dtos import ResidenceCreate, ListingContactCreate, ListingHistoryCreate
from entities.common.enums import HomeDocTypeEnum, HomeDocCategoriesEnum, ListingStatusEnum
from fusion.rental_listing.transformation import PropertyListing
from pipeline.operation import Operation
from db.session import engine

class FusionOper(Operation):
    def __init__(self):
        super().__init__()

    def run(self, input):
        residence_repo = ResidenceRepository.get_instance()
        residence_srv = ResidenceService.get_instance(residence_repo)

        with Session(engine) as session:
            try:
                propertyListings = input
                external_ids = []
                rooms_numbers_by_external_ids = {}
  
                for propertyListing in propertyListings:
                    external_ids.append(propertyListing.rentcast_id)
                    rooms_numbers_by_external_ids[propertyListing.rentcast_id] = {
                        "bedrooms": propertyListing.bedrooms,
                        "bathrooms": propertyListing.bathrooms
                    }

                ids_by_external_ids = residence_repo.get_ids_by_external_ids(
                    external_ids,
                    session
                )
                print("ids_by_external_ids:", ids_by_external_ids)

                for propertyListing in propertyListings:
                    if propertyListing.rentcast_id in ids_by_external_ids:
                        propertyListing.home_doc_id = ids_by_external_ids[propertyListing.rentcast_id]

                self.set_context_value("rooms_numbers_by_external_ids", rooms_numbers_by_external_ids)
                output = propertyListings
                print("rooms_numbers_by_external_ids:", rooms_numbers_by_external_ids)
                print("propertyListings:", propertyListings)
                
                return output
            except Exception as e:
                print(f"error: {str(e)}")
                raise

    def property_listing_to_residence(property_listing: PropertyListing) -> ResidenceCreate:
        return ResidenceCreate(
            external_id=property_listing.rentcastId,
            interior_entity_key=property_listing.interiorEntityKey,
            category=HomeDocCategoriesEnum.ONE_STORY_HOUSE,  
            type=HomeDocTypeEnum.PROPERTY, 
            description=None, 
            extra_data=[],
            area=property_listing.area,
            sub_entities_quantity=None,
            construction_year=property_listing.construction_Year,
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

