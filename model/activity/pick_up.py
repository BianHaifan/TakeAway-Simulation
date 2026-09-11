from .activity import Activity
from ..entity.rider import Rider
from ..entity.data_context import DataContext
import datetime as dt


class PickUp(Activity):
    def __init__(self, data_context: DataContext, seed: int = 0):
        super().__init__(seed=seed, uid="PickUp")
        self.data_context = data_context
        self._t_duration = lambda rider, rs: self._get_duration(rider)

    def start(self, rider: Rider):
        self.data_context.animation_events.append(
            {
                "clock_time": self.clock_time.isoformat(),
                "type": "move_to_pick_up",
                "rider": rider.name,
                "order": rider.target_order.order_id,
                "current_position": rider.position,
                "target_position": rider.target_order.position,
            }
        )
        return super().start(rider)

    def _get_duration(self, rider: Rider) -> dt.timedelta:
        distance = abs(rider.position - rider.target_order.position)
        hours = distance / rider.speed
        variation_factor = (
            1 - rider.traffic_rate
        ) + 2 * rider.traffic_rate * self._default_rs.next_double()
        hours *= variation_factor
        delay = dt.timedelta(hours=hours)
        # snapshot the rider moving
        rider.start_moving_time = self.clock_time
        rider.end_moving_time = self.clock_time + delay
        return delay

    def finish(self, rider: Rider) -> None:
        rider.load.append(rider.target_order)
        rider.position = rider.target_order.position
        if self.data_context.debug_mode:
            print(
                f"{self.clock_time}\tRider {rider.name} got the order {rider.target_order.order_id}."
            )
        self.data_context.animation_events.append(
            {
                "clock_time": self.clock_time.isoformat(),
                "type": "pick_up",
                "rider": rider.name,
                "order": rider.target_order.order_id,
            }
        )
        rider.target_order = None
        super().finish(rider)
