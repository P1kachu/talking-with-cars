#!/usr/bin/env python3

import can

INTERFACE="can0"

def print_bits(n, buf):
    for i in range(n):
        print(bin(buf[i]), end=' ')
    print()


def send_and_wait(bus, arb_id, data, extended):
    msg = can.Message(arbitration_id=arb_id, data=data, extended_id=extended)
    bus.send(msg)
    #print("TX: {0}: {1})".format(hex(msg.arbitration_id), msg.data))
    answer = bus.recv()
    #print("RX: {0}: {1})".format(hex(answer.arbitration_id), answer.data))
    return answer

bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')

# supported PIDs [0-20]
#answer = send_and_wait(bus, 0x7df, [2, 1, 0, 0, 0, 0, 0, 0], False)
#print_bits(4, answer.data)

# Engine coolant temperature
answer = send_and_wait(bus, 0x7df, [2, 1, 5, 0, 0, 0, 0, 0], False)
temperature = answer.data[3] - 40
print("Temperature: {0} degrees".format(temperature))

# RPM
answer = send_and_wait(bus, 0x7df, [2, 1, 0xc, 0, 0, 0, 0, 0], False)
print("{0} rpm".format((answer.data[3] * 256 + answer.data[4])/4))

# OBD standard this vehicle conforms to
answer = send_and_wait(bus, 0x7df, [2, 1, 0x1c, 0, 0, 0, 0, 0], False)
print("OBD Standard: {0}".format(answer.data[2]))

# Vehicle speed
answer = send_and_wait(bus, 0x7df, [2, 1, 0xd, 0, 0, 0, 0, 0], False)
print("{0} km/h".format(answer.data[3]))
