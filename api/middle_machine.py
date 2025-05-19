# This file is the API for the purpose of emulating the behavior of a middle machine

# Longterm TODO: Update the autogenerator to produce this file

from datetime import datetime
import serial
from rs485 import rs485_api

class middle_machine():

    # Defaults to using the first USB serial device if none is specified
    def __init__(self, serial_device = '/dev/ttyUSB0'):

        self.rs485_uart_parameters = {
            'baudrate': 3000000,
            'bytesize': 8,
            'parity': "N",
            'stopbits': 1,
            'message_length': 36,
        }

        self.serial_device = serial_device
        self.serial = serial.Serial(port = serial_device,
                                    baudrate = self.rs485_uart_parameters["baudrate"],
                                    bytesize = self.rs485_uart_parameters["bytesize"], 
                                    parity = self.rs485_uart_parameters["parity"], 
                                    stopbits = self.rs485_uart_parameters["stopbits"])

    def __del__(self):
        """
        Close the serial connection.
        """
        self.serial.close()
    
    def __request_and_receive(self, message_bytes) -> dict:
        """
        Transmit a request to a battery cycler channel and gather the response.
        Args:
            message_bytes (bytes): The bytes to transmit.
        Returns:
            dict: A dictionary containing the response data.
        """
        self.serial.write(message_bytes)
        # Get the present time from the system clock
        now = datetime.now()
        # Read the response from the serial port
        response_bytes = self.serial.read(self.rs485_uart_parameters["message_length"])
        # Unpack the response message
        response_dict = rs485_api.unpack_message(response_bytes)
        # Add the time to the response message
        response_dict["timestamp"] = now

        return response_dict
    
    def close(self):
        """
        Call the destructor to close the serial connection.
        """
        self.__del__()

    def request_voltage_and_current(self, battery_cycler_id, channel_id) -> dict:
        """
        Transmit a request to a battery cycler channel for voltage and current data.
        Gather the response and return it.
        Args:
            battery_cycler_id (int): The ID of the battery cycler.
            channel_id (int): The ID of the channel on the battery cycler.
        Returns:
            dict: A dictionary containing the time, voltage, current, and calculated power data.
        """
        transmit_bytes = rs485_api.pack_message(machine_id = battery_cycler_id, 
                                                channel_id = channel_id,
                                                message_type_id = rs485_api.message_type_id.VOLTAGE_AND_CURRENT_REQUEST,
                                                payload = {}
                                                )
        response_dict = self.__request_and_receive(transmit_bytes)
        
        # Check if the response is the correct acknowledge message
        if response_dict["message_type_id"] == rs485_api.message_type_id.VOLTAGE_AND_CURRENT_ACKNOWLEDGE:
            # Add calculated power to the response message
            response_dict["calculated_power"] = response_dict["voltage"] * response_dict["current"]
            # Return the unpacked message
            return response_dict
        else:
            raise ValueError("Invalid or unexpected response message type ID: {}".format(response_dict["message_type_id"]))

    def request_constant_current_discharge(self, battery_cycler_id, channel_id, discharge_current) -> dict:
        """
        Transmit a request to a battery cycler channel for a constant current discharge at a particular current.
        Gather the response and return it.
        Args:
            battery_cycler_id (int): The ID of the battery cycler.
            channel_id (int): The ID of the channel on the battery cycler.
            discharge_current (float): The current to discharge at.
        Returns:
            dict: A dictionary containing the response data.
        """
        transmit_bytes = rs485_api.pack_message(machine_id = battery_cycler_id, 
                                                channel_id = channel_id,
                                                message_type_id = rs485_api.message_type_id.CONSTANT_CURRENT_DISCHARGE_REQUEST,
                                                payload = {'current': discharge_current}
                                                )
        response_dict = self.__request_and_receive(transmit_bytes)
        
        # Check if the response is the correct acknowledge message
        if response_dict["message_type_id"] == rs485_api.message_type_id.CONSTANT_CURRENT_DISCHARGE_ACKNOWLEDGE:
            # Return the unpacked message
            return response_dict
        else:
            raise ValueError("Invalid or unexpected response message type ID: {}".format(response_dict["message_type_id"]))

    def request_constant_current_charge(self, battery_cycler_id, channel_id, charge_current) -> dict:
        """
        Transmit a request to a battery cycler channel for a constant current charge at a particular current.
        Gather the response and return it.
        Args:
            battery_cycler_id (int): The ID of the battery cycler.
            channel_id (int): The ID of the channel on the battery cycler.
            charge_current (float): The current to charge at.
        Returns:
            dict: A dictionary containing the response data.
        """
        transmit_bytes = rs485_api.pack_message(machine_id = battery_cycler_id, 
                                                channel_id = channel_id,
                                                message_type_id = rs485_api.message_type_id.CONSTANT_CURRENT_CHARGE_REQUEST,
                                                payload = {'current': charge_current}
                                                )
        response_dict = self.__request_and_receive(transmit_bytes)
        
        # Check if the response is the correct acknowledge message
        if response_dict["message_type_id"] == rs485_api.message_type_id.CONSTANT_CURRENT_CHARGE_ACKNOWLEDGE:
            # Return the unpacked message
            return response_dict
        else:
            raise ValueError("Invalid or unexpected response message type ID: {}".format(response_dict["message_type_id"]))

    def request_constant_power_discharge(self, battery_cycler_id, channel_id, discharge_power) -> dict:
        """
        Transmit a request to a battery cycler channel for a constant power discharge at a particular power.
        Gather the response and return it.
        Args:
            battery_cycler_id (int): The ID of the battery cycler.
            channel_id (int): The ID of the channel on the battery cycler.
            discharge_power (float): The power to discharge at.
        Returns:
            dict: A dictionary containing the response data.
        """
        transmit_bytes = rs485_api.pack_message(machine_id = battery_cycler_id, 
                                                channel_id = channel_id,
                                                message_type_id = rs485_api.message_type_id.CONSTANT_POWER_DISCHARGE_REQUEST,
                                                payload = {'power': discharge_power}
                                                )
        response_dict = self.__request_and_receive(transmit_bytes)
        
        # Check if the response is the correct acknowledge message
        if response_dict["message_type_id"] == rs485_api.message_type_id.CONSTANT_POWER_DISCHARGE_ACKNOWLEDGE:
            # Return the unpacked message
            return response_dict
        else:
            raise ValueError("Invalid or unexpected response message type ID: {}".format(response_dict["message_type_id"]))

    def request_constant_power_charge(self, battery_cycler_id, channel_id, charge_power) -> dict:
        """
        Transmit a request to a battery cycler channel for a constant power charge at a particular power.
        Gather the response and return it.
        Args:
            battery_cycler_id (int): The ID of the battery cycler.
            channel_id (int): The ID of the channel on the battery cycler.
            charge_power (float): The power to charge at.
        Returns:
            dict: A dictionary containing the response data.
        """
        transmit_bytes = rs485_api.pack_message(machine_id = battery_cycler_id, 
                                                channel_id = channel_id,
                                                message_type_id = rs485_api.message_type_id.CONSTANT_POWER_CHARGE_REQUEST,
                                                payload = {'power': charge_power}
                                                )
        response_dict = self.__request_and_receive(transmit_bytes)
        
        # Check if the response is the correct acknowledge message
        if response_dict["message_type_id"] == rs485_api.message_type_id.CONSTANT_POWER_CHARGE_ACKNOWLEDGE:
            # Return the unpacked message
            return response_dict
        else:
            raise ValueError("Invalid or unexpected response message type ID: {}".format(response_dict["message_type_id"]))

    def request_end_of_test(self, battery_cycler_id, channel_id) -> dict:
        """
        Transmit a request to a battery cycler channel to end the test.
        Gather the response and return it.
        Args:
            battery_cycler_id (int): The ID of the battery cycler.
            channel_id (int): The ID of the channel on the battery cycler.
        Returns:
            dict: A dictionary containing the response data.
        """
        transmit_bytes = rs485_api.pack_message(machine_id = battery_cycler_id, 
                                                channel_id = channel_id,
                                                message_type_id = rs485_api.message_type_id.END_OF_TEST_REQUEST,
                                                payload = {}
                                                )
        response_dict = self.__request_and_receive(transmit_bytes)
        
        # Check if the response is the correct acknowledge message
        if response_dict["message_type_id"] == rs485_api.message_type_id.END_OF_TEST_ACKNOWLEDGE:
            # Return the unpacked message
            return response_dict
        else:
            raise ValueError("Invalid or unexpected response message type ID: {}".format(response_dict["message_type_id"]))