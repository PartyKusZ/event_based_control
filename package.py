from enum import Enum
from typing import Optional

from object_base import ObjectBase


class PackageStates(Enum):
    IN_SORTING_PLANT = "IN_SORTING_PLANT"
    IN_TRANSPORT = "IN_TRANSPORT"
    IN_PACKAGE_STATION = "IN_PACKAGE_STATION"
    COLLECTED = "COLLECTED"
    EXPIRED = "EXPIRED"


class Package(ObjectBase):
    def __init__(
        self, package_id: int, package_station_id: int, expiration_timeout: int = 20
    ):
        super().__init__(package_id)
        self._package_station_id = package_station_id
        self._state = PackageStates.IN_SORTING_PLANT
        self._expiration_timeout = expiration_timeout
        self._delivery_time: Optional[float] = None
        self._expiration_time: Optional[float] = None

    def get_package_station_id(self) -> int:
        return self._package_station_id

    def get_state(self) -> PackageStates:
        return self._state

    def set_state(self, new_state: PackageStates) -> bool:
        self._state = new_state
        return True

    def set_delivery_time(self, time: float) -> None:
        self._delivery_time = time
        self._expiration_time = time + self._expiration_timeout

    def get_delivery_time(self) -> float:
        return self._delivery_time

    def get_expiration_time(self) -> float:
        return self._expiration_time
