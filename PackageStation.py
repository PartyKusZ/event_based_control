from ObjectBase import * 
from Position import *
from Package import *

class PackageStation(ObjectBase):

    def __init__(self, _id: int, position: Position):
        super().__init__(_id)
        self._position = position
        self._locker: list = []

    def get_num_of_lockers(self) -> int:
        return len(self._locker)
    
    def get_num_of_free_lockers(self) -> int:
        return len([locker for locker in self._locker if locker.get_state()])
    
    def load_package(self, package: Package) -> None:
        for locker in self._locker:
            if locker.get_state() == LockerState.FREE:
                 locker.load_package(package)
                 break
            else:
                raise ValueError("There is no free locker")
            
    def remove_package(self, package: Package) -> None:
        for locker in self._locker:
            if locker.get_package() == package:
                if locker.remove_package():
                    break
                else:
                    raise ValueError("Cannot remove package")
            else:
                raise ValueError("Package not found")