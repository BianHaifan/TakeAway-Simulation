from .activity import Activity
from typing import List
from ..entity.order import Order


class RiderIdle(Activity):
    def __init__(self, seed: int = 0):
        super().__init__(seed=seed, uid="RiderIdle")
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

    def attempt_finish(self) -> None:
        if not self.d_loads_ready_finish:
            return
        # only one rider currently, not use loop
        rider = self.d_loads_ready_finish[0]
        if self.q_finish_signal:
            order = self.q_finish_signal[0]
            rider.target_order = order
            self._q_finish_signal.remove(order)
            # print(f"{self.clock_time}\tRider received order {order.order_id}.")
            self.finish(rider)
