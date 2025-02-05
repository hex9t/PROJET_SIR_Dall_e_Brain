import SimpleITK as sitk
import numpy as np
import sys
import os
import glob
from scipy.ndimage import distance_transform_edt

# Fonction de correction des labels maximum
def correct_max_labels_3d(image, max_label):
    
    # Trouver les positions des voxels à corriger (valeurs max_label)
    mask_max_label = (image == max_label)

    # Créer un masque pour les voxels valides (labels existants sauf max_label)
    mask_valid_labels = (image != max_label) & (image > 0)

    # Calculer la distance au plus proche voxel valide pour chaque voxel
    distances, indices = distance_transform_edt(
        ~mask_valid_labels,  # Inverser pour considérer les voxels valides comme "sources"
        return_indices=True
    )

    # Extraire les indices des voisins valides les plus proches
    closest_z, closest_y, closest_x = indices  # Indices en 3D

    # Créer une copie de l'image pour appliquer les corrections
    corrected_image = image.copy()

    # Remplacer les voxels max_label par les valeurs des voisins les plus proches
    corrected_image[mask_max_label] = image[
        closest_z[mask_max_label],
        closest_y[mask_max_label],
        closest_x[mask_max_label]
    ]

    return corrected_image


# Fonction pour extraire un préfixe spécifique à partir du nom du fichier
def get_prefix_after_forth_underscore(file_path):
    base_name = os.path.basename(file_path)
    parts = base_name.split('_')
    x=len(parts)
    name=f"{parts[4]}"
    if x >= 6:
        z=5
        while z < x:
            name=name+f"_{parts[z]}"
            z=z+1
        return name.replace('.nii.gz', '')
    else:
        return None

if len(sys.argv) > 1:
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
else:
    print("Usage: script.py <input_folder> <output_folder>")
    sys.exit(1)

# Charger tous les fichiers .nii.gz
all_files = glob.glob(os.path.join(input_folder, "*.nii.gz"))
if not all_files:
    print(f"No files found in {input_folder} matching *.nii.gz")
    sys.exit(1)

file_groups = {}
for filename in all_files:
    prefix = get_prefix_after_forth_underscore(filename)
    if prefix:
        if prefix not in file_groups:
            file_groups[prefix] = []
        file_groups[prefix].append(filename)

# Traitement des groupes d'images
for prefix, files in file_groups.items():
    images = []
    for file_path in files:
        img = sitk.ReadImage(file_path, sitk.sitkUInt32)
        images.append(img)

    # Appliquer le majority voting
    label_voting_filter = sitk.LabelVotingImageFilter()
    result_image = label_voting_filter.Execute(images)

    # Conversion du résultat en NumPy pour correction
    result_np = sitk.GetArrayFromImage(result_image)

    # Correction des labels max
    max_label = np.max(result_np)
    corrected_result = correct_max_labels_3d(result_np, max_label)

    # Reconversion en SimpleITK Image
    corrected_result_sitk = sitk.GetImageFromArray(corrected_result)
    corrected_result_sitk.CopyInformation(result_image)

    # Sauvegarder l'image résultante
    output_path = os.path.join(output_folder, prefix + "_corrected_majority.nii.gz")
    sitk.WriteImage(corrected_result_sitk, output_path)
    print(f"Traitement complet pour le préfixe : {prefix}")
