from sqlmodel import Session
from pipeline.operation import Operation
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from db.session import engine

class FusionOper(Operation):
    def __init__(self):
        super().__init__()

    def run(self, input):
        residence_repo = ResidenceRepository.get_instance()
        residence_srv = ResidenceService.get_instance(residence_repo)

        with Session(engine) as session:
            result = residence_srv.get_by_id(575, session)
            print(result)
