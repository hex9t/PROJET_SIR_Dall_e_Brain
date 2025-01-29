import pandas as pd
import re
import json
import nibabel as nib  # To read NIfTI files
import os
import argparse
#exemple : python caption_generator_advanced.py data_kirby descriptions_3D .\metafolder\ captions_test 
#python caption_generator_advanced.py data_kirby descriptions_3D ./metafolder/ captions_test --var 5 : variance

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

def process_folder(folder_path, csv_folder, metadata_folder, output_folder, selection=None, size=None, var=None):
    # Calculate top variance structures if var is specified
    top_variance_structures = calculate_top_variance_structures(csv_folder, var) if var else None

    os.makedirs(output_folder, exist_ok=True)

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".nii.gz"):
            image_path = os.path.join(folder_path, file_name)

            if "KKI2009" in file_name:
                image_type = "Kirby"
                metadata_file = os.path.join(metadata_folder, "Kirby_info.csv")
            elif "OAS1" in file_name:
                image_type = "Oasis"
                metadata_file = os.path.join(metadata_folder, "OASIS_info.csv")
            elif "IBSR" in file_name:
                image_type = "IBSR"
                metadata_file = os.path.join(metadata_folder, "IBSR_info.csv")
            elif "IXIID-IOP" in file_name:
                image_type = "IXI"
                metadata_file = os.path.join(metadata_folder, "IXI_info.csv")
            else:
                print(f"Unknown dataset type for image: {file_name}")
                continue

            base_name = os.path.splitext(file_name)[0]
            corresponding_csv = None
            for csv_file in os.listdir(csv_folder):
                if csv_file.startswith(base_name):
                    corresponding_csv = os.path.join(csv_folder, csv_file)
                    break

            if not corresponding_csv:
                print(f"No corresponding CSV found for image: {file_name}")
                continue

            output_file = os.path.join(output_folder, f"{base_name}_captions.json")
            try:
                generate_human_like_caption(
                    image_path, corresponding_csv, metadata_file, output_file, image_type, selection, size, top_variance_structures
                )
                print(f"Processed: {file_name} with {os.path.basename(corresponding_csv)}")
            except Exception as e:
                print(f"Error processing {file_name}: {e}")
def generate_human_like_caption(image_filename, structures_file, metadata_file, output_file, image_type, selection=None, size=None):
    # Extract ID and type from image filename using regex
    match = None
    if image_type == "Kirby":
        match = re.search(r'KKI2009-(\d+)-([A-Z]+)', image_filename)
        scan_type = "FLAIR"
    elif image_type == "Oasis":
        match = re.search(r'OAS1_(\d+)_([A-Za-z0-9\-]+)', image_filename)
        scan_type = "T1"
    elif image_type == "IBSR":
        match = re.search(r'IBSR_(\d+)-([A-Z]+)', image_filename)
        scan_type = "T1"
    elif image_type == "IXI":
        match = re.search(r'IXI(\d+)-IOP-\d+-[A-Za-z0-9\-]+_majority', image_filename)
        scan_type = "T2"

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
    if metadata.empty:
        raise ValueError(f"No metadata found for ID {image_id} in file: {image_filename}")

    # Extract metadata details
    age = metadata.iloc[0]['AGE']
    gender = metadata.iloc[0]['GENDER']

    # Load the 3D image to get dimensions
    img = nib.load(image_filename)  # Load the NIfTI image
    image_data = img.get_fdata().astype(int)  # Convert the image data to integers for processing
    total_voxels = image_data.size  # Total number of voxels in the image

    # Filter out unknown structures
    filtered_structures = structures_df[structures_df['Label'] != "Unknown"]

    # Calculate brain volume
    brain_volume = filtered_structures['Voxel Volume (mm³)'].sum() / 1000  # Convert to cm³

    # Generate list of structures with volumes and percentages
    structures_with_volumes = []
    for _, row in filtered_structures.iterrows():
        label = row['Label']
        structure_volume = row['Voxel Volume (mm³)']
        percentage = round((row['Voxel Count'] / total_voxels) * 100, 2)
        structures_with_volumes.append({"label": label, "volume": structure_volume, "percentage": percentage})

    # Sort structures by volume (descending order)
    sorted_structures = sorted(structures_with_volumes, key=lambda x: x['volume'], reverse=True)

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
        "This {scan_type} scan shows a {gender} subject aged {age} with dimensions {dimensions}. Brain volume is {brain_volume:.2f} cm³. The most prominent structures are {structures}.",
        "A {scan_type} scan of a {gender} subject, {age} years old, with image dimensions {dimensions}. The total brain volume is {brain_volume:.2f} cm³, including major structures like {structures}.",
        "Here we see a {scan_type} scan of a {gender} subject aged {age}. The image dimensions are {dimensions}, and the brain volume is {brain_volume:.2f} cm³. Visible structures include {structures}.",
        "In this {scan_type} scan of a {age}-year-old {gender} subject, the image has dimensions {dimensions} and displays structures such as {structures}. The brain volume is {brain_volume:.2f} cm³.",
        "This {scan_type} scan captures the brain of a {gender} subject aged {age} with image dimensions {dimensions}. The brain volume is {brain_volume:.2f} cm³. Key structures include {structures}.",
        "This {scan_type} scan shows the brain of a {gender} subject aged {age}, with dimensions {dimensions}. The total brain volume is {brain_volume:.2f} cm³, and visible structures include {structures}.",
        "A {scan_type} scan of a {gender} subject, aged {age}, with dimensions {dimensions}. The total brain volume is {brain_volume:.2f} cm³, showing structures such as {structures}.",
        "Here is a {scan_type} scan of a {gender} subject aged {age}, with image dimensions {dimensions}. The brain volume is {brain_volume:.2f} cm³ and the visible structures include {structures}.",
        "This {scan_type} scan provides a view of the brain of a {gender} subject, aged {age}, with dimensions of {dimensions}. Brain volume is {brain_volume:.2f} cm³, and visible structures include {structures}.",
        "This is a {scan_type} scan of a {age}-year-old {gender}, with dimensions {dimensions}. The brain volume is {brain_volume:.2f} cm³, displaying structures like {structures}.",
    ]
    
    # Prepare structures text based on selected or all structures
    structures_text = ", ".join([f"{s['label']} ({s['volume']} mm³)" for s in sorted_structures[:-1]]) + f", and {sorted_structures[-1]['label']} ({sorted_structures[-1]['volume']} mm³)" if len(sorted_structures) > 1 else f"{sorted_structures[0]['label']} ({sorted_structures[0]['volume']} mm³)"

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
    output_data = {
        "image_filename": image_filename,
        "captions": captions
    }

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4, ensure_ascii=False)

    return captions


def process_folder(folder_path, csv_folder, metadata_folder, output_folder, selection=None, size=None):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".nii.gz"):  # Check for NIfTI files
            image_path = os.path.join(folder_path, file_name)

            # Determine the dataset type based on the filename pattern
            if "KKI2009" in file_name:
                image_type = "Kirby"
                metadata_file = os.path.join(metadata_folder, "Kirby_info.csv")
            elif "OAS1" in file_name:
                image_type = "Oasis"
                metadata_file = os.path.join(metadata_folder, "OASIS_info.csv")
            elif "IBSR" in file_name:
                image_type = "IBSR"
                metadata_file = os.path.join(metadata_folder, "IBSR_info.csv")
            elif "IXIID-IOP" in file_name:
                image_type = "IXI"
                metadata_file = os.path.join(metadata_folder, "IXI_info.csv")
            else:
                print(f"Unknown dataset type for image: {file_name}")
                continue

            # Find the corresponding CSV file for this image
            base_name = os.path.splitext(file_name)[0]  # Remove extension
            corresponding_csv = None
            for csv_file in os.listdir(csv_folder):
                if csv_file.startswith(base_name):
                    corresponding_csv = os.path.join(csv_folder, csv_file)
                    break

            if not corresponding_csv:
                print(f"No corresponding CSV found for image: {file_name}")
                continue

            output_file = os.path.join(output_folder, f"{base_name}_captions.json")
            try:
                generate_human_like_caption(image_path, corresponding_csv, metadata_file, output_file, image_type, selection, size)
                print(f"Processed: {file_name} with {os.path.basename(corresponding_csv)}")
            except Exception as e:
                print(f"Error processing {file_name}: {e}")


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
