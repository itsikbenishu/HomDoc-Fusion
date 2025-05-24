
from .FetchOper import FetchOper
from .Pipeline import RentalListPipeline

def run_pipeline(property_type):
    rentalListPipeline = RentalListPipeline()

    rentalListPipeline.add_oper(FetchOper(property_type))

    rentalListPipeline.run()