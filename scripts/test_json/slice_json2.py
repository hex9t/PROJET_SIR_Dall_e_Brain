import os
import re
import json
import sys
import numpy as np
import nibabel as nib
import threading
import time
from queue import Queue

# Function to extract metadata from the file name
def getInfo(inputFile):
    # Patterns for fixed and moving images
    patterns = [
        (r'reg_KKI2009-(\d+)', "KKI"),
        (r'reg_OAS1_(\d+)', "OAS"),
        (r'reg_IXI(\d+)', "IXI"),
        (r'reg_IBSR_(\d+)', "IBSR")
    ]
    Im_fix, ID_fix, Im_mov, ID_mov = "", "", "", ""

    for pattern, prefix in patterns:
        if match := re.search(pattern, inputFile):
            ID_fix, Im_fix = match.group(1), prefix

    for pattern, prefix in [(r'^KKI2009-(\d+)', "KKI"), (r'^OAS1_(\d+)', "OAS"),
                            (r'^IXI(\d+)', "IXI"), (r'^IBSR_(\d+)', "IBSR")]:
        if match := re.search(pattern, inputFile):
            ID_mov, Im_mov = match.group(1), prefix

    return Im_mov, ID_mov, Im_fix, ID_fix

# Function to find the fixed image path
def fixPath(Im_fix, ID):
    # Paths for different types of images
    paths = {
        "IBSR": "../data/T1/IBSR/seg",
        "IXI": "../data/T2/IXI/seg",
        "OAS": "../data/T1/OASIS/seg",
        "KKI": "../data/FL/Kirby/seg"
    }
    pathFile = paths.get(Im_fix, "")
    files = [f for f in os.listdir(pathFile) if f.endswith('.nii.gz')]
    for file in files:
        if f"{Im_fix}_{ID}" in file or f"{Im_fix}{ID}" in file:
            return os.path.join(pathFile, file)
    return ""

# Special handling for IBSR files
def findSegIBSR(inputFile, ID_mov, Im_fix, ID_fix):
    fixedPath = ""
    if "inv" in inputFile:
        pathFile = os.path.join(os.path.sep.join(inputFolder.split(os.path.sep)[:-1]), "seg_inv")
    elif Im_fix == "IBSR":
        pathFile = "../data/T1/IBSR/seg"
    else:
        pathFile = os.path.join(os.path.sep.join(inputFolder.split(os.path.sep)[:-1]), "seg")
    files = [f for f in os.listdir(pathFile) if f.endswith('.nii.gz')]
    for file in files:
        if f"IBSR_{ID_mov}" in file or f"IBSR_{ID_fix}" in file:
            fixedPath = os.path.join(pathFile, file)
            break
    return fixedPath

# Function to generate slice information for segmentation
def getSlicesSeg(inputImage):
    arrayImage = inputImage.get_fdata()

    sagittal_len, coronal_len, axial_len = arrayImage.shape
    sliceArray = []

    # Process sagittal slices
    for i in range(sagittal_len):
        image_slice = arrayImage[i, :, :]
        unique_values, counts = np.unique(image_slice, return_counts=True)
        sliceArray.append({
            "plane": "sagittal",
            "index": i,
            "dimensions": image_slice.shape,
            "voxel_size": [float(x) for x in inputImage.header.get_zooms()],
            "labels": [(int(label), int(count)) for label, count in zip(unique_values, counts)]
        })

    # Process coronal slices
    for i in range(coronal_len):
        image_slice = arrayImage[:, i, :]
        unique_values, counts = np.unique(image_slice, return_counts=True)
        sliceArray.append({
            "plane": "coronal",
            "index": i,
            "dimensions": image_slice.shape,
            "voxel_size": [float(x) for x in inputImage.header.get_zooms()],
            "labels": [(int(label), int(count)) for label, count in zip(unique_values, counts)]
        })

    # Process axial slices
    for i in range(axial_len):
        image_slice = arrayImage[:, :, i]
        unique_values, counts = np.unique(image_slice, return_counts=True)
        sliceArray.append({
            "plane": "axial",
            "index": i,
            "dimensions": image_slice.shape,
            "voxel_size": [float(x) for x in inputImage.header.get_zooms()],
            "labels": [(int(label), int(count)) for label, count in zip(unique_values, counts)]
        })

    return sliceArray

# Function to process a single file
def process_file(inputFile, queue):
    inputFilePath = os.path.join(inputFolder, inputFile)
    Im_mov, ID_mov, Im_fix, ID_fix = getInfo(inputFile)

    # Handle IBSR files differently
    if Im_mov == "IBSR":
        fixedImagePath = findSegIBSR(inputFile, ID_mov, Im_fix, ID_fix)
    else:
        fixedImagePath = fixPath(Im_fix, ID_fix)

    # Load the fixed image and generate slice information
    if fixedImagePath:
        fixedImage = nib.load(fixedImagePath)
        sliceArray = getSlicesSeg(fixedImage)

        # Save to JSON
        json_file = f"{Im_mov}_{ID_mov}_{Im_fix}_{ID_fix}.json"
        chemin_json_sortie = os.path.join(chemin_output, json_file)
        with open(chemin_json_sortie, 'w') as jsonfile:
            json.dump(sliceArray, jsonfile, indent=4)
        print(f"File {inputFile} processed. JSON saved as {json_file}.")
    else:
        print(f"Fixed image path not found for: {inputFile}")

    queue.task_done()

# Worker function for threads
def worker_function(queue):
    while True:
        inputFile = queue.get()
        if inputFile is None:
            break
        process_file(inputFile, queue)


# Function to process files using threads
def process_files_with_threads(files, queue):
    thread_count = 6  # Number of threads per process

    # Start worker threads
    for _ in range(thread_count):
        worker = threading.Thread(target=worker_function, args=(queue,))
        worker.daemon = True
        worker.start()

    # Add tasks to the queue
    for inputFile in files:
        queue.put(inputFile)

    # Wait for all tasks to complete
    queue.join()

# Function to handle processing for each chunk in a separate process
def process_files_in_process(files_chunk):
    queue = Queue()
    process_files_with_threads(files_chunk, queue)

# Main function
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <inputFolder>")
        sys.exit(1)

    inputFolder = sys.argv[1]

    # Prepare output directory
    inputFiles = [f for f in os.listdir(inputFolder) if f.endswith('.nii.gz')]

    # Calculate the output directory
    if inputFolder.endswith("inv"):
        chemin_output = os.path.join(os.path.sep.join(inputFolder.split(os.path.sep)[:-1]), "Slice_json_inv")
    else:
        chemin_output = os.path.join(os.path.sep.join(inputFolder.split(os.path.sep)[:-1]), "Slice_json")
    if not os.path.exists(chemin_output):
        os.makedirs(chemin_output)

    # Split the input files into 8 chunks
    num_chunks = 4
    chunk_size = len(inputFiles) // num_chunks
    inputChunks = [inputFiles[i * chunk_size:(i + 1) * chunk_size] for i in range(num_chunks)]

    # Create 8 processes, each processing a chunk of files
    start_time = time.time()
    processes = []
    for chunk in inputChunks:
        p = threading.Thread(target=process_files_in_process, args=(chunk,))
        processes.append(p)
        p.start()

    # Wait for all processes to finish
    for p in processes:
        p.join()

    end_time = time.time()
    duration = end_time - start_time
    print(f"All files processed! Total time: {duration:.2f} seconds.")
