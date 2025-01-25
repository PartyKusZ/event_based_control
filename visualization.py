import yaml
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Load CSV and YAML data
csv_file = "test.csv"
yaml_file = "config.yaml"

# Read the CSV file
data = pd.read_csv(csv_file, sep=';')

# Handle missing data
data['receive_time'] = data['receive_time'].fillna(0)

# Read the YAML file
with open(yaml_file, 'r') as f:
    config = yaml.safe_load(f)

drones = config['drones']
package_stations = config['package_stations']

# Extract package station positions
station_positions = {station['id']: station['position'] for station in package_stations}

# Prepare the figure and axes
fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

# Plot package stations
for station_id, position in station_positions.items():
    ax.plot(position[0], position[1], 'ro', label=f'Station {station_id}')
    ax.text(position[0] + 1, position[1] + 1, f'{station_id}', fontsize=10, color='red')

# Prepare drone markers
drone_markers = {}
for drone in drones:
    marker, = ax.plot([], [], 'bo', label=f"Drone {drone['id']}")
    drone_markers[drone['id']] = marker

# Animate drone movements
def init():
    for marker in drone_markers.values():
        marker.set_data([], [])
    return list(drone_markers.values())

def update(frame):
    current_time = frame / 10  # Frame as scaled time
    for drone in drones:
        drone_id = drone['id']
        velocity = drone['velocity']

        # Get the package assigned to the drone if available
        drone_data = data[(data['sending_time'] <= current_time) & 
                          (data['arrival_in_package_locker_time'] >= current_time)]

        if not drone_data.empty:
            package = drone_data.iloc[0]
            station_id = package['package_station_id']
            station_pos = station_positions[station_id]

            # Calculate the linear movement based on velocity and time
            start_time = package['sending_time']
            end_time = package['arrival_in_package_locker_time']
            travel_time = end_time - start_time

            start_position = station_pos
            end_position = station_pos  # Assuming drone delivers directly to locker at station

            # Interpolate drone position
            progress = min(1, max(0, (current_time - start_time) / travel_time))
            drone_position = [
                start_position[0] + progress * (end_position[0] - start_position[0]),
                start_position[1] + progress * (end_position[1] - start_position[1])
            ]

            drone_markers[drone_id].set_data([drone_position[0]], [drone_position[1]])
        else:
            drone_markers[drone_id].set_data([], [])

    return list(drone_markers.values())


# Create animation
ani = FuncAnimation(fig, update, frames=range(int(data['sending_time'].min() * 10), 
                                              int(data['receive_time'].max() * 10)),
                    init_func=init, blit=True, repeat=False)

# Add legend
ax.legend()
plt.show()
