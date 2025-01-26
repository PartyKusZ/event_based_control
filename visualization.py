import yaml
import csv 
import typer
from collections import defaultdict
from pathlib import Path
from drone import Drone
from package_station import PackageStation
from position import Position
import pygame

class DroneVisualizer(Drone):
    def __init__(self, drone_id: int, velocity: float):
        super().__init__(drone_id, velocity)
        self._position = Position(0, 0)
        self._image = pygame.image.load("drone.png")

    def get_position(self):
        return self._position.get_position()
    def draw(self, screen):
        screen.blit(self._image, self.get_position())

    def update(self):
        pass

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
        
    


def load_config_yaml(filepath: str)-> dict:
    with open(filepath, "r") as f:
        return yaml.safe_load(f)

def load_simulation_csv(filepath: str):
    csv_data = defaultdict(list)
    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key, value in row.items():
                csv_data[key].append(value)  
    return dict(csv_data)  



app = typer.Typer()

@app.command()
def run(config_file_yaml: Path = typer.Argument(..., help="Path to the YAML config file."),          
        simulation_file_csv: Path = typer.Argument(..., help="Path to the simulation CSV file."),
        speed_factor: int = typer.Option(1, help="Visualization Speed factor"),
        map_size_factor: int = typer.Option(5, help="Map size factor")):
    
    config = load_config_yaml(config_file_yaml)
    simulation = load_simulation_csv(simulation_file_csv)

    drones= {}
    for d in config.get("drones", []):
        drone_id = d["id"]
        velocity = d["velocity"] * speed_factor
        drones[drone_id] = DroneVisualizer(drone_id, velocity)
    
    stations = {}
    for s in config.get("package_stations", []):
        station_id = s["id"]
        position = Position(tuple(s["position"])[0] * map_size_factor, tuple(s["position"])[1] * map_size_factor)
        lockers = s["lockers"]
        stations[station_id] = PackageStationVisualizer(station_id, position, lockers)

    sorting_office = SortingOfficeVisualizer()

    pygame.init()

    screen_x, screen_y = 0, 0 

    screen_x = max(station.get_position()[0] for station in stations.values()) + 100
    screen_y = max(station.get_position()[1] for station in stations.values()) + 100

    screen = pygame.display.set_mode((screen_x, screen_y))
    screen.fill((255, 255, 255))
    pygame.display.set_caption("Air Post")
    clock = pygame.time.Clock()

    start_time = pygame.time.get_ticks()
    

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
        sorting_office.draw(screen)
        sorting_office.update()
        
        for station in stations.values():
            station.draw(screen)
            station.update()

        for drone in drones.values():
            drone.draw(screen)
            drone.update()
        
    
        pygame.display.flip()
        clock.tick(60)
        


def main():
    app()

if __name__ == "__main__":
    main()

