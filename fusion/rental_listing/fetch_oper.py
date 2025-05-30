import requests
import json
from datetime import datetime, date
from urllib.parse import quote
from pipeline.operation import Operation
from db.constants import select, update_row_by_id
from fusion.rental_listing.api_config import api_settings

class FetchOper(Operation):
    def __init__(self, property_type):
        super().__init__()  
        self._property_type = property_type
        self._folder = "fusion/rental_listing"
        self._api_example_file = "api_example"

    def run(self, input=None):
        res_select = select("SELECT * FROM rentcast_stats WHERE id = %s", (1,))
        rentcast_stats = res_select[0]
        
        print("current rentcast_stats:")
        print(rentcast_stats)
        limit = rentcast_stats["limit_value"]
        offset = rentcast_stats["offset_value"]

        if self._is_payment_date_passed(str(rentcast_stats["next_payment_date"])):
            response = self._fetch(self._property_type, limit, offset)
            rentcast_stats["api_calls_number"] = 1
            rentcast_stats["offset"] = offset +  limit
            update_row_by_id("rentcast_stats", rentcast_stats,1)
            output = response.text
        elif rentcast_stats["api_calls_number"] >= rentcast_stats["api_calls_max_number"]:    
            with open(f'{self._folder}/{self._api_example_file}.json', 'r') as api_example_file:
                api_example = json.load(api_example_file)
            output = api_example
        else:
            response = self._fetch(self._property_type, limit, offset )
            rentcast_stats["api_calls_number"] = rentcast_stats["api_calls_number"] + 1
            rentcast_stats["offset"] = offset +  limit
            update_row_by_id("rentcast_stats", rentcast_stats, 1)
            output = response.text

        print("new rentcast_stats:")
        print(rentcast_stats)
        return output

    def _fetch(self, property_type, limit, offset): 
        quoted_property_type = quote(property_type)
        url = f"{api_settings.RENTCAST_RENTAL_LISTING_API}?propertyType={quoted_property_type}&limit={limit}&offset={offset}"
        headers = {
            "accept": "application/json",
            "X-Api-Key": api_settings.RENTCAST_RENTAL_LISTING_API_KEY
            }

        response = requests.get(url, headers=headers)

        return response

    def _is_payment_date_passed(self, payment_date):
        today = date.today()
        target_date = datetime.strptime(payment_date, "%Y-%m-%d").date()

        if today <= target_date:
            return False
        else:
            return True
