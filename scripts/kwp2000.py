#!/usr/bin/env python3

import can
from time import sleep

INTERFACE="can0"

# Diagnostic session init
EXTENDED_DIAGNOSTIC = 0x3

# Security session init
REQUEST_SEED = 0x1
SEND_KEY = 0x2
VW_REQUEST_SEED = 0x3 # Different levels of security defined by the manufacturer.
VW_SEND_KEY = 0x4     # See Keyword Protocol 2000 - Part 3 (Implementation)

def can_xchg(bus, arb_id, data, extended=False):
    msg = can.Message(arbitration_id=arb_id, data=data, extended_id=extended)
    bus.send(msg)
    print("TX: {0}".format(msg))
    answer = bus.recv(0.25)
    if answer is None:
        return
    print("RX: {0}".format(answer))
    return answer

def kwp2000_init_diagnostic_session(bus, arb_id, session_type=EXTENDED_DIAGNOSTIC):
    answer = can_xchg(bus, arb_id, [2, 0x10, session_type, 0, 0, 0, 0, 0])

    if answer and answer.data[1] == (0x50):
        print("Diagnostic session susccessfuly opened")
    else:
        print("Failure in establishing ISO-TP diagnostic session")
        return None

    return answer

def compute_key(seed):
    # http://nefariousmotorsports.com/forum/index.php?topic=4983.msg50819#msg50819
    seed[1] += 0x01
    seed[2] += 0x11
    seed[3] += 0x70
    return seed

def kwp2000_init_security_session(bus, arb_id, req_seed=REQUEST_SEED, send_key=SEND_KEY):
    answer = can_xchg(bus, arb_id, [2, 0x27, req_seed, 0, 0, 0, 0, 0])

    if answer and answer.data[1] == 0x67:
        seed = list(answer.data[3:7])
        print("Security session seed: {0}".format(seed))
    else:
        print("Failure in establishing ISO-TP security session")
        return None

    data_key = [6, 0x27, send_key] + compute_key(seed) + [0]
    answer = can_xchg(bus, arb_id, [6, 0x27, send_key, 0, 0, 0, 0, 0])

    if answer and answer.data[1] == 0x67:
        print("Security session opened!")
    elif answer and answer.data[3] == 0x35:
        print("Bad key in security session init")
        return None
    elif answer and answer.data[3] == 0x36:
        print("ExceedNumberOfAttempts in security session init")
        return None
    elif answer and answer.data[3] == 0x37:
        print("requiredTimeDelayNotExpired in security session init")
        return None
    else:
        print("Failure in sending security session key")
        return None

    return answer

def kwp2000_init_upload_session(bus, arb_id):
    # Not tested right now
    # From http://nefariousmotorsports.com/forum/index.php?topic=4983.msg51246#msg51246
    #answer = can_xchg(bus, arb_id, [0x9, 0x35, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00])
    return answer

def kwp2000_test_security_session(bus):
    if kwp2000_init_diagnostic_session(bus, 0x7e0):
        while True:
            if kwp2000_init_security_session(bus, 0x7e0, VW_REQUEST_SEED, VW_SEND_KEY):
                print("GO DUMP STUFF")
                kwp2000_init_upload_session(bus, 0x7e0)
            else:
                print("Failed key exchange - Sleeping")
                sleep(5)

def kwp2000_test_other_ecu(bus):
    possible_ids = [0x077e, 0x077b, 0x077d, 0x07e8, 0x07d6, 0x0774, 0x07bb, 0x077f]
    for arb_id in possible_ids:
        if kwp2000_init_diagnostic_session(bus, arb_id):
            print("ID {0} responded".format(arb_id))
            kwp2000_init_security_session(bus, arb_id, VW_REQUEST_SEED, VW_SEND_KEY)

def kwp2000_test_other_ecu(bus):
    possible_ids = [0x077e, 0x077b, 0x077d, 0x07e8, 0x07d6, 0x0774, 0x07bb, 0x077f]
    for arb_id in possible_ids:
        if kwp2000_init_diagnostic_session(bus, arb_id):
            print("ID {0} responded".format(arb_id))
            kwp2000_init_security_session(bus, arb_id, VW_REQUEST_SEED, VW_SEND_KEY)

def kwp2000_test_readall(bus):
    if kwp2000_init_diagnostic_session(bus, 0x7e0):
        for high in range(0xff):
            for low in range(0xff):
                answer = can_xchg(bus, 0x7e0, [5, 0x22, high, low, 0x1, 0, 0, 0, 0])

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
kwp2000_test_security_session(bus)
#kwp2000_test_other_ecu(bus)
#kwp2000_test_readall(bus)

