import SimpleITK as sitk
import os
import re
import sys
import matplotlib.pyplot as plt

def getInfo():
    # Extract information from the input file name
    ID_fix = ""
    Im_fix = ""
    pattern_fix = re.search(r'reg_KKI2009-(\d+)', inputFile)
    if pattern_fix:
        ID_fix = f"{pattern_fix.group(1)}"
        Im_fix = "KKI"

    pattern_fix = re.search(r'reg_OAS1_(\d+)', inputFile)
    if pattern_fix:
        ID_fix = f"{pattern_fix.group(1)}"
        Im_fix = "OAS"

    pattern_fix = re.search(r'reg_IXI(\d+)', inputFile)
    if pattern_fix:
        ID_fix = f"{pattern_fix.group(1)}"
        Im_fix = "IXI"

    pattern_fix = re.search(r'reg_IBSR_(\d+)', inputFile)
    if pattern_fix:
        ID_fix = f"{pattern_fix.group(1)}"
        Im_fix = "IBSR"

    # Moving image info
    ID_mov = ""
    Im_mov = ""
    pattern_mov = re.search(r'^KKI2009-(\d+)', inputFile)
    if pattern_mov:
        ID_mov = f"{pattern_mov.group(1)}"
        Im_mov = "KKI"

    pattern_mov = re.search(r'^OAS1_(\d+)', inputFile)
    if pattern_mov:
        ID_mov = f"{pattern_mov.group(1)}"
        Im_mov = "OAS"

    pattern_mov = re.search(r'^IXI(\d+)', inputFile)
    if pattern_mov:
        ID_mov = f"{pattern_mov.group(1)}"
        Im_mov = "IXI"

    pattern_mov = re.search(r'^IBSR_(\d+)', inputFile)
    if pattern_mov:
        ID_mov = f"{pattern_mov.group(1)}"
        Im_mov = "IBSR"

    return Im_mov, ID_mov, Im_fix, ID_fix

def save_selected_slice(image, output_folder, file_prefix, plane, index):
    """
    Save a specific slice from a 3D image as a 2D .jpg or .png image.
    
    Parameters:
        image: SimpleITK.Image
            The input 3D image.
        output_folder: str
            The folder to save the slice.
        file_prefix: str
            Prefix for the output file name.
        plane: str
            The plane to slice ('sagittal', 'coronal', 'axial').
        index: int
            The index of the slice to save.
    """
    image_array = sitk.GetArrayViewFromImage(image)  # Get NumPy array view

    if plane == 'sagittal':
        slice_ = image_array[index, :, :]
    elif plane == 'coronal':
        slice_ = image_array[:, index, :]
    elif plane == 'axial':
        slice_ = image_array[:, :, index]
    else:
        raise ValueError("Invalid plane. Choose from 'sagittal', 'coronal', or 'axial'.")

    # Save the selected slice
    plt.figure(figsize=(8, 8))
    plt.imshow(slice_, cmap="gray")
    plt.axis('off')
    plt.title(f"Plane: {plane.capitalize()} | Slice: {index}")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    output_path = os.path.join(output_folder, f"{file_prefix}_{plane}_{index:03d}.png")
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()

if len(sys.argv) != 2:
    print("Usage: python3 script.py <inputFile>")
    sys.exit(1)

# Parse input
inputFilePath = sys.argv[1]
inputFile = os.path.basename(inputFilePath)

# Extract metadata and determine output folder
Im_mov, ID_mov, Im_fix, ID_fix = getInfo()
file_prefix = f"{Im_mov}_{ID_mov}_{Im_fix}_{ID_fix}" if Im_fix else f"{Im_mov}_{ID_mov}"
outputPath = os.path.join(os.path.dirname(os.path.dirname(inputFilePath)), f"slice_NG_{file_prefix}")
if not os.path.exists(outputPath):
    os.makedirs(outputPath)

# Load image using SimpleITK
image = sitk.ReadImage(inputFilePath)

# Ask the user for slice selection
print("Choose the plane to slice (sagittal, coronal, axial):")
plane = input().strip().lower()

print(f"Enter the slice index for {plane} plane:")
index = int(input().strip())

# Save the selected slice
save_selected_slice(image, outputPath, file_prefix, plane, index)

print(f"Selected slice saved to {outputPath}")
