import random
import yaml
from queue import Queue
from typing import Generator, Dict, Optional, List
import typer
from simpy import Environment, Process, Resource, Timeout
from simpy.resources.resource import Request
from simpy.rt import RealtimeEnvironment
from package import Package
from drone import Drone, DroneStates
from position import Position
from package_station import PackageStation
import numpy as np
from utils import *

id = int


class SortingOffice:

    def __init__(
        self,
        env: Environment,
        drones: Dict[id, Drone],
        package_stations: Dict[id, PackageStation],
    ):
        self._env = env
        self._drones = drones
        self._package_stations = package_stations

        self._packages_to_send_queue: Queue[Package] = Queue()
        self._undelivered_packages: List[Package] = []
        self._delivered_packages: List[Package] = []

        self._station_distances_lut = generate_distance_lut(package_stations)

        self._drone_resource = Resource(env, capacity=len(drones))

    def _get_closest_available_package_station(self, station_id: int) -> id:
        """If the requested package station is full, get the id of the closest available package station"""
        distances_from_A = self._station_distances_lut.get(station_id, {})

        # Filter out entries for the sorting center (0) and the station itself
        filtered = {
            station_id: dist
            for station_id, dist in distances_from_A.items()
            if isinstance(station_id, int)
            and station_id != 0
            and station_id != station_id
        }

        if not filtered:
            return None  # No valid stations to compare

        # Find the station with the minimum distance
        closest_station_id = min(filtered, key=filtered.get)
        return closest_station_id

    def _get_distance_from_sorting_centre(self, station_id: int) -> Optional[float]:
        """
        Returns the distance from the sorting centre (ID = 0) to the given station_id.
        If the lookup doesn't exist, returns None.
        """
        # Check if station_id and '0' exist in the LUT
        if station_id not in self._station_distances_lut:
            return None

        station_distances = self._station_distances_lut[station_id]
        if 0 not in station_distances:
            return None

        return station_distances[0]

    def _add_package(self, package: Package) -> None:
        """Add a package to the queue of packages to send."""
        self._packages_to_send_queue.put(package)
        print(f"[t={self._env.now}] Package {package.get_id()} added to the queue.")
        self._dispatch_package()

    def _dispatch_package(self) -> None:
        """Attempt to send a package from the queue if a drone is available."""
        while not self._packages_to_send_queue.empty():
            drone_id = self._choose_first_available_drone()
            if drone_id:
                package = (
                    self._packages_to_send_queue.get()
                )  # Get the first queued package
                station_id = package.get_package_station_id()
                self._drones[drone_id].load_package(package)

                self._env.process(self._send_package(package, station_id, drone_id))
            else:
                break

    def _send_package(
        self, package: Package, station_id: int, assigned_drone_id: int
    ) -> Generator[Request | Timeout, None, None]:
        """Process generator to send a package to the given station using a drone."""
        # Request a drone from the resource pool

        with self._drone_resource.request() as req:
            yield req  # Wait until a drone is free

            print(
                f"[t={self._env.now}] Package '{package.get_id()}' assigned to drone '{assigned_drone_id}'."
            )

            print(
                f"[t={self._env.now}] Sending package {package.get_id()} to station {station_id}..."
            )

            self._env.process(
                self._complete_delivery(assigned_drone_id, package, station_id)
            )

    def _choose_first_available_drone(self) -> Optional[id]:
        """Choose first available drone, if no drones available return None"""
        for id, drone in self._drones.items():
            if drone.get_state() == DroneStates.IDLE:
                return id

        return None

    def _complete_delivery(self, drone_id: id, package: Package, station_id: int):
        """SimPy process: Handles delivery and frees up the drone afterward."""
        # Travel time is distance ÷ speed.
        distance = self._get_distance_from_sorting_centre(station_id)
        travel_time = distance / self._drones[drone_id].get_velocity()

        print(
            f"[t={self._env.now}] Drone '{drone_id}' is traveling... Estimated time: {travel_time:.2f}s"
        )

        yield self._env.timeout(travel_time)  # Allow other events to run

        print(
            f"[t={self._env.now}] Package {package.get_id()} delivered to station {station_id}."
        )
        self._delivered_packages.append(package)

        if self._drones[drone_id].remove_package():
            print(f"[t={self._env.now}] Drone '{drone_id}' is available again.")
        else:
            raise ValueError

        self._dispatch_package()

    def _remove_not_received_package(self, package_id, station: PackageStation) -> None:
        """If a package wasn't received, remove it."""
        self._undelivered_packages = [
            p for p in self._undelivered_packages if p.package_id != package_id
        ]
        print(
            f"[t={self._env.now}] Removed package {package_id} from undelivered list for station {station.station_id}."
        )


class SystemEnvironment:
    def __init__(self, env: Environment, sorting_office: SortingOffice):
        self._env = env
        self._sorting_office = sorting_office

    def run_simulation(self, until: int = 50) -> None:
        def add_and_send_packages() -> Generator[Process | Timeout, None, None]:
            package_id = 1
            while True:
                station: PackageStation = random.choice(
                    list(self._sorting_office._package_stations.values())
                )
                package = Package(package_id, station.get_id())
                self._sorting_office._add_package(package)

                package_id += 1
                # Wait a random amount of time between 1 and 10 seconds
                delay = random.randint(10, 20)

                yield self._env.timeout(delay)

        # Start the process that adds/sends packages
        self._env.process(add_and_send_packages())

        # Run the simulation until the specified time
        self._env.run(until=until)


def load_config_yaml(filepath: str) -> dict:
    """Load the YAML configuration file and return a dict."""
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


app = typer.Typer()


@app.command()
def run_sim(
    config_file: str = typer.Argument(..., help="Path to the YAML config file."),
    until: int = typer.Option(200, help="How many simulation seconds to run."),
):
    """
    Load drones and package stations from CONFIG_FILE, then run a SimPy simulation
    for UNTIL simulation seconds.
    """
    # 1) Create environment
    env = RealtimeEnvironment(factor=0.1)

    # 2) Load config from YAML
    config = load_config_yaml(config_file)

    # 3) Build domain objects
    drones = {}
    for d in config.get("drones", []):
        drone_id = d["id"]
        velocity = d["velocity"]
        drones[drone_id] = Drone(drone_id, velocity)

    stations = {}
    for s in config.get("package_stations", []):
        station_id = s["id"]
        position = Position(tuple(s["position"])[0], tuple(s["position"])[1])
        lockers = s["lockers"]
        stations[station_id] = PackageStation(station_id, position, lockers)

    # 4) Create SortingOffice and controller
    sorting_office = SortingOffice(env, drones, stations)
    controller = SystemEnvironment(env, sorting_office)

    # 5) Run the simulation
    controller.run_simulation(until=until)

    typer.echo(f"Simulation finished at time={env.now}.")


def main():
    app()


if __name__ == "__main__":
    main()
