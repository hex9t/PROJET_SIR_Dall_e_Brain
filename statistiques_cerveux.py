import csv
import os
import json
import sys
from collections import defaultdict
import statistics

def process_age(age):
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
            id_ = int(row.get("ID", "").lstrip('0'))
            gender = row.get("GENDER", "").strip()
            age = row.get("AGE", "").strip()
            
            
            if gender == "M":
                categories["Male"].append(id_)
            elif gender == "F":
                categories["Female"].append(id_)

            age_group = process_age(age=age)
            if age_group == "Minor":
                categories["Minor"].append(id_)
            elif age_group == "Adult":
                categories["Adult"].append(id_)
            elif age_group == "Senior":
                categories["Senior"].append(id_)

    return categories

def load_anatomie(input_anatomie_csv):
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
    label_data = defaultdict(list)
    for label_id, volume_mm3, volume_ratio in data:
        label_data[label_id].append((volume_mm3, volume_ratio))

    results = {}
    for label_id, values in label_data.items():
        volumes = [v[0] for v in values]
        ratios = [v[1] for v in values]

        avg_volume = round(statistics.mean(volumes), 2)
        std_volume = round(statistics.stdev(volumes), 2) if len(volumes) > 1 else 0.00
        avg_ratio = round(statistics.mean(ratios), 2)
        std_ratio = round(statistics.stdev(ratios), 2) if len(ratios) > 1 else 0.00

        label_name = anatomie_template[label_id]["label_name"] if label_id in anatomie_template else "Unknown"

        results[label_id]= {
            "label_name":label_name,
            "avg_volume (mm³)": avg_volume,
            "std_volume (mm³)": std_volume,
            "avg_ratio (%)": f"{avg_ratio}%",
            "std_ratio (%)": f"{std_ratio}%",
        }

    return results

def save_to_json(filename, data):
    file_path = os.path.join(output_folder, filename)
    with open(file_path, 'w',encoding='utf-8') as file:
        json.dump({"Group": filename.split('.')[0], **data}, file, indent=4,ensure_ascii=False)

# File paths
input_info_path = "./data/Keywords/Kirby_info.csv" # need to change everytime
input_anatomie_csv = "./data/Keywords/Anatomie_IBSR.csv"

if len(sys.argv) < 2:
    print("Usage: python3 statistiques_cerveux.py <input_folder>")
    sys.exit(1)

input_folder = sys.argv[1]
anatomie_template = load_anatomie(input_anatomie_csv)
output_folder = './data/Kirby/seg_statistiques/'  # need to change everytime
os.makedirs(output_folder, exist_ok=True)

categories = collect_ids_by_category(input_info_path)
Male_volumes = []
Female_volumes = []
Minor_volumes = []
Adult_volumes = []
Senior_volumes = []

# Process CSV files in the input folder
for csv_file in os.listdir(input_folder):
    if csv_file.endswith(".csv"):
        file_path = os.path.join(input_folder, csv_file)

        if csv_file.startswith("OAS") or csv_file.startswith("IBSR"):
            file_id = int(csv_file.split("_")[1].lstrip('0')) # Extract the ID part for OAS and IBSR files
        elif csv_file.startswith("KKI"):
            file_id = int(csv_file.split("-")[1].lstrip('0'))  # Extract the first number after "-" for KKI files
        elif csv_file.startswith("IXI"):
            file_id = int(csv_file.split("-")[0].lstrip("IXI"))
        else:
            print(f"Skipping unrecognized file format: {csv_file}")
            continue
        
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

        for label_id, info in anatomie_template.items():
            label_name = info["label_name"]
            rgb = info["rgb"]
            if label_id in file_data:
                voxel_count = file_data[label_id]["voxel_count"]
                volume_mm3 = file_data[label_id]["volume_mm3"]
                volume_ratio = file_data[label_id]["volume_ratio"]
            else:
                voxel_count = 0
                volume_mm3 = 0.0
                volume_ratio = 0.0

            entry = (label_id, volume_mm3, volume_ratio)

            if file_id in categories["Male"]:
                Male_volumes.append(entry)
            if file_id in categories["Female"]:
                Female_volumes.append(entry)
            if file_id in categories["Minor"]:
                Minor_volumes.append(entry)
            if file_id in categories["Adult"]:
                Adult_volumes.append(entry)
            if file_id in categories["Senior"]:
                Senior_volumes.append(entry)

result_Male = calculate_statistics(Male_volumes, anatomie_template)
result_Female = calculate_statistics(Female_volumes, anatomie_template)
result_Minor = calculate_statistics(Minor_volumes, anatomie_template)
result_Adult = calculate_statistics(Adult_volumes, anatomie_template)
result_Senior = calculate_statistics(Senior_volumes, anatomie_template)

save_to_json('Male_statistics.json', result_Male)
save_to_json('Female_statistics.json', result_Female)
save_to_json('Minor_statistics.json', result_Minor)
save_to_json('Adult_statistics.json', result_Adult)
save_to_json('Senior_statistics.json', result_Senior)
