import json
import matplotlib.pyplot as plt
import os
import sys

# Usage on Windows: python boite_a_moustache.py <input_folder>
# This program generates boxplots from JSON files and saves the images in a "boxplots" folder within the input directory.

def load_json_data(json_file):
    """Load data from a JSON file."""
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def plot_boxplot(data, label_id, database_name, label_name, output_folder):
    """Draw a boxplot and save it."""
    # Extract necessary data
    min_val = data.get("min")
    q1 = data.get("Q1")
    q2 = data.get("Q2")
    q3 = data.get("Q3")
    max_val = data.get("max")
    outliers = data.get("outliers", [])

    if None in (min_val, q1, q2, q3, max_val):
        return

    # Create boxplot data
    boxplot_data = [min_val, q1, q2, q3, max_val]

    # Draw the boxplot
    plt.figure(figsize=(8, 6))
    plt.boxplot(boxplot_data, vert=False, patch_artist=True, boxprops=dict(facecolor="lightblue"))

    # Add title and labels 
    plt.title(f"Boxplot for {database_name} - Label {label_id}: {label_name}")
    plt.xlabel("Volume (mm³)")
    plt.yticks([])  

    # Add outliers 
    if outliers:
        plt.scatter(outliers, [1] * len(outliers), color='red', label="Outliers")
        plt.legend()

    # Save the image
    output_path = os.path.join(output_folder, f"{database_name}_{label_name}_boxplot.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def generate_boxplots_from_folder(json_folder):
    """Generate boxplots from all JSON files in a folder."""
    # Define output folder inside input directory
    output_folder = os.path.join(json_folder, "boxplots")
    os.makedirs(output_folder, exist_ok=True)

    for json_file in os.listdir(json_folder):
        if json_file.endswith(".json"):
            json_path = os.path.join(json_folder, json_file)
            data = load_json_data(json_path)

            group = data.get("Group", "Unknown_Group")
            parts = group.split("_")
            if len(parts) == 3:
                database_name = " ".join(parts[:2])
            elif len(parts) == 4:
                database_name = " ".join(parts[:3])

            for label_id, label_data in data.items():
                if label_id == "Group":
                    continue

                label_name = label_data.get("label_name")
                plot_boxplot(label_data, label_id, database_name, label_name, output_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python boite_a_moustache.py <input_folder>")
        sys.exit(1)
    input_folder = sys.argv[1]
    if not os.path.isdir(input_folder):
        print(f"Error: The specified folder '{input_folder}' does not exist.")
        sys.exit(1)
    generate_boxplots_from_folder(input_folder)
