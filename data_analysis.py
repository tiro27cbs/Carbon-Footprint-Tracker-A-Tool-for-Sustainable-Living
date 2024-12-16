import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns


class DataAnalysis:
    def __init__(self, data_file="emissions_data.csv"):
        self.total_emissions = 0.0
        self.data_file = data_file if data_file else "emissions_data.csv"
        self.emissions_df = pd.DataFrame(columns=["Category", "Emission (kg)", "User ID"])

        # Load existing data
        self.load_data()

    def add_emission(self, category, carbon_kg, user_id):
        """Adds an emission record with the user's ID."""
        if isinstance(carbon_kg, (int, float)):
            self.total_emissions += carbon_kg
            new_data = pd.DataFrame({"Category": [category], "Emission (kg)": [carbon_kg], "User ID": [user_id]})
            self.emissions_df = pd.concat([self.emissions_df, new_data], ignore_index=True)
            self.save_data()
        else:
            print("Invalid data type for emission. Expected a number.")

    def get_total_emissions(self, user_id=None):
        """Returns total emissions, filtered by User ID if specified."""
        if user_id:
            return self.emissions_df[self.emissions_df["User ID"] == user_id]["Emission (kg)"].sum()
        return self.emissions_df["Emission (kg)"].sum()

    def save_data(self):
        """Saves the emissions data to a CSV file."""
        directory = os.path.dirname(self.data_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        self.emissions_df.to_csv(self.data_file, index=False)

    def load_data(self):
        """Loads the emissions data from a CSV file."""
        if os.path.exists(self.data_file):
            self.emissions_df = pd.read_csv(self.data_file)
            
            # Ensure required columns exist
            required_columns = ["Category", "Emission (kg)", "User ID"]
            for col in required_columns:
                if col not in self.emissions_df.columns:
                    self.emissions_df[col] = None  
            
            self.total_emissions = self.emissions_df["Emission (kg)"].sum()
        else:
            print("No existing data file found. Starting fresh.")
            self.emissions_df = pd.DataFrame(columns=["Category", "Emission (kg)", "User ID"])


    def display_emission_data(self, user_id=None):
        """Displays emissions data filtered by User ID if specified."""
        if user_id:
            user_data = self.emissions_df[self.emissions_df["User ID"] == user_id]
            if not user_data.empty:
                print("Emissions Data for User ID:", user_id)
                print(user_data)
            else:
                print("No data available for this User ID.")
        else:
            if not self.emissions_df.empty:
                print("Emissions Data for All Users:")
                print(self.emissions_df)
            else:
                print("No emission data available.")

    def visualize_emissions(self, user_id=None):
            sns.set(style="whitegrid")
            if user_id:
                data_to_visualize = self.emissions_df[self.emissions_df["User ID"] == user_id]
                title = f"Emissions by Category (User ID: {user_id})"
            else:
                data_to_visualize = self.emissions_df
                title = "Emissions by Category (All Users)"
            
            if not data_to_visualize.empty:
                emissions_sum = data_to_visualize.groupby("Category").sum().sort_values(by="Emission (kg)", ascending=False)
                ax = emissions_sum.plot(kind="bar", y="Emission (kg)", legend=False, color=sns.color_palette("Set2", len(emissions_sum)))
                ax.bar_label(ax.containers[0], labels=[f'{v:.2f}' for v in emissions_sum["Emission (kg)"]], label_type="edge", fontsize=10)
                plt.title(title, fontsize=16)
                plt.xlabel("Emission (kg)", fontsize=12)
                plt.ylabel("Category", fontsize=12)
                plt.tight_layout()
                plt.show()
            else:
                print("No data available to visualize.")

    def compare_users_emissions(self):
        user_ids = []

        while True:
            user_id_input = input("Enter a user ID: ")
            
            if user_id_input not in self.emissions_df["User ID"].values:
                print(f"User ID '{user_id_input}' does not exist in the data. Please enter a valid User ID.")
                continue
            
            user_ids.append(user_id_input)
            
            more_users = input("Would you like to add another user? (y/n): ").lower()
            if more_users != 'y':
                break
        
        if user_ids:
            data_to_visualize = self.emissions_df[self.emissions_df["User ID"].isin(user_ids)]
            
            if not data_to_visualize.empty:
                emissions_sum = data_to_visualize.groupby(["User ID", "Category"]).sum().unstack(fill_value=0)
                emissions_sum = emissions_sum["Emission (kg)"]

                sns.set(style="whitegrid")
                ax = emissions_sum.plot(kind="bar", stacked=False, figsize=(10, 6), colormap="Set2")

                ax.set_title(f"Emissions Comparison for Selected Users", fontsize=16)
                ax.set_xlabel("Category", fontsize=12)
                ax.set_ylabel("Emission (kg)", fontsize=12)

                plt.tight_layout()
                plt.show()
            else:
                print("No data available to visualize for the selected users.")
        else:
            print("No user IDs were selected.")


    def remove_emission(self, user_id=None):
        """Removes all emission data, or only for a specific User ID."""
        if user_id:
            self.emissions_df = self.emissions_df[self.emissions_df["User ID"] != user_id]
        else:
            self.emissions_df = pd.DataFrame(columns=["Category", "Emission (kg)", "User ID"])
        self.save_data()

    def sorting_emission_data(self, ascending=True, user_id=None):
        """Sorts emission data using quicksort, filtered by User ID if specified."""

        def quicksort(arr):
            """Helper function to perform quicksort on a list of tuples."""
            if len(arr) <= 1:
                return arr
            pivot = arr[0]
            less = [x for x in arr[1:] if x[1] <= pivot[1]]
            greater = [x for x in arr[1:] if x[1] > pivot[1]]
            return quicksort(less) + [pivot] + quicksort(greater)

        if user_id:
            data_to_sort = self.emissions_df[self.emissions_df["User ID"] == user_id]
        else:
            data_to_sort = self.emissions_df

        if not data_to_sort.empty:
            data_list = data_to_sort[["User ID", "Emission (kg)","Category"]].values.tolist()

            # Apply quicksort and optionally reverse if not ascending
            sorted_list = quicksort(data_list)
            if not ascending:
                sorted_list = sorted_list[::-1]

            # Create a sorted DataFrame for display
            sorted_data = pd.DataFrame(sorted_list, columns=["User ID", "Emission (kg)","Category"])
            print(sorted_data)

        else:
            print("No data available to sort.")

    def leaderboard(self):
        """Generates a sorted leaderboard by total emissions, from lowest to highest."""
        user_emissions = self.emissions_df.groupby("User ID")["Emission (kg)"].sum().sort_values()
        print("\033[1mLeaderboard by Total Emissions (Lowest to Highest):\033[0m")
        print(user_emissions)
 