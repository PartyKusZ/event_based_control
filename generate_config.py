import random
import yaml
import typer


def main(
    num_drones: int = typer.Argument(5, help="Number of drones to generate."),
    num_stations: int = typer.Argument(
        3, help="Number of package stations to generate."
    ),
    output_file: str = typer.Argument(
        "config.yaml", help="File to write the YAML config."
    ),
):
    """
    Generate a YAML file with random drones and package stations.
    Each drone has:
      - id
      - velocity

    Each package station has:
      - id
      - position (x, y)
      - number of lockers
    """

    # Generate drone data
    drones = []
    for i in range(num_drones):
        drone_id = i + 1
        velocity = round(random.uniform(1.0, 2.5), 2)
        drones.append({"id": drone_id, "velocity": velocity})

    # Generate station data
    stations = []
    for i in range(num_stations):
        station_id = i + 1
        x = round(random.uniform(0, 100), 2)
        y = round(random.uniform(0, 100), 2)
        lockers = random.randint(5, 20)
        stations.append({"id": station_id, "position": [x, y], "lockers": lockers})

    # Build top-level config structure
    config = {"drones": drones, "package_stations": stations}

    # Write YAML to file
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False)

    typer.echo(f"YAML configuration saved to '{output_file}'.")


if __name__ == "__main__":
    typer.run(main)
