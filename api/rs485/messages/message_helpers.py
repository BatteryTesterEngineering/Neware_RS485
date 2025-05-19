# ----------------- Helper Functions -------------------------
# Implement crc8-maxim-dow algorithm manually to avoid dependency on crccheck
def calc_Crc8MaximDow(message_bytes):
    crc = 0
    for c in message_bytes:
        for i in range(0, 8):
            b = (crc & 1) ^ ((( int(c) & (1 << i))) >> i)
            crc = (crc ^ (b * 0x118)) >> 1
    return(crc)

def bus_to_real_value(bus_value, parameters):
    # Convert bus value to real value
    # Real Value = ((Bus Value * multiplier) / divisor) + offset
    physical_value = ((bus_value * parameters["multiplier"]) / parameters["divisor"]) + parameters["offset"]
    return physical_value

def real_to_bus_value(physical_value, parameters):
    # Convert real value to bus value
    # Bus Value = ((Real Value - offset) * divisor) / multiplier
    bus_value = int(((physical_value - parameters["offset"]) * parameters["divisor"]) / parameters["multiplier"])
    return bus_value
# ---------------- /Helper Functions -------------------------