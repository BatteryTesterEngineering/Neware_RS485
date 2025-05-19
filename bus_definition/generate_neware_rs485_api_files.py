import toml
import os

physical_value_parameters = ["multiplier", "divisor", "offset"]

def generate_message_files(toml_file_path, output_directory, specific_message_id_subdirectory):
    """
    Reads a TOML file defining message structures and generates corresponding Python files,
    including rs485_api.py.

    Args:
        toml_file_path (str): Path to the TOML file.
        output_directory (str): Directory where the Python files will be created.
    """

    with open(toml_file_path, 'r') as f:
        data = toml.load(f)

    # Create the output directories if they doesn't exist
    specific_message_id_directory = os.path.join(output_directory, specific_message_id_subdirectory)
    init_py_file = os.path.join(output_directory, '__init__.py')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        init_py_file = os.path.join(output_directory, '__init__.py')
        open(init_py_file, 'a').close()
    if not os.path.exists(specific_message_id_directory):
        os.makedirs(specific_message_id_directory)
        init_py_file = os.path.join(specific_message_id_directory, '__init__.py')
        open(init_py_file, 'a').close()
    
    # Generate individual message files
    for message_name, message_data in data['messages'].items():
        generate_message_file(message_name, message_data, specific_message_id_directory)

    # Generate rs485_api.py
    generate_common_messages_file(data, output_directory)

def generate_enums(base_indent, module_name, message_data):
    # Generate IntEnum classes for enums
    return_string = ""
    if 'payload' in message_data:
        for field_name, field_data in message_data['payload'].items():
            if field_data.get('value_type') == 'enum':
                enum_name = f"{module_name}_{field_name}"
                return_string += base_indent + f"class {enum_name}(IntEnum):\n"

                for enum_key, enum_value in field_data['enum_bus_mapping'].items():
                    enum_key = enum_key.replace(" ", "_").upper()
                    return_string += base_indent + f"    {enum_key} = int({enum_value})\n"
                return_string += base_indent + "\n"
    return return_string

def generate_helper_functions(base_indent, module_name, message_data):
    return_string = ""
    if 'payload' in message_data:
        for field_name, field_data in message_data['payload'].items():
            # Generate helper functions for physical value conversions
            if field_data.get('value_type') == 'physical_value':

                return_string += base_indent + f"def __get_{field_name}_parameters(args, payload):\n"

                # Generate the parameters dictionary
                return_string += base_indent + f"    {field_name}_parameters_dict = {{\n"
                # If the field is a float, then that means that we can use it directly
                for parameter in physical_value_parameters:
                    if isinstance(field_data.get(parameter), float):
                        return_string += base_indent + f"            \"{parameter}\": {field_data.get(parameter)},\n"
                return_string += base_indent + f"        }}\n"
                #  / Generate the parameters dictionary

                # If the field is a string, then that means we need to use conditionals to map it to a value that is stored in an enum with the name given
                for parameter in physical_value_parameters:
                    if isinstance(field_data.get(parameter), str):
                        field_data_selector = field_data.get(parameter)
                        conditional = "if"
                        for value_map_name, value_map_value in message_data["payload"][field_data_selector].get('enum_value_mapping').items():
                            value_map_name = value_map_name.replace(" ", "_").upper()
                            return_string += base_indent + f"    {conditional} payload[\"{field_name}_range\"] == {module_name}_{field_name}_range.{value_map_name}:\n"
                            return_string += base_indent + f"        # Get the {parameter} for {value_map_name}\n"
                            return_string += base_indent + f"        {field_name}_parameters_dict[\"{parameter}\"] = {value_map_value}\n"
                            conditional = "elif"
                        return_string += base_indent + f"    else:\n"
                        return_string += base_indent + f"        # Raise an error if the {field_name} range is invalid\n"
                        return_string += base_indent + f"        raise ValueError(\"Invalid {field_name} range: {{}}\".format({field_name}_range))\n"
                # / mapping function
                return_string += base_indent + f"    return {field_name}_parameters_dict\n\n"

            # Generate helper functions for mapping physical values to bus values when the parameters are variable
            elif field_data.get('value_type') == 'enum':
                if "enum_physical_bounds_mapping" in field_data.keys():
                    mapping_dict = field_data["enum_physical_bounds_mapping"]
                    enum_name = f"{module_name}_{field_name}"
                    value_name = field_name.replace('_range', '')
                    return_string += base_indent + f"def __get_{field_name}_enum(self, payload):\n"
                    return_string += base_indent + f"    # Get the correct {field_name} from the payload\n"
                    conditional = "if"
                    for name, value in mapping_dict.items():
                        name = name.replace(" ", "_").upper()
                        return_string += base_indent + f"    {conditional} payload[\"{value_name}\"] <= {value}:\n"
                        return_string += base_indent + f"        return {enum_name}.{name}\n"
                        conditional = "elif"
                    return_string += base_indent + f"    else:\n"
                    return_string += base_indent + f"        # Raise an error if the {value_name} is invalid\n"
                    return_string += base_indent + f"        raise ValueError(\"Invalid {value_name} value: {{}}\".format(payload[\"{value_name}\"]))\n\n"
    return return_string


def generate_pack_message_function(base_indent, message_data, dependent_fields):
    return_string = ""
    # Create the function definition
    return_string  += base_indent + "def pack_message(self, message_bytes, payload):\n"
    
    # First, we have to update any dependent fields, like the current range, channel status, etc.
    if dependent_fields:
        return_string  += base_indent + f"    # Update any dependent fields \n"
        for dependency, item in dependent_fields.items():
            return_string  += base_indent + f"    payload[\"{item}\"] = self.__get_{item}_enum(payload)\n"
        return_string  += base_indent + f"    \n"

    # Second, we have to get the bus value for any physical values
    if message_data['payload']:
        return_string  += base_indent + f"    # Get the bus value of any physical values \n"
        for field_name, field_data in message_data['payload'].items():
            # If the field is a physical value, then we need to convert it to a bus value
            if field_data.get('value_type') == 'physical_value':
                return_string  += base_indent + f"    {field_name}_bus_value = real_to_bus_value(payload[\"{field_name}\"], self.__get_{field_name}_parameters(payload))\n"
        return_string  += base_indent + f"    \n"

    # Third, we have to pack all of the message values into their proper byte positions
    if message_data['payload']:
        return_string  += base_indent + f"    # Pack the message\n"
        for field_name, field_data in message_data['payload'].items():
            # Grab some properties of the field
            first_byte = int(field_data.get('first_byte'))
            last_byte = int(field_data.get('last_byte')) + 1
            length = last_byte - first_byte
            byte_order = field_data.get('byte_order')
            if field_data.get('data_type')[0] == "u":
                signed = False
            elif field_data.get('data_type')[0] == "i":
                signed = True

            # If the field is a physical value, then we need to pack it's converted bus value
            if field_data.get('value_type') == 'physical_value':
                variable_to_pack = f"{field_name}_bus_value"
            else:
                variable_to_pack = f"payload[\"{field_name}\"]"

            # Pack the message bytes, noticing that it is different if there are multiple bytes to be packed
            if length == 1: 
                return_string  += base_indent + f"    message_bytes[{first_byte}] = {variable_to_pack}\n"
            else:
                return_string  += base_indent + f"    message_bytes[{first_byte}:{last_byte}] = {variable_to_pack}.to_bytes({length}, byteorder='{byte_order}', signed={signed})\n"

    # Done!
    return_string += base_indent + "    \n"
    return_string += base_indent + "    # Return the packed message bytes\n"
    return_string += base_indent + "    return(message_bytes)\n\n"
    return return_string



def generate_unpack_message_function(base_indent, module_name, message_data, dependent_fields):
    return_string = ""
    # Create the function definition
    return_string += base_indent + "def unpack_message(self, message_bytes):\n"
    return_string += base_indent + "    message_payload = {}\n"
    
    # Unpack the message values from the message bytes
    if message_data['payload']:
        return_string += base_indent + f"    \n"
        return_string += base_indent + f"    # Unpack the message values from the message bytes\n"
        for field_name, field_data in message_data['payload'].items():
            # Grab some properties of the field
            first_byte = int(field_data.get('first_byte'))
            last_byte = int(field_data.get('last_byte')) + 1
            length = last_byte - first_byte
            byte_order = field_data.get('byte_order')
            if field_data.get('data_type')[0] == "u":
                signed = False
            elif field_data.get('data_type')[0] == "i":
                signed = True

            # Set the variable that we want to unpack into.
            variable_name = f"{field_name}_bus_value"

            # Unpack based on the length of the field
            if length == 1:
                return_string += base_indent + f"    {variable_name} = message_bytes[{first_byte}]\n"
            else:
                return_string += base_indent + f"    {variable_name} = int.from_bytes(message_bytes[{first_byte}:{last_byte}], byteorder='{byte_order}', signed={signed})\n"

    if message_data['payload']:
        return_string += base_indent + f"    \n"
        return_string += base_indent + f"    # Convert the bus values to physical values, enums, etc.\n"
        for field_name, field_data in message_data['payload'].items():
            # If a field is not dependent on another field, then we can unpack it
            if field_name not in dependent_fields:
                # Set the variable that our value was unpacked into
                variable_name = f"{field_name}_bus_value"
                if field_data.get('value_type') == 'physical_value':
                    return_string += base_indent + f"    message_payload['{field_name}'] = bus_to_real_value({variable_name}, self.__get_{field_name}_parameters(message_payload))\n"
                elif field_data.get('value_type') == 'enum':
                    enum_name = f"{module_name}_{field_name}"
                    return_string += base_indent + f"    message_payload['{field_name}'] = {enum_name}({variable_name})\n"
        
        for field_name, field_data in message_data['payload'].items():
            # If a field is dependent on another field, then we can unpack it now
            if field_name in dependent_fields:
                # Set the variable that our value was unpacked into
                return_string += base_indent + f"    # Convert {field_name} which is dependent on {dependent_fields[field_name]} \n"
                variable_name = f"{field_name}_bus_value"
                if field_data.get('value_type') == 'physical_value':
                    return_string += base_indent + f"    message_payload['{field_name}'] = bus_to_real_value({variable_name}, self.__get_{field_name}_parameters(message_payload))\n"
                elif field_data.get('value_type') == 'enum':
                    enum_name = f"{module_name}_{field_name}"
                    return_string += base_indent + f"    message_payload['{field_name}'] = {enum_name}({variable_name})\n"



    return_string += base_indent + "    \n"
    return_string += base_indent + "    # Return the message dictionary\n"
    return_string += base_indent + "    return(message_payload)\n\n"
    return(return_string)

def generate_message_file(message_name, message_data, output_directory):
    """Generates a single message file."""
    module_name = (message_name + '_message').lower().replace(" ", "_")
    class_name = message_name.lower().replace(" ", "_")
    file_name = os.path.join(output_directory, f"{module_name}.py")

    with open(file_name, 'w') as f:
        f.write(f"# This file is auto-generated from the TOML file\n")
        f.write(f"# WARNING: Do not edit manually. Run the script 'generate_message_files.py' to regenerate this file.\n")
        f.write(f"# This file is called from \"rs485_api.py\", you should never need to access it directly\n")
        f.write(f"# This file is the API for the {message_name} message.\n")
        f.write(f"\n")

        f.write(f"from enum import IntEnum\n")
        f.write(f"from rs485.messages.message_helpers import real_to_bus_value, bus_to_real_value\n\n")

        # Generate IntEnum classes for enums
        base_indent = ""
        f.write(generate_enums(base_indent, module_name, message_data))

        # Generate the main message class
        f.write(f"class {class_name}():\n\n")
        base_indent = "    "

        # Generate helper functions for all of the payload fields
        f.write(generate_helper_functions(base_indent, module_name, message_data))

        # Generate the dependent fields
        dependent_fields = {}
        if 'payload' in message_data:
            for field_name, field_data in message_data['payload'].items():
                for parameter in physical_value_parameters:
                    if isinstance(field_data.get(parameter), str):
                        dependent_fields[field_name] = field_data.get(parameter)

        # Generate the pack_message function
        f.write(generate_pack_message_function(base_indent, message_data, dependent_fields))
        
        # Generate unpack_message function
        f.write(generate_unpack_message_function(base_indent, module_name, message_data, dependent_fields))

def generate_common_message_properties(base_indent, data):
    # Generate common message properties
    return_string = ""
    return_string += base_indent + "# ----------------- Common Message Properties -------------------------\n"

    # Generate message_type_id enum
    return_string += base_indent + "class message_type_id(IntEnum):\n"
    for message_name, message_data in data['messages'].items():
        message_type_id = message_data['message_type_id']
        enum_name = message_name.upper().replace(" ", "_")
        return_string += base_indent + f"    {enum_name} = int({hex(message_type_id)})\n"
    return_string += base_indent + "\n"

    # Map the message_type_id to the appropriate message class
    return_string += base_indent + "# Message Type Specific Class Mapping\n"
    return_string += base_indent + "__message_type_id_class_map = {\n"
    for message_name, message_data in data['messages'].items():
        message_type_id = message_data['message_type_id']
        module_name = (message_name + '_message').lower().replace(" ", "_")
        class_name = message_name.lower().replace(" ", "_")
        return_string += base_indent + f"    message_type_id.{message_name.upper()}: {class_name},\n"
    return_string += base_indent + "}\n"

    # Generate the parameters dictionary if necessary
    return_string += base_indent + "\n"
    return_string += base_indent + "# Parameter dictionaries for any bus values that need to be mapped to a real value\n"
    for field_name, field_data in data['common_message_fields'].items():
        if ("multiplier" in field_data) or ("divisor" in field_data) or ("offset" in field_data): 
            # Generate the parameters dictionary
            return_string += base_indent + f"__{field_name}_parameters_dict = {{\n"
            # If the field is a float, then that means that we can use it directly
            for parameter in physical_value_parameters:
                return_string += base_indent + f"    \"{parameter}\": {field_data.get(parameter)},\n"
            return_string += base_indent + f"}}\n"
    #  / Generate the parameters dictionary

    return_string += base_indent + "# ---------------- /Common Message Properties -------------------------\n"
    return_string += base_indent + "\n"

    return(return_string)

def generate_common_message_functions(base_indent, data):
    # Generate common message functions
    return_string = ""
    return_string += base_indent +  "# ----------------- Common Message Functions -------------------------\n"

    # Generate unpack_message function
    return_string += base_indent +  "def unpack_message(message_bytes):\n"
    return_string += base_indent +  "    message_dict = {}\n"

    # Get common message field byte locations
    machine_id_byte = data['common_message_fields']['machine_id']['first_byte']
    channel_id_byte = data['common_message_fields']['channel_id']['first_byte']
    message_type_id_byte = data['common_message_fields']['message_type_id']['first_byte']
    crc_byte = data['common_message_fields']['crc']['first_byte']
    message_length = data['rs485_uart_parameters']['message_length']

    return_string += base_indent +  "    \n"
    return_string += base_indent +  "    # Unpack the message values from the message bytes\n"
    return_string += base_indent + f"    message_dict[\"machine_id\"] = int(bus_to_real_value(message_bytes[{machine_id_byte}], __machine_id_parameters_dict))\n"
    return_string += base_indent + f"    message_dict[\"channel_id\"] = int(bus_to_real_value(message_bytes[{channel_id_byte}], __channel_id_parameters_dict))\n"
    return_string += base_indent + f"    message_dict[\"message_type_id\"] = message_type_id(message_bytes[{message_type_id_byte}])\n"
    return_string += base_indent + f"    received_crc = message_bytes[{crc_byte}]\n"
    return_string += base_indent +  "    \n"
    return_string += base_indent +  "    # Calculate the CRC based on the message bytes with CRC byte set to 0\n"
    return_string += base_indent +  "    # This is done by creating a copy of the message bytes and setting the CRC byte to 0\n"
    return_string += base_indent +  "    message_bytes_copy = bytearray(message_bytes)\n"
    return_string += base_indent + f"    message_bytes_copy[{crc_byte}] = 0x00\n"
    return_string += base_indent +  "    calculated_crc = calc_Crc8MaximDow(message_bytes_copy)\n"
    return_string += base_indent +  "    # Check if the calculated CRC matches the received CRC\n"
    return_string += base_indent +  "    if calculated_crc != received_crc:\n"
    return_string += base_indent +  "        raise ValueError(\"CRC mismatch: expected {}, got {}\".format(calculated_crc, received_crc))\n"
    return_string += base_indent +  "    \n"

    # Call the appropriate message unpack function
    return_string += base_indent +  "    # Check the message type ID and call the appropriate message unpack function\n"
    return_string += base_indent +  "    try:\n"
    return_string += base_indent +  "        message_dict.update(__message_type_id_class_map[message_dict[\"message_type_id\"]]().unpack_message(message_bytes))\n"
    return_string += base_indent +  "    except KeyError:\n"
    return_string += base_indent +  "        raise ValueError(\"Invalid message type ID: {}\".format(message_dict[\"message_type_id\"]))\n\n"
    return_string += base_indent +  "    return message_dict\n"
    return_string += base_indent +  "    \n"
    return_string += base_indent +  "    \n"

    # Generate pack_message function
    return_string += base_indent +  "def pack_message(machine_id, channel_id, message_type_id, payload = {}):\n"
    return_string += base_indent +  "    # Initialize the byte array and message parameters\n"
    return_string += base_indent + f"    message_bytes = bytearray([0x00] * {message_length})\n"
    return_string += base_indent +  "    # Pack the message\n"
    return_string += base_indent + f"    message_bytes[{machine_id_byte}] = int(real_to_bus_value(machine_id, __machine_id_parameters_dict))\n"
    return_string += base_indent + f"    message_bytes[{channel_id_byte}] = int(real_to_bus_value(channel_id, __channel_id_parameters_dict))\n"
    return_string += base_indent + f"    message_bytes[{message_type_id_byte}] = message_type_id\n"
    return_string += base_indent +  "    \n"
    return_string += base_indent +  "    # Check the message type ID and call the appropriate pack message function\n"
    return_string += base_indent +  "    try:\n"
    return_string += base_indent +  "        message_bytes = __message_type_id_class_map[message_type_id]().pack_message(message_bytes, payload)\n"
    return_string += base_indent +  "    except KeyError:\n"
    return_string += base_indent +  "        raise ValueError(\"Invalid message type ID: {}\".format(message_type_id))\n"
    return_string += base_indent +  "    \n"
    return_string += base_indent +  "    # Calculate the CRC based on the message bytes with CRC byte set to 0\n"
    return_string += base_indent +  "    crc = calc_Crc8MaximDow(message_bytes)\n"
    return_string += base_indent +  "    # Insert the CRC byte into the message\n"
    return_string += base_indent + f"    message_bytes[{crc_byte}] = crc\n"
    return_string += base_indent +  "    \n"
    return_string += base_indent +  "    return(message_bytes)\n"

    return_string += base_indent +  "# ---------------- /Common Message Functions -------------------------\n"
    return_string += base_indent +  "\n"

    return(return_string)


def generate_common_messages_file(data, output_directory):
    """Generates the rs485_api.py file."""
    file_name = os.path.join(output_directory, "rs485_api.py")
    with open(file_name, 'w') as f:

        f.write(f"# This file is auto-generated from the TOML file\n")
        f.write(f"# WARNING: Do not edit manually. Run the script 'generate_message_files.py' to regenerate this file.\n")
        f.write(f"# This file is the API for the Neware RS485 protocol.\n")
        f.write(f"\n")

        f.write("from enum import IntEnum\n\n")
        f.write("from rs485.messages.message_helpers import calc_Crc8MaximDow, real_to_bus_value, bus_to_real_value\n\n")

        # Import individual message classes
        for message_name, _ in data['messages'].items():
            module_name = (message_name+"_message").lower().replace(" ", "_")
            class_name = message_name.lower().replace(" ", "_")
            f.write(f"from rs485.messages.{module_name} import {class_name}\n")
        f.write("\n")

        # Generate the common message properties
        base_indent = ""
        f.write(generate_common_message_properties(base_indent, data))

        # Generate common message functions
        f.write(generate_common_message_functions(base_indent, data))

# Run the generator
toml_file_path = 'neware_BTS4000_rs485.toml'
output_directory = '../api/rs485'
specific_message_id_subdirectory = 'messages'
generate_message_files(toml_file_path, output_directory, specific_message_id_subdirectory)