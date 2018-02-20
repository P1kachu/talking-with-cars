#!/usr/bin/env python3

import can

INTERFACE='vcan0'
EXTENDED=False
INPUT_FILE="can.log" # Shoud be a simple `candump can0 > file`

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')

with open("can.log", 'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.rstrip().split(' ')
        line = list(filter(None, line))
        arb_id = int(line[1], 16)
        data = [int(x, 16) for x in line[3:]]
        msg = can.Message(arbitration_id=arb_id, data=data, extended_id=False)
        bus.send(msg)

