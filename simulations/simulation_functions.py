import time
import math as m

from simple_pid import PID
from simulations.helpers import spin_propellers, clamp
from gui.helpers import plot_takeoff, plot_cruise, plot_landing
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
    state.time_plot = []
    state.thrust_plot = []

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
        #state.up_thrust = measured_thrust

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

def cruise_simulation(flightstand_manager, target_velocity, target_distance, pitch_angle):
    
    print("[SIM] Starting cruise simulation")

    velocity = 0
    state.time_plot = []
    state.velocity_plot = []
    distance = 0
    initial_time = time.monotonic()
    plot_start_time = time.monotonic()
    pitch_radians = m.radians(pitch_angle)
    DRAG_COEFFICIENT = 0.0005

    pid = PID(Kp=200, Ki=120, Kd=10, setpoint=target_velocity)
    pid.output_limits = (THROTTLE_MIN, THROTTLE_MAX)

    while distance < target_distance:
        time_now = time.monotonic()
        dt = time_now - initial_time
        initial_time = time_now

        cruise_thrust = flightstand_manager.get_thrust()
        # CHANGE THIS ONCE YOU FIGURE OUT HOW WE WANT TO SIMULATE DRAG (just change cruise_thrust to net thrust)
        #cruise_acceleration = cruise_thrust / state.mass
        
        drag_force = DRAG_COEFFICIENT * velocity**2
        drag_force *= -1 if velocity < 0 else 1

        thrust_x = cruise_thrust * m.sin(pitch_radians)
        thrust_y = cruise_thrust * m.cos(pitch_radians)
    
        state.up_thrust = thrust_y
        net_force_x = thrust_x - drag_force
        # net_force_y = thrust_y - (state.mass * 9.81)

        cruise_acceleration = net_force_x / state.mass
        velocity += cruise_acceleration * dt
        distance += velocity * dt

        print(f"Velocity: {velocity:.2f} m/s | Distance: {distance:.2f} m | Thrust: {cruise_thrust:.2f} N")

        throttle_adjustment = pid(velocity)
        flightstand_manager.set_throttle(throttle_adjustment)

        state.time_plot.append(time_now - plot_start_time)
        state.velocity_plot.append(velocity)

        time.sleep(0.02)
    plot_cruise()
    print("[SIM] Cruise event executed successfully")

def land_simulation(flightstand_manager):
    """
    if (state.altitude <= 0 or state.up_thrust < state.mass * 9.81):
        print("[ERR] Landing cannot be completed, check to ensure you are not on the ground and that the drone has sufficient thrust")
        return
    """
    
    velocity = 0
    DRAG_COEFFICIENT = 0.0005
    grav_force = state.mass * 9.81

    state.velocity_plot = []
    state.time_plot = []
    state.altitude_plot = []

    pid = PID(Kp=0, Ki=10, Kd=500, setpoint=(grav_force - 0.5))
    pid.output_limits = (THROTTLE_MIN, THROTTLE_MAX)
    initial_time = time.monotonic()
    plot_start_time = time.monotonic()
    man_altitude = state.altitude * 0.10

    print("[SIM] Starting landing sequence")

    while (state.altitude > 0):
        time_now = time.monotonic()
        dt = time_now - initial_time
        initial_time = time_now
        elapsed_time = time_now - plot_start_time

        drag_force = DRAG_COEFFICIENT * velocity**2
        drag_force *= -1 if velocity < 0 else 1

        landing_thrust = flightstand_manager.get_thrust()
        net_thrust = landing_thrust - (drag_force + grav_force)

        acceleration = net_thrust / state.mass
        velocity += acceleration * dt
        state.altitude += velocity * dt

        if state.altitude < 0:
            state.altitude = 0

        state.altitude_plot.append(state.altitude)
        state.time_plot.append(elapsed_time)
        state.velocity_plot.append(velocity)

        print(f"Velocity: {velocity:2f} | Altitude: {state.altitude:2f}")

        current_throttle = flightstand_manager.throttle.output_target.target_value
        throttle_adjustment = current_throttle - pid(state.altitude)
        throttle_adjustment = clamp(throttle_adjustment, THROTTLE_MIN, THROTTLE_MAX)

        flightstand_manager.set_throttle(throttle_adjustment)
        time.sleep(0.02)
    plot_landing()