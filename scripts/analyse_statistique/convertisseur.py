import os
import json
import csv
import sys

##### Usage: python .\statistiques_cerveux.py <input_folder>
##### This program is only suitable for converting statistical analysis data json file in analyse_statistics into csv file

def json_to_csv(json_file, output_folder):
    """
    Convert a structured JSON file into a CSV file and save it in the output folder.
    """
    try:
        # Ensure the output directory exists
        os.makedirs(output_folder, exist_ok=True)

        # Define output CSV file path
        csv_file = os.path.join(output_folder, os.path.basename(json_file).replace('.json', '.csv'))

        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Ensure the JSON file contains a dictionary
        if not isinstance(data, dict):
            raise ValueError(f"Skipping {json_file}: JSON data must be a dictionary.")

        # Extract Group name
        group_name = data.get("Group", "Unknown_Group")

        # Extract the data entries (excluding the "Group" key)
        records = []
        for key, values in data.items():
            if key == "Group":
                continue  # Skip the Group metadata

            if isinstance(values, dict): 
                entry = {
                    "Group": group_name, 
                    "Region_ID": key,
                    "label_name": values.get("label_name", ""),  
                    "avg_volume (mm³)": values.get("avg_volume (mm3)", ""),
                    "std_volume (mm³)": values.get("std_volume (mm3)", ""),
                    "avg_ratio_vol_totvol (%)": values.get("avg_ratio_vol_totvol (%)", ""),
                    "ratio_std_avg (%)": values.get("ratio_std_avg (%)", ""),
                    "min": values.get("min", ""),
                    "max": values.get("max", ""),
                    "Q1": values.get("Q1", ""),
                    "Q2": values.get("Q2", ""),
                    "Q3": values.get("Q3", ""),
                    "IQR": values.get("IQR", ""),
                    "outliers": ", ".join(map(str, values.get("outliers", []))) if values.get("outliers") else "None"
                }
                records.append(entry)

        # Predefine a column order
        headers = [
            "Group", "Region_ID", "label_name",
            "avg_volume (mm³)", "std_volume (mm³)", "avg_ratio_vol_totvol (%)", "ratio_std_avg (%)",
            "min", "max", "Q1", "Q2", "Q3", "IQR",
            "outliers"
        ]

        # Write data to CSV file
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()  # Write header row
            writer.writerows(records)  # Write data rows

        print(f"Converted: {json_file} -> {csv_file}")

    except Exception as e:
        print(f"Error processing {json_file}: {e}")

def process_folder(folder_path):
    """
    Process all JSON files in the given folder and save CSV files in a 'csv' subfolder.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return

    # Define the output folder where CSV files will be saved
    output_folder = os.path.join(folder_path, "csv")

    # List all JSON files in the directory
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

    if not json_files:
        print(f"No JSON files found in {folder_path}.")
        return

    # Process each JSON file in the folder
    for json_file in json_files:
        json_to_csv(os.path.join(folder_path, json_file), output_folder)

if __name__ == "__main__":
    """
    """
    if len(sys.argv) != 2:
        print("Usage: python3 convertisseur.py folder_name")
    else:
        folder_name = sys.argv[1]
        process_folder(folder_name)
