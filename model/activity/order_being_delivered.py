from .activity import Activity
from ..entity.rider import Rider
from typing import List
from ..entity.data_context import DataContext


class BeingDelivered(Activity):
    def __init__(self, data_context: DataContext, seed: int = 0):
        super().__init__(seed=seed, uid="BeingDelivered")
        self.data_context = data_context
        self._p_start_signal: List[Rider] = []
        self._q_finish_signal: List[Rider] = []

    @property
    def p_start_signal(self) -> List[Rider]:
        return self._p_start_signal

    @property
    def q_finish_signal(self) -> List[Rider]:
        return self._q_finish_signal

    def _signal_start(self, rider: Rider):
        if rider is None:
            return
        if rider not in self._p_start_signal:
            self._p_start_signal.append(rider)
        self.schedule(self.attempt_start)

    def signal_start(self, entity) -> None:
        if isinstance(entity, Rider):
            self._signal_start(entity)
            return
        Activity.signal_start(self, entity)

    def signal_start_rider(self, rider: Rider):
        self._signal_start(rider)

    def attempt_start(self):
        if self.p_start_signal:
            self.p_start_signal.pop(0)
            super().attempt_start()

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

    def attempt_finish(self) -> None:
        if not self.q_finish_signal:
            return
        if not self.d_loads_ready_finish:
            return
        for rider in list(self.q_finish_signal):
            for order in list(rider.load):
                if (
                    order in self.d_loads_ready_finish
                    and order.position == self.data_context.customer.position
                ):
                    rider.load.remove(order)
                    if not rider.load:
                        self._q_finish_signal.remove(rider)
                    if self.data_context.debug_mode:
                        print(
                            f"{self.clock_time}\tOrder {order.order_id} has been delivered already."
                        )
                    self.finish(order)
