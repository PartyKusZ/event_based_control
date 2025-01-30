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
        if not pygame.font.get_init():
            pygame.font.init()

        self._font = pygame.font.SysFont("Arial", 10) 

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

        # Tworzenie tekstu z identyfikatorem drona
        drone_id_text = self._font.render(f"ID: {self.get_id()}", True, (0,0,0))  # Biały kolor tekstu

        # Wyświetlanie tekstu obok obrazu drona
        text_position = (self.get_position()[0] + self._image.get_width()-15, self.get_position()[1])
        screen.blit(drone_id_text, text_position)

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
    INCREASE = 1
    DECREASE = -1

    def __init__(self, id: int, position: Position, num_of_lockers: int):
        super().__init__(id, position, num_of_lockers)
        self._num_of_packages = 0
        self._image = pygame.image.load("package_station.png")
        self._man_image = pygame.image.load("man.png")

        # Flagi do kontroli wyświetlania "man"
        self._flag_man = False
        self._flag_man_start_time = 0  # Przechowuje czas rozpoczęcia wyświetlania

        if not pygame.font.get_init():
            pygame.font.init()
        self._font = pygame.font.SysFont("Arial", 10) 

    def draw(self, screen):
        # Wyświetlanie ID stacji
        id_text = self._font.render(f"ID: {self.get_id()}", True, (0,0,0))
        text_position = (self.get_position()[0] + self._image.get_width(), self.get_position()[1])
        screen.blit(id_text, text_position)

        # Wyświetlanie liczby paczek
        package_text = self._font.render(f"{self._num_of_packages}", True, (0,0,0))
        text_position = (self.get_position()[0] + self._image.get_width(),
                         self.get_position()[1] + self._image.get_height() - 5)
        screen.blit(package_text, text_position)

        # Rysowanie stacji
        screen.blit(self._image, self.get_position())

        # Jeśli flaga aktywna, sprawdź czy nie minęły 2 sekundy
        if self._flag_man:
            current_time = pygame.time.get_ticks()  # Czas w milisekundach
            elapsed_time = (current_time - self._flag_man_start_time) / 1000.0  # Konwersja na sekundy

            if elapsed_time <= 1:
                # Nadal wyświetlamy przez 2 sekundy
                self.draw_man(screen)
            else:
                # Po upływie 2 sekund wyłączamy flagę
                self._flag_man = False

    def draw_man(self, screen):
        screen.blit(self._man_image, self.get_position())
    
    def update(self, action: int):
        if action == PackageStationVisualizer.DECREASE:
            self._flag_man = True
            self._flag_man_start_time = pygame.time.get_ticks()  # zapamiętujemy początek wyświetlania
        
        self._num_of_packages += action


class SortingOfficeVisualizer:
    def __init__(self, position: Position = Position(0, 0)):
        self._position = position
        self._image = pygame.image.load("office.png")
    
    def get_position(self):
        return self._position.get_position()
    def draw(self, screen):
        screen.blit(self._image, self.get_position())

    def update(self):
    #    self._number_of_packages += action
        pass
        