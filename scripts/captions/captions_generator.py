import pandas as pd
import re
import json

def generate_human_like_caption(image_filename, structures_file, metadata_file, output_file):
    # Extract ID and type from image filename using regex
    match = re.search(r'KKI2009-(\d+)-([A-Z]+)', image_filename)
    if not match:
        raise ValueError("Invalid image filename format. ID or type not found.")

    image_id = int(match.group(1))
    image_type = match.group(2)

    # Load CSV files
    structures_df = pd.read_csv(structures_file)
    metadata_df = pd.read_csv(metadata_file)

    # Find metadata based on image ID
    metadata = metadata_df[metadata_df['ID'] == image_id]
    if metadata.empty:
        raise ValueError(f"No metadata found for ID {image_id}.")

    # Extract metadata details
    age = metadata.iloc[0]['AGE']
    gender = metadata.iloc[0]['GENDER']

    # Filter out unknown structures
    filtered_structures = structures_df[structures_df['Label'] != "Unknown"]

    # Generate list of structures with voxel counts
    structures_with_voxels = [
        f"{row['Label']} ({row['Voxel Count']} voxels)"
        for _, row in filtered_structures.iterrows()
    ]

    # Define sentence templates for variety
    templates = [
        "This is a {type} scan of a {gender} subject, aged {age}. The structures visible include {structures}.",
        "In this {type} scan of a {age}-year-old {gender}, key structures such as {structures} are highlighted.",
        "{type} imaging reveals {structures} in a {age}-year-old {gender}.",
        "A {type} scan of a {age}-year-old {gender} shows the following structures: {structures}.",
        "Key structures identified in this {type} scan of a {gender} aged {age} include {structures}.",
        "For this {type} scan, the subject is a {age}-year-old {gender}, and it highlights {structures}.",
        "This scan type ({type}) displays structures such as {structures} in a {gender} subject, aged {age}.",
        "The {type} image for this {age}-year-old {gender} shows: {structures}.",
        "In this scan ({type}), we observe {structures} in a {gender} aged {age}.",
        "This {type} imaging, of a {gender} subject who is {age} years old, highlights {structures}."
    ]

    # Generate captions using all templates
    captions = []
    structures_text = ", ".join(structures_with_voxels[:-1]) + f", and {structures_with_voxels[-1]}" if len(structures_with_voxels) > 1 else structures_with_voxels[0]

    for template in templates:
        caption = template.format(
            type=image_type,
            gender="male" if gender == "M" else "female",
            age=age,
            structures=structures_text
        )
        captions.append(caption)

    # Save the captions to a JSON file
    output_data = {
        "image_filename": image_filename,
        "captions": captions
    }

    with open(output_file, "w") as file:
        json.dump(output_data, file, indent=4)

    return captions

# Example usage
structures_csv = "test.csv"  # Path to the first CSV file
metadata_csv = "Kirby_info.csv"      # Path to the second CSV file
image_name = "KKI2009-1-FLAIR_brainMajorityDirect.nii"
output_json = "caption.json"

captions = generate_human_like_caption(image_name, structures_csv, metadata_csv, output_json)
print(captions)
