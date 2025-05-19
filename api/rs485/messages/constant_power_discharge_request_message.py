# This file is auto-generated from the TOML file
# WARNING: Do not edit manually. Run the script 'generate_message_files.py' to regenerate this file.
# This file is called from "rs485_api.py", you should never need to access it directly
# This file is the API for the constant_power_discharge_request message.

from enum import IntEnum
from rs485.messages.message_helpers import real_to_bus_value, bus_to_real_value

class constant_power_discharge_request_message_power_range(IntEnum):
    LOW_RANGE = int(0)
    MID_RANGE = int(1)
    HIGH_RANGE = int(2)

class constant_power_discharge_request():

    def __get_power_parameters(args, payload):
        power_parameters_dict = {
                "multiplier": 1.0,
                "offset": 0.0,
            }
        if payload["power_range"] == constant_power_discharge_request_message_power_range.LOW_RANGE:
            # Get the divisor for LOW_RANGE
            power_parameters_dict["divisor"] = 1.0
        elif payload["power_range"] == constant_power_discharge_request_message_power_range.MID_RANGE:
            # Get the divisor for MID_RANGE
            power_parameters_dict["divisor"] = 1.0
        elif payload["power_range"] == constant_power_discharge_request_message_power_range.HIGH_RANGE:
            # Get the divisor for HIGH_RANGE
            power_parameters_dict["divisor"] = 268.8
        else:
            # Raise an error if the power range is invalid
            raise ValueError("Invalid power range: {}".format(power_range))
        return power_parameters_dict

    def __get_power_range_enum(self, payload):
        # Get the correct power_range from the payload
        if payload["power"] <= 0.0:
            return constant_power_discharge_request_message_power_range.LOW_RANGE
        elif payload["power"] <= 0.0:
            return constant_power_discharge_request_message_power_range.MID_RANGE
        elif payload["power"] <= 60.0:
            return constant_power_discharge_request_message_power_range.HIGH_RANGE
        else:
            # Raise an error if the power is invalid
            raise ValueError("Invalid power value: {}".format(payload["power"]))

    def pack_message(self, message_bytes, payload):
        # Update any dependent fields 
        payload["power_range"] = self.__get_power_range_enum(payload)
        
        # Get the bus value of any physical values 
        power_bus_value = real_to_bus_value(payload["power"], self.__get_power_parameters(payload))
        
        # Pack the message
        message_bytes[4:8] = power_bus_value.to_bytes(4, byteorder='little', signed=True)
        message_bytes[12] = payload["power_range"]
        
        # Return the packed message bytes
        return(message_bytes)

    def unpack_message(self, message_bytes):
        message_payload = {}
        
        # Unpack the message values from the message bytes
        power_bus_value = int.from_bytes(message_bytes[4:8], byteorder='little', signed=True)
        power_range_bus_value = message_bytes[12]
        
        # Convert the bus values to physical values, enums, etc.
        message_payload['power_range'] = constant_power_discharge_request_message_power_range(power_range_bus_value)
        # Convert power which is dependent on power_range 
        message_payload['power'] = bus_to_real_value(power_bus_value, self.__get_power_parameters(message_payload))
        
        # Return the message dictionary
        return(message_payload)

