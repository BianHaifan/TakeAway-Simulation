from .order import Order


class Restaurant:
    def __init__(self, id: int, position: float, hourly_doing_rate: float):
        self.id: int = id
        self.position: float = position
        self.hourly_doing_rate: float = hourly_doing_rate
        self.order: Order | None = None

    def __repr__(self):
        return f"Restaurant-{self.id}"
