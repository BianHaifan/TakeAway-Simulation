class Customer:
    def __init__(self, position: float, name: str = ""):
        self.position: float = position
        self.name: str = name
        self.orderCount: int = 0

    def __repr__(self):
        return f"Customer {self.name}"
