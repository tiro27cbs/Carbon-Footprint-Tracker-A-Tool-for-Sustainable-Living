from api_handler import CarbonInterfaceAPI
from data_analysis import DataAnalysis
from data import FUEL_SOURCES, COUNTRY_CODES
import re


class UserInterface:
    def __init__(self, api_key):
        self.api = CarbonInterfaceAPI(api_key)
        self.data_analysis = DataAnalysis()  # Shared data analysis instance
        self.emission_estimates = EmissionEstimates(self.api, self.data_analysis)
        self.data_analysis_interface = DataAnalysisInterface(self.data_analysis)
        self.user_id = None  # Store user ID

    def run(self):
        print("Welcome to the Carbon Emission Tracker!")
        self.user_id = input("Please enter your User ID: ").strip()

        while True:
            print("\nMain Menu:")
            print("1. Estimate Emissions")
            print("2. View Emission Data")
            print("3. Switch User")
            print("0. Exit")

            main_choice = input("Enter the number of your choice: ")

            if main_choice == "1":
                self.run_estimate_emissions()
            elif main_choice == "2":
                self.run_view_emission_data()
            elif main_choice == "3":
                self.switch_user()
            elif main_choice == "0":
                print("Exiting program.")
                break
            else:
                print("Invalid choice, please try again.")

    def run_estimate_emissions(self):
        while True:
            print("\nSelect Estimate Type:")
            print("1. Electricity Emissions")
            print("2. Flight Emissions")
            print("3. Shipping Emissions")
            print("4. Fuel Combustion")
            print("5. Vehicle Emissions")
            print("0. Back to Main Menu")

            choice = input("Enter the number of your choice: ")

            if choice in ["1", "2", "3", "4", "5"]:
                self.emission_estimates.handle_choice(choice, self.user_id)
            elif choice == "0":
                break
            else:
                print("Invalid choice, please try again.")

    def run_view_emission_data(self):
        while True:
            print("\nView Emission Data:")
            print("1. Show Emission Data")
            print("2. Sort Emission Data")
            print("3. Visualize Emissions")
            print("4. Remove All Emission Data")
            print("5. Show Leaderboard")
            print("0. Back to Main Menu")

            choice = input("Enter the number of your choice: ")

            if choice in ["1", "2", "3", "4", "5"]:
                self.data_analysis_interface.handle_choice(choice, self.user_id)
            elif choice == "0":
                break
            else:
                print("Invalid choice, please try again.")

    def switch_user(self):
        new_user_id = input("\nEnter new User ID: ").strip()
        if new_user_id:
            self.user_id = new_user_id
            print(f"User ID successfully switched to: {self.user_id}")
        else:
            print("Invalid User ID. Please try again.")

class EmissionEstimates:
    def __init__(self, api, data_analysis):
        self.api = api
        self.data_analysis = data_analysis

    def handle_choice(self, choice, user_id):
        if choice == "1":
            self.handle_electricity(user_id)
        elif choice == "2":
            self.handle_flight(user_id)
        elif choice == "3":
            self.handle_shipping(user_id)
        elif choice == "4":
            self.handle_fuel_combustion(user_id)
        elif choice == "5":
            self.handle_vehicle(user_id)

    def handle_electricity(self, user_id):
        # Option to display possible countries and codes
        show_countries = input("Would you like to see a list of possible country codes? (y/n): ").lower()
        if show_countries == "y":
            print("\nAvailable Country Codes:")
            for code, name in COUNTRY_CODES.items():
                print(f"  - {name} ({code})")
        country = input("Enter country code (e.g., 'US'): ").upper()
        try:
            electricity_value = float(input("Enter electricity value (in kWh): "))
        except ValueError:
            print("Invalid value. Please enter a numeric value.")
            return

        if country not in COUNTRY_CODES:
            print("Invalid country code. Please refer to the list above.")
            return

        response = self.api.estimate_electricity(electricity_value, country)
        self.process_response(response, "Electricity Emissions", "Electricity", user_id)


    def handle_flight(self, user_id):
        passengers = int(input("Enter number of passengers: "))
        legs = []
        while True:
            print('Here you can find all IATA codes for airports: https://www.iata.org/en/publications/directories/code-search/')
            departure_airport = input("Enter departure airport code (IATA): ")
            destination_airport = input("Enter destination airport code (IATA): ")
            legs.append({"departure_airport": departure_airport, "destination_airport": destination_airport})
            more_legs = input("Do you want to add another leg? (y/n): ")
            if more_legs.lower() != "y":
                break
        response = self.api.estimate_flight(passengers, legs)
        self.process_response(response, "Flight Emissions", "Flight", user_id)

    def handle_shipping(self,user_id):
        weight_value = float(input("Enter weight value: "))
        weight_unit = input("Enter weight unit (g, lb, kg, mt): ")
        distance_value = float(input("Enter distance value: "))
        distance_unit = input("Enter distance unit (km or mi): ")
        transport_method = input("Enter transport method (ship, train, truck, plane): ")
        response = self.api.estimate_shipping(weight_value, weight_unit, distance_value, distance_unit, transport_method)
        self.process_response(response, "Shipping Emissions", "Shipping", user_id)


    def handle_fuel_combustion(self, user_id):
        # Ask if the user wants to see the available fuel types and units
        show_fuels = input("Would you like to see a list of possible fuel types and units? (y/n): ").lower()
        
        if show_fuels == "y":
            print("\nAvailable Fuel Types and Units:")
            for idx, (api_name, info) in enumerate(FUEL_SOURCES.items(), start=1):
                print(f"{idx}. {info['name']} ({api_name}): {', '.join(info['units'])}")

        # Ask the user to select a fuel source by number
        try:
            fuel_choice = int(input("\nSelect a fuel by entering its number: "))
            if not 1 <= fuel_choice <= len(FUEL_SOURCES):
                print("Invalid fuel selection. Please try again.")
                return
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return

        # Get the selected fuel based on the user's input
        selected_fuel_key = list(FUEL_SOURCES.keys())[fuel_choice - 1]
        selected_fuel_name = FUEL_SOURCES[selected_fuel_key]['name']
        selected_fuel_units = FUEL_SOURCES[selected_fuel_key]['units']

        # Display the selected fuel
        print(f"\nYou selected: {selected_fuel_name}")
        print(f"Units available for {selected_fuel_name}:")
        
        # Display available units for the selected fuel
        for idx, unit in enumerate(selected_fuel_units, start=1):
            print(f"{idx}. {unit}")
        
        # Ask the user to select a unit
        try:
            unit_choice = int(input("\nSelect a unit by entering its number: "))
            if not 1 <= unit_choice <= len(selected_fuel_units):
                print("Invalid unit selection. Please try again.")
                return
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return
        
        # Get the selected unit based on user input
        selected_unit = selected_fuel_units[unit_choice - 1]

        # Ask the user to input the amount of fuel consumed
        try:
            fuel_value = float(input(f"Enter the amount of {selected_fuel_name} consumed (in {selected_unit}): "))
        except ValueError:
            print("Invalid value. Please enter a numeric value.")
            return
        
        # Assuming the API call for fuel combustion estimation using the correct variables:
        response = self.api.estimate_fuel_combustion(selected_fuel_key, selected_unit, fuel_value)
        self.process_response(response, "Fuel Combustion Emissions", "Fuel Combustion", user_id)





    def handle_vehicle(self, user_id):
        # Step 1: Get the list of vehicle makes
        print("Fetching vehicle makes...")
        vehicle_makes_response = self.api.get_vehicle_makes()

        if not isinstance(vehicle_makes_response, list) or not vehicle_makes_response:
            print(f"Error fetching vehicle makes: {vehicle_makes_response if isinstance(vehicle_makes_response, dict) else 'Unknown error'}")
            return

        # Step 2: Display vehicle makes with numbers
        print("Available Vehicle Makes:")
        makes = []  # List to store makes and IDs for easy reference
        for i, make in enumerate(vehicle_makes_response, 1):
            make_name = make['data']['attributes']['name']
            make_id = make['data']['id']
            makes.append((make_name, make_id))  # Store (make_name, make_id) tuple for easy lookup
            print(f"{i}. {make_name}")

        # Step 3: Prompt the user to select a vehicle make by number
        try:
            vehicle_make_choice = int(input("\nEnter the number of the vehicle make you want to choose: "))
            if vehicle_make_choice < 1 or vehicle_make_choice > len(makes):
                print("Invalid choice.")
                return
            selected_make_name, selected_make_id = makes[vehicle_make_choice - 1]
            print(f"\nYou selected: {selected_make_name} (ID: {selected_make_id})")

        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        print(f"Fetching vehicle models for {selected_make_name}...")

        # Step 4: Get the vehicle models for the selected make
        vehicle_models_response = self.api.get_vehicle_models(selected_make_id)

        # Ensure vehicle_models_response is a list and not empty
        if not isinstance(vehicle_models_response, list) or not vehicle_models_response:
            print(f"Error fetching vehicle models: {vehicle_models_response if isinstance(vehicle_models_response, dict) else 'Unknown error'}")
            return

        # Step 5: Display vehicle models with numbers
        print("Available Vehicle Models:")
        models = []  # List to store models and IDs for easy reference
        for i, model in enumerate(vehicle_models_response, 1):
            model_name = model['data']['attributes']['name']
            model_year = model['data']['attributes']['year']
            model_id = model['data']['id']
            models.append((model_name, model_year, model_id))  # Store (model_name, model_year, model_id)
            print(f"{i}. {model_name} ({model_year})")

        # Step 6: Prompt the user to select a vehicle model by number
        try:
            vehicle_model_choice = int(input("\nEnter the number of the vehicle model you want to choose: "))
            if vehicle_model_choice < 1 or vehicle_model_choice > len(models):
                print("Invalid choice.")
                return
            selected_model_name, selected_model_year, selected_model_id = models[vehicle_model_choice - 1]
            print(f"\nYou selected: {selected_model_name} ({selected_model_year}) - ID: {selected_model_id}")

        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        # Step 7: Input trip details
        try:
            distance_value = float(input("Enter trip distance: "))
            distance_unit = input("Enter distance unit (km or mi): ").lower()
            if distance_unit not in ["km", "mi"]:
                print("Invalid distance unit.")
                return
        except ValueError:
            print("Invalid distance value. Please enter a number.")
            return

        # Step 8: Get the vehicle emissions estimate
        print("Fetching vehicle emissions estimate...")
        response = self.api.estimate_vehicle(distance_value, distance_unit, selected_model_id)
        self.process_response(response, "Vehicle Emissions", "Vehicle", user_id)







    def process_response(self, response, emission_type, category, user_id):
        if 'data' in response and 'attributes' in response['data']:
            carbon_kg = response['data']['attributes'].get('carbon_kg', None)
            if carbon_kg is not None:
                print(f"{emission_type}: {carbon_kg} kg CO2")
                self.data_analysis.add_emission(category, carbon_kg, user_id)
            else:
                print(f"No carbon_kg found in the response for {emission_type}.")
        else:
            print(f"Error processing {emission_type}: {response.get('error', 'Unknown error')}")

class DataAnalysisInterface:
    def __init__(self, data_analysis):
        self.data_analysis = data_analysis

    def handle_choice(self, choice, user_id):
        if choice == "1":
            self.show_emission_data(user_id)
        elif choice == "2":
            self.sort_emission_data()
        elif choice == "3":
            self.visualize_emissions(user_id)
        elif choice == "4":
            self.remove_emission_data()
        elif choice == "5":
            self.show_leaderboard()

    def show_emission_data(self, user_id):
        total_emissions = self.data_analysis.get_total_emissions(user_id)
        print(f"\033[1mTotal Emissions: {total_emissions:.2f} kg CO2\033[0m")
        self.data_analysis.display_emission_data(user_id)

    def sort_emission_data(self):
        if self.data_analysis.emissions_df.empty:
            print("No data available to sort.")
            return
        order = input("Sort in ascending order? (y/n): ").strip().lower()
        ascending = order == "y"
        self.data_analysis.sorting_emission_data(ascending=ascending)

    def visualize_emissions(self, user_id=None):
        """Visualizes emissions, filtered by User ID if specified."""
        print("1. Visualize data for all users")
        print("2. Visualize data for current user")
        print("3. Compare emissions for multiple users")
        choice = input("Select an option: ")

        if choice == "1":
            self.data_analysis.visualize_emissions()
        elif choice == "2":
            self.data_analysis.visualize_emissions(user_id)
        elif choice == "3":
            self.data_analysis.compare_users_emissions()


    def remove_emission_data(self):
        self.data_analysis.remove_emission()
        print("All emission data has been removed.")


    def show_leaderboard(self):
        self.data_analysis.leaderboard()

