#!/usr/bin/python3
import time
import os
import math
import threading
import signal
import random
import sys
import can
import struct
import car_src
import terminal_sink
import can_helpers
import car_library

'''

This file shows you an example of a TerminalSink
When launched, this script will read the can bus on the
specified interface and show you the raw values along the known
ones (on a graph)

This script is configured for a Toyota Yaris.
You can change it to any car already added in the library.

'''

# Interface selection
if len(sys.argv) < 2:
    interface = "can0"
else:
    interface = sys.argv[1]


# Change the car here
known_fields = car_library.ToyotaYaris.get_known_fields()

message_sink = terminal_sink.TerminalSink(known_fields)

try:
    listener = car_src.CarSrc(interface, message_sink, known_fields)
    message_sink.start()

    while listener.listen():
        continue
except OSError:
    print("Invalid interface ")
    exit(2)
