import pandas as pd
import re
import json
import nibabel as nib  # To read NIfTI files
import os
import argparse


###############################################
def generate_human_like_caption(image_filename, structures_file, metadata_file, output_file, image_type):
    # Extract ID and type from image filename using regex
    match = None
    if image_type == "Kirby":
        match = re.search(r'KKI2009-(\d+)-([A-Z]+)', image_filename)
        scan_type = "FLAIR"
    elif image_type == "Oasis":
        # Updated regex to match OAS1_0026_majority.nii.gz format
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

    # Generate list of structures with volumes and percentages
    structures_with_volumes = []
    for _, row in filtered_structures.iterrows():
        label = row['Label']
        structure_volume = row['Voxel Volume (mm³)']
        percentage = round((row['Voxel Count'] / total_voxels) * 100, 2)
        structures_with_volumes.append(f"{label} ({structure_volume} mm³)")

    # Define sentence templates
    templates = [
    "This is a {scan_type} scan of a {gender} subject, aged {age}, with image dimensions {dimensions}. The structures visible include {structures}.",
    "In this {scan_type} scan of a {age}-year-old {gender} with dimensions {dimensions}, key structures such as {structures} are highlighted.",
    "This {scan_type} scan shows a {gender} subject aged {age}. The image has dimensions {dimensions}, and it includes structures like {structures}.",
    "A {scan_type} scan of a {gender} subject, {age} years old, with the dimensions {dimensions}. The major visible structures include {structures}.",
    "Here is a {scan_type} scan of a {gender} subject aged {age}. The image has dimensions {dimensions} and displays structures such as {structures}.",
    "This {scan_type} scan captures the brain of a {gender} subject aged {age}, with image dimensions {dimensions}. Key structures visible include {structures}.",
    "A {scan_type} scan from a {gender} subject, {age} years old, showing detailed structures with dimensions {dimensions}. Structures include {structures}.",
    "This {scan_type} scan, taken from a {gender} subject aged {age}, displays important brain structures such as {structures}. The dimensions of the image are {dimensions}.",
    "Here we see a {scan_type} scan of a {gender} subject, aged {age}, with image dimensions {dimensions}. Visible structures include {structures}.",
    "In this {scan_type} scan, a {gender} subject aged {age} is shown with image dimensions {dimensions}. The scan highlights structures like {structures}.",
    "A {scan_type} scan of a {gender} subject, aged {age}, showing the following structures: {structures}. The image dimensions are {dimensions}.",
    "This {scan_type} scan provides a view of the brain of a {gender} subject, aged {age}, with dimensions of {dimensions}. Visible structures include {structures}.",
    "This is a {scan_type} scan of a {age}-year-old {gender}, with dimensions {dimensions}. It displays structures such as {structures}.",
]
    
    
    
    
    # Generate captions using all templates
    captions = []
    structures_text = ", ".join(structures_with_volumes[:-1]) + f", and {structures_with_volumes[-1]}" if len(structures_with_volumes) > 1 else structures_with_volumes[0]

    for template in templates:
        caption = template.format(
            scan_type=scan_type,
            gender="male" if gender == "M" else "female",
            age=age,
            dimensions=f"{img.shape[0]} x {img.shape[1]} x {img.shape[2]}",
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


def process_folder(folder_path, csv_folder, metadata_folder, output_folder):
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
                generate_human_like_caption(image_path, corresponding_csv, metadata_file, output_file, image_type)
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
    
    # Parse les arguments passés dans la ligne de commande
    args = parser.parse_args()
    
    # Appelle la fonction pour générer les légendes avec les dossiers fournis en arguments
    process_folder(args.input_folder, args.csv_folder, args.metadata_folder, args.output_folder)