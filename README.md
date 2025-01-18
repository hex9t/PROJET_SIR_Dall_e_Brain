# Projet Deep Learning pour la Génération d'Images de Cerveau à partir de Prompt Text
![Image comparant les deux Atlas](data/readmeFILES/images/logo.png)

Dans ce projet, nous continuons le travail déjà effectué par [GLucas01/projet_SIR](https://github.com/GLucas01/projet_SIR) pour construire une base de données afin d'appliquer le deep learning et générer des images de cerveaux à partir de prompts textuels. 

### Tâches principales :

1. **Correction et Enrichissement de la Base de Données** :  
   Notre objectif est d'améliorer la base de données déjà existante en y apportant des corrections et en l'enrichissant avec des données supplémentaires. Cela inclut également la préparation de captions pour des volumes d'images 3D.

2. **Comparaison des Atlas** :  
   Nous comparons deux Atlas pour déterminer s'ils sont similaires ou différents. Pour cela, nous utilisons des techniques de "recallage" direct et indirect. Les métriques utilisées pour cette comparaison sont le **Dice coefficient** et l'**Intersection over Union (IoU)**. Vous trouverez les scripts relatifs à cette tâche ci-dessous.

   Exemple de comparaison entre les deux Atlas obtenus par :
   - IXI035-IOP-0873-T2_brain_majorityInverse.nii.gz
   - 307598 IXI035-IOP-0873-T2_majorityDirect.nii.gz

   ![Image comparant les deux Atlas](images/ixi.png)

3. **Construction de Légendes pour Volumes 3D** :  
   Nous générons des captions pour des volumes d'images 3D, une tâche essentielle pour la création de notre base de données d'entraînement. Le code utilisé pour cette tâche se trouve dans le répertoire ci-dessus.

   Exemple pour le fichier `KKI2009-1-FLAIR_brainMajorityDirect.nii` :
   - Fichier JSON associé : [lien_vers_le_fichier.json](data/readmeFILES/caption.json)

### Structure du Projet

- `scripts/` : Contient les scripts de traitement et d'analyse des données.
## 📝 Description du Code

Ce script Python est conçu pour comparer deux atlas 3D au format NIfTI en évaluant leur similarité à l'aide des métriques **Dice** et **IoU** (Intersection over Union) pour chaque étiquette présente dans les atlas.

---

### 🔍 Fonctionnalités Principales

1. **Chargement d'Atlas NIfTI** :  
   Le script utilise la bibliothèque `nibabel` pour charger des fichiers au format NIfTI et les convertir en tableaux NumPy.

2. **Calcul des Scores Dice et IoU** :  
   - **Dice** mesure le degré de similitude entre deux ensembles binaires.
   - **IoU** mesure l'intersection relative à l'union des ensembles.
   Ces scores sont calculés pour chaque étiquette présente dans les deux atlas.

3. **Visualisation des Résultats** :  
   Les scores Dice et IoU sont représentés sous forme de graphique à barres pour une interprétation facile.

---

### 📂 Organisation des Fonctions

- `load_atlas(path)`:  
  Charge un fichier atlas au format NIfTI et retourne un tableau NumPy.

- `calculate_label_dice_iou(atlas1, atlas2, labels)`:  
  Calcule les scores Dice et IoU pour chaque étiquette commune entre deux atlas.

- `main()`:  
  - Vérifie les arguments passés en ligne de commande.  
  - Charge les atlas à comparer.  
  - Extrait les étiquettes communes.  
  - Calcule les scores de cohérence (Dice et IoU).  
  - Affiche les résultats sous forme de tableau et de graphique.

---

### 🚀 Instructions d'Utilisation

1. Assurez-vous d'avoir installé les bibliothèques nécessaires :
   ```bash
   pip install nibabel numpy matplotlib



