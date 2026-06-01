import dearpygui.dearpygui as dpg
from core.state import state
from models.mission_events import TakeoffEvent, HoverEvent, CruiseEvent, LandEvent
from gui.helpers import show_takeoff_window, show_hover_window, show_cruise_window, update_mission_window, clear_input_window

def drone_specifications_callback():
    state.thrust_max = dpg.get_value("max_thrust_input")
    state.power_max = dpg.get_value("max_power_input")
    state.mass = dpg.get_value("mass_input")
    state.thrust_weight_ratio = state.thrust_max / state.mass
    state.grav_force = state.mass * 9.81

    # Close drone specifications window and add info to log console
    dpg.configure_item("Drone Specifications", show=False)
    print("[INFO] Drone specifications submitted successfully")

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
            clear_input_window()
            dpg.add_text("Takeoff has been added to the mission sequence, you may continue entering missions into the mission sequence\nor press start to initiate the sequence shown in the mission screen.", parent="dynamic_event_inputs")
        case "hover":
            state.current_event = HoverEvent(hover_time=dpg.get_value("hover_time_input"))
            clear_input_window()
            dpg.add_text("Hover has been added to the mission sequence, you may continue entering missions into the mission sequence\nor press start to initiate the sequence shown in the mission screen.", parent="dynamic_event_inputs")
        case "cruise":
            state.current_event = CruiseEvent(target_velocity=dpg.get_value("cruise_velocity_input"), cruise_distance=dpg.get_value("cruise_distance_input"), pitch_angle=dpg.get_value("pitch_angle_input"))
            clear_input_window()
            dpg.add_text("Cruise has been added to the mission sequence, you may continue entering missions into the mission sequence\nor press start to initiate the sequence shown in the mission screen.", parent="dynamic_event_inputs")
        case "land":
            state.current_event = LandEvent()
            clear_input_window()
            dpg.add_text("Landing has been added to the mission sequence, you may continue entering missions into the mission sequence\nor press start to initiate the sequence shown in the mission screen.", parent="dynamic_event_inputs")
    state.event_sequence.append(state.current_event)
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

def update_button_callback():
    index = state.event_sequence.index(state.event_to_update)
    match state.event_to_update:
        case TakeoffEvent():
            state.event_sequence[index] = TakeoffEvent(target_thrust=dpg.get_value("thrust_slider"), target_altitude=dpg.get_value("altitude_input"))
            clear_input_window()
            dpg.add_text("Mission has been updated", parent="dynamic_event_inputs")
        case HoverEvent():
            state.event_sequence[index] = HoverEvent(hover_time=dpg.get_value("hover_time_input"))
            clear_input_window()
            dpg.add_text("Mission has been updated", parent="dynamic_event_inputs")
        case CruiseEvent():
            state.event_sequence[index] = CruiseEvent(target_velocity=dpg.get_value("cruise_velocity_input"), cruise_distance=dpg.get_value("cruise_distance_input"), pitch_angle=dpg.get_value("pitch_angle_input"))
            clear_input_window()
            dpg.add_text("Mission has been updated", parent="dynamic_event_inputs")
    update_mission_window()
    dpg.configure_item("update_button", show=False)