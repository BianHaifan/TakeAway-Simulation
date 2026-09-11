from .activity import Activity
from ..entity.data_context import DataContext
from ..entity.restaurant import Restaurant
import datetime as dt
from o2des.utils.dotnet_distributions import DotNetExponential


class Cooking(Activity):
    def __init__(self, data_context: DataContext, seed: int = 0):
        super().__init__(seed=seed, uid="Cooking")
        self.data_context = data_context
        self._t_duration = lambda restaurant, rs: self._get_duration(restaurant)
        self._hc_doing = {
            restaurant.id: self.add_hour_counter()
            for restaurant in self.data_context.restaurants
        }

    def _get_duration(self, restaurant: Restaurant) -> dt.timedelta:
        return dt.timedelta(
            hours=DotNetExponential.sample(
                self._default_rs, restaurant.hourly_doing_rate
            )
        )

    def start(self, restaurant: Restaurant) -> None:
        super().start(restaurant)
        self._hc_doing[restaurant.id].observe_change(1)

    def ready_finish(self, restaurant: Restaurant) -> None:
        super().ready_finish(restaurant)
        self._hc_doing[restaurant.id].observe_change(-1)

    def finish(self, restaurant: Restaurant) -> None:
        if self.data_context.debug_mode:
            print(
                f"{self.clock_time}\tRestaurant {restaurant.id} finished order {restaurant.order.order_id}."
            )
        self.data_context.animation_events.append(
            {
                "clock_time": self.clock_time.isoformat(),
                "type": "cooking_finished",
                "restaurant": restaurant.id,
                "order": restaurant.order.order_id,
            }
        )
        super().finish(restaurant)
