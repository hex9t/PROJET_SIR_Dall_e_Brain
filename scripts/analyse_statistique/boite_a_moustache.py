import json
import matplotlib.pyplot as plt
import os

def load_json_data(json_file):
    """Load data from a JSON file"""
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def plot_boxplot(data, label_id, database_name, label_name, output_folder):
    """Draw a boxplot and save it"""
    # Extract necessary data
    min_val = data["min"]
    q1 = data["Q1"]
    q2 = data["Q2"]
    q3 = data["Q3"]
    max_val = data["max"]
    outliers = data["outliers"]

    # Create boxplot data
    boxplot_data = [min_val, q1, q2, q3, max_val]

    # Draw the boxplot
    plt.figure(figsize=(8, 6))
    plt.boxplot(boxplot_data, vert=False, patch_artist=True, boxprops=dict(facecolor="lightblue"))

    # Add title and labels (in English)
    plt.title(f"Boxplot for {database_name} - Label {label_id}: {label_name}")
    plt.xlabel("Volume (mm³)")
    plt.yticks([])  # Hide the text on the left

    # Add outliers
    if outliers:
        plt.scatter(outliers, [1] * len(outliers), color='red', label="Outliers")
        plt.legend()

    # Save the image
    output_path = os.path.join(output_folder, f"{database_name}_{label_name}_boxplot.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def generate_boxplots_from_folder(json_folder, output_folder):
    """Generate boxplots from all JSON files in a folder"""
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all JSON files in the folder
    for json_file in os.listdir(json_folder):
        if json_file.endswith(".json"):
            json_path = os.path.join(json_folder, json_file)
            data = load_json_data(json_path)

            # Extract the database name
            database_name = " ".join(data.get("Group", "Unknown_Group").split("_")[:2])

            # Iterate over each label and generate a boxplot
            for label_id, label_data in data.items():
                if label_id == "Group":  # Skip the group information
                    continue
                label_name = label_data["label_name"]
                plot_boxplot(label_data, label_id, database_name, label_name, output_folder)

# Example call
json_folder = "./data/Brain_Statistics"  # Replace with your JSON folder path
output_folder = "./data/boxplots/"  # Replace with your output folder path
generate_boxplots_from_folder(json_folder, output_folder)