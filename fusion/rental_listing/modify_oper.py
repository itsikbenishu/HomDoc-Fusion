from sqlmodel import Session
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from pipeline.operation import Operation

class ModifyOper(Operation):
    def __init__(self):
        super().__init__()

    def run(self, input):
        residence_repo = ResidenceRepository.get_instance()
        residence_srv = ResidenceService.get_instance(residence_repo)

        session = self.get_context_value("session")
        if not session:
            raise Exception("Session not found in context. Modify Operation must be run within Modify Batch.")

        try:
            property = input

            if(hasattr(property,"id")):
                modified_residence = residence_srv.update(
                    property,
                    session,
                    auto_commit=False  
                )
                print(f"Updating a property with id: {modified_residence.id} and address: {modified_residence.interior_entity_key}")
            else:
                modified_residence = residence_srv.create(
                    property,
                    session,
                    auto_commit=False  
                )
                print(f"Creating a new property with id: {modified_residence.id} and address: {modified_residence.interior_entity_key}")
            output = modified_residence
            
            return output
        except Exception as e:
            print(f"Error in Modify Operation: {str(e)}")
            raise