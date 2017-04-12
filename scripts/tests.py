#!/usr/bin/env python3

import can

INTERFACE="vcan0"

def send_and_wait(bus, arb_id, data, extended):
    msg = can.Message(arbitration_id=arb_id, data=data, extended_id=extended)
    bus.send(msg)
    print("TX: {0}: {1})".format(hex(msg.arbitration_id), msg.data))
    answer = bus.recv()
    print("RX: {0}: {1})".format(hex(answer.arbitration_id), answer.data))
    return answer

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
send_and_wait(bus, 0x7de, [0, 25, 0, 1, 3, 1, 4, 1], False)
send_and_wait(bus, 0x7df, [2, 1, 5, 0, 0, 0, 0, 0], False)
send_and_wait(bus, 0x7df, [2, 1, 0, 0, 0, 0, 0, 0], False)
