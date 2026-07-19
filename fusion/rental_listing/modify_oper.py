import logging
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from pipeline.operation import Operation

logger = logging.getLogger(__name__)

class ModifyOper(Operation):
    def __init__(self):
        super().__init__()

    def run(self, input):
        residence_repo = ResidenceRepository.get_instance()
        residence_srv = ResidenceService.get_instance(residence_repo)

        session = self.get_context_value("session")
        if not session:
            raise Exception("Session not found in context. Modify Operation must be run within Modify Batch.")

        preloaded_home_docs = self.get_context_value("preloaded_home_docs") or {}

        try:
            residence_id, residence = input

            if(residence_id):
                modified_residence = residence_srv.update(
                    item_id=residence_id,
                    data=residence,
                    session=session,
                    auto_commit=False,
                    preloaded=preloaded_home_docs.get(residence_id),
                    reload=False
                )
                logger.debug(f"Updating a residence with id: {modified_residence.id} and address: {modified_residence.interior_entity_key}")
            else:
                modified_residence = residence_srv.create(
                    data=residence,
                    session=session,
                    auto_commit=False,
                    reload=False
                )
                logger.debug(f"Creating a new residence with id: {modified_residence.id} and address: {modified_residence.interior_entity_key}")
            output = modified_residence

            return output
        except Exception as e:
            logger.error(f"Error in Modify Operation: {str(e)}")
            raise