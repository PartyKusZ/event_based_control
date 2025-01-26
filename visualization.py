from  __future__  import annotations
import yaml
import csv 
import typer
from collections import defaultdict
from pathlib import Path
from position import Position
import pygame
from typing import List
from visualiztion_objects import *



class Action:
    def __init__(self, 
                 dispatch_time: float, 
                 package_id: int, 
                 station_id: int, 
                 drone_id: int, 
                 delivery_time: float, 
                 collection_time: float):
        
        self._dispatch_time = dispatch_time
        self._package_id = package_id
        self._station_id = station_id
        self._drone_id = drone_id
        self._delivery_time = delivery_time
        self._collection_time = collection_time
    @staticmethod

    def get_actions(simulation: dict) -> List[Action]:
        actions = []
        for i in range(len(simulation["Dispatch Time"])):
            action = Action(
                float(simulation["Dispatch Time"][i]),
                int(simulation["Package ID"][i]),
                int(simulation["Station ID"][i]),
                int(simulation["Drone ID"][i]),
                float(simulation["Delivery Time"][i]),
                float(simulation["Collection Time"][i]) if simulation["Collection Time"][i] != ""  else float("inf")
            )
            actions.append(action)
        return actions
        

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
        velocity = d["velocity"] * speed_factor * map_size_factor
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
    pygame.display.set_caption("Air Post")
    clock = pygame.time.Clock()

    start_time = pygame.time.get_ticks()
    
    actions = Action.get_actions(simulation)
    drones[1].set_destination(stations[7].get_position()[0], stations[7].get_position()[1])
    while True:
        
        current_time = (pygame.time.get_ticks() - start_time) / 1000.0 * speed_factor
        delta_time = clock.tick(60) / 1000.0 
        
        print(current_time)

        screen.fill((255, 255, 255))

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
            drone.update(delta_time)
        
    
        pygame.display.flip()
        


def main():
    app()

if __name__ == "__main__":
    main()

