from simulations.simulation_functions import takeoff_simulation, hover_simulation, cruise_simulation, land_simulation
from models.mission_events import TakeoffEvent, HoverEvent, CruiseEvent, LandEvent
from core.state import state
from config.settings import THROTTLE_MIN
from gui.plots import plot_takeoff, plot_cruise, plot_landing

class MissionManager:
    def __init__(self, flightstand_manager):
        self.flightstand_manager = flightstand_manager
        self.event_sequence = state.event_sequence
        state.mission_manager = self
    
    def execute_mission(self):
        for event in self.event_sequence:
            match event:
                case TakeoffEvent():
                    takeoff_simulation(self.flightstand_manager, event.target_thrust, event.target_altitude)
                    plot_takeoff()
                case HoverEvent():
                    hover_simulation(self.flightstand_manager, event.hover_time)
                case CruiseEvent():
                    cruise_simulation(self.flightstand_manager, event.target_velocity, event.cruise_distance)
                    plot_cruise()
                case LandEvent():
                    land_simulation(self.flightstand_manager)
                    plot_landing()
                case _:
                    pass
        self.flightstand_manager.set_throttle(THROTTLE_MIN)