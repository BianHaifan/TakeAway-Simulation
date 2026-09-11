from .activity import Activity
from ..entity.restaurant import Restaurant
from typing import List


class BeingPrepared(Activity):
    def __init__(self, seed: int = 0):
        super().__init__(seed=seed, uid="BeingPrepared")
        self._q_finish_signal: List[Restaurant] = []

    @property
    def q_finish_signal(self) -> List[Restaurant]:
        return self._q_finish_signal

    def _signal_finish(self, restaurant: Restaurant):
        if restaurant is None:
            return
        if restaurant not in self._q_finish_signal:
            self._q_finish_signal.append(restaurant)
        self.schedule(self.attempt_finish)

    def signal_finish(self, entity) -> None:
        if isinstance(entity, Restaurant):
            self._signal_finish(entity)
            return
        Activity.signal_finish(self, entity)

    def signal_finish_restaurant(self, restaurant: Restaurant):
        self._signal_finish(restaurant)

    def attempt_finish(self) -> None:
        for restaurant in list(self.q_finish_signal):
            order = restaurant.order
            if order is not None and order in list(self.d_loads_ready_finish):
                self.q_finish_signal.remove(restaurant)
                restaurant.order = None
                # print(
                #     f"{self.clock_time}\tOrder {order.order_id} has been cooked already."
                # )
                self.finish(order)
