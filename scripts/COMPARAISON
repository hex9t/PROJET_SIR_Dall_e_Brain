import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import sys
from scipy.spatial.distance import directed_hausdorff
from collections import defaultdict
import concurrent.futures


def calculate_metrics_for_pair(atlas1, atlas2, labels):
    """
    Calculer les métriques (Dice, IoU, Hausdorff) pour une paire d'images.
    """
    results = {}
    for label in labels:
        binary1 = (atlas1 == label)
        binary2 = (atlas2 == label)

        # Intersection et union
        intersection = np.logical_and(binary1, binary2).sum()
        union = np.logical_or(binary1, binary2).sum()

        # Dice et IoU
        dice = 2 * intersection / (binary1.sum() + binary2.sum() + 1e-6)
        iou = intersection / (union + 1e-6)

        # Hausdorff
        coords1 = np.argwhere(binary1)
        coords2 = np.argwhere(binary2)
        if coords1.size > 0 and coords2.size > 0:
            coords1_sample = coords1[::10] if len(coords1) > 10000 else coords1
            coords2_sample = coords2[::10] if len(coords2) > 10000 else coords2
            hausdorff = max(
                directed_hausdorff(coords1_sample, coords2_sample)[0],
                directed_hausdorff(coords2_sample, coords1_sample)[0]
            )
        else:
            hausdorff = np.nan

        results[label] = {"Dice": dice, "IoU": iou, "Hausdorff": hausdorff}
    return results


def load_atlas(path):
    """Charger un fichier atlas au format NIfTI et le convertir en tableau NumPy."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier introuvable: {path}")
    nii = nib.load(path)
    return nii.get_fdata().astype(int)


def find_matching_files(directory1, directory2):
    """
    Trouver les fichiers correspondants entre deux répertoires avec "majority" et "corrected"/"Corrected" dans leurs noms.
    Correspondance basée sur un identifiant unique commun dans les noms de fichiers.
    """
    files1 = [f for f in os.listdir(directory1) if f.endswith(".nii.gz") and "majority" in f.lower() and "corrected" in f.lower()]
    files2 = [f for f in os.listdir(directory2) if f.endswith(".nii.gz") and "majority" in f.lower() and "corrected" in f.lower()]

    matching_files = []
    for file1 in files1:
        id1_match = re.search(r"(OAS1_\d+|IXI\d+|KKI2009-\d+|[A-Za-z0-9]+)", file1)
        if not id1_match:
            continue
        id1 = id1_match.group(1)

        for file2 in files2:
            id2_match = re.search(r"(OAS1_\d+|IXI\d+|KKI2009-\d+|[A-Za-z0-9]+)", file2)
            if not id2_match:
                continue
            id2 = id2_match.group(1)

            if id1 == id2:
                matching_files.append((os.path.join(directory1, file1), os.path.join(directory2, file2)))

    return matching_files


def plot_global_metrics(metrics_aggregate, metric_name, save_plot=False):
    """
    Générer un graphique global pour une métrique spécifique.
    """
    labels = list(metrics_aggregate.keys())
    # Convert labels to strings to ensure they are treated as categorical data
    labels = [str(label) for label in labels]
    mean_scores = [np.nanmean(metrics_aggregate[int(label)][metric_name]) for label in labels]

    plt.figure(figsize=(12, 6))
    plt.bar(labels, mean_scores, color="skyblue", label=f"Moyenne {metric_name} par étiquette")
    plt.xlabel("Labels")
    plt.ylabel(metric_name)
    plt.title(f"{metric_name} moyenne sur toutes les comparaisons")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    if save_plot:
        plt.savefig(f"global_{metric_name}_plot.png")
    plt.show()


def main():
    if len(sys.argv) != 3:
        print("Utilisation: python script.py <repertoire1> <repertoire2>")
        sys.exit(1)

    directory1 = sys.argv[1]
    directory2 = sys.argv[2]

    if not os.path.isdir(directory1) or not os.path.isdir(directory2):
        print("Erreur : Les chemins fournis ne sont pas des répertoires valides.")
        sys.exit(1)

    print("Recherche des fichiers correspondants contenant 'majority' et 'corrected'/'Corrected'...")
    matching_files = find_matching_files(directory1, directory2)

    if not matching_files:
        print("Aucun fichier correspondant trouvé avec les critères 'majority' et 'corrected'/'Corrected'.")
        sys.exit(0)

    print(f"{len(matching_files)} fichier(s) correspondant(s) trouvé(s).")

    # Initialiser les agrégats de métriques
    metrics_aggregate = defaultdict(lambda: {"Dice": [], "IoU": [], "Hausdorff": []})

    # Define the range of labels you want to evaluate (2 to 60 inclusive)
    label_range = range(2, 61)

    def process_pair(file_pair):
        file1, file2 = file_pair
        print(f"\nComparaison entre:\n  - {file1}\n  - {file2}")

        atlas1 = load_atlas(file1)
        atlas2 = load_atlas(file2)

        # Use the predefined label range instead of np.unique
        common_labels = label_range

        results = calculate_metrics_for_pair(atlas1, atlas2, common_labels)

        return results

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        future_to_pair = {executor.submit(process_pair, pair): pair for pair in matching_files}
        for future in concurrent.futures.as_completed(future_to_pair):
            pair = future_to_pair[future]
            try:
                results = future.result()
                for label, metrics in results.items():
                    metrics_aggregate[label]["Dice"].append(metrics["Dice"])
                    metrics_aggregate[label]["IoU"].append(metrics["IoU"])
                    metrics_aggregate[label]["Hausdorff"].append(metrics["Hausdorff"])
            except Exception as exc:
                print(f"Exception occurred while processing pair {pair}: {exc}")

    print("\nGénération des graphiques globaux...")

    # Générer les graphiques globaux
    plot_global_metrics(metrics_aggregate, "Dice", save_plot=True)
    plot_global_metrics(metrics_aggregate, "IoU", save_plot=True)
    plot_global_metrics(metrics_aggregate, "Hausdorff", save_plot=True)

    # Calculer les moyennes globales
    print("\nMoyennes globales pour toutes les comparaisons :")
    for metric_name in ["Dice", "IoU", "Hausdorff"]:
        all_scores = [score for label in metrics_aggregate for score in metrics_aggregate[label][metric_name]]
        mean_score = np.nanmean(all_scores)
        print(f"{metric_name} moyenne = {mean_score:.4f}")


if __name__ == "__main__":
    main()
