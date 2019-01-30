#!/usr/bin/env python3

import can
import random
import time

INTERFACE="can0"

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')

dictionnary = {}

for i in range(200):
    msg = bus.recv()
    print(i, msg)
    if msg.arbitration_id not in dictionnary:
        dictionnary[msg.arbitration_id] = msg.dlc
    else:
        pass


for x in dictionnary:
    print(hex(x))

time.sleep(2)

for i in dictionnary:
    for _ in range(100):
        data = [random.randint(0, 255) for x in range(dictionnary[i])]
        msg = can.Message(arbitration_id=i, data=data, extended_id=False)
        bus.send(msg)
        time.sleep(0.005)
