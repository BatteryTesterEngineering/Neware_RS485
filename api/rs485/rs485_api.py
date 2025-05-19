# This file is auto-generated from the TOML file
# WARNING: Do not edit manually. Run the script 'generate_message_files.py' to regenerate this file.
# This file is the API for the Neware RS485 protocol.

from enum import IntEnum

from rs485.messages.message_helpers import calc_Crc8MaximDow, real_to_bus_value, bus_to_real_value

from rs485.messages.constant_voltage_charge_request_message import constant_voltage_charge_request
from rs485.messages.constant_voltage_charge_acknowledge_message import constant_voltage_charge_acknowledge
from rs485.messages.constant_voltage_discharge_request_message import constant_voltage_discharge_request
from rs485.messages.constant_voltage_discharge_acknowledge_message import constant_voltage_discharge_acknowledge
from rs485.messages.constant_current_charge_request_message import constant_current_charge_request
from rs485.messages.constant_current_charge_acknowledge_message import constant_current_charge_acknowledge
from rs485.messages.constant_current_discharge_request_message import constant_current_discharge_request
from rs485.messages.constant_current_discharge_acknowledge_message import constant_current_discharge_acknowledge
from rs485.messages.constant_power_discharge_request_message import constant_power_discharge_request
from rs485.messages.constant_power_discharge_acknowledge_message import constant_power_discharge_acknowledge
from rs485.messages.voltage_and_current_request_message import voltage_and_current_request
from rs485.messages.voltage_and_current_acknowledge_message import voltage_and_current_acknowledge
from rs485.messages.end_of_test_request_message import end_of_test_request
from rs485.messages.end_of_test_acknowledge_message import end_of_test_acknowledge
from rs485.messages.constant_power_charge_request_message import constant_power_charge_request
from rs485.messages.constant_power_charge_acknowledge_message import constant_power_charge_acknowledge

# ----------------- Common Message Properties -------------------------
class message_type_id(IntEnum):
    CONSTANT_VOLTAGE_CHARGE_REQUEST = int(0x17)
    CONSTANT_VOLTAGE_CHARGE_ACKNOWLEDGE = int(0x97)
    CONSTANT_VOLTAGE_DISCHARGE_REQUEST = int(0x18)
    CONSTANT_VOLTAGE_DISCHARGE_ACKNOWLEDGE = int(0x98)
    CONSTANT_CURRENT_CHARGE_REQUEST = int(0x1a)
    CONSTANT_CURRENT_CHARGE_ACKNOWLEDGE = int(0x9a)
    CONSTANT_CURRENT_DISCHARGE_REQUEST = int(0x1b)
    CONSTANT_CURRENT_DISCHARGE_ACKNOWLEDGE = int(0x9b)
    CONSTANT_POWER_DISCHARGE_REQUEST = int(0x1c)
    CONSTANT_POWER_DISCHARGE_ACKNOWLEDGE = int(0x9c)
    VOLTAGE_AND_CURRENT_REQUEST = int(0x1f)
    VOLTAGE_AND_CURRENT_ACKNOWLEDGE = int(0x9f)
    END_OF_TEST_REQUEST = int(0x25)
    END_OF_TEST_ACKNOWLEDGE = int(0xa5)
    CONSTANT_POWER_CHARGE_REQUEST = int(0x31)
    CONSTANT_POWER_CHARGE_ACKNOWLEDGE = int(0xb1)

# Message Type Specific Class Mapping
__message_type_id_class_map = {
    message_type_id.CONSTANT_VOLTAGE_CHARGE_REQUEST: constant_voltage_charge_request,
    message_type_id.CONSTANT_VOLTAGE_CHARGE_ACKNOWLEDGE: constant_voltage_charge_acknowledge,
    message_type_id.CONSTANT_VOLTAGE_DISCHARGE_REQUEST: constant_voltage_discharge_request,
    message_type_id.CONSTANT_VOLTAGE_DISCHARGE_ACKNOWLEDGE: constant_voltage_discharge_acknowledge,
    message_type_id.CONSTANT_CURRENT_CHARGE_REQUEST: constant_current_charge_request,
    message_type_id.CONSTANT_CURRENT_CHARGE_ACKNOWLEDGE: constant_current_charge_acknowledge,
    message_type_id.CONSTANT_CURRENT_DISCHARGE_REQUEST: constant_current_discharge_request,
    message_type_id.CONSTANT_CURRENT_DISCHARGE_ACKNOWLEDGE: constant_current_discharge_acknowledge,
    message_type_id.CONSTANT_POWER_DISCHARGE_REQUEST: constant_power_discharge_request,
    message_type_id.CONSTANT_POWER_DISCHARGE_ACKNOWLEDGE: constant_power_discharge_acknowledge,
    message_type_id.VOLTAGE_AND_CURRENT_REQUEST: voltage_and_current_request,
    message_type_id.VOLTAGE_AND_CURRENT_ACKNOWLEDGE: voltage_and_current_acknowledge,
    message_type_id.END_OF_TEST_REQUEST: end_of_test_request,
    message_type_id.END_OF_TEST_ACKNOWLEDGE: end_of_test_acknowledge,
    message_type_id.CONSTANT_POWER_CHARGE_REQUEST: constant_power_charge_request,
    message_type_id.CONSTANT_POWER_CHARGE_ACKNOWLEDGE: constant_power_charge_acknowledge,
}

# Parameter dictionaries for any bus values that need to be mapped to a real value
__machine_id_parameters_dict = {
    "multiplier": 1.0,
    "divisor": 1.0,
    "offset": 1.0,
}
__channel_id_parameters_dict = {
    "multiplier": 1.0,
    "divisor": 1.0,
    "offset": 1.0,
}
# ---------------- /Common Message Properties -------------------------

# ----------------- Common Message Functions -------------------------
def unpack_message(message_bytes):
    message_dict = {}
    
    # Unpack the message values from the message bytes
    message_dict["machine_id"] = int(bus_to_real_value(message_bytes[0], __machine_id_parameters_dict))
    message_dict["channel_id"] = int(bus_to_real_value(message_bytes[1], __channel_id_parameters_dict))
    message_dict["message_type_id"] = message_type_id(message_bytes[2])
    received_crc = message_bytes[3]
    
    # Calculate the CRC based on the message bytes with CRC byte set to 0
    # This is done by creating a copy of the message bytes and setting the CRC byte to 0
    message_bytes_copy = bytearray(message_bytes)
    message_bytes_copy[3] = 0x00
    calculated_crc = calc_Crc8MaximDow(message_bytes_copy)
    # Check if the calculated CRC matches the received CRC
    if calculated_crc != received_crc:
        raise ValueError("CRC mismatch: expected {}, got {}".format(calculated_crc, received_crc))
    
    # Check the message type ID and call the appropriate message unpack function
    try:
        message_dict.update(__message_type_id_class_map[message_dict["message_type_id"]]().unpack_message(message_bytes))
    except KeyError:
        raise ValueError("Invalid message type ID: {}".format(message_dict["message_type_id"]))

    return message_dict
    
    
def pack_message(machine_id, channel_id, message_type_id, payload = {}):
    # Initialize the byte array and message parameters
    message_bytes = bytearray([0x00] * 36)
    # Pack the message
    message_bytes[0] = int(real_to_bus_value(machine_id, __machine_id_parameters_dict))
    message_bytes[1] = int(real_to_bus_value(channel_id, __channel_id_parameters_dict))
    message_bytes[2] = message_type_id
    
    # Check the message type ID and call the appropriate pack message function
    try:
        message_bytes = __message_type_id_class_map[message_type_id]().pack_message(message_bytes, payload)
    except KeyError:
        raise ValueError("Invalid message type ID: {}".format(message_type_id))
    
    # Calculate the CRC based on the message bytes with CRC byte set to 0
    crc = calc_Crc8MaximDow(message_bytes)
    # Insert the CRC byte into the message
    message_bytes[3] = crc
    
    return(message_bytes)
# ---------------- /Common Message Functions -------------------------

