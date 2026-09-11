from .activity import Activity
from ..entity.data_context import DataContext
from ..entity.rider import Rider
import datetime as dt


class Deliver(Activity):
    def __init__(self, data_context: DataContext, seed: int = 0):
        super().__init__(seed=seed, uid="Deliver")
        self.data_context = data_context
        self._t_duration = lambda rider, rs: self._get_duration(rider)

    def start(self, rider: Rider):
        self.data_context.animation_events.append(
            {
                "clock_time": self.clock_time.isoformat(),
                "type": "move_to_deliver",
                "rider": rider.name,
                "current_position": rider.position
            }
        )
        return super().start(rider)

    def _get_duration(self, rider: Rider) -> dt.timedelta:
        distance = abs(self.data_context.customer.position - rider.position)
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
        rider.position = self.data_context.customer.position
        for order in rider.load:
            order.position = self.data_context.customer.position
            if self.data_context.debug_mode:
                print(
                    f"{self.clock_time}\tRider {rider.name} delivered the order {order.order_id}."
                )
            self.data_context.animation_events.append(
                {
                    "clock_time": self.clock_time.isoformat(),
                    "type": "deliver",
                    "rider": rider.name,
                    "order": order.order_id,
                }
            )
        super().finish(rider)
