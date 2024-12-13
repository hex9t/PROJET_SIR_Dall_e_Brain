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

def save_slices_as_images(image, output_folder, file_prefix):
    """
    Save slices from a 3D image as 2D .jpg or .png images.
    
    Parameters:
        image: SimpleITK.Image
            The input 3D image.
        output_folder: str
            The folder to save the slices.
        file_prefix: str
            Prefix for the output file names.
    """
    image_array = sitk.GetArrayViewFromImage(image)  # Get NumPy array view
    sagittal_len, coronal_len, axial_len = image_array.shape

    # Save slices in axial, coronal, and sagittal planes
    for i in range(sagittal_len):
        slice_ = image_array[i, :, :]
        plt.imshow(slice_, cmap="gray")
        plt.axis('off')
        plt.savefig(os.path.join(output_folder, f"{file_prefix}_sagittal_{i:03d}.png"), bbox_inches='tight', pad_inches=0)
        plt.close()

    for i in range(coronal_len):
        slice_ = image_array[:, i, :]
        plt.imshow(slice_, cmap="gray")
        plt.axis('off')
        plt.savefig(os.path.join(output_folder, f"{file_prefix}_coronal_{i:03d}.png"), bbox_inches='tight', pad_inches=0)
        plt.close()

    for i in range(axial_len):
        slice_ = image_array[:, :, i]
        plt.imshow(slice_, cmap="gray")
        plt.axis('off')
        plt.savefig(os.path.join(output_folder, f"{file_prefix}_axial_{i:03d}.png"), bbox_inches='tight', pad_inches=0)
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

# Save slices as images
save_slices_as_images(image, outputPath, file_prefix)

print(f"All slices saved to {outputPath}")