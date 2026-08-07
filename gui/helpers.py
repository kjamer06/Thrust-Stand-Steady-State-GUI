import dearpygui.dearpygui as dpg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from pathlib import Path


from core.state import state

TEXTURE_SIZES = {}

def update_mission_window():
    dpg.delete_item("mission_window_display", children_only=True)
    for event in state.event_sequence:
        event.draw()

def load_texture(path, tag):
    width, height, channels, data = dpg.load_image(path)
    TEXTURE_SIZES[tag] = (width, height)

    with dpg.texture_registry():
        dpg.add_static_texture(width=width, height=height, default_value=data, tag=tag)

def add_scaled_image(tag, desired_width):
    orig_w, orig_h = TEXTURE_SIZES[tag]
    scaled_height = int(desired_width * orig_h / orig_w)

    dpg.add_image(tag, width=desired_width, height=scaled_height)

def clear_input_window():
    dpg.delete_item("dynamic_event_inputs", children_only=True)
    dpg.configure_item("dynamic_event_inputs", horizontal=False)

def show_update_button():
    dpg.configure_item("update_button", show=True)

def show_takeoff_window():
    clear_input_window()
    dpg.add_text("Takeoff Event Inputs", parent="dynamic_event_inputs")

    dpg.add_input_float(label="Thrust (N)", min_value=(state.mass * 9.81), max_value=state.thrust_max, default_value=(state.mass * 9.81), format="%.2f", parent="dynamic_event_inputs", tag="thrust_slider")
    dpg.add_input_int(label="Altitude (m)", max_value=100, parent="dynamic_event_inputs",tag="altitude_input")

def edit_takeoff_window(target_thrust, target_altitude):
    clear_input_window()
    dpg.add_text("Takeoff Event Inputs", parent="dynamic_event_inputs")

    dpg.add_input_float(label="Thrust (N)", min_value=(state.mass * 9.81), max_value=state.thrust_max, default_value=(state.mass * 9.81), format="%.2f", parent="dynamic_event_inputs", tag="thrust_slider")
    dpg.add_input_int(label="Altitude (m)", max_value=100, default_value=target_altitude, parent="dynamic_event_inputs",tag="altitude_input")

def show_hover_window():
    clear_input_window()

    dpg.add_text("Hover Event Inputs", parent="dynamic_event_inputs")
    dpg.add_input_float(label="Hover Time (s)", tag="hover_time_input", default_value=0, format="%.2f", parent="dynamic_event_inputs")

def edit_hover_window(target_hover_time):
    clear_input_window()

    dpg.add_text("Hover Event Inputs", parent="dynamic_event_inputs")
    dpg.add_input_float(label="Hover Time (s)", tag="hover_time_input", default_value=target_hover_time, format="%.2f", parent="dynamic_event_inputs")

def show_cruise_window():
    clear_input_window()

    dpg.add_text("Cruise Event Inputs", parent="dynamic_event_inputs")

    dpg.add_input_float(label="Cruise Velocity (m/s)", tag="cruise_velocity_input", default_value=0, format="%.2f", parent="dynamic_event_inputs")
    dpg.add_input_float(label="Cruise Distance (m)", tag="cruise_distance_input", default_value=0, format="%.2f", parent="dynamic_event_inputs")

def edit_cruise_window(target_velocity, cruise_distance, pitch_angle):
    clear_input_window()

    dpg.add_text("Cruise Event Inputs", parent="dynamic_event_inputs")

    dpg.add_input_float(label="Cruise Velocity (m/s)", tag="cruise_velocity_input", default_value=target_velocity, format="%.2f", parent="dynamic_event_inputs")
    dpg.add_input_float(label="Cruise Distance (m)", tag="cruise_distance_input", default_value=cruise_distance, format="%.2f", parent="dynamic_event_inputs")
    dpg.add_input_float(label="Pitch Angle (degrees)", tag="pitch_angle_input", default_value=pitch_angle, format="%.2f", parent="dynamic_event_inputs")