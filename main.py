import random
import yaml
from typing import Generator
import typer
from simpy import Environment, Process, Resource, Timeout
from simpy.resources.resource import Request
from simpy.rt import RealtimeEnvironment

id = str


########################### Placeholder Packages ###########################
class Package:
    def __init__(self, package_id, destination_station_id):
        self.package_id = package_id
        self.destination_station_id = destination_station_id


class Drone:
    def __init__(self, name, speed=1.0):
        self.name = name
        self.speed = speed


class PackageStation:

    def __init__(self, station_id, position, no_of_lockers):
        self.station_id = station_id
        self.position = position
        self.no_of_lockers = no_of_lockers


########################### Placeholder Packages ###########################


class SortingOffice:
    def __init__(
        self,
        env: Environment,
        drones: list[Drone],
        package_stations: list[PackageStation],
    ):
        self._env = env
        self._drones = drones
        self._package_stations = package_stations

        self._packages_to_send = []
        self._undelivered_packages = []
        self._delivered_packages = []

        # Placeholder, calculate the distances from the position of each package station
        self._station_distances_lut = {
            station.station_id: random.uniform(5.0, 15.0) for station in package_stations
        }

        # Drones are a resource
        self._drone_resource = Resource(env, capacity=len(drones))

    def _get_distance(self, package_station_id: id) -> float:
        """Return the distance from the sorting office to the station."""
        return self._station_distances_lut.get(package_station_id, 10.0)

    def _get_closest_available_package_station(
        self,
    ) -> id:
        """If the requested package station is full, get the id of the closest available package station"""

    def _add_package(self, package: Package) -> None:
        """Add a package to the queue of packages to send."""
        self._packages_to_send.append(package)
        print(f"[t={self._env.now}] Package {package.package_id} added to the queue.")

    def _send_package(
        self, package: Package, station: PackageStation
    ) -> Generator[Request | Timeout, None, None]:
        """Process generator to send a package to the given station using a drone."""
        print(
            f"[t={self._env.now}] Sending package {package.package_id} to station {station.station_id}..."
        )

        # Request a drone from the resource pool
        with self._drone_resource.request() as req:
            yield req  # Wait until a drone is free

            # Randomly choose from available drones
            chosen_drone = random.choice(self._drones)
            print(
                f"[t={self._env.now}] Drone '{chosen_drone.name}' picked up package {package.package_id}."
            )

            # Travel time is distance ÷ speed.
            distance = self._get_distance(station.station_id)
            travel_time = distance / chosen_drone.speed

            # Simulate traveling to station
            yield self._env.timeout(travel_time)
            print(
                f"[t={self._env.now}] Package {package.package_id} delivered to station {station.station_id}."
            )

            # Update delivered list
            self._delivered_packages.append(package)

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
                station = random.choice(self._sorting_office._package_stations)

                package = Package(package_id, station.station_id)
                self._sorting_office._add_package(package)

                yield self._env.process(
                    self._sorting_office._send_package(package, station)
                )

                package_id += 1
                # Wait a random amount of time between 1 and 10 seconds
                delay = random.randint(1, 10)
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
    until: int = typer.Option(100, help="How many simulation seconds to run."),
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
    drones = []
    for d in config.get("drones", []):
        drone_id = d["id"]
        velocity = d["velocity"]
        drone_name = f"Drone_{drone_id}"
        drones.append(Drone(name=drone_name, speed=velocity))

    stations = []
    for s in config.get("package_stations", []):
        station_id = s["id"]
        position = tuple(s["position"])
        lockers = s["lockers"]
        stations.append(PackageStation(station_id, position, lockers))

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
