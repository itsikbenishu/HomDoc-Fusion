import requests
import json
from datetime import datetime, date
from urllib.parse import quote
from Pipeline.Operation import Operation
from .apiConfig import api_settings

class FetchOper(Operation):
    def __init__(self, property_type):
        super().__init__()  
        self._property_type = property_type
        self._folder = "Fusion/RentalListing"
        self._rentcast_stats_file = "rentcast_stats"
        self._api_example_file = "api_example"

    def run(self, input=None):
        with open(f'{self._folder}/{self._rentcast_stats_file}.json', 'r') as rentcast_stats_file_r:
            rentcast_stats = json.load(rentcast_stats_file_r)

        print(rentcast_stats)
        limit =  rentcast_stats["limit"]
        offset =  rentcast_stats["offset"]

        if self._is_payment_date_passed(rentcast_stats["next_payment_date"]):
            response = self._fetch(self._property_type, limit, offset )
            rentcast_stats["api_calls_number"] = 1
            rentcast_stats["offset"] = offset +  limit
            output = response.text
        elif rentcast_stats["api_calls_number"] >= rentcast_stats["api_calls_max_number"]:    
            with open(f'{self._folder}/{self._api_example_file}.json', 'r') as api_example_file:
                api_example = json.load(api_example_file)
            output = api_example
        else:
            response = self._fetch(self._property_type, limit, offset )
            rentcast_stats["api_calls_number"] = rentcast_stats["api_calls_number"] + 1
            rentcast_stats["offset"] = offset +  limit
            with open(f'{self._folder}/{self._rentcast_stats_file}.json', 'w') as rentcast_stats_file_w:
                json.dump(rentcast_stats, rentcast_stats_file_w, indent=2)
            output = response.text

        print(rentcast_stats)
        print(output)
        return  output

    def _fetch(property_type, limit, offset): 
        quoted_property_type = quote(property_type)
        url = f"{api_settings.RENTCAST_RENTAL_LISTING_API}?propertyType={quoted_property_type}&limit={limit}&offset={offset}"
        headers = {
            "accept": "application/json",
            "X-Api-Key": api_settings.RENTCAST_RENTAL_LISTING_API_KEY
            }

        response = requests.get(url, headers=headers)

        print(response.text)
        return response

    def _is_payment_date_passed(payment_date):
        today = date.today()
        target_date = datetime.strptime(payment_date, "%Y-%m-%d").date()

        if today <= target_date:
            return False
        else:
            return True
