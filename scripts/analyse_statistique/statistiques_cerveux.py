import csv
import os
import json
import sys
from collections import defaultdict
import statistics
import numpy as np

##### example of excution the programme:  python3 statistiques_cerveux.py ./Data_analyse/Kirby_seg/csv_files/ (on Linux) (the input files are the csv files)
##### need to change line 133,134,142 to modify the correct path.

def process_age(age):
    """
    Processes the age value and categorizes it into 'Minor', 'Adult', or 'Senior'.
    If the input does not contain a digit, it is categorized as 'Unknown'.
    """
    if not any(char.isdigit() for char in age):
        return 'Unknown'
    age = float(age.replace(',', '.'))
    if age < 18:
        return "Minor"
    elif age < 65:
        return "Adult"
    else:
        return "Senior"

def collect_ids_by_category(file_path):
    """
    Reads a CSV file containing IDs, gender, and age data,
    and categorizes IDs based on gender and age groups.
    """
    categories = {
        "Male": [],
        "Female": [],
        "Minor": [],
        "Adult": [],
        "Senior": []
    }
    
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            id_ = int(row.get("ID", "").lstrip('0'))  # Remove leading zeros from ID
            gender = row.get("GENDER", "").strip()
            age = row.get("AGE", "").strip()
            
            if gender == "M":
                categories["Male"].append(id_)
            elif gender == "F":
                categories["Female"].append(id_)
            
            age_group = process_age(age=age)
            if age_group in categories:
                categories[age_group].append(id_)
    
    return categories

def load_anatomie(input_anatomie_csv):
    """
    Loads anatomical label information from a CSV file.
    Returns a dictionary mapping label IDs to label names and RGB values.
    """
    anatomie_template = {}
    with open(input_anatomie_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            label_id = int(row["ID"])
            label_name = row["Labels"]
            rgb = row["RGB"]
            anatomie_template[label_id] = {"label_name": label_name, "rgb": rgb}
    return anatomie_template

def calculate_statistics(data, anatomie_template):
    """
    Calculates statistical measures for brain structure volumes and ratios.
    Computes mean, standard deviation, quartiles, IQR, and identifies outliers.
    """
    label_data = defaultdict(list)
    for label_id, volume_mm3, volume_ratio in data:
        label_data[label_id].append((volume_mm3, volume_ratio))

    results = {}
    for label_id, values in label_data.items():
        volumes = [v[0] for v in values]
        ratios = [v[1] for v in values]

        avg_volume = statistics.mean(volumes)
        std_volume = statistics.pstdev(volumes)
        avg_ratio = statistics.mean(ratios)
        ratio_std_avg = (std_volume / avg_volume) * 100 if std_volume > 0 else 0.00
        
        # Compute quartiles and interquartile range
        q1, q2, q3 = np.percentile(volumes, [25, 50, 75])
        iqr = q3 - q1
        min_val = min([v for v in volumes if v >= q1 - 1.5 * iqr], default=min(volumes))
        max_val = max([v for v in volumes if v <= q3 + 1.5 * iqr], default=max(volumes))
        outliers = [v for v in volumes if v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr]

        label_name = anatomie_template.get(label_id, {}).get("label_name", "Unknown")

        results[label_id] = {
            "label_name": label_name,
            "avg_volume (mm³)": avg_volume,
            "std_volume (mm³)": std_volume,
            "avg_ratio_vol_totvol (%)": avg_ratio,
            "ratio_std_avg (%)": ratio_std_avg,
            "min": min_val,
            "max": max_val,
            "Q1": q1,
            "Q2": q2,
            "Q3": q3,
            "IQR": iqr,
            "outliers": outliers
        }

    # Sort results by ratio_std_avg in descending order
    sorted_results = dict(sorted(results.items(), key=lambda item: item[1]["ratio_std_avg (%)"], reverse=True))
    
    return sorted_results

def save_to_json(filename, data, base_name):
    """
    Saves the computed statistics into a JSON file.
    The group name is dynamically created using base_name.
    """
    group_name = f"{base_name}_{filename.split('.')[0]}"
    file_path = os.path.join(output_folder, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump({"Group": group_name, **data}, file, indent=4, ensure_ascii=False)

# Define input file paths
input_info_path = "./data/Keywords/IBSR_info.csv"   # Path to subject info CSV
input_anatomie_csv = "./data/Keywords/Anatomie_IBSR.csv"  # Path to anatomical labels CSV

if len(sys.argv) < 2:
    print("Usage: python3 statistiques_cerveux.py <input_folder>")
    sys.exit(1)

input_folder = sys.argv[1]
anatomie_template = load_anatomie(input_anatomie_csv)
output_folder = './data/IBSR/seg_statistiques/'  # Output folder path
os.makedirs(output_folder, exist_ok=True)

base_name = os.path.normpath(output_folder).split(os.sep)[1]

# Categorize IDs based on gender and age
categories = collect_ids_by_category(input_info_path)
grouped_volumes = {group: [] for group in categories}

# Process each CSV file in the input folder
for csv_file in os.listdir(input_folder):
    if csv_file.endswith(".csv"):
        file_path = os.path.join(input_folder, csv_file)
        file_id = int(csv_file.split("_")[1].lstrip('0')) if csv_file.startswith(("OAS", "IBSR")) else \
                  int(csv_file.split("-")[1].lstrip('0')) if csv_file.startswith("KKI") else \
                  int(csv_file.split("-")[0].lstrip("IXI"))
        
        file_data = {}
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                label_id = int(row["ID"])
                file_data[label_id] = {
                    "voxel_count": int(row["Voxel Count"]),
                    "volume_mm3": float(row["Volume (mm³)"]),
                    "volume_ratio": float(row["Volume Ratio (%)"]),
                }
        
        for group, ids in categories.items():
            if file_id in ids:
                grouped_volumes[group].extend([(lid, d["volume_mm3"], d["volume_ratio"]) for lid, d in file_data.items()])

# Save statistics for each category
for group, volumes in grouped_volumes.items():
    save_to_json(f'{group}_statistics.json', calculate_statistics(volumes, anatomie_template), base_name)
