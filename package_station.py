from object_base import ObjectBase
from position import Position
from package import Package
from locker import Locker, LockerStates
from typing import List


class PackageStation(ObjectBase):

    def __init__(self, id: int, position: Position, num_of_lockers: int):
        super().__init__(id)
        self._position = position
        self._locker: List[Locker] = [Locker(i) for i in range(num_of_lockers)]

    def get_num_of_lockers(self) -> int:
        return len(self._locker)

    def get_num_of_free_lockers(self) -> int:
        return len(
            [
                locker
                for locker in self._locker
                if locker.get_state() == LockerStates.FREE
            ]
        )

    def load_package(self, package: Package) -> None:
        for locker in self._locker:
            if locker.get_state() == LockerStates.FREE:
                locker.load_package(package)
                break
            else:
                raise ValueError("There is no free locker")

    def remove_package(self, package: Package) -> None:
        for locker in self._locker:
            if locker.get_state() == LockerStates.OCCUPIED:
                if locker.get_package() == package:
                    locker.remove_package()
                    break
                else:
                    raise ValueError("Package not found")
            else:
                raise ValueError("There is no occupied locker")
