import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

def load_nii(filepath):
    """
    Load a NIfTI (.nii.gz) file and return the 3D numpy array.
    """
    nii = nib.load(filepath)
    return nii.get_fdata()

def calculate_dice_per_label(image1, image2, label):
    """
    Calculate the Dice Coefficient for a specific label.
    """
    mask1 = (image1 == label)
    mask2 = (image2 == label)

    intersection = np.sum(mask1 & mask2)
    size1 = np.sum(mask1)
    size2 = np.sum(mask2)

    if size1 + size2 == 0:
        return 1.0 if size1 == size2 else 0.0

    return (2 * intersection) / (size1 + size2)

def calculate_dice_for_labels(image1, image2):
    """
    Calculate Dice Coefficients for each label present in the first image.
    """
    unique_labels = np.unique(image1)
    dice_scores = {}

    for label in unique_labels:
        dice_score = calculate_dice_per_label(image1, image2, label)
        dice_scores[label] = dice_score

    # Calculate the weighted average Dice (by the size of each label in image1)
    total_voxels = np.prod(image1.shape)
    weighted_dice = sum(
        dice_scores[label] * (np.sum(image1 == label) / total_voxels) for label in unique_labels
    )
    return dice_scores, weighted_dice

def plot_results(dice_scores, weighted_dice, image1):
    """
    Plot the Dice Coefficient results for better visualization.
    """
    labels = list(dice_scores.keys())
    scores = list(dice_scores.values())

    # Bar plot for Dice Coefficients
    plt.figure(figsize=(12, 6))
    plt.bar(labels, scores, color='skyblue')
    plt.xlabel("Labels")
    plt.ylabel("Dice Coefficient")
    plt.title("Dice Coefficient per Label")
    plt.xticks(labels, rotation=90)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    # Pie chart for label sizes in image1
    sizes = [np.sum(image1 == label) for label in labels]
    plt.figure(figsize=(10, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 8})
    plt.title("Proportion of Voxels per Label in Image 1")
    plt.tight_layout()
    plt.show()

    print(f"\nFinal Weighted Average Dice Coefficient: {weighted_dice:.4f}")

def main(image1_path, image2_path):
    """
    Compare two multi-class segmented brain images using Dice Coefficient.
    """
    # Load images
    image1 = load_nii(image1_path)
    image2 = load_nii(image2_path)

    # Calculate Dice Coefficient for each label and the final result
    print("Calculating Dice Coefficients for each label...\n")
    dice_scores, weighted_dice = calculate_dice_for_labels(image1, image2)

    print("\nSummary of Results:")
    for label, score in dice_scores.items():
        print(f"Label {label}: Dice Coefficient = {score:.4f}")
    print(f"\nFinal Weighted Average Dice Coefficient: {weighted_dice:.4f}")
    print("Labels in image1:", np.unique(image1))
    print("Labels in image2:", np.unique(image2))

    # Plot results
    plot_results(dice_scores, weighted_dice, image1)

# Example usage
image1_path = "KKI2009-01-FLAIR_brain_majorityInverse.nii.gz"
image2_path = "KKI2009-01-FLAIR_brainMajorityDirect.nii.gz"

main(image1_path, image2_path)
