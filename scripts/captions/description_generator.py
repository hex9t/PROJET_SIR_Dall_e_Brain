import csv
import numpy as np
import nibabel as nib  # To handle 3D medical image formats (e.g., NIfTI)
import re
import os
import argparse
# exemple d'utiliser python description_generator.py Anatomie_IBSR.csv "e:\SIR\data\T1\IBSR\seg" dossier_output

# Configure argument parser
parser = argparse.ArgumentParser(description="3D Image Description Generator")
parser.add_argument("input_csv_path", type=str, help="Path to the input CSV file")
parser.add_argument("input_images_folder", type=str, help="Folder containing 3D image files")
parser.add_argument("output_folder", type=str, help="Folder where CSV files will be saved")
args = parser.parse_args()

# Get arguments from the command line
input_csv_path = args.input_csv_path
input_images_folder = args.input_images_folder
output_folder = args.output_folder

# Create the results folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Step 1: Parse the input CSV file to create a dictionary
label_dict = {}
with open(input_csv_path, mode="r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        label_id = int(row["ID"])
        label_name = row["Labels"]
        # Use regex to extract only numeric values from the RGB field
        rgb = list(map(int, re.findall(r'\d+', row["RGB"])))
        label_dict[label_id] = {"label_name": label_name, "rgb": rgb}

# Step 2: Process each image in the input folder
for image_filename in os.listdir(input_images_folder):
    if image_filename.endswith(".nii.gz"):  # Process only NIfTI files
        input_image_path = os.path.join(input_images_folder, image_filename)

        # Load the 3D image
        img = nib.load(input_image_path)  # Load the NIfTI image
        image_data = img.get_fdata().astype(int)  # Convert the image data to integers for processing
        voxel_size = img.header.get_zooms()[:3]  # Get voxel size (x, y, z) in mm
        voxel_volume = np.prod(voxel_size)  # Calculate voxel volume in mm³

        # Step 3: Analyze the image and count voxels for each label
        unique_labels, voxel_counts = np.unique(image_data, return_counts=True)

        # Prepare the output CSV file path
        output_csv_path = os.path.join(output_folder, f"{os.path.splitext(image_filename)[0]}_description3D.csv")

        # Step 4: Generate the output CSV with labels, voxel counts, and voxel volumes
        with open(output_csv_path, mode="w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            # Write the header
            csv_writer.writerow(["ID", "Label", "RGB", "Voxel Count", "Voxel Volume (mm³)"])

            for label_id, count in zip(unique_labels, voxel_counts):
                if label_id in label_dict:
                    label_name = label_dict[label_id]["label_name"]
                    rgb = label_dict[label_id]["rgb"]
                    total_volume = round(count * voxel_volume, 2)  # Calculate total volume for the label
                    csv_writer.writerow([label_id, label_name, rgb, count, total_volume])
                else:
                    # Handle unknown labels
                    total_volume = round(count * voxel_volume, 2)
                    csv_writer.writerow([label_id, "Unknown", [0, 0, 0], count, total_volume])

                    # Optional: Warn if volumes seem unusually large
                    if total_volume > 1_500_000:  # Adjust threshold as needed
                        print(f"Warning: Large volume detected for unknown label {label_id} ({total_volume} mm³)")

        print(f"Processed {image_filename}, output saved to {output_csv_path}")

print("Processing complete.")


######################################
