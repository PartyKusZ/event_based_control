from typing import Tuple

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_position(self) -> Tuple[int, int]:
        return self.x, self.y
    
    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y