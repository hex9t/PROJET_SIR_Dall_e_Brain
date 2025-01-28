import os
import sys
import json
import matplotlib.pyplot as plt

def load_json_files(folder_path):
    data = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data[os.path.splitext(filename)[0].split('_')[0].lower()] = json.load(file)
    return data

def get_labels(data):
    first_file = next(iter(data.values()))
    return [(key, item['label_name']) for key, item in first_file.items() if isinstance(item, dict) and 'label_name' in item]

def plot_histogram(data, label_key, label_name, compare_type):
    values = []
    file_names = []

    for file_name, content in data.items():
        if label_key in content:
            value = content[label_key]
            if compare_type == "volume":
                values.append(value['avg_volume (mm³)'])
            elif compare_type == "ratio":
                values.append(float(value['avg_ratio (%)'].strip('%')))
            file_names.append(file_name)

    plt.figure(figsize=(10, 6))
    plt.bar(file_names, values)
    plt.title(f'Comparison of {label_name} Across Groups')
    plt.ylabel('Volume (mm³)' if compare_type == "volume" else 'Ratio (%)')
    plt.xlabel('Group')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 compare.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    data = load_json_files(folder_path)

    if not data:
        print("No JSON files found in the specified folder.")
        return

    labels = get_labels(data)
    print(f"Total number of labels: {len(labels)} (Label Range: {labels[0][0]} to {labels[-1][0]})")

    while True:
        try:
            label_key = input(f"Enter the label key to compare ({labels[0][0]} to {labels[-1][0]}): ").strip()
            if label_key.isdigit() and int(label_key) in [int(k[0]) for k in labels]:
                label_name = dict(labels)[label_key]
                compare_type = input("Enter 'volume' to compare average volumes or 'ratio' to compare average ratios: ").strip().lower()
                if compare_type in ["volume", "ratio"]:
                    plot_histogram(data, label_key, label_name, compare_type)
                else:
                    print("Invalid comparison type. Please enter 'volume' or 'ratio'.")
            else:
                print(f"Invalid input. Please enter a valid label key between {labels[0][0]} and {labels[-1][0]}.")
        except ValueError:
            print("Invalid input. Please enter a valid label key.")
        except KeyboardInterrupt:
            print("Exiting.")
            break

if __name__ == "__main__":
    main()
