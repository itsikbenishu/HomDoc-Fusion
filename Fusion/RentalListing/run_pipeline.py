
from Fusion.RentalListing import FetchOper,Pipeline

def run_pipeline(property_type):
    rentalListPipeline = Pipeline.RentalListPipeline()

    rentalListPipeline.add_oper(FetchOper(property_type))

    rentalListPipeline.run()