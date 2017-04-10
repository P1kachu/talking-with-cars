#!/usr/bin/env python3

import can
from canConstant import CAN

INTERFACE = "can0"
ID = CAN.RPM
vwPoloRPMFactor = 15.5

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
msg = can.Message(arbitration_id=ID,
        data = [1, 0, 0, 3 * vwPoloRPMFactor],
        extended_id=False)
bus.send(msg)
#notifier = can.Notifier(bus, [can.Printer()])
