#!/usr/bin/env python3

import can

INTERFACE="vcan0"

def print_bits(n, buf):
    for i in range(n):
        print(bin(buf[i]), end=' ')
    print()


def send_and_wait(bus, arb_id, data, extended):
    msg = can.Message(arbitration_id=arb_id, data=data, extended_id=extended)
    bus.send(msg)
    #print("TX: {0}: {1})".format(hex(msg.arbitration_id), msg.data))
    answer = bus.recv()
    print("RX: {0}: {1})".format(hex(answer.arbitration_id), answer.data))
    return answer

def get_ecu_name(bus):
    answer = send_and_wait(bus, 0x7df, [2, 9, 0, 0, 0, 0, 0, 0], False)
    if not ((1 << 0xa) & answer.data[3])
        print("ECU name command not supported")
        return
    answer = send_and_wait(bus, 0x7df, [2, 9, 0xa, 0, 0, 0, 0, 0], False)
    answer += answer.data
    answer += bus.recv(),data
    answer += bus.recv().data
    answer += bus.recv().data
    answer += bus.recv().data



bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')

# supported PIDs [0-20]
answer = send_and_wait(bus, 0x7df, [2, 1, 0, 0, 0, 0, 0, 0], False)
print_bits(4, answer.data)

# supported PIDs [21-40]
answer = send_and_wait(bus, 0x7df, [2, 1, 0x20, 0, 0, 0, 0, 0], False)
print_bits(4, answer.data)

# supported PIDs [41-60]
answer = send_and_wait(bus, 0x7df, [2, 1, 0x40, 0, 0, 0, 0, 0], False)
print_bits(4, answer.data)

# supported PIDs [61-80]
answer = send_and_wait(bus, 0x7df, [2, 1, 0x60, 0, 0, 0, 0, 0], False)
print_bits(4, answer.data)


# Engine coolant temperature
asnwer = send_and_wait(bus, 0x7df, [2, 1, 5, 0, 0, 0, 0, 0], False)
temperature = answer.data[3] - 40
print("Temperature: {0} degrees".format(temperature))

# RPM
asnwer = send_and_wait(bus, 0x7df, [2, 1, 0xc, 0, 0, 0, 0, 0], False)
print("{0} rpm".format((answer.data[3] * 256 + answer.data[4])/4))

# OBD standard this vehicle conforms to
asnwer = send_and_wait(bus, 0x7df, [2, 1, 0x1c, 0, 0, 0, 0, 0], False)
print("OBD Standard: {0}".format(answer.data[2]))

get_ecu_name(bus)
