import csv
import os
import json
import sys
from collections import defaultdict
import statistics
import numpy as np

##### Example of excution the programme:  python .\statistiques_cerveux.py <input_folder>
##### Need to change line 163,164,172 to modify to the correct path.

def process_age(age):
    """
    Create the groupe 'Minor', 'Adult', or 'Senior'.
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
    
    with open(file_path, mode="r", encoding="ISO-8859-1") as file:
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
    """
    anatomie_template = {}
    with open(input_anatomie_csv, mode="r", encoding="ISO-8859-1") as file:
        reader = csv.DictReader(file)
        for row in reader:
            label_id = int(row["ID"])
            label_name = row["Labels"]
            rgb = row["RGB"]
            anatomie_template[label_id] = {"label_name": label_name, "rgb": rgb}
    return anatomie_template

def calculate_statistics(data, anatomie_template):
    """
    Calculates statistical measures for brain structure.
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
            "avg_volume (mm3)": avg_volume,
            "std_volume (mm3)": std_volume,
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

def calculate_total_statistics(total_volumes):
    """
    Calculates statistical measures for the total of brain structure. 
    """
    if not total_volumes:
        return {}

    avg_volume = statistics.mean(total_volumes)
    std_volume = statistics.pstdev(total_volumes)
    avg_ratio = 100.0 
    ratio_std_avg = (std_volume / avg_volume) * 100 if avg_volume > 0 else 0.0

    q1, q2, q3 = np.percentile(total_volumes, [25, 50, 75])
    iqr = q3 - q1
    min_val = min([v for v in total_volumes if v >= q1 - 1.5 * iqr], default=min(total_volumes))
    max_val = max([v for v in total_volumes if v <= q3 + 1.5 * iqr], default=max(total_volumes))
    outliers = [v for v in total_volumes if v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr]

    return {
        "label_name": "Total brain",
        "avg_volume (mm3)": avg_volume,
        "std_volume (mm3)": std_volume,
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

def save_to_json(filename, data, base_name):
    """
    Saves the computed statistics into a JSON file.
    """
    group_name = f"{base_name}_{filename.split('.')[0]}"
    file_path = os.path.join(output_folder, filename)
    with open(file_path, 'w', encoding='ISO-8859-1') as file:
        json.dump({"Group": group_name, **data}, file, indent=4, ensure_ascii=False)

# Define input file paths
input_info_path = os.path.join("Keywords", "OASIS_info.csv")   # Path to subject info CSV
input_anatomie_csv = os.path.join("Keywords", "Anatomie_IBSR.csv") # Path to anatomical labels CSV

if len(sys.argv) < 2:
    print("Usage: python statistiques_cerveux.py <input_folder>")
    sys.exit(1)

input_folder = os.path.normpath(sys.argv[1]) 
anatomie_template = load_anatomie(input_anatomie_csv)
output_folder = os.path.join("FL", "Kirby_OASIS", "analyse_statistics") # Output folder path
os.makedirs(os.path.normpath(output_folder), exist_ok=True)

base_name = os.path.normpath(output_folder).split(os.sep)[1]

# Categorize IDs based on gender and age
categories = collect_ids_by_category(input_info_path)
grouped_volumes = {group: [] for group in categories}
grouped_volumes["Overall"] = []

# Store the total volume of brain for each file
group_total_volumes = {group: [] for group in categories}
group_total_volumes["Overall"] = []

# Distinguish between single-name databases and multi-name
database_name = os.path.basename(os.path.dirname(input_folder)) 
if "_" in database_name:  
    primary_db, secondary_db = database_name.split("_")  
    is_composite_db = True
else:
    primary_db = database_name
    secondary_db = None
    is_composite_db = False

# Process each CSV file in the input folder
for csv_file in os.listdir(input_folder):
    if csv_file.endswith(".csv"):
        file_path = os.path.join(input_folder, csv_file)

        if not is_composite_db:
            file_id = int(csv_file.split("_")[1].lstrip('0')) if csv_file.startswith(("OAS", "IBSR")) else \
                        int(csv_file.split("-")[1].lstrip('0')) if csv_file.startswith("KKI") else \
                        int(csv_file.split("-")[0].lstrip("IXI"))
        else: # Need to change to a smarter way to get the ID of the file. A vous de jouer ==-== .
            if primary_db == "IBSR" and secondary_db == "Kirby":
                file_id = int(csv_file.split("-")[1].lstrip('0'))  
            elif primary_db == "IBSR" and secondary_db == "IXI":
                first_part = csv_file.split("-")[0]
                file_id = int(first_part.split("_")[-1].lstrip("IXI"))
            elif primary_db == "IBSR" and secondary_db == "OASIS":
                file_id = int(csv_file.split("_")[5].lstrip('0'))  
            elif primary_db == "OASIS" and secondary_db == "IBSR":
                first_part = csv_file.split("_")[9]
                file_id = int(first_part.split(".")[0].lstrip('0')) 
            elif primary_db == "OASIS" and secondary_db == "Kirby":
                file_id = int(csv_file.split("-")[2].lstrip('0'))
            elif primary_db == "Kirby" and secondary_db == "IXI":
                first_part = csv_file.split("_")[3]
                file_id = int(first_part.split("-")[0].lstrip("IXI"))
            elif primary_db == "Kirby" and secondary_db == "OASIS":
                file_id = int(csv_file.split("_")[4].lstrip('0'))
            else:
                raise ValueError(f"Unknown: {secondary_db}")
        
        file_data = {}
        with open(file_path, mode="r", encoding="ISO-8859-1") as file:
            reader = csv.DictReader(file)
            for row in reader:
                label_id = int(row["ID"])
                file_data[label_id] = {
                    "voxel_count": int(row["Voxel Count"]),
                    "volume_mm3": float(row.get("Voxel Volume (mm³)", row.get("Voxel Volume (mm�)", "0"))),
                    "volume_ratio": float(row["Volume Ratio (%)"]),
                }

        
        subject_total = sum(d["volume_mm3"] for lid, d in file_data.items() if lid != 0)

        for group, ids in categories.items():
            if file_id in ids:
                grouped_volumes[group].extend([(lid, d["volume_mm3"], d["volume_ratio"]) for lid, d in file_data.items()])
                group_total_volumes[group].append(subject_total)
    
    grouped_volumes["Overall"].extend([(lid, d["volume_mm3"], d["volume_ratio"]) for lid, d in file_data.items()])
    group_total_volumes["Overall"].append(subject_total)
    
# Save statistics for each category
for group, volumes in grouped_volumes.items():
    stats = calculate_statistics(volumes, anatomie_template)
    total_stats = calculate_total_statistics(group_total_volumes[group])
    stats["Total"] = total_stats
    save_to_json(f'{group}_statistics.json', stats, base_name)

