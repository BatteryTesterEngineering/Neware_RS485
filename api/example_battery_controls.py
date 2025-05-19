# This script demonstrates how to use the middle_machine class to control a battery cycler.

from middle_machine import middle_machine
import time

# Make sure to set the serial device to the correct port for your system
# For example, on Windows it might be 'COM3', on Linux it might be '/dev/ttyUSB0', on Mac it might be '/dev/tty.usbserial-A10Q8NUI'
serial_device = '/dev/ttyUSB0'  # Replace with your serial device!

middle_machine = middle_machine(serial_device=serial_device)

battery_cycler_id = 21
channel_id = 2
constant_current = 2.0
constant_power = 5.0
step_duration_s = 2
read_interval_s = 0.1

def read_and_print(command_type, command_value):
    for i in range(int(step_duration_s/read_interval_s)):
        # Wait for the read interval
        time.sleep(read_interval_s)
        # Read the current and voltage values
        update = middle_machine.request_voltage_and_current(
                                                    battery_cycler_id = battery_cycler_id, 
                                                    channel_id = channel_id)
        
        # Print the current, voltage, and power values
        print(f"{update['timestamp']}, {command_type}, {command_value:.3f}, {update['voltage']:.3f}, {update['current']:.3f}, {update['calculated_power']:.3f}")


# Print a header
print(f"Timestamp, Command, Command Value, Read Voltage (V), Read Current (V), Calculated Power (W)")

# Set the channel to discharge current
middle_machine.request_constant_current_discharge(
                                                battery_cycler_id = battery_cycler_id, 
                                                channel_id = channel_id, 
                                                discharge_current = constant_current)
read_and_print("constant_current_discharge", constant_current)

# Set the channel to rest
middle_machine.request_constant_current_discharge(
                                                battery_cycler_id = battery_cycler_id, 
                                                channel_id = channel_id, 
                                                discharge_current = 0.0)
read_and_print("rest", 0.0)

# Set the channel to charge current
middle_machine.request_constant_current_charge(
                                                battery_cycler_id = battery_cycler_id, 
                                                channel_id = channel_id, 
                                                charge_current = constant_current)
read_and_print("constant_current_charge", constant_current)


# Set the channel to rest
middle_machine.request_constant_current_discharge(
                                                battery_cycler_id = battery_cycler_id, 
                                                channel_id = channel_id, 
                                                discharge_current = 0.0)
read_and_print("rest", 0.0)

# Set the channel to discharge power
middle_machine.request_constant_power_discharge(
                                                battery_cycler_id = battery_cycler_id, 
                                                channel_id = channel_id, 
                                                discharge_power = constant_power)

read_and_print("constant_power_discharge", constant_power)

# Set the channel to rest
middle_machine.request_constant_current_discharge(
                                                battery_cycler_id = battery_cycler_id, 
                                                channel_id = channel_id, 
                                                discharge_current = 0.0)
read_and_print("rest", 0.0)

# Set the channel to charge power
middle_machine.request_constant_power_charge(
                                                battery_cycler_id = battery_cycler_id, 
                                                channel_id = channel_id, 
                                                charge_power = constant_power)

read_and_print("constant_power_charge", constant_power)

# Set the channel to rest
middle_machine.request_constant_current_discharge(
                                                battery_cycler_id = battery_cycler_id, 
                                                channel_id = channel_id, 
                                                discharge_current = 0.0)
read_and_print("rest", 0.0)

# Set the channel to end the test
middle_machine.request_end_of_test(
                                                battery_cycler_id = battery_cycler_id, 
                                                channel_id = channel_id)
read_and_print("end_of_test", 0.0)


# Close the connection to the battery cycler
middle_machine.close()
