import datetime as dt


class Order:
    def __init__(self, order_id: int, order_time: dt.datetime):
        self.order_id: int = order_id
        self.order_time: dt.datetime = order_time
        self.position: float = 0.0

    def __repr__(self):
        return f"Order {self.order_id}"
