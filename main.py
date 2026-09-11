from model.entity.data_context import DataContextInitializer
from model.model import Model
import datetime as dt
from config.simulation_config import (WARM_UP_HOURS, SIMULATION_HOURS)

def main():
    context = DataContextInitializer.create()
    model = Model(data_context=context, seed=2026)
    print(f"Simulation warm-up started: {WARM_UP_HOURS} hours")
    model.warmup(period=dt.timedelta(hours=WARM_UP_HOURS))
    print("Simulation warm-up completed. Measurement starts now.")
    print()

    model.run(duration=dt.timedelta(hours=SIMULATION_HOURS))
    print("============================================================")
    for restaurant_id, hc in model.cooking._hc_doing.items():
        print(f"Busy rate of restaurant {restaurant_id} is: {hc.average_count}.")
    print("============================================================")
    print(f"Busy rate of rider {context.rider.name} is: {1-model.rider_idle.d_hour_counter.average_count}.") 
    print("============================================================")
    print(f"Average waiting time of orders is: {model.average_order_waiting_time} hours.")





if __name__ == "__main__":
    main()