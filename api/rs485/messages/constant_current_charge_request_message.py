# This file is auto-generated from the TOML file
# WARNING: Do not edit manually. Run the script 'generate_message_files.py' to regenerate this file.
# This file is called from "rs485_api.py", you should never need to access it directly
# This file is the API for the constant_current_charge_request message.

from enum import IntEnum
from rs485.messages.message_helpers import real_to_bus_value, bus_to_real_value

class constant_current_charge_request_message_current_range(IntEnum):
    LOW_RANGE = int(0)
    MID_RANGE = int(1)
    HIGH_RANGE = int(2)

class constant_current_charge_request():

    def __get_current_parameters(args, payload):
        current_parameters_dict = {
                "multiplier": 1.0,
                "offset": 0.0,
            }
        if payload["current_range"] == constant_current_charge_request_message_current_range.LOW_RANGE:
            # Get the divisor for LOW_RANGE
            current_parameters_dict["divisor"] = 16128.0
        elif payload["current_range"] == constant_current_charge_request_message_current_range.MID_RANGE:
            # Get the divisor for MID_RANGE
            current_parameters_dict["divisor"] = 2688.0
        elif payload["current_range"] == constant_current_charge_request_message_current_range.HIGH_RANGE:
            # Get the divisor for HIGH_RANGE
            current_parameters_dict["divisor"] = 1344.0
        else:
            # Raise an error if the current range is invalid
            raise ValueError("Invalid current range: {}".format(current_range))
        return current_parameters_dict

    def __get_current_range_enum(self, payload):
        # Get the correct current_range from the payload
        if payload["current"] <= 1.0:
            return constant_current_charge_request_message_current_range.LOW_RANGE
        elif payload["current"] <= 6.0:
            return constant_current_charge_request_message_current_range.MID_RANGE
        elif payload["current"] <= 12.0:
            return constant_current_charge_request_message_current_range.HIGH_RANGE
        else:
            # Raise an error if the current is invalid
            raise ValueError("Invalid current value: {}".format(payload["current"]))

    def pack_message(self, message_bytes, payload):
        # Update any dependent fields 
        payload["current_range"] = self.__get_current_range_enum(payload)
        
        # Get the bus value of any physical values 
        current_bus_value = real_to_bus_value(payload["current"], self.__get_current_parameters(payload))
        
        # Pack the message
        message_bytes[4:8] = current_bus_value.to_bytes(4, byteorder='little', signed=True)
        message_bytes[8] = payload["current_range"]
        
        # Return the packed message bytes
        return(message_bytes)

    def unpack_message(self, message_bytes):
        message_payload = {}
        
        # Unpack the message values from the message bytes
        current_bus_value = int.from_bytes(message_bytes[4:8], byteorder='little', signed=True)
        current_range_bus_value = message_bytes[8]
        
        # Convert the bus values to physical values, enums, etc.
        message_payload['current_range'] = constant_current_charge_request_message_current_range(current_range_bus_value)
        # Convert current which is dependent on current_range 
        message_payload['current'] = bus_to_real_value(current_bus_value, self.__get_current_parameters(message_payload))
        
        # Return the message dictionary
        return(message_payload)

