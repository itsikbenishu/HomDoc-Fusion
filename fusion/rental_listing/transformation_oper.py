from pydantic import ValidationError
from pipeline.operation import Operation
from fusion.rental_listing.transformation import property_listing_transfom

class TransformationOper(Operation):
    def __init__(self):
        super().__init__()  

    def _serialize_pydantic_error(self, validation_error):
        def clean_error(err):
            err = err.copy()
            if "ctx" in err:
                err["ctx"] = {
                    k: str(v) if isinstance(v, Exception) else v
                    for k, v in err["ctx"].items()
                }
            return err

        return [clean_error(err) for err in validation_error.errors()]


    def run(self, input=None):
        property_listing = input

        validated_listings = []
        errors = []

        for item in property_listing:
            try:
                listing = property_listing_transfom(item)
                validated_listings.append(listing)
            except ValidationError as e:
                errors.append({
                    "id": item.get("id"),
                    "errors": self._serialize_pydantic_error(e)
                })
            except Exception as e:
                errors.append({
                    "id": item.get("id"),
                    "error": str(e)  
                })

        print(f"validated: {len(validated_listings)} listings")
        print(f"error: {len(errors)} errors")
        print(errors)

        output = validated_listings

        return output




