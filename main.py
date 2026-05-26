"""
 Mission simulation script for TYTO Series 1585 Thrust Stand
 User will be able to configure a sequence of events to mimic a given mission profile which will be implemented
 with a GUI interface. The user will be able to simulate events such as takeoff, hovering at target power, cruise at
 target trim, etc.

 REMINDER: THIS WAS BUILT AND TESTED WITH SIMULATED BOARD IN TYTO FLIGHT STAND SOFTWARE
 ACTUAL THRUST STAND WILL BE MUCH DIFFERENT SO CHANGE VALUES WHEN STAND GETS HERE

 IMPORTANT: TYTO Flight Stand software is required to run this program, the link to which can be found below:
 https://www.tytorobotics.com/blogs/manuals-and-datasheets/software-download

 Main function calls the GUI initialization function to start the program. This project was my first real attempt at 
 building a modular GUI application so if there are any inefficiencies or bad practices please inform me if you are reading this.

"""
from core.flightstand_manager import FlightStandManager
from core.mission_manager import MissionManager
from core import state

from gui.main_window import initialize_GUI

def main():
    flightstand_manager = FlightStandManager()
    state.flightstand_manager = flightstand_manager
    mission_manager = MissionManager(flightstand_manager=flightstand_manager)
    state.mission_manager = mission_manager

    initialize_GUI()

if __name__ == "__main__":
    main()