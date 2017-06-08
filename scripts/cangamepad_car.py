#!/usr/bin/env python3

import can
import socket
import struct

INTERFACE='vcan0'
IP='10.1.1.100'
PORT=12345
can_29bits_diagnostic_id = 0x18DB33F1
diagnostic_id = can_29bits_diagnostic_id
extended = (diagnostic_id == can_29bits_diagnostic_id)

def _is_answer(answer, data):
    '''
    Check if the message received answers our query
    '''
    ret = True

    if len(answer.data) < 3:
        return False

    ret &= (answer.data[1] == data[1] + 0x40) # REQUEST MODE
    ret &= (answer.data[2] == data[2])        # REQUEST PID

    return ret

def can_xchg(bus, arb_id, data, ext=False):
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

    return answer.data[byte_nb]

def get_speed(bus):
    answer = can_xchg(bus, diagnostic_id, [2, 1, 0xd, 0, 0, 0, 0, 0], extended)
    if answer is None:
        return 0
    return answer.data[3]

def get_accel_pos(bus):
    answer = can_xchg(bus, diagnostic_id, [2, 1, 0x49, 0, 0, 0, 0, 0], extended)
    if answer is None:
        return 0
    return answer.data[3]

def get_handbrake(bus):
    return can29_recv(bus, 0x0a18a000, 0) != 0

def get_pedals(bus):
    clutch_p = can29_recv(bus, 0x0628a001, 5)
    clutch_p = min(int(clutch_p / 0x10), 2) & 0b10

    brake_p = can29_recv(bus, 0x0810a000, 2)
    brake_p = bin(brake_p >> 4).count("1") - 1

    accel_p = get_accel_pos(bus)
    accel_p = int((accel_p - 0x26) / 255)

    return (clutch_p, brake_p, accel_p)


if __name__ in "__main__":
    bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", PORT))

    test = 0
    while 1:
       speed = get_speed(bus)
       handbrake = get_handbrake(bus)
       (clutch, brakes, accelerator) = get_pedals(bus)
       steering_angle = test #TODO

       ### DEBUG
       test += 1
       if test == 255:
           test = 0
       print(speed, handbrake, clutch, brakes, accelerator, steering_angle)
       ### DEBUG

       msg = b''
       msg += struct.pack("B", speed)
       msg += struct.pack("?", handbrake)
       msg += struct.pack("B", clutch)
       msg += struct.pack("B", brakes)
       msg += struct.pack("B", accelerator)
       msg += struct.pack("!I", steering_angle)
       msg += struct.pack("!I", steering_angle) # Hack to solve unpack issue
       s.sendto(msg, (IP, PORT))


