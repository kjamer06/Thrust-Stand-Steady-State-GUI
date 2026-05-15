"""
Mission simulation script for TYTO Series 1585 Thrust Stand
 User will be able to configure a sequence of events to mimic a given mission profile which will be implemented
 with a GUI interface. The user will be able to simulate events such as takeoff, hovering at target power, cruise at
 target trim, etc.

 REMINDER: THIS WAS BUILT AND TESTED WITH SIMULATED BOARD IN TYTO FLIGHT STAND SOFTWARE
 ACTUAL THRUST STAND WILL BE MUCH DIFFERENT SO CHANGE VALUES WHEN STAND GETS HERE

 IMPORTANT: TYTO Flight Stand software is required to run this program, the link to which can be found below:
 https://www.tytorobotics.com/blogs/manuals-and-datasheets/software-download

"""

import time
import dearpygui.dearpygui as dpg
import matplotlib as mpl
from matplotlib.image import thumbnail
from flightstand import FlightStand
from Button import *

#Constants (they will be assigned once in the drone specifications window so they kinda are constants but not really)
THROTTLE_MAX = 2000
THROTTLE_MIN = 1000
THRUST_MAX = 1.8
POWER_MAX = 47
THRUST_WEIGHT_RATIO = None

# Flightstand initialization
flightstand = FlightStand()
throttle = flightstand.find_output_by_type(flightstand.Proto.ESC)
throttle.output_target.target_value = 1000
throttle.output_target.active = True
flightstand.update_output(throttle, ['output_target'])

thrust_sensor = flightstand.find_input_by_type(flightstand.Proto.FORCE_FZ)
rotation_speed_sensor = flightstand.find_input_by_type(flightstand.Proto.ROTATION_SPEED_FREQUENCY)
voltage_sensor = flightstand.find_input_by_type(flightstand.Proto.VOLTAGE_HV_INPUT)
current_sensor = flightstand.find_input_by_type(flightstand.Proto.CURRENT_HALL_CURRENT)

event_sequence = []

# DPG Functions
def sequence_builder(sender):
    match sender:
        case "takeoff_button":
            event_sequence.append("takeoff")
        case "hover_button":
            event_sequence.append("hover")
        case "cruise_button":
            event_sequence.append("cruise")
        case "land_button":
            event_sequence.append("land")
        case "undo_button":
            if len(event_sequence) > 0:
                event_sequence.pop()
            else:
                dpg.add_text("[ERR] Tried to remove event while sequence is empty", parent="console_section")
        case "clear_button":
            event_sequence.clear()

def drone_specifications_callback():
    global THRUST_MAX, POWER_MAX, MASS, THRUST_WEIGHT_RATIO
    THRUST_MAX = dpg.get_value("max_thrust_input")
    POWER_MAX = dpg.get_value("max_power_input")
    MASS = dpg.get_value("mass_input")
    THRUST_WEIGHT_RATIO = THRUST_MAX / MASS

    # Close drone specifications window and add info to log console
    dpg.configure_item("Drone Specifications", show=False)
    dpg.add_text("[INFO] Drone specifications submitted successfully", parent="console_section")

# Simulation functions
def spin_propellers():
    dpg.add_text("[SIM] Initializing Propellers", parent="console_section")
    spin_time = time.monotonic() + 10

    while time.monotonic() < spin_time:
        rotation_value = flightstand.get_latest_input_sample(rotation_speed_sensor).filtered_value
        rotation_error = (500 - rotation_value) / 1000

        if throttle.output_target.target_value + rotation_error > THROTTLE_MAX or throttle.output_target.target_value + rotation_error < THROTTLE_MIN:
            throttle.output_target.target_value -= rotation_error
        else:
            throttle.output_target.target_value += rotation_error
        flightstand.update_output(throttle, ['output_target'])

"""
Things to improve:
 1. Bounds errors and input handling (allegedly done, test next time you are here)
 2. Go to target thrust is good, just research setting the height if needed.
 3. Implement error handling
 4. Research better control systems for target thrust if needed
"""

def takeoff_simulation(target_thrust):
    flightstand.update_output(throttle, ['output_target'])
    if target_thrust <= MASS * 9.81:
        dpg.add_text("[ERR] Target thrust is too low to takeoff", parent="console_section")
    else:
        takeoff_time = time.monotonic() + 10
        spin_propellers()
        dpg.add_text("[SIM] Starting takeoff simulation", parent="console_section")
        while time.monotonic() < takeoff_time:
            measured_thrust = flightstand.get_latest_input_sample(thrust_sensor).filtered_value
            thrust_error = target_thrust - measured_thrust

            if throttle.output_target.target_value + thrust_error > THROTTLE_MAX or throttle.output_target.target_value + thrust_error < THROTTLE_MIN:
                throttle.output_target.target_value -= thrust_error
            else:
                throttle.output_target.target_value += thrust_error
            #########################################################################
            flightstand.update_output(throttle, ['output_target'])

def hover_simulation(target_power):
    dpg.add_text("[SIM] Starting hover simulation", parent="console_section")
    hover_time = time.monotonic() + dpg.get_value("hover_time_input")
    while time.monotonic() < hover_time:
        voltage_value = flightstand.get_latest_input_sample(voltage_sensor).filtered_value
        current_value = flightstand.get_latest_input_sample(current_sensor).filtered_value
        power_value = voltage_value * current_value
        power_error = (target_power - power_value) / 10
        if throttle.output_target.target_value + power_error > THROTTLE_MAX or throttle.output_target.target_value + power_error < THROTTLE_MIN:
            throttle.output_target.target_value -= power_error
        else:
            throttle.output_target.target_value += power_error

        flightstand.update_output(throttle, ['output_target'])

"""
Things to do for cruise and landing simulation:
1. Cruise simulation will take in a velocity, and distance and calculate the time needed to complete the cruise segment
2. Cruise simulation will then adjust the throttle to maintain target velocity for the duration of the cruise segment
3. Landing simulation will take in a descent rate and calculate the time needed to complete the landing segment.
4. Landing simulation will then decrease the throttle at a rate that achieves the target descent rate and maintain that descent rate for the duration of the landing segment.
"""
def cruise_simulation():
    dpg.add_text("[SIM] Starting cruise simulation", parent="console_section")


def landing_simulation():
    dpg.add_text("[SIM] Starting landing simulation", parent="console_section")
    while throttle.output_target.target_value > THROTTLE_MIN:
        throttle.output_target.target_value -= 0.1
        flightstand.update_output(throttle, ['output_target'])


def simulation_loop():
    if dpg.get_value("thrust_slider") > 0 or dpg.get_value("power_slider") > 0:
        for event in event_sequence:
            match event:
                case "takeoff":
                    takeoff_simulation(dpg.get_value("thrust_slider"))
                case "hover":
                    hover_simulation(dpg.get_value("power_slider"))
                case "cruise":
                    cruise_simulation()
                case "land":
                    landing_simulation()
        dpg.add_text("[SIM] Simulation finished with no errors", parent="console_section")
    else:
        dpg.add_text("[ERR] Target thrust or power is 0", parent="console_section")

    # End sequence will set throttle values back to 1000 and exit the program cleanly
    throttle.output_target.target_value = 1000
    flightstand.update_output(throttle, ['output_target'])

# Main function handles the GUI frontend and general program initialization.
def main():
    board = flightstand.create_simulated_board()
    dpg.create_context()

    # Main fixed window
    with dpg.window(
            tag="main_window",
            label="TYTO Series 1585 Thrust Stand Control Script",
            pos=(0, 0),
            width=1310,
            height=725,
            no_move=True,
            no_resize=True,
            no_collapse=True,
            no_close=True
    ):
        
        with dpg.child_window(
                tag="input_section",
                pos=(0, 0),
                width=1300,
                height=190,
                border=True
        ):
            dpg.add_text("Input target values here")

            dpg.add_input_float(
                label="Thrust (N)",
                tag="thrust_slider",
                max_value=THRUST_MAX,
                default_value=0,
                format="%.2f"
            )

            dpg.add_input_float(
                label="Power (W)",
                tag="power_slider",
                max_value=POWER_MAX,
                default_value=0,
                format="%.2f"
            )

            dpg.add_input_float(
                label="Cruise Velocity (m/s)",
                tag="cruise_velocity_input",
                default_value=0,
                format="%.2f"
            )

            dpg.add_input_float(
                label="Hover Time (s)",
                tag="hover_time_input",
                default_value=0,
                format="%.2f"
            )

        # The console section will display the status of the simulation and any error that might occur throughout the mission sequence
        with dpg.child_window(
                tag="console_section",
                pos=(0, 195),
                width=1000,
                height=500,
                border=True
        ):
            dpg.add_text("Console")

        # The events section will display the buttons to add events to the sequence as well as the current sequence of events. The mission sequence will be updated in real time as the user adds and removes events from the sequence.
        with dpg.child_window(
                tag="events_section",
                pos=(1005, 195),
                width=295,
                height=500,
                border=True
        ):
            dpg.add_text(
                "Select a mission objective to add into\n"
                "the mission sequence"
            )

            dpg.add_button(
                label="Takeoff",
                height=50,
                width=70,
                callback=sequence_builder,
                tag="takeoff_button"
            )

            dpg.add_button(
                label="Hover",
                height=50,
                width=70,
                callback=sequence_builder,
                tag="hover_button"
            )

            dpg.add_button(
                label="Cruise",
                height=50,
                width=70,
                callback=sequence_builder,
                tag="cruise_button"
            )

            dpg.add_button(
                label="Land",
                height=50,
                width=70,
                callback=sequence_builder,
                tag="land_button"
            )

            dpg.add_button(
                label="Undo",
                height=50,
                width=70,
                callback=sequence_builder,
                tag="undo_button"
            )

            dpg.add_button(
                label="Clear",
                height=50,
                width=70,
                callback=sequence_builder,
                tag="clear_button"
            )

            dpg.add_button(
                label="Start",
                height=50,
                width=70,
                callback=simulation_loop,
                tag="start_button"
            )

            with dpg.child_window(
                    pos=(80, 60),
                    width=200,
                    height=420,
                    tag="mission_window",
                    border=True
            ):
                dpg.add_text("Mission Sequence")
                mission_display = dpg.add_text("")
    with dpg.window(
                tag="Drone Specifications",
                modal=True,
                height=200,
                width=350,
                label="Drone Specifications"
        ):
            dpg.add_text("Input drone specifications here")
            dpg.add_input_float(
                label="Max Thrust (N)",
                tag="max_thrust_input",
                default_value=THRUST_MAX,
                format="%.2f"
            )
            dpg.add_input_float(
                label="Max Power (W)",
                tag="max_power_input",
                default_value=POWER_MAX,
                format="%.2f"
            )
            dpg.add_input_float(
                label="Mass (kg)",
                tag="mass_input",
                default_value=0,
                format="%.2f"
            )

            dpg.add_button(
                label="Submit",
                callback= drone_specifications_callback,
                tag="submit_specs_button"
            )

    # Initialize the GUI window and start the application 
    dpg.create_viewport(
        title='TYTO Series 1585 Thrust Stand Control Script',
        width=1310,
        height=725,
        resizable=False
    )

    dpg.setup_dearpygui()
    dpg.set_primary_window("main_window", True)

    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        dpg.set_value(mission_display, '\n'.join(event_sequence))
        dpg.render_dearpygui_frame()

    dpg.destroy_context()

if __name__ == "__main__":
    main()