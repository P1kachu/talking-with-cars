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
    #print("TX: {0}: {1})".format(hex(msg.arbitration_id), msg.data))
    answer = bus.recv()
    #print("RX: {0}: {1})".format(hex(answer.arbitration_id), answer.data))
    return answer

def bf(bus):
    for y in range(0xff):
        for x in range(0xff):
            answer = can_xchg(bus, 0x7df, [3, 1, x, y, 0, 0, 0, 0])
            if answer is not None:
                print(answer)


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

# Mode 1 supported PIDs
answer = can_xchg(bus, 0x7df, [2, 1, 0x00, 0, 0, 0, 0, 0])
print(get_bits_msb(4, answer.data))
answer = can_xchg(bus, 0x7df, [2, 1, 0x20, 0, 0, 0, 0, 0])
print(get_bits_msb(4, answer.data))
answer = can_xchg(bus, 0x7df, [2, 1, 0x40, 0, 0, 0, 0, 0])
print(get_bits_msb(4, answer.data))
answer = can_xchg(bus, 0x7df, [2, 1, 0x60, 0, 0, 0, 0, 0])
print(get_bits_msb(4, answer.data))

# Mode 9 supported PIDs
answer = can_xchg(bus, 0x7df, [2, 9, 0x00, 0, 0, 0, 0, 0])
bits = get_bits_msb(4, answer.data)
if bits[0xa]:
    answer = can_xchg(bus, 0x7df, [2, 9, 0x09, 0, 0, 0, 0, 0])
    answer = can_xchg(bus, 0x7df, [2, 9, 0x0a, 0, 0, 0, 0, 0])
    for i in range(answer.data[3] - 1):
        print(bus.recv())
else:
    print("PID 9:0xa not supported")

