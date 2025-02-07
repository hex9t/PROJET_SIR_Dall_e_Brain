import os
import json
import threading

# Définir des variables globales
wrong_info = "T1"
right_info = "FLAIR"

def replace_none_in_json(directory, wrong_info, right_info):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):  # Vérifie si le fichier est un JSON
            file_path = os.path.join(directory, filename)
            
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            
            if "captions" in data and isinstance(data["captions"], list):
                 data["captions"] = [caption.replace(wrong_info, right_info) for caption in data["captions"]]
            
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            
            print(f"Modifié : {filename}")

def process_directory(directory, wrong_info, right_info):
    # Traiter chaque sous-dossier (A, B, C, D)
    for subfolder in ['captions_exhaustive', 'captions_selection', 'captions_size_10', 'captions_var_10']:
        subfolder_path = os.path.join(directory, subfolder)
        if os.path.isdir(subfolder_path):
            replace_none_in_json(subfolder_path, wrong_info, right_info)

# Remplacez par le chemin du dossier contenant vos dossiers A, B, C, D
base_directory = r"E:\SIR\FL\Kirby_OASIS\captions_3d"

# Créer 4 threads pour traiter les 4 sous-dossiers
threads = []
for _ in range(4):
    thread = threading.Thread(target=process_directory, args=(base_directory, wrong_info, right_info))
    threads.append(thread)
    thread.start()

# Attendre que tous les threads se terminent
for thread in threads:
    thread.join()

print("Tous les fichiers ont été modifiés.")

