import requests
import json

class CarbonInterfaceAPI:
    def __init__(self, api_key):
        self.base_url = "https://www.carboninterface.com/api/v1/estimates"
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_estimate(self, estimate_type, params):
        """ Create an estimate for the given type and parameters """
        try:
            data = {"type": estimate_type, **params}
            response = requests.post(self.base_url, headers=self.headers, json=data)
            if response.status_code in [200,201]:
                return response.json()
            else:
                return {"error": f"Failed to create estimate: {response.text}"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_estimate(self, estimate_id):
        """ Retrieve a specific estimate by its ID """
        try:
            url = f"{self.base_url}/{estimate_id}"
            response = requests.get(url, headers=self.headers)
            if response.status_code in [200,201]:
                return response.json()
            else:
                return {"error": f"Failed to retrieve estimate: {response.text}"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def estimate_electricity(self, electricity_value, country, state=None, electricity_unit='kwh'):
        params = {
            "electricity_value": electricity_value,
            "country": country,
            "state": state if state else "",
            "electricity_unit": electricity_unit
        }
        return self.create_estimate('electricity', params)

    def estimate_flight(self, passengers, legs, distance_unit="km"):
        params = {
            "passengers": passengers,
            "legs": legs,
            "distance_unit": distance_unit
        }
        return self.create_estimate('flight', params)

    def estimate_shipping(self, weight_value, weight_unit, distance_value, distance_unit, transport_method):
        params = {
            "weight_value": weight_value,
            "weight_unit": weight_unit,
            "distance_value": distance_value,
            "distance_unit": distance_unit,
            "transport_method": transport_method
        }
        return self.create_estimate('shipping', params)

    def estimate_fuel_combustion(self, selected_fuel_key, selected_unit, fuel_value):
        params = {
            "fuel_source_type": selected_fuel_key,
            "fuel_source_unit": selected_unit,
            "fuel_source_value": fuel_value
        }
        return self.create_estimate('fuel_combustion', params)
    

    def get_vehicle_makes(self):
        """ Fetch the list of vehicle makes """
        url = "https://www.carboninterface.com/api/v1/vehicle_makes"
        response = requests.get(url, headers=self.headers)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return {"error": f"Failed to fetch vehicle makes: {response.text}"}

    def get_vehicle_models(self, vehicle_make_id):
        """ Fetch vehicle models based on the vehicle make ID """
        url = f"https://www.carboninterface.com/api/v1/vehicle_makes/{vehicle_make_id}/vehicle_models"
        response = requests.get(url, headers=self.headers)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return {"error": f"Failed to fetch vehicle models: {response.text}"}

    def estimate_vehicle(self, distance_value, distance_unit, vehicle_model_id):
        """ Estimate the vehicle emissions based on the trip and vehicle model """
        params = {
            "type": "vehicle",
            "distance_value": distance_value,
            "distance_unit": distance_unit,
            "vehicle_model_id": vehicle_model_id
        }
        return self.create_estimate('vehicle', params)