#!/usr/bin/env python3

import can
import datetime
import os
import threading
import time


'''
Script used to record the way I was driving, to create a test suite for
another project I'm working on
'''

diagnostic_id = 0x7df
INTERFACE='vcan0'
KILLFILE='/tmp/canstop'

global KILLSWITCH
KILLSWITCH=False

rpm = 0
speed = 0
accelerator = 0

def _is_answer(answer, data):
    '''
    Check if the message received answers our query
    '''
    if len(answer.data) < 3:
        return False

    if (answer.data[1] != data[1] + 0x40) and (answer.data[1] != 0x7f):
        # REQUEST MODE
        return False
    if (answer.data[2] != data[2]) and (answer.data[2] != data[1]):
        # REQUEST PID
        return False

    return True

def can_xchg(bus, arb_id, data, ext=False):
    '''
    Noise proof
    '''
    msg = can.Message(arbitration_id=arb_id, data=data)

    answer = None
    bus.send(msg)

    while not answer or not _is_answer(answer, data):
        try:
            answer = bus.recv()
        except:
            pass

    return answer

def get_rpm(bus):
    while not KILLSWITCH:
        try:
            answer = can_xchg(bus, diagnostic_id, [2, 1, 0xc, 0, 0, 0, 0, 0])
            if answer is None:
                return

            global rpm
            rpm = (answer.data[3] << 8) + answer.data[4]
        except:
            pass

def get_speed(bus):
    while not KILLSWITCH:
        try:
            answer = can_xchg(bus, diagnostic_id, [2, 1, 0xd, 0, 0, 0, 0, 0])
            if answer is None:
                return

            global speed
            speed = answer.data[3]
        except:
            pass

def get_accel_pos(bus):
    while not KILLSWITCH:
        try:
            answer = can_xchg(bus, diagnostic_id, [2, 1, 0x49, 0, 0, 0, 0, 0])
            if answer is None:
                return

            global accelerator
            accelerator = answer.data[3]
        except:
            pass

if "__main__" in __name__:
    speed_bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
    rpm_bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
    accelerator_bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')

    begin = datetime.datetime.now()
    f = open("can.{0}.logs".format(str(begin).replace(" ", "_")), "w+", buffering=1)

    threading.Timer(0, get_speed, [speed_bus]).start()
    threading.Timer(0, get_rpm, [rpm_bus]).start()
    threading.Timer(0, get_accel_pos, [accelerator_bus]).start()

    while True:
        delta = datetime.datetime.now() - begin
        f.write("{0} - {1} - {2} - {3}\n".format(delta, rpm, speed, accelerator))
        #print("{0} - {1} - {2} - {3}".format(delta, rpm, speed, accelerator))
        time.sleep(0.1)

        if os.path.isfile(KILLFILE):
            global KILLSWITCH
            KILLSWITCH=True
            f.close()
            break

