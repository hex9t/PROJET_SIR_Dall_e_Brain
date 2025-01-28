import csv
import numpy as np
import os
import sys
import re
import pandas as pd

# Templates for text generation
templates = [
    "This {type} scan captures the brain of a {gender} individual, aged {age}.The structures visible include {structures}. The total brain volume is approximately {total_volume} mm³.",
    "In this {type} scan of a {age}-year-old {gender}, important brain structures such as {structures} are clearly visible. The brain's total volume is {total_volume} mm³.",
    "{type} imaging reveals detailed {structures} in the brain of a {age}-year-old {gender}. The overall brain volume is measured at {total_volume} mm³.",
    "A {type} scan of a {age}-year-old {gender} highlights the following brain structures: {structures}. The total brain volume is {total_volume} mm³.",
    "Key brain features identified in this {type} scan of a {gender} aged {age} include {structures}. The entire brain volume amounts to {total_volume} mm³.",
    "For this {type} scan, the subject is a {age}-year-old {gender}, showcasing {structures} in the brain. The total brain volume calculated is {total_volume} mm³.",
    "This {type} imaging study shows brain structures such as {structures} in a {gender} individual, aged {age}. The total brain volume is approximately {total_volume} mm³.",
    "The {type} scan of this {age}-year-old {gender} reveals: {structures}. The total volume of the brain is {total_volume} mm³.",
    "In this scan ({type}), the brain of a {gender} aged {age} is observed, showing {structures}. The brain's total volume is {total_volume} mm³.",
    "This {type} imaging presents the brain of a {gender} subject who is {age} years old, emphasizing {structures}. The total brain volume is calculated to be {total_volume} mm³."
]

# Path to the info files
infoPath = "./data/Keywords"

# Verify command-line arguments
if len(sys.argv) != 2:
    print("Usage: python3 test_description.py <inputFolder>")
    sys.exit(1)

# Input folder and output setup
inputFolder = sys.argv[1]
inputFiles = [f for f in os.listdir(inputFolder) if f.endswith('csv')]
if inputFolder.endswith("inv"):
    outputPath = os.path.join(os.path.sep.join(inputFolder.split(os.path.sep)[:-1]), "Keywords_inv")
else:
    outputPath = os.path.join(os.path.sep.join(inputFolder.split(os.path.sep)[:-1]), "Descriptions")
if not os.path.exists(outputPath):
    os.makedirs(outputPath)

# Combine structure names and volumes into a single string with sorting options
def get_structures_summary(structures_data, sort_by="label", num_structures=None):
    # Filter out "Unknown" labels
    filtered_structures = structures_data[structures_data['Label'] != "Unknown"]

    # Sort structures based on the specified sort_by parameter
    if sort_by == "label":
        sorted_structures = filtered_structures.sort_values(by="Label")
    elif sort_by == "gresseur":  # Sort by volume in descending order
        sorted_structures = filtered_structures.sort_values(by="Volume (mm³)", ascending=False)
    elif sort_by == "random":
        sorted_structures = filtered_structures.sample(frac=1).reset_index(drop=True)
    else:
        raise ValueError(f"Unsupported sort_by option: {sort_by}")

    # If num_structures is specified, select the top N structures
    if num_structures is not None:
        sorted_structures = sorted_structures.head(num_structures)

    # Combine volumes into a string
    return ", ".join(
        f"{row['Label']} {row['Volume (mm³)']:.2f} mm³\n"
        for _, row in sorted_structures.iterrows()
    )

# Calculate total brain volume by summing valid structure volumes
def calculate_total_volume(structures_data):
    # Filter out "Unknown" labels and sum the volume column
    valid_structures = structures_data[structures_data['Label'] != "Unknown"]
    return valid_structures['Volume (mm³)'].sum()

# Extract ID and ImageSource from file name
def parse_file_name(file_name):
    if file_name.startswith("OAS"):
        match = re.match(r"OAS\d+_(\d+)_", file_name)
        if match:
            return "OAS", match.group(1).zfill(4)
    elif file_name.startswith("KKI"):
        match = re.match(r"KKI\d+-\d+-?(\d+)", file_name)
        if match:
            return "KKI", match.group(1)
    elif file_name.startswith("IXI"):
        match = re.match(r"IXI(\d+)-", file_name)
        if match:
            return "IXI", match.group(1).zfill(3)
    elif file_name.startswith("IBSR"):
        match = re.match(r"IBSR_(\d+)_", file_name)
        if match:
            return "IBSR", match.group(1).zfill(2)
    return None, None

# Extract age and gender from info.csv
def extract_info(Im, ID):
    if Im == 'OAS':
        infoFilePath = os.path.join(infoPath, 'OASIS_info.csv')
    elif Im == 'IXI':
        infoFilePath = os.path.join(infoPath, 'IXI_info.csv')
    elif Im == 'KKI':
        infoFilePath = os.path.join(infoPath, 'Kirby_info.csv')
    elif Im == 'IBSR':
        infoFilePath = os.path.join(infoPath, 'IBSR_info.csv')
    else:
        print(f"Infos about {Im} not found")
        return None, None

    with open(infoFilePath, 'r', newline='', encoding='utf-8') as fichier_infos:
        reader = csv.DictReader(fichier_infos)
        genre, age = "", ""
        for ligne in reader:
            if ligne['ID'].lstrip('0') == ID.lstrip('0'):
                age = ligne['AGE']
                if age == 'JUV':
                    age = 'unknown'
                genre = "male" if ligne['GENDER'] == "M" else "female"
                break

        return genre, age

# Get scan modality
def get_modalite(Im):
    if Im == 'OAS':
        return "T1"
    elif Im == 'IXI':
        return "T2"
    elif Im == 'KKI':
        return "FLAIR"
    elif Im == 'IBSR':
        return "T1"
    else:
        print(f"Modality about {Im} not found")
        return "Unknown"

# Generate descriptions for each input CSV
for file in inputFiles:
    inputFilePath = os.path.join(inputFolder, file)
    outputFilePath = os.path.join(outputPath, file)

    Im, ID = parse_file_name(file)
    if not Im or not ID:
        print(f"Could not parse file name: {file}")
        continue

    # Load the structure information from the current file
    structures_data = pd.read_csv(inputFilePath)

    # Filter out "Unknown" labels and calculate total valid structures
    valid_structures_data = structures_data[structures_data['Label'] != "Unknown"]
    total_structures = len(valid_structures_data)
    print(f"Total valid structures available: {total_structures}")

    # Calculate total brain volume directly from CSV
    total_volume = calculate_total_volume(valid_structures_data)
    print(f"Total brain volume for {file} (csv): {total_volume:.2f} mm³")

    # Prompt user for the desired number of structures to display
    while True:
        try:
            num_structures = int(input(f"Enter the number of structures to display (1-{total_structures}): "))
            if 1 <= num_structures <= total_structures:
                break
            else:
                print("Invalid input. Please enter a number within the valid range.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    # Generate structures summary
    structures_summary = get_structures_summary(valid_structures_data, sort_by="gresseur", num_structures=num_structures)

    # Extract additional information
    gender, age = extract_info(Im, ID)
    modality = get_modalite(Im)

    # Generate description
    choice_num = np.random.choice(len(templates))
    description = templates[choice_num].format(type=modality, gender=gender, age=age, structures=structures_summary, total_volume=total_volume)

    # Write the output to a new CSV file
    with open(outputFilePath, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["Description"])
        writer.writeheader()
        writer.writerow({"Description": description})

    print(f"Description written to {outputFilePath}")
