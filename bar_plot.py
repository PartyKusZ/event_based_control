import matplotlib.pyplot as plt
from collections import defaultdict
import csv
import glob
import numpy as np


def load_simulation_csv(filepath: str):
    csv_data = defaultdict(list)
    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key, value in row.items():
                csv_data[key].append(value)
    return dict(csv_data)

# Get all CSV files
csv_files = glob.glob("*.csv")

time_differences = []
labels = []

for file in csv_files:
    # Load data from CSV file
    
    data = load_simulation_csv(file)
    
    # Convert necessary columns to numeric
    data['Dispatch Time'] = list(map(float, data['Dispatch Time']))
    data['Postage Time'] = list(map(float, data['Postage Time']))
    
    # Calculate difference between Postage Time and Dispatch Time
    time_difference = [p - d for p, d in zip(data['Postage Time'], data['Dispatch Time'])]
    time_differences.append(time_difference)
    print(f"name: {file} min {np.min(time_difference)}, max {np.max(time_difference)}, mean {np.mean(time_difference)}, std {np.std(time_difference)}")
    labels.append(file)

# Plot the box plot
plt.figure(figsize=(10, 6))
plt.boxplot(time_differences, labels=labels, patch_artist=True)
plt.xlabel('CSV Files')
plt.ylabel('Time Difference (Postage - Dispatch)')
plt.title('Box Plot of Time Difference Between Postage and Dispatch Time for Multiple CSV Files')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show plot
plt.show()