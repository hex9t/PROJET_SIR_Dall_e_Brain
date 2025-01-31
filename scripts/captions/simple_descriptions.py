import os
import pandas as pd

# Dossier contenant les fichiers CSV des volumes
volumes_folder = 'description_3d_oasis'  # Remplacer par le chemin réel du dossier contenant les fichiers CSV
# Dossier où sauvegarder les fichiers de sortie
output_folder = 'oasis_simple_descriptions'  # Remplacer par le chemin réel du dossier de sortie

# Créer le dossier de sortie s'il n'existe pas
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Charger le fichier de regroupements
groupings_df = pd.read_csv('simplified_IBSR.csv', encoding='ISO-8859-1')  # Le deuxième fichier CSV avec les regroupements

# Fonction pour traiter chaque fichier CSV des volumes
def process_volume_file(volume_file):
    # Charger le fichier CSV des volumes
    volumes_df = pd.read_csv(volume_file, encoding='ISO-8859-1')

    # Créer un dictionnaire avec les Voxel Count et Voxel Volume par ID
    volume_dict = dict(zip(volumes_df['ID'], zip(volumes_df['Voxel Count'], volumes_df['Voxel Volume (mm³)'])))

    # Créer une nouvelle liste pour stocker les résultats
    new_data = []

    # Parcourir chaque ligne du fichier de regroupements
    for _, row in groupings_df.iterrows():
        labels = row['Labels']

        # Extraire les IDs en s'assurant qu'ils sont des entiers et en ignorant les valeurs non valides
        ids = []
        for label in labels.split(', '):
            try:
                ids.append(int(label))  # Essayer de convertir chaque ID en entier
            except ValueError:
                continue  # Si la conversion échoue, ignorer cette valeur (par exemple 'Unknown')

        description = row['Description']
        rgb = row['RGB']

        # Calculer la somme des Voxel Count et Voxel Volume pour les IDs de ce regroupement
        total_voxel_count = 0
        total_voxel_volume = 0
        for i in ids:
            if i in volume_dict:
                total_voxel_count += volume_dict[i][0]
                total_voxel_volume += volume_dict[i][1]
            else:
                print(f"ID {i} non trouvé dans le fichier des volumes.")  # Avertir sur les IDs manquants

        # Ajouter les données agrégées à la liste
        new_data.append([ids[0] if ids else 'Unknown', labels, description, rgb, total_voxel_count, total_voxel_volume])

    # Créer un DataFrame avec les résultats
    new_df = pd.DataFrame(new_data, columns=['ID', 'Labels', 'Description', 'RGB', 'Voxel Count', 'Voxel Volume 3'])

    # Sauvegarder les résultats dans un nouveau fichier CSV
    output_file = os.path.join(output_folder, f"{os.path.basename(volume_file)}_simple.csv")
    new_df.to_csv(output_file, index=False)
    print(f"Le fichier CSV simplifié pour {volume_file} a été créé avec succès.")

# Parcourir tous les fichiers CSV dans le dossier des volumes
for file_name in os.listdir(volumes_folder):
    if file_name.endswith('.csv'):
        volume_file_path = os.path.join(volumes_folder, file_name)
        process_volume_file(volume_file_path)
