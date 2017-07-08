#!/usr/bin/env python3

import time
import socket
import struct
import sys
from evdev import UInput, InputDevice, ecodes as e

# CANPad - Gamepad client - v2.0
# Use this script on the receiver computer
# to send data over evdev by hijacking your controller

DEFAULT_XBOX_CONTROLLER_PATH = '/dev/input/event13'
PORT=12345
STEERING_MAX_ABS_CNST = 0x450
STEERING_MAX_GAME_CNST = 32767

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
    if len(sys.argv) > 1:
        gamepad_path = sys.argv[1]
    else:
        gamepad_path = DEFAULT_XBOX_CONTROLLER_PATH

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", PORT))
    print("Created socket")

    xbox = InputDevice(gamepad_path)
    print("Waiting for input")
    while True:
        data = s.recv(1024)
        (speed, handbrake, clutch, brakes, accelerator, steering_angle) = parse_data(data)
        if handbrake:
            xbox.write(e.EV_KEY, e.BTN_SOUTH, 1)
        else:
            xbox.write(e.EV_KEY, e.BTN_SOUTH, 0)

        xbox.write(e.EV_ABS, e.ABS_X, steering_angle)
        xbox.write(e.EV_ABS, e.ABS_RZ, accelerator)
        xbox.write(e.EV_ABS, e.ABS_Z, brakes)

        #print(handbrake, brakes, accelerator, steering_angle)
        #time.sleep(0.3)
except Exception as e:
    print(e)
    pass

