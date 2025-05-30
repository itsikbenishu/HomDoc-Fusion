
from fusion.rental_listing.fetch_oper import FetchOper
from fusion.rental_listing.pipeline import RentalListPipeline
from fusion.rental_listing.transformation_oper import TransformationOper

def run_pipeline(property_type):
    rental_list_pipeline = RentalListPipeline()

    rental_list_pipeline.add_oper(FetchOper(property_type))
    rental_list_pipeline.add_oper(TransformationOper())

    return rental_list_pipeline.run()