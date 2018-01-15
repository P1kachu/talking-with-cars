#!/usr/bin/python3

import can
import math
import os
import random
import signal
import sys
import threading
import time
import can_helpers


'''

    Read from the CAN bus and then send data to a sink
    Does not do any computations

'''
class CarSrc():
    def __init__(self, interface, message_sink, known_fields = {}):
        self.bus = can.interface.Bus(channel=interface, bustype='socketcan_native')
        self.known_fields = known_fields
        self.sink = message_sink

    def listen(self):
        try:
            msg = self.bus.recv(0.1)
        except OSError as e:
            print("Network error: %s" % e)
            return False

        if msg == None:
            return True

        self.register_message(msg)
        return True

    def register_message(self, can_message):
        can_id = can_message.arbitration_id
        data_len = can_message.dlc
        data = can_message.data

        self.sink.register_message(can_message)
