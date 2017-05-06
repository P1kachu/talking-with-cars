#!/usr/bin/env python3

import can
from time import sleep

INTERFACE="can0"

EXTENDED_DIAGNOSTIC = 0x3
DIAGNOSTIC_SESSION = 0x10
SECURITY_SESSION = 0x27

GENERAL_REJECT = 0x10
BUSY_REPEAT_REQUEST = 0x21
SECU_SESSION_BAD_KEY = 0x35
SECU_SESSION_EXCEED_NUMBER = 0x36
SECU_SESSION_DELAY_NOT_EXPIRED = 0x37

IGNORE_KEY = -1
REQUEST_SEED = 0x1
SEND_KEY = 0x2
VW_REQUEST_SEED = 0x3 # Different levels of security defined by the manufacturer.
VW_SEND_KEY = 0x4     # See Keyword Protocol 2000 - Part 3 (Implementation)

def can_xchg(bus, arb_id, data, extended=False):
    msg = can.Message(arbitration_id=arb_id, data=data, extended_id=extended)
    bus.send(msg)
    print("TX: {0}".format(msg))

    answer = bus.recv(0.1)
    if answer is None:
        return

    print("RX: {0}".format(answer))
    return answer

def kwp2000_init_diagnostic_session(bus, arb_id, session_type=EXTENDED_DIAGNOSTIC):
    answer = can_xchg(bus, arb_id, [2, DIAGNOSTIC_SESSION, session_type, 0, 0, 0, 0, 0])

    if answer and answer.data[1] == (DIAGNOSTIC_SESSION + 0x40):
        #print("Diagnostic session susccessfuly opened")
        pass
    else:
        print("Failure in establishing ISO-TP diagnostic session")
        return None

    return answer

def compute_key(seed):
    return seed

def _kwp2000_init_security_session_error(code):
    if code == SECU_SESSION_BAD_KEY:
        print("Bad key in security session init")
    elif code == SECU_SESSION_EXCEED_NUMBER:
        print("ExceedNumberOfAttempts in security session init")
    elif code == SECU_SESSION_DELAY_NOT_EXPIRED:
        print("requiredTimeDelayNotExpired in security session init")
    elif code == BUSY_REPEAT_REQUEST:
        print("BUSY_REPEAT_REQUEST - sleeping")
        sleep(0.3)
    else:
        print("Failure in sending security session key")


def kwp2000_init_security_session(bus, arb_id, req_seed=REQUEST_SEED, send_key=SEND_KEY):
    answer = can_xchg(bus, arb_id, [2, SECURITY_SESSION, req_seed, 0, 0, 0, 0, 0])

    if answer and answer.data[1] == (SECURITY_SESSION + 0x40):
        seed = list(answer.data[3:7])
        print("Security session seed: {0}".format(seed))
    else:
        _kwp2000_init_security_session_error(answer.data[3])
        return None

    if send_key == IGNORE_KEY:
        return None

    data_key = [6, SECURITY_SESSION, send_key] + compute_key(seed) + [0]
    answer = can_xchg(bus, arb_id, data_key)

    if answer and answer.data[1] == (SECURITY_SESSION + 0x40):
        #print("Security session opened!")
        pass
    else:
        _kwp2000_init_security_session_error(answer.data[3])
        return None

    return answer

def kwp2000_test_security_session(bus, key=SEND_KEY, arb_id=0x7e0):
    iteration_nb = 15

    while True:
        if kwp2000_init_diagnostic_session(bus, arb_id):
            if kwp2000_init_security_session(bus, arb_id, VW_REQUEST_SEED, key):
                print("GO DUMP STUFF")
                return
            elif key != IGNORE_KEY:
                print("Failed key exchange - Sleeping")
                sleep(5)

        iteration_nb -= 1
        if iteration_nb == 0:
            return

def kwp2000_test_other_ecus(bus):
    possible_ids = [0x0700, 0x0703, 0x0704, 0x0706, 0x0707, 0x0708, 0x070A,
                    0x0711, 0x0713, 0x0714, 0x0715, 0x0751, 0x076C, 0x07E0,
                    0x07F1]
    for arb_id in possible_ids:
        if kwp2000_init_diagnostic_session(bus, arb_id):
            kwp2000_test_security_session(bus, key=IGNORE_KEY, arb_id=arb_id)

def kwp2000_test_readall(bus, arb_id=0x7e0):
    if kwp2000_init_diagnostic_session(bus, arb_id):
        for high in range(0xff):
            for low in range(0xff):
                answer = can_xchg(bus, arb_id, [5, 0x22, high, low, 0x1, 0x1, 0, 0])
                sleep(0.05)



#### MAIN ####

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
#kwp2000_test_other_ecus(bus)
kwp2000_test_readall(bus)

