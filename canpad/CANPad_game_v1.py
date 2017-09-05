#!/usr/bin/env python3

import uinput
import time
import random
import socket
import struct

# CANPad - Gamepad client - v1.0
# Use this script on the receiver computer
# to send data over uinput to your game

#CONTROLLER = "Microsoft X-Box 360 pad - P1ka"
CONTROLLER = "P1ka - Fiat 500c CANPad 1.0"
VENDOR = 0x45e
PRODUCT = 0x28e
VERSION = 101
PORT=12345
STEERING_MAX_ABS_CNST = 0x450
STEERING_MAX_GAME_CNST = 32767

events = (
    uinput.BTN_SOUTH,                       # Handbrake
    uinput.BTN_EAST,
    uinput.BTN_NORTH,
    uinput.BTN_WEST,                        # TODO: Change camera
    uinput.BTN_TL,                          # TODO: Gear down
    uinput.BTN_TR,                          # TODO: Gear up
    uinput.BTN_SELECT,
    uinput.BTN_START,
    uinput.BTN_MODE,
    uinput.BTN_THUMBL,
    uinput.BTN_THUMBR,

    uinput.ABS_X + (-32768, 32767, 0, 0),   # Steering wheel
    uinput.ABS_Y + (-32768, 32767, 0, 0),
    uinput.ABS_RX + (-32768, 32767, 0, 0),
    uinput.ABS_RY + (-32768, 32767, 0, 0),
    uinput.ABS_GAS + (0, 255, 0, 0),        # Accelerator
    uinput.ABS_BRAKE + (0, 255, 0, 0),      # Brakes
    uinput.ABS_HAT0X + (-1, 1, 0, 0),
    uinput.ABS_HAT0Y + (-1, 1, 0, 0),

    )

def convert(data):
    return struct.unpack_from("BBBBBI", data)

def get_steering(steering_angle):
    steering_angle -= STEERING_MAX_ABS_CNST
    steering_angle = int((steering_angle / STEERING_MAX_ABS_CNST) * STEERING_MAX_GAME_CNST)
    return steering_angle

def parse_data(data):
    speed, handbrake, clutch, brakes, accelerator, steering_angle = convert(data)
    steering = get_steering(steering_angle)
    brakes = int(brakes/2 * 255)
    accelerator = int(min(accelerator / 1, 1) * 255)
    #print(speed, handbrake, clutch, brakes, accelerator, steering_angle)
    return (speed, handbrake, clutch, brakes, accelerator, steering)


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", PORT))
    print("Created socket")

    with uinput.Device(events,
                       name=CONTROLLER,
                       vendor=VENDOR,
                       product=PRODUCT,
                       bustype=3,
                       version=VERSION,
                       ) as device:
        print("Device created")
        time.sleep(1)
        print("Launching emulation")
        while True:
            data = s.recv(1024)
            (speed, handbrake, clutch, brakes, accelerator, steering_angle) = parse_data(data)
            if handbrake:
                device.emit(uinput.BTN_SOUTH, 1, syn=True)
            else:
                device.emit(uinput.BTN_SOUTH, 0, syn=True)
            device.emit(uinput.ABS_X, steering_angle, syn=True)
            if not clutch:
                device.emit(uinput.ABS_GAS, accelerator, syn=True)
            device.emit(uinput.ABS_BRAKE, brakes, syn=True)
            #print(handbrake, brakes, accelerator, steering_angle)
            #time.sleep(0.3)
except Exception as e:
    print(e)
    pass

