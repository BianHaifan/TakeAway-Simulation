from o2des.core import Sandbox
from .entity.data_context import DataContext
from .generator.order_generator import OrderGenerator
from .generator.restaurant_generator import RestaurantGenerator
from .generator.rider_generator import RiderGenerator
from .activity.restaurant_idle import RestaurantIdle
from .activity.cooking import Cooking
from .activity.order_being_prepared import BeingPrepared
from .activity.order_waiting_for_picking_up import WaitingForPickingUp
from .activity.order_being_delivered import BeingDelivered
from .activity.rider_idle import RiderIdle
from .activity.pick_up import PickUp
from .activity.deliver import Deliver
from .entity.order import Order


class Model(Sandbox):
    def __init__(self, data_context: DataContext, seed: int = 0):
        super().__init__(seed=seed, uid="Model")
        self.data_context: DataContext = data_context
        self.total_finish_time: float = 0.0
        self.finish_order_count: int = 0
        self.on_warmup.add(self._reset_custom_stats)
        # --- Generators ---
        self.order_generator = self.add_child(
            OrderGenerator(
                data_context=data_context,
                hourly_order_rate=10,
                seed=self._default_rs.next(),
            )
        )
        self.restaurant_generator = self.add_child(
            RestaurantGenerator(data_context=data_context, seed=self._default_rs.next())
        )
        self.rider_generator = self.add_child(
            RiderGenerator(data_context=data_context, seed=self._default_rs.next())
        )
        # --- Activities ---
        self.restaurant_idle = self.add_child(
            RestaurantIdle(data_context=data_context, seed=self._default_rs.next())
        )
        self.cooking = self.add_child(
            Cooking(data_context=data_context, seed=self._default_rs.next())
        )
        self.order_being_prepared = self.add_child(
            BeingPrepared(data_context=data_context, seed=self._default_rs.next())
        )
        self.order_waiting_for_picking_up = self.add_child(
            WaitingForPickingUp(data_context=data_context, seed=self._default_rs.next())
        )
        self.order_being_delivered = self.add_child(
            BeingDelivered(data_context=data_context, seed=self._default_rs.next())
        )
        self.rider_idle = self.add_child(
            RiderIdle(data_context=data_context, seed=self._default_rs.next())
        )
        self.pick_up = self.add_child(
            PickUp(data_context=data_context, seed=self._default_rs.next())
        )
        self.deliver = self.add_child(
            Deliver(data_context=data_context, seed=self._default_rs.next())
        )
        # =========================================================
        # Event Wiring (Core Entity Flow)
        # =========================================================

        # --- Restaurant flow ---
        self._connect_generator_flow(self.restaurant_generator, self.restaurant_idle)
        self._connect_activity_flow(self.restaurant_idle, self.cooking)
        self._connect_activity_flow(self.cooking, self.restaurant_idle)
        # --- Order flow ---
        self._connect_generator_flow(self.order_generator, self.order_being_prepared)
        self._connect_activity_flow(
            self.order_being_prepared, self.order_waiting_for_picking_up
        )
        self._connect_activity_flow(
            self.order_waiting_for_picking_up, self.order_being_delivered
        )
        self._connect_termination(
            self.order_being_delivered,
            lambda order: order.position == data_context.customer.position,
            self._record_order_finish,
        )
        # --- Rider flow ---
        self._connect_generator_flow(self.rider_generator, self.rider_idle)
        self._connect_activity_flow(self.rider_idle, self.pick_up)
        self._connect_conditional_event_flow(
            self.pick_up,
            self.rider_idle,
            lambda rider: len(rider.load) < rider.capacity,
        )
        self._connect_conditional_event_flow(
            self.pick_up, self.deliver, lambda rider: len(rider.load) == rider.capacity
        )
        self._connect_activity_flow(self.deliver, self.rider_idle)
        # =========================================================
        # Signal Wiring (Cross-Flow Coordination)
        # =========================================================
        self.order_generator.on_finish.add(
            lambda order: self.restaurant_idle.signal_finish_order(order)
        )
        self.cooking.on_finish.add(
            lambda restaurant: self.order_being_prepared.signal_finish_restaurant(
                restaurant
            )
        )
        self.order_being_prepared.on_finish.add(
            lambda order: self.rider_idle.signal_finish_order(order)
        )
        self.pick_up.on_finish.add(
            lambda rider: self.order_waiting_for_picking_up.signal_finish_rider(rider)
        )
        self.deliver.on_start.add(
            lambda rider: self.order_being_delivered.signal_start_rider(rider)
        )
        self.deliver.on_finish.add(
            lambda rider: self.order_being_delivered.signal_finish_rider(rider)
        )

    def _record_order_finish(self, order: Order) -> None:
        self.total_finish_time += (
            self.clock_time - order.order_time
        ).total_seconds() / 3600.0
        self.finish_order_count += 1

    def _reset_custom_stats(self):
        self.total_finish_time = 0.0
        self.finish_order_count = 0
        self.data_context.animation_events.clear()

    @property
    def average_order_waiting_time(self):
        return self.total_finish_time / self.finish_order_count

    def _connect_generator_flow(self, source, target) -> None:
        """
        Connect generator.on_finish -> target.signal_start (unconditional).
        One-way only: generators don't have depart/on_start (no 4-state machine).
        Matches Reference Generator.ConnectTo().
        """
        source.on_finish.add(lambda entity: target.signal_start(entity))

    def _connect_activity_flow(self, source, target) -> None:
        """
        Full two-way ConnectTo matching the reference behavior ActivityHandler.ConnectTo().

        1. source.on_finish -> target.signal_start (forward entity)
        2. target.on_start -> source.depart (departure trigger)

        This ensures entities held in f_loads_finished of source are removed
        when target starts them.
        """
        source.on_finish.add(lambda entity: target.signal_start(entity))
        target.on_start.add(lambda entity: source.depart(entity))

    def _connect_conditional_event_flow(self, source, target, predicate) -> None:
        """
        Two-way ConnectTo with filter, matching the reference behavior ConnectTo(filter).

        1. source.on_finish -> target.signal_start (if predicate(entity) is True)
        2. target.on_start -> source.depart (unconditional, safe guard in depart)
        """
        source.on_finish.add(
            lambda entity: target.signal_start(entity) if predicate(entity) else None
        )
        target.on_start.add(lambda entity: source.depart(entity))

    def _connect_termination(self, source, predicate, before_depart=None) -> None:
        """
        Terminal ConnectTo matching the reference behavior Terminate(filter).

        When predicate(entity) is True, calls source.depart(entity)
        so the entity exits the process flow cleanly.
        """

        def terminate(entity):
            if not predicate(entity):
                return
            if before_depart is not None:
                before_depart(entity)
            source.depart(entity)

        source.on_finish.add(terminate)
