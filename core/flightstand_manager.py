from api.flightstand import FlightStand
from core import state

"""
This class will initialize the flightstand and provide easy access to sensor readings and controlling the throttle for 
the control PID functions 
"""
class FlightStandManager:
    def __init__(self):
        self.flightstand = FlightStand()
        self.board = self.flightstand.create_simulated_board()

        self.throttle = self.flightstand.find_output_by_type(self.flightstand.Proto.ESC)
        
        # Sensors will be initialized here for easy access
        self.thrust_sensor = self.flightstand.find_input_by_type(self.flightstand.Proto.FORCE_FZ)
        self.voltage_sensor = self.flightstand.find_input_by_type(self.flightstand.Proto.VOLTAGE_HV_INPUT)
        self.current_sensor = self.flightstand.find_input_by_type(self.flightstand.Proto.CURRENT_HALL_CURRENT)
        self.rotation_speed_sensor = self.flightstand.find_input_by_type(self.flightstand.Proto.ROTATION_SPEED_FREQUENCY)

        # Initialize throttle to a safe default value
        self.throttle.output_target.target_value = 1000
        self.throttle.output_target.active = True

        state.flightstand_manager = self

    def set_throttle(self, value):
        self.throttle.output_target.target_value = value
        self.flightstand.update_output(self.throttle, ['output_target'])

    def get_thrust(self):
        return self.flightstand.get_latest_input_sample(self.thrust_sensor).filtered_value

    def get_power(self):
        voltage_value = self.flightstand.get_latest_input_sample(self.voltage_sensor).filtered_value
        current_value = self.flightstand.get_latest_input_sample(self.current_sensor).filtered_value

        return voltage_value * current_value
    
    def get_rotation_speed(self):
        return self.flightstand.get_latest_input_sample(self.rotation_speed_sensor).filtered_value