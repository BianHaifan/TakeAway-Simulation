from .generator import Generator
import datetime as dt
from o2des.utils.dotnet_distributions import DotNetExponential
from ..entity.order import Order
from ..entity.data_context import DataContext


class OrderGenerator(Generator):
    def __init__(
        self, data_context: DataContext, hourly_order_rate: float, seed: int = 0
    ):
        super().__init__(id="OrderGenerator", seed=seed)
        self.data_context = data_context
        self.hourly_order_rate = hourly_order_rate
        self._next_order_id = 0
        self.schedule(
            self._generate_order,
            delay=dt.timedelta(
                hours=DotNetExponential.sample(self._default_rs, self.hourly_order_rate)
            ),
        )

    def _generate_order(self):
        self.schedule(
            self._generate_order,
            delay=dt.timedelta(
                hours=DotNetExponential.sample(self._default_rs, self.hourly_order_rate)
            ),
        )
        order = Order(self._next_order_id, self.clock_time)
        self.arrive(order)
        self._next_order_id += 1
        if self.data_context.debug_mode:
            print(f"{self.clock_time}\tCustomer generate a new order {order.order_id}.")
        self.data_context.animation_events.append(
            {
                "clock_time": self.clock_time.isoformat(),
                "type": "generate_order",
                "order": order.order_id,
            }
        )
