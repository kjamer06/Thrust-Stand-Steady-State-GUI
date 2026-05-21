import dearpygui.dearpygui as dpg
import time

from simple_pid import PID
from simulations.helpers import spin_propellers, clamp
from gui.helpers import plot_takeoff, plot_cruise
from config.settings import THROTTLE_MIN, THROTTLE_MAX
from core.state import state

def takeoff_simulation(flightstand_manager, target_thrust, target_altitude):
    if target_thrust <= state.mass * 9.81:
        print("[ERR] Target thrust is too low to takeoff")
        return

    spin_propellers(flightstand_manager=flightstand_manager)
    print("[SIM] Starting takeoff simulation")


    pid = PID(Kp=100, Ki=1, Kd=80, setpoint=target_thrust)
    pid.output_limits = (-50, 50)

    filtered_thrust = 0
    velocity = 0
    altitude = 0
    initial_time = time.monotonic()
    plot_start_time = time.monotonic()

    while altitude < target_altitude:
        time_now = time.monotonic()
        dt = time_now - initial_time
        initial_time = time_now

        time_elapsed = time_now - plot_start_time

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

        state.thrust_plot.append(filtered_thrust)
        state.time_plot.append(time_elapsed)
        state.altitude_plot.append(altitude)

        
        time.sleep(0.02)
    plot_takeoff()
    print("[SIM] Takeoff event executed successfully")
    
def hover_simulation(flightstand_manager, duration):
    print("[SIM] Starting hover simulation")
    hover_thrust = state.mass * 9.81

    pid = PID(Kp= 22, Ki=0.8, Kd=8, setpoint=hover_thrust)
    pid.output_limits = (1000, 2000)

    filtered_thrust = 0
    hover_time = time.monotonic() + int(duration)
    while time.monotonic() < hover_time:
        current_thrust = flightstand_manager.get_thrust()
        filtered_thrust = (0.9 * filtered_thrust) + (0.1 * current_thrust)

        throttle_adjustment = pid(filtered_thrust)
        flightstand_manager.set_throttle(throttle_adjustment)
        time.sleep(0.02)
    print("[SIM] Hover event executed successfully")

def cruise_simulation(flightstand_manager, target_velocity, target_distance):
    print("[SIM] Starting cruise simulation")

    filtered_thrust = 0
    velocity = 0
    state.time_plot = []
    state.velocity_plot = []
    distance = 0
    initial_time = time.monotonic()
    plot_start_time = time.monotonic()

    pid = PID(Kp=130, Ki=50, Kd=5, setpoint=target_velocity)
    pid.output_limits = (1000, 2000)

    while distance < target_distance:
        time_now = time.monotonic()
        dt = time_now - initial_time
        initial_time = time_now

        cruise_thrust = flightstand_manager.get_thrust()
        # CHANGE THIS ONCE YOU FIGURE OUT HOW WE WANT TO SIMULATE DRAG (just change cruise_thrust to net thrust)
        #cruise_acceleration = cruise_thrust / state.mass
        
        DRAG_COEFFICIENT = 0.0005

        drag_force = DRAG_COEFFICIENT * velocity**2

        # Prevent drag direction from flipping incorrectly
        drag_force *= -1 if velocity < 0 else 1

        net_force = cruise_thrust - drag_force

        cruise_acceleration = net_force / state.mass
        ##############################################################
        velocity += cruise_acceleration * dt
        distance += velocity * dt

        print(f"Velocity: {velocity:.2f} m/s | Distance: {distance:.2f} m | Thrust: {cruise_thrust:.2f} N")

        current_throttle = flightstand_manager.throttle.output_target.target_value
        throttle_adjustment = pid(velocity)
        flightstand_manager.set_throttle(throttle_adjustment)

        state.time_plot.append(time_now - plot_start_time)
        state.velocity_plot.append(velocity)

        time.sleep(0.02)
    plot_cruise()
    print("[SIM] Cruise event executed successfully")

def land_simulation(flightstand_manager):
    print("[SIM] Starting landing sequence")

