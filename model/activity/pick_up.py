from .activity import Activity
from ..entity.rider import Rider
import datetime as dt


class PickUp(Activity):
    def __init__(self, seed: int = 0):
        super().__init__(seed=seed, uid="PickUp")
        self._t_duration = lambda rider, rs: self._get_duration(rider)

    def _get_duration(self, rider: Rider) -> dt.timedelta:
        distance = abs(rider.position - rider.target_order.position)
        hours = distance / rider.speed
        variation_factor = (
            1 - rider.traffic_rate
        ) + 2 * rider.traffic_rate * self._default_rs.next_double()
        hours *= variation_factor
        return dt.timedelta(hours=hours)

    def finish(self, rider: Rider) -> None:
        rider.load.append(rider.target_order)
        rider.position = rider.target_order.position
        # print(
        #     f"{self.clock_time}\tRider {rider.name} got the order {rider.target_order.order_id}."
        # )
        rider.target_order = None
        super().finish(rider)
        
