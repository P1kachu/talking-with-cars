#!/usr/bin/env python3

import can
import time

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
        break

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

# Mazda Demio UDS session
#can_xchg_advanced(bus, 0x7df, [0x2, 0x10, 0x01, 0, 0, 0, 0, 0], False)
"""
can0  TX - -  7DF   [8]  02 10 01 00 00 00 00 00   '........'
can0  RX - -  7E9   [8]  06 50 01 00 32 01 F4 00   '.P..2...'
"""

# Nissan Leaf UDS session
#for i in range(0x600, 0x800):
#    print(hex(i))
#    can_xchg_advanced(bus, i, [0x2, 0x10, 0x01, 0, 0, 0, 0, 0], False)
#    time.sleep(0.1)

# BMW 530d UDS session
for i in range(0x600, 0x800):
    print(hex(i))
    can_xchg_advanced(bus, i, [0x2, 0x10, 0x01, 0, 0, 0, 0, 0], False)
    time.sleep(0.1)
"""
2117-  can0  03C   [8]  20 A8 02 12 01 00 2A FF
2118-  can0  130   [5]  F7 FF FF FF FF
2119-  can0  7DE   [8]  02 10 01 00 00 00 00 00
2120-  can0  03C   [8]  7D A9 02 12 01 00 2A FF
2121-  can0  130   [5]  F7 FF FF FF FF
2122-  can0  7DF   [8]  02 10 01 00 00 00 00 00
2123:  can0  7EC   [8]  06 50 01 00 32 01 F4 55
2124-  can0  7E9   [8]  03 7F 10 22 AA AA AA AA
2125:  can0  7EF   [8]  06 50 01 00 32 01 F4 FF
2126-  can0  03C   [8]  9A AA 02 12 01 00 2A FF
2127-  can0  130   [5]  F7 FF FF FF FF
2128-  can0  7E0   [8]  02 10 01 00 00 00 00 00
2129-  can0  03C   [8]  C7 AB 02 12 01 00 2A FF
2130-  can0  130   [5]  F7 FF FF FF FF
2131-  can0  7E1   [8]  02 10 01 00 00 00 00 00
2132-  can0  7C1   [8]  0E 1A 00 0C FF 00 01 00
2133:  can0  7E9   [8]  06 50 01 00 32 01 F4 AA
2134-  can0  799   [7]  1D 01 17 04 0F 02 0A
2135-  can0  03C   [8]  49 AC 02 12 01 00 2A FF
2136-  can0  130   [5]  F7 FF FF FF FF
2137-  can0  7E2   [8]  02 10 01 00 00 00 00 00
2138-  can0  03C   [8]  14 AD 02 12 01 00 2A FF
2139-  can0  130   [5]  F7 FF FF FF FF
2140-  can0  7E3   [8]  02 10 01 00 00 00 00 00
2141-  can0  03C   [8]  F3 AE 02 12 01 00 2A FF
2142-  can0  130   [5]  F7 FF FF FF FF
2143-  can0  7E4   [8]  02 10 01 00 00 00 00 00
2144:  can0  7EC   [8]  06 50 01 00 32 01 F4 55
2145-  can0  03C   [8]  F2 A0 02 12 01 00 2A FF
2146-  can0  130   [5]  F7 FF FF FF FF
2147-  can0  7E5   [8]  02 10 01 00 00 00 00 00
2148-  can0  03C   [8]  AF A1 02 12 01 00 2A FF
2149-  can0  130   [5]  F7 FF FF FF FF
2150-  can0  7E6   [8]  02 10 01 00 00 00 00 00
2151-  can0  799   [7]  1F 01 17 04 0D 03 0A
2152-  can0  03C   [8]  48 A2 02 12 01 00 2A FF
2153-  can0  130   [5]  F7 FF FF FF FF
2154-  can0  7E7   [8]  02 10 01 00 00 00 00 00
2155:  can0  7EF   [8]  06 50 01 00 32 01 F4 FF
2156-  can0  03C   [8]  15 A3 02 12 01 00 2A FF
2157-  can0  130   [5]  F7 FF FF FF FF
2158-  can0  7E8   [8]  02 10 01 00 00 00 00 00
2159-  can0  03C   [8]  9B A4 02 12 01 00 2A FF
2160-  can0  130   [5]  F7 FF FF FF FF
2161-  can0  7E9   [8]  02 10 01 00 00 00 00 00
--
2183-  can0  130   [5]  F7 FF FF FF FF
2184-  can0  7F0   [8]  02 10 01 00 00 00 00 00
2185-  can0  799   [7]  1F 01 16 04 0C 03 0A
2186-  can0  03C   [8]  49 AC 02 12 01 00 2A FF
2187-  can0  130   [5]  F7 FF FF FF FF
2188-  can0  7F1   [8]  02 10 01 00 00 00 00 00
2189:  can0  7F9   [8]  06 50 01 00 32 01 F4 00
2190-  can0  03C   [8]  14 AD 02 12 01 00 2A FF
2191-  can0  130   [5]  F7 FF FF FF FF
2192-  can0  7F2   [8]  02 10 01 00 00 00 00 00
2193-  can0  03C   [8]  F3 AE 02 12 01 00 2A FF
2194-  can0  130   [5]  F7 FF FF FF FF
2195-  can0  7F3   [8]  02 10 01 00 00 00 00 00
"""
