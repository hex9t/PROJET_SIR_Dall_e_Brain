import csv
import os
import re
import numpy as np
import nibabel as nib  

# File paths
input_csv_path = "./data/Keywords/Anatomie_IBSR.csv"  # The input CSV file
input_image_folder = "./Data_analyse/IXI_seg"  # The folder containing 3D image files
output_folder = os.path.join(input_image_folder, "csv_files") # The output folder for CSV files

# Ensure output folder exists
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

# Step 2: Process each NIfTI file in the folder
for file_name in os.listdir(input_image_folder):
    if file_name.endswith(".nii.gz"):  # Only process NIfTI files
        input_image_path = os.path.join(input_image_folder, file_name)
        output_csv_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.csv")
        
        # Read the 3D image
        img = nib.load(input_image_path)  # Load the NIfTI image
        image_data = img.get_fdata().astype(int)  # Convert the image data to integers for processing
        voxel_size = np.prod(img.header.get_zooms()[:3])  # Compute voxel size in mm^3
        
        # Analyze the image and count voxels for each label
        unique_labels, voxel_counts = np.unique(image_data, return_counts=True)

        # Calculate total volume excluding label ID 0
        total_volume_nonzero = sum(count * voxel_size for label, count in zip(unique_labels, voxel_counts) if label != 0)

        # Generate the output CSV with labels, voxel counts, volumes, and volume ratio
        with open(output_csv_path, mode="w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            # Write the header
            csv_writer.writerow(["ID", "Label", "RGB", "Voxel Count", "Volume (mm³)", "Volume Ratio (%)"])

            for label_id, count in zip(unique_labels, voxel_counts):
                volume_mm3 = count * voxel_size  # Calculate the volume in mm³
                if label_id in label_dict:
                    label_name = label_dict[label_id]["label_name"]
                    rgb = label_dict[label_id]["rgb"]
                    # Calculate volume ratio (exclude label ID 0 from total volume)
                    volume_ratio = (volume_mm3 / total_volume_nonzero * 100) if label_id != 0 else 0
                    csv_writer.writerow([label_id, label_name, rgb, count, f"{volume_mm3:.2f}", f"{volume_ratio:.2f}"])
                else:
                    # Handle unknown labels (optional)
                    volume_ratio = (volume_mm3 / total_volume_nonzero * 100) if label_id != 0 else 0
                    csv_writer.writerow([label_id, "Unknown", [0, 0, 0], count, f"{volume_mm3:.2f}", f"{volume_ratio:.2f}"])

        print(f"Processed file: {file_name}, output saved to {output_csv_path}")
