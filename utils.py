import math
from typing import Dict, Union

from package_station import PackageStation


def generate_distance_lut(
    stations: Dict[int, PackageStation],
) -> Dict[int, Dict[int, float]]:
    """
    Compute a distance lookup table for each station in 'stations'.
    Returns a nested dict with the structure:

        {
            station_id_A: {
                0: <distance from (0,0) to station A>,
                station_id_B: <distance between station A and station B>,
                station_id_C: <distance between station A and station C>,
                ...
            },
            station_id_B: {
                0: <distance from (0,0) to station B>,
                station_id_A: <distance between station B and station A>,
                ...
            }
            ...
        }
    """
    distance_lut: Dict[int, Dict[Union[int, str], float]] = {}

    for station_id, station in stations.items():
        x, y = station.get_position()
        dist_from_centre = math.dist((0, 0), (x, y))

        distance_lut[station_id] = {0: dist_from_centre}

    station_ids = list(stations.keys())

    for i in range(len(station_ids)):
        for j in range(i + 1, len(station_ids)):
            id_a = station_ids[i]
            id_b = station_ids[j]

            x_a, y_a = stations[id_a].get_position()
            x_b, y_b = stations[id_b].get_position()

            dist_ab = math.dist((x_a, y_a), (x_b, y_b))

            distance_lut[id_a][id_b] = dist_ab
            distance_lut[id_b][id_a] = dist_ab

    return distance_lut
