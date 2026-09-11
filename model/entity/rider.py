from typing import List
from .order import Order
import datetime as dt


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
        # These two attributes are useless for simulation, only for snapshot
        self.start_moving_time: dt.datetime = dt.datetime.min
        self.end_moving_time: dt.datetime = dt.datetime.min

    def __repr__(self):
        return f"Rider {self.name}"
