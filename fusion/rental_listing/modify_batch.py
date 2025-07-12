from pipeline.batch import Batch
from pipeline.operation import Operation
from sqlmodel import Session
from db.session import engine


class ModifyBatch(Batch):
    def __init__(self, operation):
        super().__init__(operation)  

    def run(self, input):
        data = input
        if not isinstance(data, list):
            raise TypeError("data at Batch must be a list, got {type(data).__name__}")
        output = list()

        with Session(engine) as session:
            try:
                self._operation.set_context_value("session", session)
                
                for elem in data:
                    try:
                        result = self._operation.run(elem)
                        output.append(result)
                    except Exception as e:
                        print(f"Error processing element: {str(e)}")
                        session.rollback()
                        raise Exception(f"Failed to process element: {str(e)}")
                
                session.commit()
                print(f"Successfully processed {len(output)} elements")
                
            except Exception as e:
                print(f"Batch processing error: {str(e)}")
                session.rollback()
                raise Exception(f"Batch processing failed: {str(e)}")

        return output
