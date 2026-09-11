from typing import List
from .order import Order


class Rider:
    def __init__(
        self,
        name: str = "",
        position: float = 0.0,
        speed: float = 1.0,
        traffic_rate: float = 0.0,
        capacity: int = 1,
    ):
        self.name: str = name
        self.position: float = position
        self.speed: float = speed
        self.traffic_rate: float = traffic_rate
        self.capacity: int = capacity
        self.load: List[Order] = []
        self.target_order: Order = None

    def __repr__(self):
        return f"Rider {self.name}"
