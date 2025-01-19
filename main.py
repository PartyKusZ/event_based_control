import random
from typing import Generator

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
    def __init__(self, station_id, location):
        self.station_id = station_id
        self.location = location


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


if __name__ == "__main__":
    env = RealtimeEnvironment(factor=0.2, strict=False)

    drones = [Drone(name=f"Drone_{i}", speed=random.uniform(0.8, 1.2)) for i in range(2)]
    stations = [
        PackageStation(
            station_id=i, location=(random.random() * 100, random.random() * 100)
        )
        for i in range(3)
    ]

    sorting_office = SortingOffice(env, drones, stations)

    controller = SystemEnvironment(env, sorting_office)
    controller.run_simulation(until=100)  # run for 30 time units
