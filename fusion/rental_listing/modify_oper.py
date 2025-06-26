from sqlmodel import Session
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from entities.home_doc.service import HomeDocService
from entities.home_doc.repository import HomeDocRepository
from entities.common.enums import HomeDocCategoriesEnum, HomeDocTypeEnum
from entities.home_doc.models import HomeDoc
from pipeline.operation import Operation
from db.session import engine

class ModifyOper(Operation):
    def __init__(self):
        super().__init__()

    def run(self, input):
        residence_repo = ResidenceRepository.get_instance()
        residence_srv = ResidenceService.get_instance(residence_repo)

        with Session(engine) as session:
            try:
                property = input

                if(hasattr(property,"id")):
                    residence_srv.updtae(
                        property,
                        session
                    )
                else:
                    residence_srv.create(
                        property,
                        session
                    )
                output = property
                
                return output
            except Exception as e:
                print(f"error: {str(e)}")
                raise