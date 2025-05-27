
from Fusion.RentalListing.FetchOper import FetchOper
from Fusion.RentalListing.Pipeline import RentalListPipeline
from Fusion.RentalListing.TransformationOper import TransformationOper

def run_pipeline(property_type):
    rental_list_pipeline = RentalListPipeline()

    rental_list_pipeline.add_oper(FetchOper(property_type))
    rental_list_pipeline.add_oper(TransformationOper())

    return rental_list_pipeline.run()