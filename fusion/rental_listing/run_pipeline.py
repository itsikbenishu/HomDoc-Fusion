from fusion.rental_listing.pipeline import RentalListPipeline
from fusion.rental_listing.transformation_oper import TransformationOper
from fusion.rental_listing.fusion_oper import FusionOper
from fusion.rental_listing.fetch_oper import FetchOper

def run_pipeline(property_type):
    rental_list_pipeline = RentalListPipeline()

    rental_list_pipeline.add_oper(FetchOper(property_type))
    rental_list_pipeline.add_oper(TransformationOper())
    rental_list_pipeline.add_oper(FusionOper())

    return rental_list_pipeline.run()