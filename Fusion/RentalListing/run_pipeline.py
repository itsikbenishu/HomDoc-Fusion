
from .FetchOper import FetchOper
from .Pipeline import Pipeline

def run_pipeline(property_type):
    rentalListPipeline = Pipeline.RentalListPipeline()

    rentalListPipeline.add_oper(FetchOper(property_type))

    rentalListPipeline.run()