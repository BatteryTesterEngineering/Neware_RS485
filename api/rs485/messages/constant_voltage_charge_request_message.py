# This file is auto-generated from the TOML file
# WARNING: Do not edit manually. Run the script 'generate_message_files.py' to regenerate this file.
# This file is called from "rs485_api.py", you should never need to access it directly
# This file is the API for the constant_voltage_charge_request message.

from enum import IntEnum
from rs485.messages.message_helpers import real_to_bus_value, bus_to_real_value

class constant_voltage_charge_request():

    def __get_voltage_parameters(args, payload):
        voltage_parameters_dict = {
                "multiplier": 1.0,
                "divisor": 3225.6,
                "offset": 0.0,
            }
        return voltage_parameters_dict

    def pack_message(self, message_bytes, payload):
        # Get the bus value of any physical values 
        voltage_bus_value = real_to_bus_value(payload["voltage"], self.__get_voltage_parameters(payload))
        
        # Pack the message
        message_bytes[4:8] = voltage_bus_value.to_bytes(4, byteorder='little', signed=True)
        
        # Return the packed message bytes
        return(message_bytes)

    def unpack_message(self, message_bytes):
        message_payload = {}
        
        # Unpack the message values from the message bytes
        voltage_bus_value = int.from_bytes(message_bytes[4:8], byteorder='little', signed=True)
        
        # Convert the bus values to physical values, enums, etc.
        message_payload['voltage'] = bus_to_real_value(voltage_bus_value, self.__get_voltage_parameters(message_payload))
        
        # Return the message dictionary
        return(message_payload)

