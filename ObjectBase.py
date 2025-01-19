from abc import ABC, abstractmethod
import typing

class ObjectBase(ABC):
    def __init__(self, id: int):
        if not isinstance(id, int) or id < 0:
            raise ValueError("id must be a positive integer")
        self._id = id  # Prywatny atrybut
    
    @abstractmethod
    def get_id(self) -> int:
        return self._id
