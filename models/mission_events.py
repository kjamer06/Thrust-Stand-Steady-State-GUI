from dataclasses import dataclass
import dearpygui.dearpygui as dpg
from gui.helpers import edit_cruise_window, edit_cruise_window, edit_hover_window, edit_takeoff_window, show_update_button
from core.state import state

def mission_event_clicked_callback(sender, app_data, user_data):
    match user_data:
        case TakeoffEvent():
            edit_takeoff_window(target_thrust=user_data.target_thrust, target_altitude=user_data.target_altitude)
            state.event_to_update = user_data
            show_update_button()
        case HoverEvent():
            edit_hover_window(target_hover_time=user_data.hover_time)
            state.event_to_update = user_data
            show_update_button()
        case CruiseEvent():
            edit_cruise_window(target_velocity=user_data.target_velocity, cruise_distance=user_data.cruise_distance, pitch_angle=user_data.pitch_angle)
            state.event_to_update = user_data
            show_update_button()
        

@dataclass
class TakeoffEvent:
    target_thrust: float
    target_altitude: float
    def draw(self):
        dpg.add_button(label=f"Takeoff @ Thrust: {round(self.target_thrust, 4)} N", width=275, height=18, parent="mission_window_display", 
                callback=mission_event_clicked_callback, user_data=TakeoffEvent(target_thrust=self.target_thrust, target_altitude=self.target_altitude))
        
@dataclass
class HoverEvent:
    hover_time: float
    def draw(self):
        dpg.add_button(label=f"Hover for {self.hover_time} s", width=275, height=18, parent="mission_window_display", callback=mission_event_clicked_callback, user_data=self)

@dataclass
class CruiseEvent:
    target_velocity: float
    cruise_distance: float
    pitch_angle: float
    def draw(self):
        dpg.add_button(label=f"Cruise at {self.target_velocity} m/s for {self.cruise_distance} m at {self.pitch_angle} deg", width=275, height=18, parent="mission_window_display", callback=mission_event_clicked_callback, user_data=self)

@dataclass
class LandEvent:
    def draw(self):
        dpg.add_button(label="Land", width=275, height=18, parent="mission_window_display", callback=mission_event_clicked_callback)