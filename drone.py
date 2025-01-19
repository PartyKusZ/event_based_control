from enum import Enum
from object_base import ObjectBase
from package import Package


class DroneStates(Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"


class Drone(ObjectBase):
    def __init__(self, drone_id: int, velocity: float):
        super().__init__(drone_id)
        self._velocity = velocity
        self._state = DroneStates.IDLE
        self._package = None

    def get_velocity(self) -> float:
        return self._velocity

    def get_state(self) -> DroneStates:
        return self._state

    def load_package(self, package: Package) -> bool:
        if self._state == DroneStates.IDLE:
            self._package = package
            self._state = DroneStates.BUSY
            return True
        return False

    def remove_package(self) -> bool:
        if self._state == DroneStates.BUSY:
            self._package = None
            self._state = DroneStates.IDLE
            return True
        return False
