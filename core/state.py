class AppState:
    def __init__(self):
        self.event_sequence = []

        self.thrust_max = 1.8
        self.power_max = 47
        self.throttle_max = None
        self.throttle_min = None
        
        self.mission_manager = None
        self.flightstand_manager = None
        self.current_event = None
        self.event_to_update = None
        self.thrust_weight_ratio = None

        # Simulation values
        self.mass = 0
        self.drag_coefficient = 0.0005
        self.up_thrust = 0
        self.grav_force = None
        
        self.altitude = 0
        self.displacement = 0

        self.vertical_velocity = 0
        self.horizontal_velocity = 0

        self.vertical_acceleration = 0
        self.horizontal_acceleration = 0

        # MATPLOTLIB ARRAYS
        self.altitude_plot = []
        self.time_plot = []
        self.thrust_plot = []
        self.velocity_plot = []
        self.power_plot = []

        self.takeoff_PID = [1000,1500,100]
        self.hover_PID = [300,200,600]
        self.cruise_alt_PID = [300,200,600]
        self.cruise_vel_PID = [1.4,0.05,1.6]
        self.landing_PID = [300,20,600]

state = AppState()