import pandas as pd
import re
import json
import nibabel as nib  # To read NIfTI files
import os
import argparse
#exemple : 
#python simple_captions.py image_data simple_descriptions ./metafolder/ dossier_output

relevant_structures = [
    "2, 41",  # White matter of cerebral hemispheres
    "3, 42",  # Cortex of cerebral hemispheres
    "10, 48, 49",  # Thalamus
    "11, 50",  # Caudate nucleus
    "12, 51",  # Putamen
    "13, 52",  # Globus pallidus
    "17, 53",  # Hippocampus
    "18, 54",  # Amygdala
    "16",  # Brainstem
    "28, 60"  # Ventral diencephalon
]
###############################################
def calculate_top_variance_structures(csv_folder, n):
    """Calculate the top n structures with the highest variance across all CSV files in the folder."""
    structure_variances = {}

    for csv_file in os.listdir(csv_folder):
        if csv_file.endswith(".csv"):
            file_path = os.path.join(csv_folder, csv_file)
            df = pd.read_csv(file_path, encoding='latin1')
            
            for _, row in df.iterrows():
                label = row['Label']
                if label == "Unknown":
                    continue
                volume = row['Voxel Volume (mm³)']
                if label not in structure_variances:
                    structure_variances[label] = []
                structure_variances[label].append(volume)

    # Calculate variance for each structure
    variance_results = {label: pd.Series(volumes).var() for label, volumes in structure_variances.items()}
    
    # Sort by variance in descending order and take the top n
    top_structures = sorted(variance_results.items(), key=lambda x: x[1], reverse=True)[:n]
    return [label for label, _ in top_structures]
import random
import pandas as pd
import nibabel as nib
import re
import json
import random

def generate_human_like_caption(image_filename, structures_file, metadata_file, output_file,a, image_type, selection=None, size=None):
    # Extract ID and type from image filename using regex
    match = None
    if image_type == "Kirby":
        match = re.search(r'KKI2009-(\d+)-([A-Z]+)', image_filename)
        scan_type = "FLAIR"
    elif image_type == "Oasis":
        match = re.search(r'OAS1_(\d+)_([A-Za-z0-9\-]+)', image_filename)
        scan_type = "T1"
    elif image_type == "IBSR":
        match = re.search(r'IBSR_(\d+)_([A-Za-z0-9\-]+)', image_filename)
        scan_type = "T1"
    elif image_type == "IXI":
        match = re.search(r'IXI(\d+)-IOP-\d+-[A-Za-z0-9\-]+', image_filename)
        scan_type = "T2"
    scan_type = a    

    if not match:
        raise ValueError(f"Invalid image filename format for file: {image_filename}")

    image_id = int(match.group(1))
    if image_type == "Kirby":
        image_type = match.group(2)  # For Kirby, use the second match group as the type
    
    # Load CSV files
    structures_df = pd.read_csv(structures_file, encoding='latin1')
    metadata_df = pd.read_csv(metadata_file, encoding='latin1')

    # Find metadata based on image ID
    metadata = metadata_df[metadata_df['ID'] == image_id]

# Si aucune métadonnée n'est trouvée, utiliser les valeurs par défaut
    if metadata.empty:
        age = "unknown"
        gender = "human"
    else:
        # Extraire l'âge et gérer les valeurs manquantes
        if image_type == "IXI":
            age = metadata.iloc[0]['AGE']
            age = int(float(age.replace(",", "."))) if pd.notna(age) else "unknown"
        else:
            age = metadata.iloc[0]['AGE']
            age = age if pd.notna(age) else "unknown"

        # Extraire le genre et gérer les valeurs manquantes
        gender = metadata.iloc[0]['GENDER']
        gender = gender if pd.notna(gender) else "human"

    # Load the 3D image to get dimensions
    img = nib.load(image_filename)  # Load the NIfTI image
    image_data = img.get_fdata().astype(int)  # Convert the image data to integers for processing
    total_voxels = image_data.size  # Total number of voxels in the image

    # Filter structures to include only those relevant for brain volume calculation
    filtered_structures = structures_df[structures_df['Labels'] != "Unknown"]

    # Calculate brain volume
    brain_volume = round(filtered_structures['Voxel Volume 3'].sum() / 1000)

    # Generate list of structures with volumes and percentages
    structures_with_volumes = []
    for _, row in filtered_structures.iterrows():
        labels = row['Labels'].split(",")  # Handle multiple labels in the 'Labels' column
        structure_volume = row['Voxel Volume 3'] / 1000
        if structure_volume <= 0:  # Ignore structures with zero volume
            continue
        percentage = round((row['Voxel Count'] / total_voxels) * 100, 2)
        for label in labels:
            structures_with_volumes.append({
                "description": row['Description'],  # Replace 'label' with 'description'
                "volume": structure_volume,
                "percentage": percentage
            })

    # Sort structures by volume (descending order)
    sorted_structures = sorted(structures_with_volumes, key=lambda x: x['volume'], reverse=True)
    sorted_structures = sorted_structures[:22]

    # Handle the size argument
    if size is not None:
        sorted_structures = sorted_structures[:size]

    # Handle selection argument
    if selection is not None:
        selected_structures = []
        selection = [int(s) for s in selection.split()]
        for index in selection:
            if 1 <= index <= len(sorted_structures):
                selected_structures.append(sorted_structures[index - 1])
        sorted_structures = selected_structures

    # Define sentence templates
    templates = [
        "This {scan_type} scan shows a {gender} subject aged {age} with dimensions {dimensions}. Brain volume is {brain_volume} cm3. The most prominent structures are {structures}",
        "A {scan_type} scan of a {gender} subject, {age} years old, with image dimensions {dimensions}. The total brain volume is {brain_volume} cm3, including major structures like {structures}",
        "Here we see a {scan_type} scan of a {gender} subject aged {age}. The image dimensions are {dimensions}, and the brain volume is {brain_volume} cm3. Visible structures include {structures}",
        "In this {scan_type} scan of a {age}-year-old {gender} subject, the image has dimensions {dimensions} and displays structures such as {structures} The brain volume is {brain_volume} cm3.",
        "This {scan_type} scan captures the brain of a {gender} subject aged {age} with image dimensions {dimensions}. The brain volume is {brain_volume} cm3. Key structures include {structures}",
        "This {scan_type} scan shows the brain of a {gender} subject aged {age}, with dimensions {dimensions}. The total brain volume is {brain_volume} cm3, and visible structures include {structures}",
        "Here is a {scan_type} scan of a {gender} subject aged {age}, with image dimensions {dimensions}. The brain volume is {brain_volume} cm3 and the visible structures include {structures}",
        "This {scan_type} scan provides a view of the brain of a {gender} subject, aged {age}, with dimensions of {dimensions}. Brain volume is {brain_volume} cm3, and visible structures include {structures}",
        "This is a {scan_type} scan of a {age}-year-old {gender}, with dimensions {dimensions}. The brain volume is {brain_volume} cm3, displaying structures like {structures}",
    ]
    
    # Prepare structures text based on selected or all structures
    unique_structures = {}
    for struct in structures_with_volumes:
        key = struct["description"].lower()  # Convertir en minuscule
        if key not in unique_structures or struct["volume"] > unique_structures[key]["volume"]:
            unique_structures[key] = {**struct, "description": key}  # Remplacer par la version minuscule

    # Convert dictionary back to a sorted list
    sorted_structures = sorted(unique_structures.values(), key=lambda x: x['volume'], reverse=True)
    sorted_structures = [s for s in sorted_structures if s["volume"] > 1]

    # List of connectors
    # Connectors
    connectors = [
        "and", "additionally", "furthermore", "also", "moreover", "next", 
        "in addition", "besides", "as well as", "then", "subsequently", "in particular", 
        "alternatively", "on the other hand"]

    structures_sentences = []
    
    # Define a list of different ways to announce the volume
    volume_phrases = [
    "has a volume of", "has this volume", "measures", "displays a volume of", 
    "has a size of", "is of volume", "shows a volume of", "holds a volume of",
    "is measured at", "has a capacity of", "amounts to", "comprises a volume of", 
    "spans a volume of", "occupies a volume of", "accounts for a volume of", 
    "fills a volume of", "is quantified as", "takes up a volume of", 
    "represents a volume of", "encapsulates a volume of", "is measured to be", 
    "features a volume of", "includes a volume of"
]

    # Build the structure sentences with connectors
    for i, s in enumerate(sorted_structures):
        volume = round(s["volume"] * 1000) if s["volume"] < 100 else round(s["volume"])
        unit = "mm3" if s["volume"] < 100 else "cm3"
        volume_phrase = random.choice(volume_phrases)
        sentence = f"the {s['description']} {volume_phrase} {volume} {unit}"
        
        # add connector if not the first structure
        if i > 0:
            sentence = random.choice(connectors) + " " + sentence
        
        structures_sentences.append(sentence)

    # Construire le texte des structures
    if structures_sentences:
        structures_text = ", ".join(structures_sentences[:-1])  # Joindre toutes sauf la dernière
        if len(structures_sentences) > 1:
            structures_text += ", " + structures_sentences[-1] + "."  # Ajouter la dernière avec un point
        else:
            structures_text = structures_sentences[-1] + "."  # Si une seule structure, juste un point
    else:
        structures_text = ""


    # Generate captions using all templates
    captions = []
    for template in templates:
        caption = template.format(
            scan_type=scan_type,
            gender="male" if gender == "M" else "female",
            age=age,
            dimensions=f"{img.shape[0]} x {img.shape[1]} x {img.shape[2]}",
            brain_volume=brain_volume,
            structures=structures_text
        )
        captions.append(caption)

    # Save the captions to a JSON file
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump({"captions": captions}, json_file, ensure_ascii=False, indent=4)

    return captions


import os
import os

import os

def process_folder(folder_path, csv_folder, metadata_folder, output_folder, selection=None, size=None):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    dataset_keywords = {
        "KKI2009": "Kirby",
        "OAS1": "Oasis",
        "IBSR": "IBSR",
        "IXI": "IXI"
    }

    dataset_keywords_modalite = {
        "KKI2009": "FLAIR",
        "OAS1": "T1",
        "IBSR": "T1",
        "IXI": "T2"
    }

    a = "T1"  # Initialize a to store the first detected modality

    # Loop through all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".nii.gz"):  # Check for NIfTI files
            image_path = os.path.join(folder_path, file_name)

            # Detect the dataset type
            last_dataset = None
            last_index = -1

            for keyword, dataset in dataset_keywords.items():
                index = file_name.rfind(keyword)  # Find the last occurrence of the keyword
                if index != -1 and index > last_index:
                    last_dataset = dataset
                    last_index = index

            if not last_dataset:
                print(f"Unknown dataset type for image: {file_name}")
                continue

            # Set a to the first detected dataset's modality
            if a is None and last_dataset in dataset_keywords_modalite:
                a = dataset_keywords_modalite[last_dataset]

            metadata_file = os.path.join(metadata_folder, f"{last_dataset}_info.csv")

            # Find the corresponding CSV file
            base_name = os.path.splitext(file_name)[0]  # Remove extension
            corresponding_csv = None
            for csv_file in os.listdir(csv_folder):
                if csv_file.startswith(base_name):
                    corresponding_csv = os.path.join(csv_folder, csv_file)
                    break

            if not corresponding_csv:
                print(f"No corresponding CSV found for image: {file_name}")
                continue
            a = "FLAIR"

            output_file = os.path.join(output_folder, f"{base_name}_captions.json")
            generate_human_like_caption(image_path, corresponding_csv, metadata_file, output_file, a, last_dataset, selection, size)
            print(f"Processed: {file_name} with {os.path.basename(corresponding_csv)} (Dataset: {last_dataset}, Modality: {a})")



if __name__ == "__main__":
    # Initialisation de argparse pour prendre les paramètres depuis la ligne de commande
    parser = argparse.ArgumentParser(description="Generate captions for medical scans.")
    
    # Ajoute des arguments pour chaque dossier
    parser.add_argument("input_folder", type=str, help="Path to the folder containing images")
    parser.add_argument("csv_folder", type=str, help="Path to the folder containing CSV files")
    parser.add_argument("metadata_folder", type=str, help="Path to the metadata folder")
    parser.add_argument("output_folder", type=str, help="Path to save the JSON files")
    parser.add_argument("--selection", type=str, help="Selection of structures (e.g., '1 2 3')", default=None)
    parser.add_argument("--size", type=int, help="Number of top structures to display", default=None)
    parser.add_argument("--var", type=int, help="Number of structures with the highest variance to display", default=None)

    
    # Parse les arguments passés dans la ligne de commande
    args = parser.parse_args()
    
    # Appelle la fonction pour générer les légendes avec les dossiers fournis en arguments
    process_folder(args.input_folder, args.csv_folder, args.metadata_folder, args.output_folder, args.selection, args.size)
