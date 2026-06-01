from core.state import state
import time

def find_limits():
    flightstand_manager = state
    
    print("[WARN] INITIALIZING CHARACTERISTIC TESTS IN 10 SECONDS")

    time.sleep(10)

    flightstand_manager.set_throttle(state.throttle_max)
    start_time = time.monotonic()
    while start_time < time.monotonic() + 5:
        pass