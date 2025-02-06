import os
import json
import re

def remove_connectors_from_json(directory):
    connectors = [
        "and", "additionally", "furthermore", "also", "moreover", "next", 
        "in addition", "besides", "as well as", "then", "subsequently", "in particular", 
        "alternatively", "on the other hand"
    ]
    
    pattern = re.compile(r'\b(' + '|'.join(re.escape(connector) for connector in connectors) + r')\b', re.IGNORECASE)
    
    for filename in os.listdir(directory):
        if filename.endswith(".json"):  # Vérifie si le fichier est un JSON
            file_path = os.path.join(directory, filename)
            
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            
            if "captions" in data and isinstance(data["captions"], list):
                data["captions"] = [pattern.sub("", caption).strip() for caption in data["captions"]]
            
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            
            print(f"Modifié : {filename}")

# Remplacez par le chemin du dossier contenant vos fichiers JSON
dossier_json = r"D:\SIR\T1\IBSR_OASIS\captions_3d_simple\captions_var_10"
remove_connectors_from_json(dossier_json)
