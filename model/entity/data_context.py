from typing import List, Dict, Optional, Tuple
from .customer import Customer
from .restaurant import Restaurant
from .rider import Rider
import os
import csv
from pathlib import Path

REQUIRED_INPUT_FILES = ("customer.csv", "restaurant.csv", "rider.csv")
INPUT_DIRECTORY = "input"


class DataContext:
    def __init__(self):
        self.customer: Customer = None
        self.restaurants: List[Restaurant] = []
        self.rider: Rider = None
        self.debug_mode: bool = False
        # useless attribute for simulation, only for animation
        self.animation_events: List[dict] = []


class DataContextInitializer:
    @staticmethod
    def create() -> DataContext:
        _check_input_files()
        context = DataContext()
        _load_customer(context, Path(os.path.join(INPUT_DIRECTORY, "customer.csv")))
        _load_restaurant(context, Path(os.path.join(INPUT_DIRECTORY, "restaurant.csv")))
        _load_rider(context, Path(os.path.join(INPUT_DIRECTORY, "rider.csv")))
        return context


def _check_input_files() -> None:
    if not os.path.isdir(INPUT_DIRECTORY):
        raise FileNotFoundError(f"The {INPUT_DIRECTORY} folder doesn't exist.")
    for file in REQUIRED_INPUT_FILES:
        if not os.path.isfile(os.path.join(INPUT_DIRECTORY, file)):
            raise FileNotFoundError(f"The {file} doesn't exist.")


def _read_rows(
    path: Path, expected_headers: Optional[List[str]] = None
) -> Tuple[List[str], List[Dict[str, Optional[str]]]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        headers = reader.fieldnames or []
        if expected_headers is not None and headers != expected_headers:
            raise ValueError(
                f"{path}: expected headers {expected_headers}, got {headers}"
            )
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: at least one data row is required")
    return headers, rows


def _required(row: Dict[str, Optional[str]], column: str, path: Path) -> str:
    value = (row.get(column) or "").strip()
    if not value:
        raise ValueError(f"{path}: required value missing for '{column}'")
    return value


def _load_customer(context: DataContext, path: Path) -> None:
    _, rows = _read_rows(path, ["position", "name"])
    if len(rows) > 1:
        raise ValueError("Only could have 1 customer.")
    row = rows[0]
    position = float(_required(row, "position", path))
    name = _required(row, "name", path)
    customer = Customer(position, name)
    context.customer = customer


def _load_restaurant(context: DataContext, path: Path) -> None:
    _, rows = _read_rows(path, ["id", "position", "hourly_doing_rate"])
    for row in rows:
        restaurant_id = int(_required(row, "id", path))
        position = float(_required(row, "position", path))
        hourly_doing_rate = float(_required(row, "hourly_doing_rate", path))
        restaurant = Restaurant(restaurant_id, position, hourly_doing_rate)
        context.restaurants.append(restaurant)


def _load_rider(context: DataContext, path: Path) -> None:
    _, rows = _read_rows(
        path, ["name", "position", "speed", "traffic_rate", "capacity"]
    )
    if len(rows) > 1:
        raise ValueError("Only could have 1 rider.")
    row = rows[0]
    name = _required(row, "name", path)
    position = float(_required(row, "position", path))
    speed = float(_required(row, "speed", path))
    traffic_rate = float(_required(row, "traffic_rate", path))
    capacity = int(_required(row, "capacity", path))
    rider = Rider(name, position, speed, traffic_rate, capacity)
    context.rider = rider
