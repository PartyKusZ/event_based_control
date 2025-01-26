from position import Position
from typing import List
import pygame
from drone import Drone
from package_station import PackageStation
class DroneVisualizer(Drone):

    def __init__(self, drone_id: int, velocity: float):
        super().__init__(drone_id, velocity)
        self._position = Position(0, 0)
        self._image = pygame.image.load("drone.png")
        self._destination = None
        self._start_time = 0

    def get_destination(self):
         return self._destination.get_position() if self._destination else None
    
    def set_destination(self, x: int, y: int):
        self._destination = Position(x, y)
    def get_start_time(self):
        return self._start_time
    def set_start_time(self, start_time: float):
        self._start_time = start_time    
    
    def get_position(self):
        return self._position.get_position()
    def draw(self, screen):
        screen.blit(self._image, self.get_position())

    def update(self, delta_time: float):
        if self._destination is None:
            return  # Brak celu, dron nie zmienia pozycji

        # Aktualna pozycja drona
        current_x, current_y = self._position.get_position()
        # Docelowa pozycja
        dest_x, dest_y = self._destination.get_position()

        # Oblicz wektor do celu
        direction_x = dest_x - current_x
        direction_y = dest_y - current_y

        # Oblicz dystans do celu
        distance_to_destination = (direction_x**2 + direction_y**2)**0.5

        # Ustaw epsilon dla porównania
        epsilon = 1e-5

        if distance_to_destination < epsilon:
            # Jeśli dystans jest mniejszy niż epsilon, uznaj, że dron dotarł do celu
            self._position = Position(dest_x, dest_y)
            self._destination = Position(0, 0)
            return

        # Normalizacja wektora kierunku
        direction_x /= distance_to_destination
        direction_y /= distance_to_destination

        # Oblicz przesunięcie na podstawie prędkości i delta czasu
        displacement = self.get_velocity() * delta_time
        move_x = direction_x * displacement
        move_y = direction_y * displacement

        # Jeśli przemieszczenie przekroczy dystans do celu, ustaw drona na pozycji celu
        if displacement >= distance_to_destination:
            self._position = Position(dest_x, dest_y)
        else:
            # Aktualizacja pozycji drona
            new_x = current_x + move_x
            new_y = current_y + move_y
            self._position = Position(new_x, new_y)
        

class PackageStationVisualizer(PackageStation):
    def __init__(self, id: int, position: Position, num_of_lockers: int):
        super().__init__(id, position, num_of_lockers)
        self._image = pygame.image.load("package_station.png")

    def draw(self, screen):
        screen.blit(self._image, self.get_position())
    
    def update(self):
        pass

class SortingOfficeVisualizer:
    def __init__(self, position: Position = Position(0, 0)):
        self._position = position
        self._image = pygame.image.load("office.png")
    
    def get_position(self):
        return self._position.get_position()
    def draw(self, screen):
        screen.blit(self._image, self.get_position())

    def update(self):
       pass
        