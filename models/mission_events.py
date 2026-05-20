from dataclasses import dataclass
import dearpygui.dearpygui as dpg

@dataclass
class TakeoffEvent:
    target_thrust: float
    target_altitude: float
    def draw(self):
        dpg.add_button(label=f"Takeoff @ Thrust: {round(self.target_thrust, 4)} N", width=275, height=18, parent="mission_window_display")
        

@dataclass
class HoverEvent:
    hover_time: float
    def draw(self):
        dpg.add_button(label=f"Hover for {self.hover_time} s", width=275, height=18, parent="mission_window_display")

@dataclass
class CruiseEvent:
    target_velocity: float
    cruise_distance: float
    def draw(self):
        dpg.add_button(label=f"Cruise: Target Velocity = {self.target_velocity} m/s, Distance = {self.cruise_distance} m", width=275, height=18, parent="mission_window_display")

@dataclass
class LandEvent:
    def draw(self):
        dpg.add_button(label="Land", width=275, height=18, parent="mission_window_display")