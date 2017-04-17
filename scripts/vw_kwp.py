#!/usr/bin/env python3

import can

INTERFACE="can0"

def can_xchg(bus, arb_id, data, extended=False):
    msg = can.Message(arbitration_id=arb_id, data=data, extended_id=extended)
    bus.send(msg)
    print("TX: {0}".format(msg))
    answer = bus.recv(0.25)
    if answer is None:
        return
    print("RX: {0}".format(answer))
    return answer

def vw_kwp_init(bus, initial_id=0x200):
    '''
    Open a channel

    Step 1: request an ID
    ---------------------

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

    answer = can_xchg(bus, initial_id, [7, 0x1, 0xc0, 0x0, 0x10, 0x0, 0x3, 0x1])

    if not answer:
        print("No answer in init (session request)")
        return

    '''
    Ex: 0x201 0x7 0x00 0xD0 0x00 0x03 0x40 0x07 0x01

    - 0x201: TP2.0 module ID (module response is always 0x00?)
    -   0x7: DLC
    -   0x0: TP2.0 module ID
    -  0xD0: Positive response
    -   0x0: RX ID
    -   0x3: RX Prefix + validity nibble (see above)
    -  0x40: TX ID
    -   0x7: TX Prefix + validity nibble (valid, tells us to use 0x470)
    -   0x1: Application type
    '''

    if answer.arbitration_id == 0x201 and answer.data[1] == 0xD0:
        rx_id = answer.data[2] + (answer.data[3] << 8)
        tx_id = answer.data[4] + (answer.data[5] << 8)
    else:
        print("Invalid answer in init (session request): {0}".format(answer))
        return

    '''
    Step 2: Set session parameters
    ------------------------------

    Ex: 0x740 0x6 0xA0 0x0F 0x8A 0xFF 0x32 0xFF

    - 0x740: New ID given by receiver
    -   0x6: DLC
    -  0xA0: Parameter request
    -   0xF: Number of packets to be send between ACKs
    -  0x8A:
    -  0xFF: -- Timing parameters
    -  0x32: -- see ../notes/vehicular-networks.md
    -  0xFF:

    Answer follows the same format.

    '''

    answer = can_xchg(bus, 0x740, [6, 0xa0, 0x0f, 0x8a, 0xff, 0x32, 0xff])

    if not answer:
        print("No answer in init (parameters request)")
        return

    if answer.data[0] != 0xa1:
        print("Invalid answer in init (parameters request): {0}".format(answer))


    '''
    Step 3: Test connection
    -----------------------

    Parameters request with opcode 0xa3 will return the same message for
    testing
    '''

    check_req = answer
    check_req.arbitration_id = 0x300
    check_req.data[0] = 0xa3
    check_resp = can_xchg(bus, 0x740, check_req.data)

    if check_resp != check_req:
        print("Channel test failed: {0} != {1}".format(check_req, check_resp))
        return


bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
vw_kwp_init(bus)
