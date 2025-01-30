import csv
import random
from pathlib import Path
from queue import Queue
from typing import Dict, Generator, Optional

import typer
import yaml
from drone import Drone, DroneStates
from package import Package
from package_station import PackageStation
from position import Position
from simpy import Environment, Process, Resource, Timeout
from simpy.resources.resource import Request
from simpy.rt import RealtimeEnvironment
from utils import *


class SortingOffice:

    def __init__(
        self,
        env: Environment,
        drones: Dict[int, Drone],
        package_stations: Dict[int, PackageStation],
    ):
        self._env = env
        self._drones = drones
        self._package_stations = package_stations

        self._station_distances_lut = generate_distance_lut(package_stations)

        self._packages_to_send_queue: Queue[Package] = Queue()
        self._drone_resource = Resource(env, capacity=len(drones))
        self._csv_filename = Path("package_deliveries.csv")

        with self._csv_filename.open(mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Dispatch Time",
                    "Package ID",
                    "Station ID",
                    "Drone ID",
                    "Delivery Time",
                    "Collection Time",
                    "Postage Time"
                ]
            )

    def _get_distance_from_sorting_centre(self, station_id: int) -> Optional[float]:
        """
        Returns the distance from the sorting centre (ID = 0) to the given station_id.
        If the lookup doesn't exist, returns None.
        """
        if station_id not in self._station_distances_lut:
            return None

        station_distances = self._station_distances_lut[station_id]
        if 0 not in station_distances:
            return None

        return station_distances[0]

    def _add_package(self, package: Package) -> None:
        """Add a package to the queue of packages to send."""
        self._packages_to_send_queue.put(package)
        print(
            f"[t={round(self._env.now, 2)}] Package {package.get_id()} added to the queue."
        )
        self._dispatch_package()

    def _dispatch_package(self) -> None:
        """Attempt to send a package from the queue if a drone is available."""
        while not self._packages_to_send_queue.empty():
            drone_id = self._get_first_free_drone_id()
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
        with self._drone_resource.request() as req:
            yield req

            print(
                f"[t={round(self._env.now, 2)}] Package '{package.get_id()}' assigned to drone '{assigned_drone_id}'."
            )

            print(
                f"[t={round(self._env.now, 2)}] Sending package {package.get_id()} to station {station_id}..."
            )

            self._env.process(
                self._complete_delivery(assigned_drone_id, package, station_id)
            )

    def _get_first_free_drone_id(self) -> Optional[int]:
        """Choose first available drone, if no drones available return None"""
        for id, drone in self._drones.items():
            if drone.get_state() == DroneStates.IDLE:
                return id

        return None

    def _complete_delivery(
        self, drone_id: id, package: Package, station_id: int
    ) -> Generator[Timeout, None, None]:
        """Handle delivery, free up the drone after delivery is complete."""
        distance = (
            self._get_distance_from_sorting_centre(station_id) * 2
        )  # There and back
        travel_time = distance / self._drones[drone_id].get_velocity()

        print(
            f"[t={round(self._env.now, 2)}] Drone '{drone_id}' is traveling... Estimated time: {travel_time:.2f}s"
        )

        package.set_delivery_time(self._env.now + (travel_time / 2))
        collection_time = self._env.now + (travel_time / 2) + random.uniform(5.0, 25.0)
        if collection_time > package.get_expiration_time():
            collection_time = None

        self._log_package(
            round(self._env.now, 2),
            package.get_id(),
            package.get_package_station_id(),
            drone_id,
            round(package.get_delivery_time(), 2),
            package._postage_time,
            round(collection_time, 2) if collection_time is not None else None,
        )

        # Drone unavailable until it returns
        yield self._env.timeout(travel_time)

        print(
            f"[t={round(self._env.now, 2)}] Package {package.get_id()} delivered to station {station_id}."
        )

        if self._drones[drone_id].remove_package():
            print(
                f"[t={round(self._env.now, 2)}] Drone '{drone_id}' is available again."
            )

        self._dispatch_package()

    def _log_package(
        self,
        time_of_dispatch: float,
        package_id: int,
        station_id: int,
        drone_id: int,
        delivery_time: float,
        postage_time: float,
        collection_time: Optional[None] = None,
    ) -> None:
        with self._csv_filename.open(mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    time_of_dispatch,
                    package_id,
                    station_id,
                    drone_id,
                    delivery_time,
                    collection_time,
                    postage_time
                ]
            )


class SystemEnvironment:

    def __init__(
        self,
        env: Environment,
        sorting_office: SortingOffice,
        random_time_lower_bound: int,
        random_time_upper_bound: int,
    ):
        self._env = env
        self._sorting_office = sorting_office
        self._random_time_lower_bound = random_time_lower_bound
        self._random_time_upper_bound = random_time_upper_bound

    def run_simulation(self, until: int = 50) -> None:
        def add_and_send_packages() -> Generator[Process | Timeout, None, None]:
            package_id = 1
            while True:
                station: PackageStation = random.choice(
                    list(self._sorting_office._package_stations.values())
                )
                package = Package(package_id, station.get_id())
                package._postage_time = self._env.now
                self._sorting_office._add_package(package)

                package_id += 1

                # Wait a random amount of time between each package
                delay = random.randint(
                    self._random_time_lower_bound, self._random_time_upper_bound
                )

                yield self._env.timeout(delay)

        self._env.process(add_and_send_packages())

        self._env.run(until=until)


def load_config_yaml(filepath: str) -> dict:
    """Load the YAML configuration file and return a dict."""
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


app = typer.Typer()


@app.command()
def run_sim(
    config_file: Path = typer.Argument(..., help="Path to the YAML config file."),
    until: int = typer.Option(200, help="How many simulation seconds to run."),
    factor: float = typer.Option(1.0, help="Simulation time scaling factor."),
    random_time_ub: int = typer.Option(
        20, help="Lower bound of randomized package generation."
    ),
    random_time_lb: int = typer.Option(
        10, help="upper bound of randomized package generation."
    ),
):
    """
    Load drones and package stations from CONFIG_FILE, then run a SimPy simulation
    for UNTIL simulation seconds.
    """
    # 1) Create environment
    env = RealtimeEnvironment(factor=factor)

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
    controller = SystemEnvironment(env, sorting_office, random_time_lb, random_time_ub)

    # 5) Run the simulation
    controller.run_simulation(until=until)

    typer.echo(f"Simulation finished at time={env.now}.")


def main():
    app()


if __name__ == "__main__":
    main()
