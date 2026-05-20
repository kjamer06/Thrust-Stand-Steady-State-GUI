import dearpygui.dearpygui as dpg
from core.state import state
from models.mission_events import TakeoffEvent, HoverEvent, CruiseEvent, LandEvent
from gui.helpers import show_takeoff_window, show_hover_window, show_cruise_window, update_mission_window

def mission_event_clicked_callback(sender):
    pass

def drone_specifications_callback():
    state.thrust_max = dpg.get_value("max_thrust_input")
    state.power_max = dpg.get_value("max_power_input")
    state.mass = dpg.get_value("mass_input")
    state.thrust_weight_ratio = state.thrust_max / state.mass

    # Close drone specifications window and add info to log console
    dpg.configure_item("Drone Specifications", show=False)
    dpg.add_text("[INFO] Drone specifications submitted successfully", parent="console_section")

def takeoff_button_callback():
    state.current_event = "takeoff"
    show_takeoff_window()

def hover_button_callback():
    state.current_event = "hover"
    show_hover_window()
    
def cruise_button_callback():
    state.current_event = "cruise"
    show_cruise_window()

def land_button_callback():
    state.current_event = "land"
    
def add_button_callback():
    match state.current_event:
        case "takeoff":
            state.current_event = TakeoffEvent(target_thrust=dpg.get_value("thrust_slider"), target_altitude=dpg.get_value("altitude_input"))
        case "hover":
            state.current_event = HoverEvent(hover_time=dpg.get_value("hover_time_input"))
        case "cruise":
            state.current_event = CruiseEvent(target_velocity=dpg.get_value("cruise_velocity_input"), cruise_distance=dpg.get_value("cruise_distance_input"))
        case "land":
            state.current_event = LandEvent()
    state.event_sequence.append(state.current_event)
    print(state.event_sequence)
    update_mission_window()

def undo_button_callback():
    state.event_sequence.pop()
    update_mission_window()
    print(state.event_sequence)

def clear_button_callback():
    state.event_sequence.clear()
    update_mission_window()
    print(state.event_sequence)

def start_button_callback():
    state.mission_manager.execute_mission()

