#!/usr/bin/env python3

import can
from canConstant import CAN

INTERFACE = "can0"
ID = CAN.DASH_MISC_1
data = [CAN.LEFT_TURN_SIGNAL, 0, CAN.BACKLIGHT_ON, 0, 0, 0, 0, 0]

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
msg = can.Message(arbitration_id=ID,
        data = [2,0,1,0,0,0,0,0],
        extended_id=False)
bus.send(msg)
#notifier = can.Notifier(bus, [can.Printer()])
