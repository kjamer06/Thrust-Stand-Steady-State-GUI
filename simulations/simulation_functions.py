import dearpygui.dearpygui as dpg
import time

from simple_pid import PID
from simulations.helpers import spin_propellers, clamp
from config.settings import THROTTLE_MIN, THROTTLE_MAX
from core.state import state


def takeoff_simulation(flightstand_manager, target_thrust, target_altitude):
    if target_thrust <= state.mass * 9.81:
        dpg.add_text("[ERR] Target thrust is too low to takeoff", parent="console_section")
        return

    spin_propellers(flightstand_manager=flightstand_manager)
    dpg.add_text("[SIM] Starting takeoff simulation", parent="console_section")


    pid = PID(Kp=90, Ki=2, Kd=63, setpoint=target_thrust)
    pid.output_limits = (-50, 50)

    filtered_thrust = 0
    velocity = 0
    altitude = 0
    initial_time = time.monotonic()

    while altitude < target_altitude:
        time_now = time.monotonic()
        dt = time_now - initial_time
        initial_time = time_now

        measured_thrust = flightstand_manager.get_thrust()
        
        gravity_force = state.mass * 9.81
        net_force = measured_thrust - gravity_force
        
        acceleration = net_force / state.mass

        velocity += acceleration * dt
        altitude += velocity * dt
        
        if altitude < 0:
            altitude = 0
            velocity = 0 

        print(f"Altitude: {altitude:.2f} m | Thrust: {measured_thrust:.2f} N")
        

        filtered_thrust = (0.9 * filtered_thrust) + (0.1 * measured_thrust)

        throttle_adjustment = pid(filtered_thrust)
        
        current_throttle = flightstand_manager.throttle.output_target.target_value
        new_throttle = clamp(current_throttle + throttle_adjustment, THROTTLE_MIN, THROTTLE_MAX)

        flightstand_manager.set_throttle(new_throttle)
        state.altitude = altitude
        
        time.sleep(0.02)

    dpg.add_text("[SIM] Takeoff event executed successfully", parent="console_section")
    
def hover_simulation(flightstand_manager, duration):
    dpg.add_text("[SIM] Starting hover simulation", parent="console_section")
    hover_thrust = state.mass * 9.81

    pid = PID(Kp= 22, Ki=0.8, Kd=8, setpoint=hover_thrust)
    pid.output_limits = (-50, 50)
    pid.sample_time = 0.2

    filtered_thrust = 0
    hover_time = time.monotonic() + int(duration)
    while time.monotonic() < hover_time:
        current_thrust = flightstand_manager.get_thrust()
        filtered_thrust = (0.9 * filtered_thrust) + (0.1 * current_thrust)

        throttle_adjustment = pid(filtered_thrust)
        current_throttle = flightstand_manager.throttle.output_target.target_value
        new_throttle = current_throttle + throttle_adjustment
        new_throttle = clamp(new_throttle, THROTTLE_MIN, THROTTLE_MAX)

        flightstand_manager.set_throttle(new_throttle)
        time.sleep(0.02)
    dpg.add_text("[SIM] Hover event executed successfully", parent="console_section")

def cruise_simulation(flightstand_manager, target_velocity, target_distance):
    dpg.add_text("[SIM] Starting cruise simulation", parent="console_section")


def land_simulation(flightstand_manager):
    dpg.add_text("[SIM] Starting landing sequence", parent="console_section")