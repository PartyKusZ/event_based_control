from objectBase import ObjectBase
from enum import Enum
from typing import Optional

class PackageStates(Enum):
    IN_SORTING_PLANT = "IN_SORTING_PLANT"
    IN_TRANSPORT = "IN_TRANSPORT"
    IN_PACKAGE_STATION = "IN_PACKAGE_STATION"
    COLLECTED = "COLLECTED"
    EXPIRED = "EXPIRED"

class Package(ObjectBase):
    def __init__(self, package_id: int, package_station_id: int):
        super().__init__(package_id)
        self._package_station_id = package_station_id
        self._state = PackageStates.IN_SORTING_PLANT
        self._loading_date: Optional[float] = None
        self._expiry_date: Optional[float] = None

    def get_state(self) -> PackageStates:
        return self._state

    def set_state(self, new_state: PackageStates) -> bool:
        self._state = new_state
        return True