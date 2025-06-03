from sqlmodel import Session
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from entities.home_doc.service import HomeDocService
from entities.home_doc.repository import HomeDocRepository
from entities.common.enums import HomeDocCategoriesEnum, HomeDocTypeEnum
from entities.home_doc.models import HomeDocs
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
                # יצירת דירות הבדיקה
                created_residences = []
    
            except Exception as e:
                print(f"שגיאה: {str(e)}")
                session.rollback()
                raise