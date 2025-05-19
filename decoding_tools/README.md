# Decoding Tools
This directory provides tools for sniffing an active Neware RS485 Bus and decoding the messages on it. 

## logger.py
```logger.py``` records all of the bytes on a UART bus, and attempts to break the byte stream into 36 char messages for interpretation. It is up to the user to ensure that their RS485 adapter is on the correct UART line (Middle Machine TX or Middle Machine RX) to record the messages that they want to see. It is also possible to run 2 instances of this logger, recording to different files, and placed on both RS485 lines. This allows for a complete picture of the full duplex communication.