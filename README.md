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
Voici un fichier complet README.md avec les modifications demandées :

markdown
Copier
Modifier
# 🧠 Code Comparaison Atlas

Ce script compare deux atlas 3D au format NIfTI en calculant les métriques **Dice** et **IoU** pour chaque étiquette commune entre les deux. Les résultats sont affichés dans le terminal et sous forme de graphique.

---

## ✨ Fonctionnalités

- Chargement d'atlas NIfTI avec `nibabel`.
- Calcul des scores **Dice** (similitude) et **IoU** (intersection/union) pour chaque étiquette.
- Visualisation des résultats avec `matplotlib`.

---

## 🚀 Utilisation

1. Installer les dépendances :
   ```bash
   pip install nibabel numpy matplotlib
Lancer le script :

bash
Copier
Modifier
python script.py <chemin_atlas1> <chemin_atlas2>
Exemple d'exécution :

bash
Copier
Modifier
python script.py atlas1.nii atlas2.nii
🔑 Code Principal
Voici une partie clé du code, responsable du calcul des scores Dice et IoU pour chaque étiquette :

python
Copier
Modifier
def calculate_label_dice_iou(atlas1, atlas2, labels):
    results = {}
    for label in labels:
        binary1 = (atlas1 == label).astype(int)
        binary2 = (atlas2 == label).astype(int)
        intersection = np.logical_and(binary1, binary2).sum()
        union = np.logical_or(binary1, binary2).sum()
        dice = 2 * intersection / (binary1.sum() + binary2.sum() + 1e-6)
        iou = intersection / (union + 1e-6)
        results[label] = {"Dice": dice, "IoU": iou}
    return results
