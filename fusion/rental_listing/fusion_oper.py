from sqlmodel import Session
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from entities.home_doc.service import HomeDocService
from entities.home_doc.repository import HomeDocRepository
from entities.common.enums import HomeDocCategoriesEnum, HomeDocTypeEnum
from entities.home_doc.models import HomeDoc
from pipeline.operation import Operation
from db.session import engine

class FusionOper(Operation):
    def __init__(self):
        super().__init__()

    def run(self, input):
        residence_repo = ResidenceRepository.get_instance()
        residence_srv = ResidenceService.get_instance(residence_repo)
        home_doc_repo = HomeDocRepository.get_instance()
        home_doc_srv = HomeDocService.get_instance(home_doc_repo)

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

                for propertyListing in propertyListings:
                    if propertyListing.rentcast_id in ids_by_external_ids:
                        propertyListing.home_doc_id = ids_by_external_ids[propertyListing.rentcast_id]

            except Exception as e:
                print(f"error: {str(e)}")
                raise
