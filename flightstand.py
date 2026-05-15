import datetime
import math
import sys
import time
import atexit
import typing
import threading

import grpc
import google.protobuf.field_mask_pb2 as field_mask
from google.protobuf.timestamp_pb2 import Timestamp

import flight_stand_api_v1_pb2 as fs
import flight_stand_api_v1_pb2_grpc as fs_grpc


class FlightStand:
    """
    This helper class simplifies gRPC calls to the Flight Stand API by encapsulating the setup of a gRPC stub and
    reducing the lines of code needed for common operations. It offers convenience but is optional. Note that not all
    features of the .proto file are implemented, and direct gRPC calls can still be made for more customization.
    See the https://gitlab.com/TytoRobotics/flightstand-api/-/blob/main/proto/flight_stand_api_v1.proto file for further
    details about the API commands available.

    To directly make gRPC calls while using this Flight Stand class, see this example:

    core = FlightStand()
    # Tare the sensors
    print("Taring sensors...")
    tare_inputs_response = core.stub.TareInputs(core.Proto.TareInputsRequest())
    print("Tare done.")

    Instead of using this FlightStand class, you can also use exclusively gRPC by following the example
    advanced_grpc_data_streaming.py.
    """

    Proto = fs
    """
    This field allows the user to call proto constants. Example usage:
    core = FlightStand()
    thrust_sensor = core.find_input_by_type(core.Proto.FORCE_FZ)
    """

    def __init__(self, server_address='localhost:50051', heartbeat=False):
        """
        Initializes the FlightStand object by connecting to the Flight Stand core software.

        :param server_address: The address of the Flight Stand core software.
        :param heartbeat: Whether this instance should send a heartbeat to the core. This is needed unless the GUI is
        also running in parallel to prevent a cutoff.
        """
        print("Connecting to core at address " + server_address + "...")
        channel = grpc.insecure_channel(server_address)
        stub = fs_grpc.FlightStandStub(channel)
        self.stub: fs_grpc.FlightStandStub = stub
        get_server_status_request = fs.GetServerStatusRequest()
        try:
            self.stub.GetServerStatus(get_server_status_request)
        except grpc.RpcError as rpc_error:
            print(rpc_error)
            print("Could not connect to the core. Most likely the Flight Stand Software is not running.",
                  file=sys.stderr)
            exit()
        print("Core connected!")  # If we reach this line without an error thrown, it means the core responded.
        self.print_hardware_list()
        self._current_output_values = {}  # Supports the get_external_output_state method
        self._boards_to_disconnect = []  # When the script ends, automatically disconnect created boards

        # Register the cleanup method to be called on program exit
        atexit.register(self.cleanup)

        # Automatically clear any cutoff, because a cutoff is triggered when the program exits.
        self.clear_cutoff()

        # Setup for the heartbeat
        if heartbeat:
            # Create a threading Event
            self.stop_event = threading.Event()
            # Create thread
            self.thread = threading.Thread(target=self.send_heartbeat)
            self.thread.start()

    @staticmethod
    def run_at_interval(interval: float, code_to_run: typing.Callable):
        """
        Helper method to trigger code execution at a specific interval. This method never exits.
        The interval is the time between each execution of the loop in seconds, so 0.1 interval means 10 executions per
        second.

        :param interval: The time interval between each code execution in seconds.
        :param code_to_run: The code to be executed at the specified interval.
        """
        start_time = time.time()
        while True:
            code_to_run()

            # Calculate the next start time
            start_time += interval

            # Adjust the sleep time based on the next start time
            remaining_time = start_time - time.time()
            if remaining_time > 0:
                time.sleep(remaining_time)

    def list_boards(self) -> list[fs.Board]:
        """
        Returns the list of boards that are ready to use.

        :return: A list of boards that are ready to use.
        """
        list_boards_response = self.stub.ListBoards(fs.ListBoardsRequest())
        boards = list_boards_response.boards

        filtered_boards = [board for board in boards if board.ready]
        return filtered_boards

    def get_board(self, board_name: str) -> fs.Board | None:
        """
        Retrieves a board by its name.

        :param board_name: The name of the board to retrieve.
        :return: The board object if found, or None if not found.
        """
        try:
            return self.stub.GetBoard(fs.GetBoardRequest(name=board_name))
        except grpc.RpcError as rpc_error:
            print(f"Received error while calling GetBoard: {rpc_error.details()}")
            return None

    def get_output(self, output_name: str) -> fs.Output | None:
        """
        Retrieves an output by its name.

        :param output_name: The name of the output to retrieve.
        :return: The output object if found, or None if not found.
        """
        try:
            return self.stub.GetOutput(fs.GetOutputRequest(name=output_name))
        except grpc.RpcError as rpc_error:
            print(f"Received error while calling GetOutput: {rpc_error.details()}")
            return None

    def get_input(self, input_name: str) -> fs.Input | None:
        """
        Retrieves an input by its name.

        :param input_name: The name of the input to retrieve.
        :return: The input object if found, or None if not found.
        """
        try:
            return self.stub.GetInput(fs.GetInputRequest(name=input_name))
        except grpc.RpcError as rpc_error:
            print(f"Received error while calling GetInput: {rpc_error.details()}")
            return None

    def list_inputs(self, board: fs.Board = None) -> list[fs.Input]:
        """
        Returns a list of inputs available, optionally filtered by board.

        :param board: If provided, filter the inputs by the specified board.
        :return: A list of input objects.
        """
        list_inputs_response = self.stub.ListInputs(fs.ListInputsRequest())

        if board is not None:
            filtered_inputs = []
            for i in list_inputs_response.inputs:
                if i.name.startswith(f"{board.name}/inputs/"):
                    filtered_inputs.append(i)
            return filtered_inputs

        return list_inputs_response.inputs

    def list_outputs(self, board: fs.Board = None) -> list[fs.Output]:
        """
        Returns a list of outputs available, optionally filtered by board.

        :param board: If provided, filter the outputs by the specified board.
        :return: A list of output objects.
        """
        list_outputs_response = self.stub.ListOutputs(fs.ListOutputsRequest())

        if board is not None:
            filtered_outputs = []
            for output in list_outputs_response.outputs:
                if output.name.startswith(f"{board.name}/outputs/"):
                    filtered_outputs.append(output)
            return filtered_outputs

        return list_outputs_response.outputs

    def find_input_by_type(self, input_type: fs.InputType) -> fs.Input | None:
        """
        Finds an input by its type.

        :param input_type: The type of the input to find.
        :return: The input object if found, or None if not found.
        """
        inputs = self.list_inputs()
        for i in inputs:
            if i.input_type == input_type:
                return i
        return None

    def find_output_by_type(self, output_type: fs.OutputType) -> fs.Output | None:
        """
        Finds an output by its type.

        :param output_type: The type of the output to find.
        :return: The output object if found, or None if not found.
        """
        outputs = self.list_outputs()
        for o in outputs:
            if o.output_type == output_type:
                return o
        return None

    def list_transformations(self) -> list[fs.InputTransformation]:
        """
        Returns a list of input transformations available.

        :return: A list of inputTransformation objects.
        """
        response = self.stub.ListInputTransformations(fs.ListInputTransformationsRequest())

        return response.input_transformations

    def get_latest_input_sample(self, input_msg: fs.Input) -> fs.Sample | None:
        """
        Retrieves the latest sample for a given input.

        :param input_msg: The input object to retrieve the latest sample for.
        :return: The latest sample if available, or None if no sample is found.
        """
        list_samples_response = self.stub.ListSamples(fs.ListSamplesRequest())
        for sample in list_samples_response.sample_group.samples:
            if sample.signal_name == input_msg.signal_name:
                return sample
        return None
    
    def get_latest_input_samples(self, input_msg: list[fs.Input]) -> list[fs.Sample] | None:
        """
        Retrieves the latest samples for given inputs.

        :param input_msg: The input objects to retrieve the latest samples for.
        :return: The latest samples if available, or an empty slice if no samples are found.
        """
        list_samples_response = self.stub.ListSamples(fs.ListSamplesRequest())
        samples = []
        for input in input_msg:
            for sample in list_samples_response.sample_group.samples:
                if sample.signal_name == input.signal_name:
                    samples.append(sample)
        return samples

    def create_simulated_board(self) -> fs.Board:
        """
        Creates a simulated board and connects it to the Flight Stand core.

        :return: The simulated board object.
        """
        # Todo: update the proto so the created board is returned
        self.stub.CreateSimulatedBoard(fs.CreateSimulatedBoardRequest())
        time.sleep(4)  # Give the simulated board time to connect
        boards = self.list_boards()
        for board in reversed(boards):
            if board.name.startswith("/boards/simulated_"):
                print("Connected " + board.name)

                # Add this board to the list of boards to disconnect when the program exits
                self._boards_to_disconnect.append(board.name)

                return board
        raise Exception("No simulated board found")

    def update_input(self, input: fs.Input, mask_fields: list[str]) -> fs.Input:
        """
        Updates the input with the specified mask fields.

        :param input: The input object to update.
        :param mask_fields: A list of fields to update in the input.
        :return: The updated input object.
        """
        # By following the .proto we see a mask is required to tell the core which
        # fields of the input are being updated.
        # See https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#fieldmask
        input_mask = field_mask.FieldMask()
        input_mask.paths.extend(mask_fields)

        # Create the update request
        update_request = fs.UpdateInputRequest(input=input, mask=input_mask)
        return self.stub.UpdateInput(update_request)

    def update_output(self, output: fs.Output, mask_fields: list[str]) -> fs.Output:
        """
        Updates the output with the specified mask fields.

        :param output: The output object to update.
        :param mask_fields: A list of fields to update in the output.
        :return: The updated output object.
        """
        # By following the .proto we see a mask is required to tell the core which
        # fields of the output are being updated.
        # See https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#fieldmask
        output_mask = field_mask.FieldMask()
        output_mask.paths.extend(mask_fields)

        # Create the update request
        update_request = fs.UpdateOutputRequest(output=output, mask=output_mask)
        return self.stub.UpdateOutput(update_request)

    def print_hardware_list(self):
        """
        Prints a list of available hardware, inputs, and outputs.
        """
        # List available hardware
        print("\nListing available hardware:")
        for b in self.list_boards():
            if not b.disconnected and not b.connection_error:
                print(b.name + ": " + b.display_name)

        # List all available inputs (sensors)
        print("\nListing available inputs:")
        for i in self.list_inputs():
            # Print some properties an input has. See the .proto for details.
            print(i.name + ": type=" + str(i.input_type))

        # List all available outputs (ESC and servo controls)
        print("\nListing available outputs:")
        for o in self.list_outputs():
            # Print some properties an output has. See the .proto for details.
            print(o.name + ": type=" + str(o.output_type))
        print()

    def connect_external_board(self, inputs: list[fs.ExternalInput], outputs: list[fs.ExternalOutput],
                               display_name: str = "", model_number: str = "", serial_number: str = "") -> fs.Board:
        """
        Connects an external board with the specified inputs and outputs and returns this board.

        :param inputs: A list of external input objects to connect.
        :param outputs: A list of external output objects to connect.
        :param display_name: Optional, the display name of the board.
        :param model_number: Optional, the model name of the board.
        :param serial_number: Optional, the serial number of the board
        :return: The connected external board object.
        """
        print("Connecting external hardware...")
        external_board_request = fs.CreateExternalBoardRequest()
        external_board_request.external_inputs.extend(inputs)
        external_board_request.external_outputs.extend(outputs)
        external_board_request.serial_number = serial_number
        external_board_request.display_name = display_name
        external_board_request.model_number = model_number
        core = self.stub.GetCore(fs.GetCoreRequest())
        if not core.license_feature_external_boards:
            print("Cannot add an external board since this feature requires a license key (free). Contact "
                  "support@tytorobotics.com to request a license key.", file=sys.stderr)
            exit()
        board = self.stub.CreateExternalBoard(external_board_request)
        print("Connected " + board.name)

        # Add this board to the list of boards to disconnect when the program exits
        self._boards_to_disconnect.append(board.name)

        return board

    @staticmethod
    def create_sample(input_msg: fs.Input, value: float, sample_time: float = None, active: bool = True) -> fs.Sample:
        """
        Creates an external sample.

        :param input_msg: The input object associated with the sample.
        :param value: The value of the sample.
        :param sample_time: The time of the sample (default is current time).
        :param active: The active status of the sample (default is True).
        :return: The created sample object.
        """
        # Create a new Sample object
        sample = FlightStand.Proto.Sample()

        # Set the signal name based on the input's signal
        sample.signal_name = input_msg.raw_signal_name

        # Convert the time to a protobuf timestamp
        if not sample_time:
            sample_time = time.time()
        timestamp = Timestamp()
        timestamp.FromDatetime(datetime.datetime.fromtimestamp(sample_time, tz=datetime.timezone.utc))
        sample.sample_time.CopyFrom(timestamp)

        # Set the active status and value of the sample
        if math.isnan(value):
            value = 0
            active = False
        sample.active = active
        sample.value = value

        return sample

    def write_external_samples(self, samples: list[fs.Sample]):
        """
        Forwards external hardware sensor readings to the Flight Stand.

        :param samples: A list of external samples to forward.
        """
        write_external_samples_request = fs.WriteExternalSamplesRequest()
        write_external_samples_request.samples.extend(samples)
        self.stub.WriteExternalSamples(write_external_samples_request)

    def get_external_output_state(self, output: fs.Output) -> (float, bool):
        """
        Poll this method to determine the state to set the external output to. The FlightStand class assumes the real
        hardware outputs follow the result of this method. The first returned value is the output value, and the second
        is for if the output is activated (activate checkbox in the Flight Stand's manual control tab).

        :param output: The output object to retrieve the state for.
        :return: A tuple containing the output value and activation status.
        """
        # Acknowledge the change of output to represent the real output (different from the target, especially when a
        # rate limiter is specified by the user). The target is where the Flight Stand Software wants the output to be,
        # while the current_output_value is where your external output is currently expected at, and is what will be
        # recorded/displayed by the Flight Stand Software.

        # Get the latest output target the flight stand core asks for. This can change when the user moves the manual
        # control slider, or when a cutoff occurs, or by using automatic control.
        output = self.get_output(output.name)

        # Get the current time
        t = time.time()

        # Set the initial value for the output
        if output.name not in self._current_output_values:
            self._current_output_values[output.name] = {
                "value": output.output_target.target_value,
                "time": t
            }
        output_value = self._current_output_values[output.name]["value"]

        # Enforce the rate limit parameter
        if output.output_target.rate_limit_per_second > 0:
            # time since this method was called last for this output
            dt = t - self._current_output_values[output.name]["time"]

            # Calculate how much the output can move per iteration. Note that a smoother ramp will be achieved if your
            # hardware can support faster update rates (smaller dt) by polling this method more often.
            max_output_change = dt * output.output_target.rate_limit_per_second
            output_change = output.output_target.target_value - self._current_output_values[output.name]
            output_change = max(-max_output_change, min(max_output_change, output_change))
            output_value += output_change
        else:
            # Go instantly to the target value
            output_value = output.output_target.target_value

        # Enforce the step size parameter. For example if your output is a standard PWM signal, it supports values
        # between 1000 and 2000, but with a step size of 1, so 1100.3 would not be meaningful with the real hardware.
        real_value = output_value
        if output.step_size > 0:
            val = real_value / output.step_size
            val = round(val)
            real_value = val * output.step_size

        # Update the Flight Stand Software to notify of the latest output value
        timestamp = Timestamp()
        timestamp.FromDatetime(datetime.datetime.fromtimestamp(t))
        updated_output_state = fs.Sample(signal_name=output.signal_name,
                                         sample_time=timestamp,
                                         active=output.output_target.active,
                                         value=real_value)

        self.write_external_samples([updated_output_state])

        # Save the state for next iteration
        self._current_output_values[output.name] = {
            "value": output_value,
            "time": t
        }

        return real_value, output.output_target.active

    def send_heartbeat(self):
        """
        Sends a heartbeat to the server every second
        """
        while not self.stop_event.is_set():
            get_server_status_request = fs.GetServerStatusRequest()
            try:
                # print("Heartbeat")
                self.stub.GetServerStatus(get_server_status_request)
            except grpc.RpcError as rpc_error:
                print("Could not connect to the core. Most likely the Flight Stand Software is not running.")
            # Sleep for 1 second
            time.sleep(1)

    def cleanup(self):
        """
        Performs any necessary cleanup tasks before exiting.
        """
        # Perform any necessary cleanup tasks before exiting
        print("Cleanup")

        # Stop the heartbeat thread
        if hasattr(self, 'stop_event'):
            self.stop_event.set()
            # Wait for the thread to finish
            self.thread.join()

        try:
            # Perform any necessary cleanup tasks before exiting
            self.stub.TriggerCutoff(fs.TriggerCutoffRequest())
            print("Script stopped, triggering cutoff")
        except grpc.RpcError as e:
            pass
        for board_name in self._boards_to_disconnect:
            try:
                self.stub.DisconnectBoard(fs.DisconnectBoardRequest(board_name=board_name))
                print("Script stopped, disconnecting " + board_name)
            except grpc.RpcError as e:
                pass

    def clear_cutoff(self):
        """
        Clears any cutoff that may have been triggered.
        """
        try:
            self.stub.ClearCutoff(fs.ClearCutoffRequest())
            print("Cutoff cleared")
        except grpc.RpcError as e:
            pass  # Most likely no cutoff to clear

    def take_sample(self):
        """
        Takes a data sample on the current test.
        """
        self.stub.TakeSampleTestRecorder(fs.TakeSampleTestRecorderRequest())
        time.sleep(0.1)  # We put a delay on purpose because taking manual samples is rate limited. Use the continuous
        # recording feature for higher sample rate recording.
        print("Sample taken")

    def save_test(self) -> str:
        """
        Saves a test and returns the name of the newly saved test.

        :return: The name of the saved test.
        """
        save_test_recorder_response = self.stub.SaveTestRecorder(fs.SaveTestRecorderRequest())
        print("Saved test: " + save_test_recorder_response.test_name)
        return save_test_recorder_response.test_name

    def clear_test(self):
        """
        Clears test data.
        """
        self.stub.ClearTestRecorder(fs.ClearTestRecorderRequest())
        print("Test data cleared")

    def get_test_recorder(self) -> fs.TestRecorder:
        """
        Retrieves the test recorder object.

        :return: The test recorder object.
        """
        return self.stub.GetTestRecorder(fs.GetTestRecorderRequest())

    def update_test_recorder(self, test: fs.TestRecorder, mask_fields: list[str]) -> fs.TestRecorder:
        """
        Updates the test recorder with the specified mask fields.

        :param test: The test recorder object to update.
        :param mask_fields: A list of fields to update in the test recorder.
        :return: The updated test recorder object.
        """
        # By following the .proto we see a mask is required to tell the core which
        # fields of the test recorder are being updated.
        # See https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#fieldmask
        output_mask = field_mask.FieldMask()
        output_mask.paths.extend(mask_fields)

        # Create the update request
        update_request = fs.UpdateTestRecorderRequest(test_recorder=test, mask=output_mask)
        return self.stub.UpdateTestRecorder(update_request)

    def get_test(self, test_name: str) -> fs.Test:
        """
        Returns a test's metadata.
        :param test_name:
        :return: Test object
        """
        get_test_request = fs.GetTestRequest(name=test_name)
        return self.stub.GetTest(get_test_request)

    def retrieve_test_data(self, test_name: str, is_continuous_recording: bool = False,
                           continuous_segment_index: int = 0,
                           resample_step_duration: float = 0.0,
                           low_pass_filter_cutoff_hz: float = 0.0,
                           page_size: int = 1000) -> list[fs.SampleGroup]:
        """
        Retrieves the recorded data samples for a test. Specify the test name, and optional parameters. This method
        automatically handles the pagination and only returns once all the requested samples have been retrieved. Keep
        in mind Python will crash if attempting to retrieve too much data, such as high sample rate long duration
        tests. Use the resample_step_duration parameter to reduce the amount of data.

        :param page_size: The number of samples to retrieve per page. Default is 1000. If you encounter an EOF error, try lowering this value.
        :param low_pass_filter_cutoff_hz: Specify a low pass filter on the data. Leave 0 to have no filter.
        :param resample_step_duration: If getting data from continuous recording, a resample time resolution can be
            specified to reduce the amount of data to work with. For example a step duration of 1 second will return an
            interpolated Sample for every second.
        :param continuous_segment_index: The index of the continuous segment from which to get the data from. Zero
            based.
        :param is_continuous_recording: True if data to be returned is from continuous recording. False for manual
            samples.
        :param test_name: Resource name of format /tests/TEST-ID
        :return:
        """
        # The returned data may be split in different chunks as it may exceed the max response size. Read the API
        # documentation for details. The important part is to keep track of the returned token, and use it in the next
        # call in a loop, until the returned token is empty.

        rows = []
        request = fs.ListTestSamplesRequest()
        request.test_name = test_name
        request.continuous_recording = is_continuous_recording
        request.continuous_segment_index = continuous_segment_index
        request.low_pass_filter_cutoff_hz = low_pass_filter_cutoff_hz
        request.page_size = page_size

        # Transform the duration to a google.protobuf.Duration object
        # Calculate the whole number of seconds
        resample_step_duration_seconds = int(resample_step_duration)
        # Calculate the nanoseconds part (1 second = 1_000_000_000 nanosecond)
        resample_step_duration_nanos = int((resample_step_duration - resample_step_duration_seconds) * 1_000_000_000)
        request.resample_step_duration.seconds = resample_step_duration_seconds
        request.resample_step_duration.nanos = resample_step_duration_nanos

        while True:
            try:
                list_test_data_response = self.stub.ListTestData(request)
            except:
                print("Waiting for data...")
                time.sleep(0.1)
                continue

            if len(list_test_data_response.sample_groups) > 0:
                rows.extend(list_test_data_response.sample_groups)
                print("Retrieved " + str(len(list_test_data_response.sample_groups)) + " rows of data")

            # As per API documentation, if the response's token is empty as well as the response's samples, it means the
            # data to be returned is still being prepared, we need to wait.
            if list_test_data_response.next_page_token == "" and len(list_test_data_response.sample_groups) == 0:
                print("... preparing data - progress = " + str(list_test_data_response.progress) + " % ...")
                time.sleep(0.05)
                continue

            if list_test_data_response.next_page_token == "":
                print("Finished loading data for a total of " + str(len(rows)) + " rows")
                return rows

            print("Next page token: " + list_test_data_response.next_page_token)
            request.page_token = list_test_data_response.next_page_token

    def get_input_sample_from_test_data(self, input_msg: fs.Input | fs.InputTransformation,
                                        test_data: list[fs.SampleGroup],
                                        test_data_index: int) -> fs.Sample | None:
        """
        Retrieves the sample associated with the given input or input transformation from a list of test data
        (obtained using the retrieve_test_data method).

        :param test_data_index: which row of the test data to retrieve
        :param test_data: list of test data points, obtained by calling the retrieve_test_data method.
        :param input_msg: The input object to retrieve the sample for.
        :return: The sample at the provided index if available, or None if no sample is found.
        """
        if test_data_index >= len(test_data):
            return None

        for sample in test_data[test_data_index].samples:
            if sample.signal_name == input_msg.signal_name:
                return sample

        return None

    def list_powertrains(self) -> list[Proto.Powertrain] | None:
        """
        Lists all powertrains

        :return: A list of powertrain objects.
        """
        try:
            return self.stub.ListPowertrains(fs.ListPowertrainsRequest()).powertrains
        except grpc.RpcError as rpc_error:
            print(f"Received error while calling ListPowertrains: {rpc_error.details()}")
            return None

    def update_powertrain(self, powertrain: fs.Powertrain, mask_fields: list[str]) -> fs.Powertrain:
        """
        Updates the powertrain with the specified mask fields.

        :param powertrain: The powertrain object to update.
        :param mask_fields: A list of fields to update in the powertrain.
        :return: The updated powertrain object.
        """
        # By following the .proto we see a mask is required to tell the core which
        # fields of the powertrain are being updated.
        # See https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#fieldmask
        mask = field_mask.FieldMask()
        mask.paths.extend(mask_fields)

        # Create the update request
        update_request = fs.UpdatePowertrainRequest(powertrain=powertrain, mask=mask)
        return self.stub.UpdatePowertrain(update_request)

    def create_balancing_session(self, params: fs.BalancingSession):
        request = fs.CreateBalancingSessionRequest(balancing_session=params)
        self.stub.CreateBalancingSession(request)

    def execute_balance_run(self, remove_previous_weight: bool, correction_weights: list[fs.BalanceWeight] | None):
        """
        Executes a balance run on the current balancing session. See the .proto for details on using this command.

        :param remove_previous_weight: if the previous weight has been removed or kept
        :param correction_weights: the correction weights that are applied on the rotor for this run
        :return:
        """
        request = fs.ExecuteBalancingRunRequest(remove_previous_weight=remove_previous_weight,
                                                correction_weights=correction_weights)
        self.stub.ExecuteBalancingRun(request)

    def list_balancing_sessions(self) -> fs.ListBalancingSessionsResponse:
        # print("Listing balancing sessions:")
        response = self.stub.ListBalancingSessions(fs.ListBalancingSessionsRequest())
        return response

    def get_balancing_session(self) -> fs.BalancingSession:
        """
        Gets the active balancing session (the last one in the list)
        :return: The balancing session
        """
        sessions = self.list_balancing_sessions().balancing_sessions
        if len(sessions) == 0:
            raise Exception("No balancing session available")
        return sessions[len(sessions)-1]

    def delete_balance_run(self, name: str):
        """
        :param name: name of the session to be deleted
        """
        print("Deleting session: " + name)
        self.stub.DeleteBalancingSession(fs.DeleteBalancingSessionRequest(name=name))

    def list_balance_run_data(self, name: str, run_index: int) -> fs.ListBalanceRunDataResponse:
        """
        :param name: name of the session to get the data from
        :param run_index: the run index of the session to get the data from, zero based.
        """
        return self.stub.ListBalanceRunData(fs.ListBalanceRunDataRequest(name=name, run_index=run_index))

    def update_time_action_sequence(self,sequence: fs.TimedActionSequence, mask_fields: list[str]) -> fs.TimedActionSequence:
        """
        This function is used to append the current time sequence to the previously initialized time sequence. 
        The update time action sequence requires an input of a timed action sequence.

        param sequence: The timed action sequence to be appended to the previously initialized time sequence.
        return: The updated timed action sequence object.
        """
        sequence_mask = field_mask.FieldMask()
        sequence_mask.paths.extend(mask_fields)
        update_time_request = fs.UpdateTimedActionSequenceRequest(timed_action_sequence=sequence, mask=sequence_mask)

        return self.stub.UpdateTimedActionSequence(update_time_request)

    def clear_timed_action_sequence(self):
        """
        Clears any actions that are appeneded to a sequence
        """
        clear_request = fs.ClearTimedActionSequenceRequest()
        
        return self.stub.ClearTimedActionSequence(clear_request)

    def list_cutoff_conditions(self) -> list[fs.CutoffCondition]:
        """
        Returns a list of cutoff conditions available.

        return: A list of cutoff conditions
        """
        list_cutoff_response = self.stub.ListCutoffConditions(fs.ListCutoffConditionsRequest())
        
        return list_cutoff_response.cutoff_conditions

    def update_input_transformation(self, transformation: list[fs.InputTransformation]) -> fs.InputTransformation:
        """
        Update the input transformation with the specified mask fields.

        param transformation: The input transformation object to update.
        return: The updated input transformation
        """
        update_input_transform_request = fs.UpdateInputTransformationsRequest()
        update_input_transform_request.input_transformations.extend(transformation)

        return self.stub.UpdateInputTransformations(update_input_transform_request)

    def flash_firmware(self, board_name = str):
        """
        Flash the firmware of the device with the specified name.

        param board_name: The name of the device to flash.
        """
        flash_request = fs.FlashBoardFirmwareRequest(board_name=board_name)
        self.stub.FlashBoardFirmware(flash_request)

    def get_powertrain(self, powertrain_name: str) -> fs.Powertrain:
        """
        Retrieves a powertrain by its name.

        param powertrain_name: The name of the powertrain to retrieve.
        return: The powertrain object if found, or None if not found.
        """
        try:
            return self.stub.GetPowertrain(fs.GetPowertrainRequest(name=powertrain_name))
        except grpc.RpcError as rpc_error:
            print(f"Received error while calling GetPowertrain: {rpc_error.details()}")
            return None
        
    def get_signal(self, signal_name: str) -> fs.Signal:
        """
        Retrieves a signal by its name.

        param signal_name: The name of the signal to retrieve.
        return: The signal object if found, or None if not found.
        """
        try:
            return self.stub.GetSignal(fs.GetSignalRequest(signal_name=signal_name))
        except grpc.RpcError as rpc_error:
            print(f"Received error while calling GetSignal: {rpc_error.details()}")
            return None
        
    def update_test(self, test: fs.Test, mask_fields: list[str]) -> fs.Test:
        """
        Updates the test with the specified mask fields.

        param test: The test object to update.
        param mask_fields: A list of fields to update in the test.
        return: The updated test object.
        """
        # By following the .proto we see a mask is required to tell the core which
        # fields of the test are being updated.
        # See https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#fieldmask
        test_mask = field_mask.FieldMask()
        test_mask.paths.extend(mask_fields)

        # Create the update request
        update_request = fs.UpdateTestRequest(test=test, mask=test_mask)
        return self.stub.UpdateTest(update_request)