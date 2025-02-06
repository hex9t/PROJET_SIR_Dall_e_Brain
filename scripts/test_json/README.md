### **README - Extraction et Analyse de Segmentation des Images Médicales**  

#### **📌 Description**  
Ce script Python permet d’extraire et d’analyser des images médicales au format **NIfTI (.nii.gz)** en générant des fichiers **JSON** contenant des informations sur les coupes sagittales, coronales et axiales. Il est conçu pour traiter des fichiers d’IRM segmentés de différentes bases de données (**IBSR, IXI, OASIS, KKI**) et organiser les résultats sous forme structurée.  

Il s'agit toutefois d'**un contenu de test** qui n'a pas été déployé dans l'application finale. Pour plus de détails, veuillez vous référer au rapport dans l'annexe' D.

Actuellement, chaque programme testé présente des goulots d'étranglement en termes de performances, tels que la vitesse de lecture et d'écriture du disque dur et la vitesse de lecture et d'écriture du WSL ou de l'espace RAM. J'ai mis mon programme ici car peut-être qu'un jour le multitraitement/threading sera utile pour ce projet.

---

#### **📂 Fonctionnalités**  
✅ slice_json : **Traitement multithread**  
✅ slice_json2.py : **Traitement multiprocess+multithread** 
---

#### **📌 Utilisation**  
💡 **Prérequis :** Installer les bibliothèques nécessaires :  
```bash
pip install numpy nibabel
```
💡 **Exécution du script :**  
```bash
python3 script.py <chemin_du_dossier_d’entrée>
```
👉 Exemple :  
```bash
python3 script.py ../data/T1/IBSR/reg
```
Le script va automatiquement analyser tous les fichiers `.nii.gz` dans le dossier spécifié et générer des fichiers **JSON** contenant les informations sur les coupes.

---

#### **📌 Structure des fichiers JSON générés**  
Chaque fichier JSON contient une liste de dictionnaires représentant les coupes d’image analysées. Exemple :  
```json
[
    {
        "plane": "sagittal",
        "index": 10,
        "dimensions": [256, 256],
        "voxel_size": [1.0, 1.0, 1.2],
        "labels": [[0, 50000], [1, 3000], [2, 1500]]
    },
    ...
]
```
---

#### **📌 Organisation des fichiers de sortie**  
Les fichiers JSON sont enregistrés dans un dossier dédié :  
- **Si les fichiers d’entrée sont dans un dossier "inv"** → Résultats dans `Slice_json_inv/`  
- **Sinon** → Résultats dans `Slice_json/`  

---
