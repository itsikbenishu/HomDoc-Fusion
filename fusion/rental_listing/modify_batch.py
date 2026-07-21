import logging
import time
from pipeline.batch import Batch
from sqlmodel import Session
from db.session import engine
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService

logger = logging.getLogger(__name__)


class ModifyBatch(Batch):
    def __init__(self, operation):
        super().__init__(operation)

    def run(self, input):
        data = input
        if not isinstance(data, list):
            raise TypeError("data at Batch must be a list, got {type(data).__name__}")
        output = list()

        residence_repo = ResidenceRepository.get_instance()
        residence_srv = ResidenceService.get_instance(residence_repo)
        subphases = {}

        with Session(engine) as session:
            try:
                self._operation.set_context_value("session", session)

                preload_start = time.perf_counter()
                update_ids = [residence_id for residence_id, _ in data if residence_id]
                preloaded_home_docs = residence_repo.get_by_ids(update_ids, session)
                self._operation.set_context_value("preloaded_home_docs", preloaded_home_docs)
                subphases["preload"] = time.perf_counter() - preload_start

                write_start = time.perf_counter()
                with session.no_autoflush:
                    for elem in data:
                        try:
                            result = self._operation.run(elem)
                            output.append(result)
                        except Exception as e:
                            logger.error(f"Error processing element: {str(e)}")
                            session.rollback()
                            raise Exception(f"Failed to process element: {str(e)}")
                session.flush()
                subphases["write_loop"] = time.perf_counter() - write_start

                all_ids = [home_doc.id for home_doc in output]
                session.commit()
                logger.info(f"Successfully processed {len(output)} elements")

                reload_start = time.perf_counter()
                reloaded_home_docs = residence_repo.get_by_ids(all_ids, session)
                output = [residence_srv.to_response(reloaded_home_docs[home_doc_id]) for home_doc_id in all_ids]
                subphases["reload"] = time.perf_counter() - reload_start

                self.set_context_value(f"{self.__class__.__name__}_subphases", subphases)

            except Exception as e:
                logger.error(f"Batch processing error: {str(e)}")
                session.rollback()
                raise Exception(f"Batch processing failed: {str(e)}")

        return output
