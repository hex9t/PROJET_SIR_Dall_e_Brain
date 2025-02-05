# Script de correction des labels 3D et de vote majoritaire

Ce script permet de traiter des fichiers d'image volumétriques en format `.nii.gz` (généralement utilisés pour les images médicales en 3D) en appliquant un vote majoritaire pour résoudre les conflits de labels, puis en corrigeant les voxels avec le label maximum en utilisant les valeurs des voxels voisins les plus proches.

## Fonctionnalités

- **Lecture et traitement des fichiers `.nii.gz`** : Le script charge les images en format NIfTI et effectue un traitement basé sur le vote majoritaire sur les groupes d'images.
- **Correction des labels maximum** : Après avoir effectué le vote majoritaire, les voxels étiquetés avec la valeur maximale sont corrigés en remplaçant la valeur par celle des voisins les plus proches ayant un label valide.
- **Organisation des fichiers** : Les fichiers sont regroupés par préfixe extrait du nom du fichier (au-delà du quatrième underscore) et traités séparément.
- **Sauvegarde des résultats** : Les résultats corrigés sont enregistrés dans un dossier de sortie spécifié, avec un préfixe modifié pour indiquer le traitement effectué.

## Prérequis

- Python 3.x
- Bibliothèques Python : `SimpleITK`, `numpy`, `scipy`

Vous pouvez installer les dépendances nécessaires avec pip :

```bash
pip install SimpleITK numpy scipy
