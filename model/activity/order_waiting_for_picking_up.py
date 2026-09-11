from .activity import Activity
from ..entity.rider import Rider
from typing import List


class WaitingForPickingUp(Activity):
    def __init__(self, seed: int = 0):
        super().__init__(seed=seed, uid="WaitingForPickingUp")
        self._q_finish_signal: List[Rider] = []

    @property
    def q_finish_signal(self) -> List[Rider]:
        return self._q_finish_signal

    def _signal_finish(self, rider: Rider):
        if rider is None:
            return
        if rider not in self._q_finish_signal:
            self._q_finish_signal.append(rider)
        self.schedule(self.attempt_finish)

    def signal_finish(self, entity) -> None:
        if isinstance(entity, Rider):
            self._signal_finish(entity)
            return
        Activity.signal_finish(self, entity)

    def signal_finish_rider(self, rider: Rider):
        self._signal_finish(rider)

    def attempt_finish(self):
        if not self.q_finish_signal:
            return
        if not self.d_loads_ready_finish:
            return
        matched = False
        for rider in list(self.q_finish_signal):
            for order in self.d_loads_ready_finish:
                if order in rider.load and order.position == rider.position:
                    matched = True
                    # print(
                    #     f"{self.clock_time}\tOrder {order.order_id} has been picked up already."
                    # )
                    self.finish(order)
            if matched:
                self.q_finish_signal.remove(rider)
