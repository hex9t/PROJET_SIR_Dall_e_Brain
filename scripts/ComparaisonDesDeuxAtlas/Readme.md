# Comparaison d'Atlas avec IoU, Dice et Hausdorff

  **Description**

Ce script permet de comparer deux atlas provenant de deux répertoires (un répertoire contenant les atlas obtenus par recalage direct et l'autre contenant les atlas obtenus par recalage inverse. Pour plus d'informations, vous pouvez consulter le README.md dans le répertoire principal). Il applique des métriques de similarité (IoU, Dice et la distance de Hausdorff) sur chaque label des images et génère des graphiques représentant les valeurs moyennes de ces métriques.

  **Fonctionnalités**

Chargement des images segmentées au format NIfTI (.nii.gz)
Recherche automatique des fichiers correspondants entre deux répertoires
Calcul des métriques IoU, Dice et Hausdorff pour chaque label
Agrégation et visualisation des résultats sous forme de graphiques
Exécution parallèle pour accélérer le traitement

  **Prérequis**
Avant d'exécuter le script, assurez-vous d'avoir installé les dépendances nécessaires:
**pip install nibabel numpy matplotlib scipy concurrent.futures**

  **Utilisation**

Exécutez le script avec les chemins des deux répertoires à comparer :
**python COMPARAISON.py <répertoire1> <répertoire2>**

  **Arguments :**

<répertoire1> : Chemin du premier répertoire contenant les atlas segmentés
<répertoire2> : Chemin du second répertoire contenant les atlas segmentés

  **Exemple :**

python COMPARAISON.py SIR/T2/IXI/seg SIR/T2/IXI/seg_direct/

  **Détails des Métriques:**

Le script calcule les métriques suivantes pour chaque label des images segmentées :

Dice coefficient : Mesure la similarité entre deux ensembles
Intersection over Union (IoU) : Évalue le chevauchement entre les segments
Distance de Hausdorff : Quantifie la différence entre deux ensembles de points

  **Résultats:**

Affichage des scores pour chaque label
Génération de trois graphiques représentant les moyennes des métriques pour tous les labels de tous les pairs d'atlas
Calcul des moyennes globales pour IoU, Dice et Hausdorff

  **Structure du Code**

Chargement des atlas depuis les fichiers NIfTI
Recherche des fichiers correspondants basés sur les noms de fichiers
Calcul des métriques en parallèle pour optimiser le temps de traitement
Affichage des résultats et génération des graphiques
