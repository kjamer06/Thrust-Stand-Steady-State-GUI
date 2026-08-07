from simulations.simulation_functions import *
from core.flightstand_manager import FlightStandManager
from core.state import state

flightstand_manager = FlightStandManager()
state.flightstand_manager = flightstand_manager
state.mass = 0.12
state.grav_force = state.mass * 9.81

takeoff_simulation(flightstand_manager, 1.5, 50)
#hover_simulation(flightstand_manager, 10)
#cruise_simulation(flightstand_manager, 50, 50)
land_simulation(flightstand_manager)

flightstand_manager.set_throttle(1000)