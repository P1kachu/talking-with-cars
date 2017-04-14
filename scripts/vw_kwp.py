#!/usr/bin/env python3

import can

INTERFACE="vcan0"

def can_xchg(bus, arb_id, data, extended=False):
    msg = can.Message(arbitration_id=arb_id, data=data, extended_id=extended)
    bus.send(msg)
    print("TX: {0})".format(msg))
    answer = bus.recv(1)
    if answer is None:
        return
    print("RX: {0})".format(answer))
    return answer

def vw_kwp_init(bus):
    '''
    Open a channel

    Ex: 0x200 0x7 0x01 0xC0 0x00 0x10 0x00 0x03 0x01
    - 0x200 > VW TP2.0, inital ID when opening channel
    -   0x7 > DLC
    -   0x1 > TP2.0 module ID (here, ECU)
    -  0xC0 > Setup request
    -   0x0 > RX ID
    -  0x10 > RX Prefix + validity nibble
              0b00010000 = 0b1 << 4   +   0
                           Invalid       ID prefix
              RX ID is invalid, so won't be used by receiver, which will tell
              us what to use
    -   0x0 > TX ID
    -   0x3 > TX Prefix + validity nibble
              0b00000011 = 0b0 << 4   +   3
                           Valid          ID prefix
              TX ID is valid, we tell the receiver what ID to use back
    -   0x1 > Application (type seems to be always 1 for KWP)

    So we set up a request using any ID choosen by the receiver, and listening
    to (TX ID + TX prefix << 8) == 0x300
    '''

    answer = can_xchg(bus, 0x200, [7, 0x1, 0xc0, 0x0, 0x10, 0x0, 0x3, 0x1])

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
vw_kwp_init(bus)


