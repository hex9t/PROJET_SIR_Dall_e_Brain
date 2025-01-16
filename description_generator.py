import csv
import numpy as np
import nibabel as nib  # To handle 3D medical image formats (e.g., NIfTI)

# File paths
input_csv_path = "Anatomie_IBSR.csv"  # The input CSV file
input_image_path = "KKI2009-01-FLAIR_brainMajorityDirect.nii.gz"  # The 3D image file
output_csv_path = "test.csv"  # The output CSV file

# Step 1: Parse the input CSV file to create a dictionary
label_dict = {}
with open(input_csv_path, mode="r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    import re

    for row in csv_reader:
        label_id = int(row["ID"])
        label_name = row["Labels"]
        # Use regex to extract only numeric values from the RGB field
        rgb = list(map(int, re.findall(r'\d+', row["RGB"])))
        label_dict[label_id] = {"label_name": label_name, "rgb": rgb}



# Step 2: Read the 3D image
img = nib.load(input_image_path)  # Load the NIfTI image
image_data = img.get_fdata().astype(int)  # Convert the image data to integers for processing

# Step 3: Analyze the image and count voxels for each label
unique_labels, voxel_counts = np.unique(image_data, return_counts=True)

# Step 4: Generate the output CSV with labels and voxel counts
with open(output_csv_path, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    # Write the header
    csv_writer.writerow(["ID", "Label", "RGB", "Voxel Count"])

    for label_id, count in zip(unique_labels, voxel_counts):
        if label_id in label_dict:
            label_name = label_dict[label_id]["label_name"]
            rgb = label_dict[label_id]["rgb"]
            csv_writer.writerow([label_id, label_name, rgb, count])
        else:
            # Handle unknown labels (optional)
            csv_writer.writerow([label_id, "Unknown", [0, 0, 0], count])

print(f"Output saved to {output_csv_path}")
