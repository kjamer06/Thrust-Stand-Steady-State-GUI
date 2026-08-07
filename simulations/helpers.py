import time
import dearpygui.dearpygui as dpg
from core.state import state
from config.settings import THROTTLE_MAX, THROTTLE_MIN

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def spin_propellers(flightstand_manager):
    print("[SIM] Initializing Propellers")
    spin_time = time.monotonic() + 10

    while time.monotonic() < spin_time:
        rotation_value = flightstand_manager.get_rotation_speed()
        rotation_error = (500 - rotation_value) / 1000

        if flightstand_manager.throttle.output_target.target_value + rotation_error > THROTTLE_MAX or flightstand_manager.throttle.output_target.target_value + rotation_error < THROTTLE_MIN:
            flightstand_manager.throttle.output_target.target_value -= rotation_error
        else:
            flightstand_manager.throttle.output_target.target_value += rotation_error
        flightstand_manager.flightstand.update_output(flightstand_manager.throttle, ['output_target'])