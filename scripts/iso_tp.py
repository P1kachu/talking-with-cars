#!/usr/bin/env python3

import can

INTERFACE="can0"

# Diagnostic session init
EXTENDED_DIAGNOSTIC = 0x3

# Security session init
REQUEST_SEED = 0x1
SEND_KEY = 0x2
VW_REQUEST_SEED = 0x3
VW_SEND_KEY = 0x4


def can_xchg(bus, arb_id, data, extended=False):
    msg = can.Message(arbitration_id=arb_id, data=data, extended_id=extended)
    bus.send(msg)
    print("TX: {0}".format(msg))
    answer = bus.recv(0.25)
    if answer is None:
        return
    print("RX: {0}".format(answer))
    return answer

def iso_tp_init_diagnostic_session(bus, arb_id, session_type=EXTENDED_DIAGNOSTIC):
    answer = can_xchg(bus, arb_id, [2, 0x10, session_type, 0, 0, 0, 0, 0])

    if answer and answer.data[1] == (0x50):
        print("Diagnostic session susccessfuly opened")
    else:
        print("Failure in establishing ISO-TP diagnostic session")
        return None

    return answer

def iso_tp_init_security_session(bus, arb_id, req_seed=REQUEST_SEED, send_key=SEND_KEY):
    for i in range(10):
        answer = can_xchg(bus, arb_id, [2, 0x27, req_seed, 0, 0, 0, 0, 0])
        answer = can_xchg(bus, arb_id, [6, 0x27, send_key, 0, 0, 0, 0, 0])

    if answer and answer.data[1] == 0x67:
        seed = answer.data[3:5]
        print("Security session seed: {0}".format(seed))
    else:
        print("Failure in establishing ISO-TP security session")
        return None

    answer = can_xchg(bus, arb_id, [6, 0x27, send_key, 0, 0, 0, 0, 0])

    if answer and answer.data[1] == 0x67:
        print("Security session opened!")
    elif answer and answer.data[3] == 0x35:
        print("Bad key in security session init")
        return None
    else:
        print("Failure in sending security session key")
        return None

    return answer

'''
def iso_tp_init_upload_session(bus, arb_id):
    answer = can_xchg(bus, arb_id, [0x10, 0xb, 0x34, 0, 0x44, 0, 0x1, 0])

    if answer and answer.data[0] == (0x30):
        pass
    else:
        print("Failure in establishing ISO-TP upload session")
        return None

    answer = can_xchg(bus, arb_id, [0x21, 0x08, 0x0, 0x6, 0xff, 0xf8, 0, 0])
    return answer
'''

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
if iso_tp_init_diagnostic_session(bus, 0x7e0):
    if iso_tp_init_security_session(bus, 0x7e0, VW_REQUEST_SEED, VW_SEND_KEY):
        print("OK")
