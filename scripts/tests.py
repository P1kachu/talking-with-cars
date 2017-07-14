#!/usr/bin/env python3

import can

INTERFACE="can0"

def get_bits_msb(nb_data_bytes, buf):
    bits = []
    for i in range(3, nb_data_bytes + 3):
        for reverse in range(7, -1, -1):
            bits.append(((1 << reverse) & buf[i]) >> reverse)
    return bits


def can_xchg(bus, arb_id, data, extended=False):
    msg = can.Message(arbitration_id=arb_id, data=data, extended_id=extended)
    bus.send(msg)
    print("TX: {0}".format(msg))
    answer = bus.recv(0.2)
    if not answer:
        return
    print("RX: {0}".format(answer))
    return answer

def bruteforce_byte_0(bus, arb_id):
    for i in range(0x20):
        can_xchg(bus, arb_id, [i, 0, 0, 0, 0, 0, 0, 0])
        can_xchg(bus, arb_id, [i, 64, 64, 64, 64, 64, 64, 64])
        can_xchg(bus, arb_id, [i, 128, 128, 128, 128, 128, 128, 128])
        can_xchg(bus, arb_id, [i, 255, 255, 255, 255, 255, 255, 255])

def bruteforce_byte_1(bus, arb_id):
    for i in range(0x20):
        can_xchg(bus, arb_id, [1, i, 0, 0, 0, 0, 0, 0])
    for i in range(0x20):
        can_xchg(bus, arb_id, [1, i, 64, 64, 64, 64, 64, 64])
    for i in range(0x20):
        can_xchg(bus, arb_id, [1, i, 128, 128, 128, 128, 128, 128])
    for i in range(0x20):
        can_xchg(bus, arb_id, [1, i, 255, 255, 255, 255, 255, 255])

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')

'''
# Engine coolant temperature
answer = can_xchg(bus, 0x7df, [2, 1, 5, 0, 0, 0, 0, 0], False)
temperature = answer.data[3] - 40
print("Temperature: {0} degrees".format(temperature))

# RPM
answer = can_xchg(bus, 0x7df, [2, 1, 0xc, 0, 0, 0, 0, 0], False)
print("{0} rpm".format((answer.data[3] * 256 + answer.data[4])/4))

# OBD standard this vehicle conforms to
answer = can_xchg(bus, 0x7df, [2, 1, 0x1c, 0, 0, 0, 0, 0], False)
print("OBD Standard: {0}".format(answer.data[2]))

# Vehicle speed
answer = can_xchg(bus, 0x7df, [2, 1, 0xd, 0, 0, 0, 0, 0], False)
print("{0} km/h".format(answer.data[3]))

# Throttle position
answer = can_xchg(bus, 0x7df, [2, 1, 0x11, 0, 0, 0, 0, 0], False)
print("Throttle position: {0}%".format(answer.data[3]))
'''

'''
# Mode 1 supported PIDs
answer = can_xchg(bus, 0x7df, [2, 1, 0x00, 0, 0, 0, 0, 0])
print(get_bits_msb(4, answer.data))
answer = can_xchg(bus, 0x7df, [2, 1, 0x20, 0, 0, 0, 0, 0])
print(get_bits_msb(4, answer.data))
answer = can_xchg(bus, 0x7df, [2, 1, 0x40, 0, 0, 0, 0, 0])
print(get_bits_msb(4, answer.data))

# Mode 9 supported PIDs
answer = can_xchg(bus, 0x7df, [2, 9, 0x00, 0, 0, 0, 0, 0])
bits = get_bits_msb(4, answer.data)
print(bits)
if bits[0xa]:
    answer = can_xchg(bus, 0x7df, [2, 9, 0x09, 0, 0, 0, 0, 0])
    answer = can_xchg(bus, 0x7df, [2, 9, 0x0a, 0, 0, 0, 0, 0])
    for i in range(answer.data[3] - 1):
        print(bus.recv())
else:
    print("PID 9:0xa not supported")

# Testing like stupid
bruteforce_byte_0(bus, 0x711)
bruteforce_byte_0(bus, 0x711)
bruteforce_byte_1(bus, 0x7f1)

# Vehicle specific testing
for i in range(0xffffff):
    msg = can_xchg(bus, 0x7df, [0x3, 0x22, i & 0xff, i >> 8 & 0xff, i >> 16, 0, 0, 0])
    #if msg:
    #    print("Response received for PID {0}: {1}".format(i, msg))
    #    break

polo_id_data_mappings = {
        0x0210a006: [0x06, 0x00, 0x06, 0x00, 0x06, 0x00, 0x06, 0x00]
        0x0a28a000: [0x06, 0x00, 0x00, 0x00],
        }
for i in range(0xffff):
    arb_id = 0x0a28a000
    data = polo_id_data_mappings[arb_id]
    msg = can.Message(arbitration_id=arb_id, data=data, extended_id=True)
    bus.send(msg)
'''

def _is_answer(answer, data):
    '''
    Check if the message received answers our query
    '''
    if len(answer.data) < 3:
        return False

    if answer.data[1] != data[1] + 0x40:
        # REQUEST MODE
        return False
    if answer.data[2] != data[2]:
        # REQUEST PID
        return False

    return True

def can_xchg_advanced(bus, arb_id, data, ext=False):
    '''
    Noise proof
    '''
    msg = can.Message(arbitration_id=arb_id,
            data=data,
            extended_id=ext)

    answer = None
    while not answer or not _is_answer(answer, data):
        # 29bits CAN requires to resend the message until
        # the answer is received.
        try:
            bus.send(msg)
            answer = bus.recv(0.05)
        except:
            pass

    return answer

def can29_recv(bus, arb_id, byte_nb):
    answer = bus.recv(0.1)

    while not answer or answer.arbitration_id != arb_id or len(answer.data) <= byte_nb:
        answer = bus.recv(0.1)

    if byte_nb == WHOLE_MESSAGE_CNST:
        return answer

    return answer.data[byte_nb]

def is_handbrake_set(bus):
    answer = None
    arb_id = 0x18DA28F1
    data = [0x3, 0x22, 0x08, 0x89, 0, 0, 0, 0]
    #data = [0x3, 0x22, 0x08, 0x85, 0, 0, 0, 0]
    while not answer or answer.arbitration_id != 0x18daf128:
        try:
            msg = can.Message(arbitration_id=arb_id, data=data, extended_id=True)
            bus.send(msg)
            answer = bus.recv(0.1)
        except OSError:
            pass

    # Send UDS ACK
    msg = can.Message(arbitration_id=arb_id, data=[0x30, 0, 0, 0, 0, 0, 0, 0], extended_id=True)
    bus.send(msg)

    return answer.data[4] & 1

# UDS session
can_xchg_advanced(bus, 0x18DA30f1, [0x2, 0x10, 0x03, 0, 0, 0, 0, 0], True)
is_handbrake_set(bus)
