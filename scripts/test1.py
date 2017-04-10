#!/usr/bin/env python3

import can

INTERFACE="vcan0"

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
msg = can.Message(arbitration_id=0x7de,
        data = [0, 25, 0, 1, 3, 1, 4, 1],
        extended_id=False)
bus.send(msg)
#notifier = can.Notifier(bus, [can.Printer()])
