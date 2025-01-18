import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

def calculate_label_dice_iou(atlas1, atlas2, labels):
    """
    Calculer Dice et IoU pour chaque étiquette.
    :param atlas1: Tableau NumPy représentant le premier atlas.
    :param atlas2: Tableau NumPy représentant le deuxième atlas.
    :param labels: Liste des étiquettes contenant toutes les valeurs à comparer.
    :return: Dictionnaire contenant les Dice et IoU pour chaque étiquette.
    """
    results = {}

    for label in labels:
        # Extraire l'image binaire pour chaque étiquette
        binary1 = (atlas1 == label).astype(int)
        binary2 = (atlas2 == label).astype(int)

        # Calculer l'intersection et l'union
        intersection = np.logical_and(binary1, binary2).sum()
        union = np.logical_or(binary1, binary2).sum()

        # Calculer Dice et IoU
        dice = 2 * intersection / (binary1.sum() + binary2.sum() + 1e-6)  # Éviter la division par zéro
        iou = intersection / (union + 1e-6)

        # Sauvegarder les résultats
        results[label] = {"Dice": dice, "IoU": iou}

    return results

def load_atlas(path):
    """Charger un fichier atlas au format NIfTI et le convertir en tableau NumPy"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier introuvable: {path}")

    nii = nib.load(path)
    return nii.get_fdata().astype(int)

def main():
    # Vérifier les arguments de la ligne de commande
    if len(sys.argv) != 3:
        print("Utilisation: python script.py <chemin_atlas1> <chemin_atlas2>")
        sys.exit(1)

    atlas1_path = sys.argv[1]
    atlas2_path = sys.argv[2]

    # Charger les atlas
    print("Chargement des atlas...")
    atlas1 = load_atlas(atlas1_path)
    atlas2 = load_atlas(atlas2_path)

    # Extraire les étiquettes
    labels1 = np.unique(atlas1)
    labels2 = np.unique(atlas2)
    print(f"Étiquettes Atlas 1: {labels1}")
    print(f"Étiquettes Atlas 2: {labels2}")

    # Vérifier la cohérence des étiquettes
    common_labels = np.intersect1d(labels1, labels2)
    print(f"Étiquettes communes: {common_labels}")

    # Calculer les indicateurs de cohérence
    print("Calcul des indicateurs de cohérence...")
    results = calculate_label_dice_iou(atlas1, atlas2, common_labels)

    # Afficher les résultats
    print("\nRésultats de la comparaison des étiquettes:")
    for label, metrics in results.items():
        print(f"Étiquette {label}: Dice = {metrics['Dice']:.4f}, IoU = {metrics['IoU']:.4f}")

    # Visualiser les résultats
    dice_scores = [metrics["Dice"] for metrics in results.values()]
    iou_scores = [metrics["IoU"] for metrics in results.values()]

    plt.figure(figsize=(12, 6))
    x = np.arange(len(common_labels))
    plt.bar(x - 0.2, dice_scores, width=0.4, label='Dice')
    plt.bar(x + 0.2, iou_scores, width=0.4, label='IoU')
    plt.xlabel('Étiquettes')
    plt.ylabel('Scores')
    plt.title('Scores Dice et IoU par étiquette')
    plt.xticks(x, common_labels, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
