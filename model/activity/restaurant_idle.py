from .activity import Activity
from ..entity.order import Order
from ..entity.data_context import DataContext
from typing import List


class RestaurantIdle(Activity):
    def __init__(self, data_context: DataContext, seed: int = 0):
        super().__init__(seed=seed, uid="RestaurantIdle")
        self.data_context = data_context
        self._q_finish_signal: List[Order] = []

    @property
    def q_finish_signal(self) -> List[Order]:
        return self._q_finish_signal

    def _signal_finish(self, order: Order):
        if order is None:
            return
        if order not in self._q_finish_signal:
            self._q_finish_signal.append(order)
        self.schedule(self.attempt_finish)

    def signal_finish(self, entity) -> None:
        if isinstance(entity, Order):
            self._signal_finish(entity)
            return
        Activity.signal_finish(self, entity)

    def signal_finish_order(self, order: Order):
        self._signal_finish(order)

    def attempt_finish(self):
        for order in list(self.q_finish_signal):
            for restaurant in list(self.d_loads_ready_finish):
                if restaurant.order is None:
                    restaurant.order = order
                    order.position = restaurant.position
                    self.q_finish_signal.remove(order)
                    if self.data_context.debug_mode:
                        print(
                            f"{self.clock_time}\tAssign order {order.order_id} to restaurant {restaurant.id}."
                        )
                    self.data_context.animation_events.append(
                        {
                            "clock_time": self.clock_time.isoformat(),
                            "type": "order_assigned",
                            "restaurant": restaurant.id,
                            "order": order.order_id
                        }
                    )
                    self.finish(restaurant)
                    break
