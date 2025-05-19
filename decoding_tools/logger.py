# This script logs bytes and attemts to decode them
import serial
import datetime
import csv

device = "/dev/ttyUSB0"
bytes_output_file = "bytes.csv"
messages_output_file = "messages.csv"

baud_rate = 3000000
gap_duration_s = 0.001
message_length = 36
gap_duration_delta = datetime.timedelta(seconds = gap_duration_s)

def log_write(all_bytes):

    with open(bytes_output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, all_bytes[0].keys())
        writer.writeheader()
        for byte in all_bytes:
            writer.writerow(byte)


def decode(all_bytes):
    prev_timestamp = all_bytes[0]["timestamp"]
    message = []
    all_messages = []
    first_gap_complete = False

    for byte in all_bytes:
        if first_gap_complete == False:
            if byte["timestamp"] > (prev_timestamp + gap_duration_delta):
                # We found the first gap
                first_gap_complete = True
                # Save the byte at the beginning of our new message
                message.append(byte["byte"])
                message_timestamp = byte["timestamp"]
            
            # We haven't found the first gap yet, so update our previous timestamp to this message's timestamp
            prev_timestamp = byte["timestamp"]

        else:
            # Now we just sort based on number of bytes

            # Add our byte to the message
            message.append(byte["byte"])

            # If that was the first byte, then add our timestamp as the message timestamp
            if len(message) == 1:
                message_timestamp = byte["timestamp"]
            # if the message is greater than or equal to max length, then end the message
            elif len(message) >= message_length:
                message_dict = {"timestamp": message_timestamp, "len": len(message), "message": message}
                all_messages.append(message_dict)
                message = []
    
    with open(messages_output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, all_messages[0].keys())
        writer.writeheader()
        for message in all_messages:
            writer.writerow(message)


with serial.Serial(port = device, baudrate = baud_rate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE) as ser:
    print("Logging started. Ctrl-C to stop.")
    all_bytes = []
    try:
        while True:
            if ser.inWaiting():
                # We have a valid byte waiting
                # Read it
                byte_raw = ser.read(1)
                #byte_raw = ser.read(ser.inWaiting())
                byte_time = datetime.datetime.now()
                byte_dict = {"timestamp": byte_time, "byte": byte_raw}
                all_bytes.append(byte_dict)

    except KeyboardInterrupt:
        log_write(all_bytes)
        decode(all_bytes)
        print("Logging stopped and saved")
