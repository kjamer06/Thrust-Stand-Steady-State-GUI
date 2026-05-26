class AppState:
    def __init__(self):
        self.event_sequence = []

        self.thrust_max = 1.8
        self.power_max = 47
        self.mass = 0
        self.altitude = 0
        self.up_thrust = 0
        self.killswitch = False
        self.mission_manager = None
        self.flightstand_manager = None
        self.current_event = None
        self.event_to_update = None
        self.drag_coefficient = 0.95
        # MATPLOTLIB ARRAYS
        self.altitude_plot = []
        self.time_plot = []
        self.thrust_plot = []
        self.velocity_plot = []

    # THIS IS VERY VITAL TO PROGRAM IF THIS SWITCH IS FLIPPED FOR ANY REASON THE PROGRAM WILL SHUT OFF AND RESET ALL VALUES TO SAFE DEFAULTS
    def kill_switch(self):
        self.killswitch = True

state = AppState()