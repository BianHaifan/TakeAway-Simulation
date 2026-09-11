import json
import os


def _snapshot_model_state(model) -> dict:
    restaurants = []
    for restaurant in model.data_context.restaurants:
        restaurant_state = {}
        restaurant_state["id"] = restaurant.id
        restaurant_state["position"] = restaurant.position
        if restaurant.order is None:
            restaurant_state["cooking"] = None
        else:
            restaurant_state["cooking"] = restaurant.order.order_id
        restaurant_state["ready"] = [
            order.order_id
            for order in model.order_waiting_for_picking_up.d_loads_ready_finish
            if order.position == restaurant.position
        ]
        restaurants.append(restaurant_state)

    snapshot_state = {
        "scene": {
            "road_start": 0.0,
            "road_end": 500.0,
            "customer_position": model.data_context.customer.position,
        },
        "clock_time": model.clock_time.isoformat(),
        "rider": _snapshot_rider_state(model),
        "restaurants": restaurants,
        "unassigned_orders": [
            order.order_id
            for order in model.order_being_prepared.r_loads_requested_start
        ],
    }
    return snapshot_state


def _snapshot_rider_state(model) -> dict:
    rider = model.data_context.rider
    rider_state = {
        "name": rider.name,
        "state": "idle",
        "position": rider.position,
        "target_order": rider.target_order,
        "load": [order.order_id for order in rider.load],
        "receive": None,
    }
    if rider in model.pick_up.s_loads_started:
        rider_state["state"] = "to_pickup"
        moving_distance = (
            (model.clock_time - rider.start_moving_time)
            / (rider.end_moving_time - rider.start_moving_time)
            * (rider.target_order.position - rider.position)
        )
        if rider.position > rider.target_order.position:
            moving_distance = -moving_distance
        rider_state["position"] += moving_distance
    elif rider in model.deliver.s_loads_started:
        rider_state["state"] = "to_deliver"
        moving_distance = (
            (model.clock_time - rider.start_moving_time)
            / (rider.end_moving_time - rider.start_moving_time)
            * (model.data_context.customer.position - rider.position)
        )
        rider_state["position"] += moving_distance
    else:
        rider_state["receive"] = rider.target_order
    return rider_state


def dump_snapshot_json(model) -> None:
    state = _snapshot_model_state(model)
    with open(
        os.path.join("dashboard", "public", "animation_initial_state.json"),
        "w",
        encoding="utf-8-sig",
    ) as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
