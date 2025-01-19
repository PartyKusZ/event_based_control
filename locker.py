from enum import Enum
from objectBase import ObjectBase
from package import Package


class LockerStates(Enum):
    FREE = "FREE"
    OCCUPIED = "OCCUPIED"


class Locker(ObjectBase):
    def __init__(self, locker_id: int):
        super().__init__(locker_id)
        self._state = LockerStates.FREE
        self._package = None

    def get_state(self) -> LockerStates:
        return self._state

    def load_package(self, package: Package) -> bool:
        if self._state == LockerStates.FREE:
            self._package = package
            self._state = LockerStates.OCCUPIED
            return True
        return False

    def remove_package(self) -> bool:
        if self._state == LockerStates.OCCUPIED:
            self._package = None
            self._state = LockerStates.FREE
            return True
        return False
    
    def get_package(self) -> Package:
        return self._package
