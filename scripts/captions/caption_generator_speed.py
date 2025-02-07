import pandas as pd
import re
import json
import nibabel as nib  # Pour lire les fichiers NIfTI
import os
import random
from multiprocessing import Pool

# Entrées (définies directement dans le code, pas via la ligne de commande)
INPUT_FOLDER = r"E:\SIR\FL\Kirby_OASIS\seg"          # Dossier des images
CSV_FOLDER = r"E:\SIR\FL\Kirby_OASIS\descriptions"     # Dossier des CSV de description
METADATA_FOLDER = r"E:\SIR\Keywords"                   # Dossier des métadonnées
OUTPUT_BASE_FOLDER = r"E:\SIR\FL\Kirby_OASIS\captions_3d"  # Dossier de sortie

###############################################
def calculate_top_variance_structures(csv_folder, n):
    """Calcule les n structures avec la plus grande variance et retourne leurs IDs."""
    structure_variances = {}
    # Associer chaque label à son ID
    label_to_id = {}
    # Parcourir les CSV pour collecter les volumes
    for csv_file in os.listdir(csv_folder):
        if csv_file.endswith(".csv"):
            file_path = os.path.join(csv_folder, csv_file)
            df = pd.read_csv(file_path, encoding='latin1')
            for _, row in df.iterrows():
                label = row['Label']
                if label == "Unknown":
                    continue
                volume = row['Voxel Volume (mm³)']
                structure_id = row['ID']  # On suppose que le CSV contient une colonne "ID"
                if label not in structure_variances:
                    structure_variances[label] = []
                    label_to_id[label] = structure_id
                structure_variances[label].append(volume)
    # Calculer la variance de chaque structure
    variance_results = {label: pd.Series(volumes).var() for label, volumes in structure_variances.items()}
    # Trier par variance décroissante et prendre les n premiers
    top_structures = sorted(variance_results.items(), key=lambda x: x[1], reverse=True)[:n]
    top_ids = [label_to_id[label] for label, _ in top_structures]
    return top_ids

def generate_human_like_caption(image_filename, csv_folder, structures_file, metadata_file, output_file, a, image_type, selection=None, size=None, var=None):
    # Extraire l'ID et le type à partir du nom de fichier
    match = None
    if image_type == "Kirby":
        match = re.search(r'KKI2009-(\d+)-([A-Z]+)', image_filename)
        scan_type = "FLAIR"
    elif image_type == "Oasis":
        match = re.search(r'OAS1_(\d+)_([A-Za-z0-9\-]+)', image_filename)
        scan_type = "T1"
    elif image_type == "IBSR":
        match = re.search(r'IBSR_(\d+)_(.+)', image_filename)
        scan_type = "T1"
    elif image_type == "IXI":
        match = re.search(r'IXI(\d+)-IOP-\d+-([A-Z]+)', image_filename)
        scan_type = "T2"
    scan_type = a

    if not match:
        raise ValueError(f"Format de nom de fichier invalide : {image_filename}")

    image_id = int(match.group(1))
    if image_type == "Kirby":
        image_type = match.group(2)

    # Charger les fichiers CSV
    structures_df = pd.read_csv(structures_file, encoding='latin1')
    metadata_df = pd.read_csv(metadata_file, encoding='latin1')

    # Rechercher les métadonnées correspondant à l'image
    metadata = metadata_df[metadata_df['ID'] == image_id]
    if metadata.empty:
        age = "unknown"
        gender = "human"
    else:
        if image_type == "IXI":
            age = metadata.iloc[0]['AGE']
            age = int(float(age.replace(",", "."))) if pd.notna(age) else "unknown"
        else:
            age = metadata.iloc[0]['AGE']
            age = age if pd.notna(age) else "unknown"
        gender = metadata.iloc[0]['GENDER']
        gender = gender if pd.notna(gender) else "human"

    # Charger l'image 3D et obtenir ses dimensions
    img = nib.load(image_filename)
    image_data = img.get_fdata().astype(int)
    total_voxels = image_data.size

    # Filtrer les structures inconnues
    filtered_structures = structures_df[structures_df['Label'] != "Unknown"]
    # Calculer le volume du cerveau
    brain_volume = round(filtered_structures['Voxel Volume (mm³)'].sum() / 1000)

    # Générer la liste des structures avec volume et pourcentage
    structures_with_volumes = []
    for _, row in filtered_structures.iterrows():
        structure_id = row['ID']
        label = row['Label']
        structure_volume = row['Voxel Volume (mm³)'] / 1000
        percentage = round((row['Voxel Count'] / total_voxels) * 100, 2)
        structures_with_volumes.append({
            "id": structure_id,
            "label": label,
            "volume": structure_volume,
            "percentage": percentage
        })

    # Trier par volume décroissant
    sorted_structures = sorted(structures_with_volumes, key=lambda x: x['volume'], reverse=True)

    # Filtrer selon le paramètre size
    if size is not None:
        sorted_structures = sorted_structures[:size]

    # Filtrer selon selection
    if selection is not None:
        selected_structures = [s for s in sorted_structures if int(s['id']) in selection]
        sorted_structures = selected_structures

    # Filtrer selon var (si c'est une liste, l'utiliser directement)
    if var is not None:
        if isinstance(var, list):
            variance_ids = var
        else:
            variance_ids = calculate_top_variance_structures(csv_folder, var)
        selected_structures = [s for s in sorted_structures if int(s['id']) in variance_ids]
        sorted_structures = selected_structures

    # Définir les modèles de phrase
    templates = [
        "This {scan_type} scan shows a {gender} subject aged {age} with dimensions {dimensions}. Brain volume is {brain_volume} cm3. The most prominent structures are {structures}",
        "A {scan_type} scan of a {gender} subject, {age} years old, with image dimensions {dimensions}. The total brain volume is {brain_volume} cm3, including major structures like {structures}",
        "Here we see a {scan_type} scan of a {gender} subject aged {age}. The image dimensions are {dimensions}, and the brain volume is {brain_volume} cm3. Visible structures include {structures}",
        "In this {scan_type} scan of a {age}-year-old {gender} subject, the image has dimensions {dimensions} and displays structures such as {structures} The brain volume is {brain_volume} cm3.",
        "This {scan_type} scan captures the brain of a {gender} subject aged {age} with image dimensions {dimensions}. The brain volume is {brain_volume} cm3. Key structures include {structures}",
        "This {scan_type} scan shows the brain of a {gender} subject aged {age}, with dimensions {dimensions}. The total brain volume is {brain_volume} cm3, and visible structures include {structures}",
        "Here is a {scan_type} scan of a {gender} subject aged {age}, with image dimensions {dimensions}. The brain volume is {brain_volume} cm3 and the visible structures include {structures}",
        "This {scan_type} scan provides a view of the brain of a {gender} subject, aged {age}, with dimensions of {dimensions}. Brain volume is {brain_volume} cm3, and visible structures include {structures}",
        "This is a {scan_type} scan of a {age}-year-old {gender}, with dimensions {dimensions}. The brain volume is {brain_volume} cm3, displaying structures like {structures}",
    ]
    
    # Construire le texte de description des structures
    unique_structures = {}
    for struct in sorted_structures:
        key = struct["label"].lower()
        if key not in unique_structures or struct["volume"] > unique_structures[key]["volume"]:
            unique_structures[key] = {**struct, "description": key}
    sorted_structures = sorted(unique_structures.values(), key=lambda x: x['volume'], reverse=True)
    sorted_structures = [s for s in sorted_structures if s["volume"] > 1]

    connectors = [
        "and", "additionally", "furthermore", "also", "moreover", "next", 
        "in addition", "besides", "as well as", "then", "subsequently", "in particular", 
        "alternatively", "on the other hand"
    ]

    structures_sentences = []
    volume_phrases = [
        "has a volume of", "has this volume", "measures", "displays a volume of", 
        "has a size of", "is of volume", "shows a volume of", "holds a volume of",
        "is measured at", "has a capacity of", "amounts to", "comprises a volume of", 
        "spans a volume of", "occupies a volume of", "accounts for a volume of", 
        "fills a volume of", "is quantified as", "takes up a volume of", 
        "represents a volume of", "encapsulates a volume of", "is measured to be", 
        "features a volume of", "includes a volume of"
    ]

    for i, s in enumerate(sorted_structures):
        volume = round(s["volume"] * 1000) if s["volume"] < 100 else round(s["volume"])
        unit = "mm3" if s["volume"] < 100 else "cm3"
        volume_phrase = random.choice(volume_phrases)
        sentence = f"the {s['description']} {volume_phrase} {volume} {unit}"
        if i > 0:
            sentence = random.choice(connectors) + " " + sentence
        structures_sentences.append(sentence)

    if structures_sentences:
        structures_text = ", ".join(structures_sentences[:-1])
        if len(structures_sentences) > 1:
            structures_text += ", " + structures_sentences[-1] + "."
        else:
            structures_text = structures_sentences[-1] + "."
    else:
        structures_text = ""

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

    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump({"captions": captions}, json_file, ensure_ascii=False, indent=4)

    return captions

def process_single_file(file_name, folder_path, csv_folder, metadata_folder, output_folder, dataset_keywords, dataset_keywords_modalite, variance_ids):
    # Traiter uniquement les fichiers .nii.gz
    if not file_name.endswith(".nii.gz"):
        return
    image_path = os.path.join(folder_path, file_name)

    # Déterminer le type de dataset
    last_dataset = None
    last_index = -1
    for keyword, dataset in dataset_keywords.items():
        index = file_name.rfind(keyword)
        if index != -1 and index > last_index:
            last_dataset = dataset
            last_index = index
    if not last_dataset:
        return

    # Définir la modalité selon le dataset
    a = dataset_keywords_modalite.get(last_dataset, "T1")
    metadata_file = os.path.join(metadata_folder, f"{last_dataset}_info.csv")

    base_name = os.path.splitext(file_name)[0]
    corresponding_csv = None
    for csv_file in os.listdir(csv_folder):
        if csv_file.startswith(base_name):
            corresponding_csv = os.path.join(csv_folder, csv_file)
            break
    if not corresponding_csv:
        return

    # Générer les légendes sans filtre
    output_file_exhaustive = os.path.join(output_folder, "captions_exhaustive", f"{base_name}_captions.json")
    generate_human_like_caption(image_path, csv_folder, corresponding_csv, metadata_file, output_file_exhaustive, a, last_dataset, selection=None, size=None, var=None)

    # Générer les légendes avec filtre de sélection fixe
    output_file_selection = os.path.join(output_folder, "captions_selection", f"{base_name}_captions.json")
    generate_human_like_caption(image_path, csv_folder, corresponding_csv, metadata_file, output_file_selection, a, last_dataset, selection=[2,41,3,42,4,43,10,48,49,17,53,18,54,11,50,12,51,13,52,14,16,26,58], size=None, var=None)

    # Générer les légendes en conservant les 10 premières structures
    output_file_size_10 = os.path.join(output_folder, "captions_size_10", f"{base_name}_captions.json")
    generate_human_like_caption(image_path, csv_folder, corresponding_csv, metadata_file, output_file_size_10, a, last_dataset, selection=None, size=10, var=None)

    # Générer les légendes avec filtrage par variance pré-calculée
    output_file_var_10 = os.path.join(output_folder, "captions_var_10", f"{base_name}_captions.json")
    generate_human_like_caption(image_path, csv_folder, corresponding_csv, metadata_file, output_file_var_10, a, last_dataset, selection=None, size=None, var=variance_ids)

    # Afficher un message après traitement du fichier
    print(f"Processed: {file_name}")

def process_folder(folder_path, csv_folder, metadata_folder, output_folder, variance_ids):
    # Créer le dossier de sortie et ses sous-dossiers
    os.makedirs(output_folder, exist_ok=True)
    subfolders = ['captions_exhaustive', 'captions_selection', 'captions_size_10', 'captions_var_10']
    for sub in subfolders:
        os.makedirs(os.path.join(output_folder, sub), exist_ok=True)

    dataset_keywords = {
        "KKI2009": "Kirby",
        "OAS1": "Oasis",
        "IBSR": "IBSR",
        "IXI": "IXI"
    }
    dataset_keywords_modalite = {
        "KKI2009": "FLAIR",
        "OAS1": "T1",
        "IBSR": "T1",
        "IXI": "T2"
    }

    files = os.listdir(folder_path)
    nii_files = [f for f in files if f.endswith(".nii.gz")]

    # Préparer les arguments pour le traitement en parallèle
    args_list = [
        (f, folder_path, csv_folder, metadata_folder, output_folder, dataset_keywords, dataset_keywords_modalite, variance_ids)
        for f in nii_files
    ]
    with Pool(processes=8) as pool:
        pool.starmap(process_single_file, args_list)

if __name__ == "__main__":
    # Calculer une fois la variance (ex: 10 premiers IDs)
    variance_ids = calculate_top_variance_structures(CSV_FOLDER, 10)
    # Traiter tous les fichiers en parallèle en passant variance_ids
    process_folder(INPUT_FOLDER, CSV_FOLDER, METADATA_FOLDER, OUTPUT_BASE_FOLDER, variance_ids)

