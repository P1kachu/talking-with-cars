#!/usr/bin/env python3

import can
import socket
import struct

# CANPad - Car server - v1.0
# Use this script on the car to send the data
# over UDP

INTERFACE='can0'
IP='10.1.1.100'
PORT=12345

can_29bits_diagnostic_id = 0x18DB33F1
diagnostic_id = can_29bits_diagnostic_id
extended = (diagnostic_id == can_29bits_diagnostic_id)

WHOLE_MESSAGE_CNST=-1
MAX_STEERING_CNST=0x450

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

    if byte_nb == WHOLE_MESSAGE_CNST:
        return answer

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
    answer = None
    arb_id = 0x18DA28F1 # ABS ECU
    data = [0x3, 0x22, 0x08, 0x89, 0, 0, 0, 0]
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

    return answer.data[5] & 1

def get_pedals(bus):
    # 0 or 1
    clutch_p = can29_recv(bus, 0x0628a001, 5)
    clutch_p = min(int(clutch_p / 0x10), 2) & 0b10

    # 0 to 2
    brake_p = can29_recv(bus, 0x0810a000, 2)
    brake_p = bin(brake_p >> 4).count("1") - 1

    # 0 to 100
    accel_p = can29_recv(bus, 0x0618a001, 7)
    accel_p = int(accel_p / 255 * 100)

    return (clutch_p, brake_p, accel_p)

def get_steering_wheel(bus):
    # http://www.fiatforum.com/tech-talk/451078-obd-ii-epid-steering-wheel-angle.html#post4271629
    # https://www.sparkfun.com/datasheets/Widgets/ELM327_AT_Commands.pdf
    answer = None
    arb_id = 0x18DA30f1 # Steering column ECU
    data = [0x3, 0x22, 0x09, 0x48, 0, 0, 0, 0]
    while not answer or answer.arbitration_id != 0x18daf130:
        try:
            msg = can.Message(arbitration_id=arb_id, data=data, extended_id=True)
            bus.send(msg)
            answer = bus.recv(0.1)
        except OSError:
            pass

    # Send UDS ACK
    msg = can.Message(arbitration_id=arb_id, data=[0x30, 0, 0, 0, 0, 0, 0, 0], extended_id=True)
    bus.send(msg)

    value = answer.data[5] * 256 + answer.data[6]

    if value > 0x8000:
        value = -(0x10000 - value)

    # 0 to MAX_STEERING_CNST * 2 (because sent as unsigned)
    return value + MAX_STEERING_CNST

if __name__ in "__main__":
    bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", PORT))

    # Initialize an UDS critical diagnosis session (for the ECUs)
    # https://en.wikipedia.org/wiki/Unified_Diagnostic_Services
    can_xchg(bus, 0x18DA30f1, [0x2, 0x10, 0x03, 0, 0, 0, 0, 0], True)

    while 1:
       speed = get_speed(bus)
       handbrake = get_handbrake(bus)
       (clutch, brakes, accelerator) = get_pedals(bus)
       steering_angle = get_steering_wheel(bus)

       msg = b''
       msg += struct.pack("B", speed)
       msg += struct.pack("B", handbrake)
       msg += struct.pack("B", clutch)
       msg += struct.pack("B", brakes)
       msg += struct.pack("B", accelerator)
       msg += struct.pack("3B", 0, 0, 0) # Padding
       msg += struct.pack("L", steering_angle)
       print(msg)
       s.sendto(msg, (IP, PORT))


