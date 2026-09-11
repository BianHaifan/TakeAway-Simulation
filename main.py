from model.entity.data_context import DataContextInitializer
from model.model import Model
import datetime as dt
from config.simulation_config import WARM_UP_HOURS, SIMULATION_HOURS
import pandas as pd
import os
from logger.snapshot import dump_snapshot_json
import json

OUTPUT_FOLDER = os.path.join("dashboard", "public")


def main():
    context = DataContextInitializer.create()
    model = Model(data_context=context, seed=2026)

    # This running is for debug
    # model.data_context.debug_mode = True
    # model.run(duration=dt.timedelta(hours=2))

    print(f"Simulation warm-up started: {WARM_UP_HOURS} hours")
    model.warmup(period=dt.timedelta(hours=WARM_UP_HOURS))
    print("Simulation warm-up completed. Measurement starts now.")
    print()
    dump_snapshot_json(model)

    model.run(duration=dt.timedelta(hours=SIMULATION_HOURS))
    # This running is for animation data, otherwise too long to show
    # model.run(duration=dt.timedelta(hours=2)) 
    print("============================================================")
    restaurant_rows = []
    for restaurant_id, hc in model.cooking._hc_doing.items():
        print(f"Busy rate of restaurant {restaurant_id} is: {hc.average_count}.")
        restaurant_rows.append(
            {"restaurant_id": restaurant_id, "busy_rate": hc.average_count}
        )
    restaurant_output = pd.DataFrame(
        restaurant_rows, columns=["restaurant_id", "busy_rate"]
    )
    restaurant_output.to_csv(os.path.join(OUTPUT_FOLDER, "restaurant.csv"), index=False)
    print("============================================================")
    rider_name = context.rider.name
    rider_busy_rate = 1 - model.rider_idle.d_hour_counter.average_count
    print(f"Busy rate of rider {rider_name} is: {rider_busy_rate}.")
    rider_output = pd.DataFrame(
        data=[[rider_name, rider_busy_rate]],
        columns=["rider_name", "busy_rate"],
    )
    rider_output.to_csv(os.path.join(OUTPUT_FOLDER, "rider.csv"), index=False)
    print("============================================================")
    print(
        f"Average waiting time of orders is: {model.average_order_waiting_time} hours."
    )
    order_output = pd.DataFrame(
        data=[
            ["order_nums", model.finish_order_count],
            ["average_waiting_time", model.average_order_waiting_time],
        ],
        columns=["label", "value"],
    )
    order_output.to_csv(os.path.join(OUTPUT_FOLDER, "order.csv"), index=False)
    with open(
        os.path.join(OUTPUT_FOLDER, "animation_events.json"), "w", encoding="utf-8-sig"
    ) as f:
        json.dump(model.data_context.animation_events, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
