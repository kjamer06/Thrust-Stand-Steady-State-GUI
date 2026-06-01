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

   # spin_propellers(flightstand_manager=flightstand_manager)
    print("[SIM] Starting takeoff simulation")

    pid = PID(Kp=2000, Ki=1500, Kd=0, setpoint=target_thrust)
    pid.output_limits = (1000, 2000)

    state.altitude = 0
    state.vertical_velocity = 0

    initial_time = time.monotonic()
    plot_start_time = time.monotonic()
    state.time_plot = []
    state.thrust_plot = []

    while state.altitude < target_altitude:
        time_now = time.monotonic()
        dt = time_now - initial_time
        initial_time = time_now
        time_elapsed = time_now - plot_start_time

        drag_direction = 1 if state.vertical_velocity >= 0 else -1
        drag_force = state.drag_coefficient * (state.vertical_velocity**2) * drag_direction
        measured_thrust = flightstand_manager.get_thrust()
        net_force = measured_thrust - state.grav_force - drag_force

        state.vertical_acceleration = net_force / state.mass
        state.vertical_velocity += state.vertical_acceleration * dt
        state.altitude += state.vertical_velocity * dt

        if state.altitude < 0:
            state.altitude = 0
            state.vertical_velocity = 0
        if state.altitude > target_altitude:
            state.altitude = target_altitude
            state.vertical_velocity = 0
            state.vertical_acceleration = 0

        print(f"Altitude: {state.altitude:.2f} m | Thrust: {measured_thrust:.2f} N | Fg {state.grav_force:2f}")

        throttle_adjustment = pid(measured_thrust, dt)

        flightstand_manager.set_throttle(throttle_adjustment)

        state.thrust_plot.append(measured_thrust)
        state.time_plot.append(time_elapsed)
        state.altitude_plot.append(state.altitude)

        time.sleep(0.02)
    plot_takeoff()
    print("[SIM] Takeoff event executed successfully")
    
def hover_simulation(flightstand_manager, duration):
    print("[SIM] Starting hover simulation")
    pid = PID(Kp=300, Ki=200, Kd=600, setpoint=state.altitude)
    pid.output_limits = (1000, 2000)

    dt = 0.02 
    hover_time = time.monotonic() + int(duration)
    
    while time.monotonic() < hover_time:
        start_time = time.monotonic()

        print(f"Altitude: {state.altitude:.2f} | Target: {pid.setpoint}")

    
        throttle = pid(state.altitude)
        flightstand_manager.set_throttle(throttle)
        thrust_y = flightstand_manager.get_thrust() 

        drag_direction = 1 if state.vertical_velocity >= 0 else -1
        drag_force = state.drag_coefficient * (state.vertical_velocity**2) * drag_direction
        
        net_force = thrust_y - state.grav_force - drag_force
        state.vertical_acceleration = net_force / state.mass
        state.vertical_velocity += state.vertical_acceleration * dt
        state.altitude += state.vertical_velocity * dt

        loop_execution_time = time.monotonic() - start_time
        sleep_time = max(0, dt - loop_execution_time)
        time.sleep(sleep_time)

    print("[SIM] Hover event executed successfully")

def cruise_simulation(flightstand_manager, target_velocity, target_distance):
    print("[SIM] Starting cruise simulation")

    state.time_plot = []
    state.altitude_plot = []
    state.thrust_plot = []

    state.displacement = 0
    state.vertical_velocity = 0
    state.vertical_acceleration = 0
    state.horizontal_velocity = 0
    state.horizontal_acceleration = 0
    state.pitch_angle = 0

    altitude_pid = PID(Kp=300, Ki=200, Kd=600, setpoint=state.altitude)
    altitude_pid.output_limits = (1000, 2000)
    
    velocity_pid = PID(Kp=1.4, Ki=0.05, Kd=1.6, setpoint=target_velocity)
    velocity_pid.output_limits = (-30, 30)

    t1 = time.monotonic()
    plot_time = time.monotonic()
    while state.displacement < target_distance:
        throttle_adjustment = altitude_pid(state.altitude)
        flightstand_manager.set_throttle(throttle_adjustment)
        pitch_rad = m.radians(state.pitch_angle)
        state.pitch_angle = velocity_pid(state.horizontal_velocity)

        t2 = time.monotonic()
        dt = t2 - t1
        t1 = t2
        elapsed_time = t2 - plot_time

        drag_direction_y = 1 if state.vertical_velocity >= 0 else -1
        drag_force_y = state.drag_coefficient * (state.vertical_velocity**2) * drag_direction_y

        drag_direction_x = 1 if state.horizontal_velocity >= 0 else -1
        drag_force_x = state.drag_coefficient * (state.horizontal_velocity**2) * drag_direction_x


        current_thrust = flightstand_manager.get_thrust()
        thrust_x = current_thrust * m.sin(pitch_rad)
        thrust_y = current_thrust * m.cos(pitch_rad)

        state.vertical_acceleration = (thrust_y - (state.mass * 9.81)) / state.mass
        state.vertical_velocity += state.vertical_acceleration * dt
        state.altitude += state.vertical_velocity * dt

        state.horizontal_acceleration = (thrust_x - drag_force_x) / state.mass
        state.horizontal_velocity += state.horizontal_acceleration * dt
        state.displacement += state.horizontal_velocity * dt

        state.altitude_plot.append(state.altitude)
        state.time_plot.append(elapsed_time)
        state.thrust_plot.append(current_thrust)

        print(f"Velocity: {state.horizontal_velocity:2f} | Distance: {state.displacement:2f} | Altitude: {state.altitude:2f}| Current Thrust: {current_thrust:2f} | Target Alt: {altitude_pid.setpoint} | Angle: {state.pitch_angle}")

        time.sleep(0.02)
    plot_cruise()
    print("[SIM] Cruise event executed successfully")

def land_simulation(flightstand_manager):    
    velocity = 0
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

        drag_force = state.drag_coefficient * velocity**2
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