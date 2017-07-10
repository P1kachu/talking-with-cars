#!/usr/bin/env python3

import time
import socket
import struct
import sys
from evdev import UInput, InputDevice, ecodes as e, InputEvent

# CANPad - Gamepad client - v2.0
# Use this script on the receiver computer
# to send data over evdev by hijacking your controller
# Settings for Dirt Showdown

# Path to XBox evdev
DEFAULT_XBOX_CONTROLLER_PATH = '/dev/input/event13'

# UDP port to receive data from
PORT=12345

# Max steering angle sent by car
STEERING_MAX_ABS_CNST = 0x450

# Max steering angle understood by game
# This allows one to fully steer in the game
# without the need to fully steer in the car
# when FULL_WHEEL_ENABLED is False
STEERING_MAX_VIRTUAL_CNST = int(STEERING_MAX_ABS_CNST / 5)
FULL_WHEEL_ENABLED = False

# Max value taken by the gamepad
STEERING_MAX_GAME_CNST = 32767

VERBOSE = False

# Gamepad buttons mapping
HANDBRAKE_BUTTON = e.BTN_EAST
STEERING_BUTTON = e.ABS_X
ACCELERATOR_BUTTON = e.ABS_RZ
BRAKES_BUTTON = e.ABS_Z


def convert(data):
    return struct.unpack_from("BBBBBI", data)

def get_steering(steering_angle):
    steering_angle -= STEERING_MAX_ABS_CNST
    if FULL_WHEEL_ENABLED:
        steering_angle = int((steering_angle / STEERING_MAX_ABS_CNST) * STEERING_MAX_GAME_CNST)
    else:
        steering_angle = int((steering_angle / STEERING_MAX_VIRTUAL_CNST) * STEERING_MAX_GAME_CNST)
    return steering_angle

def parse_data(data):
    speed, handbrake, clutch, brakes, accelerator, steering_angle = convert(data)
    steering = get_steering(steering_angle)
    brakes = int(brakes/2 * 255)
    accelerator = int(min(accelerator / 1, 1) * 255)
    return (speed, handbrake, clutch, brakes, accelerator, steering)


try:
    if len(sys.argv) > 1:
        gamepad_path = sys.argv[1]
    else:
        print("[*] Usage: {0} PATH_TO_XBOX_EVDEV".format(sys.argv[0]))
        print("[*] Defaulting to path: {0}".format(DEFAULT_XBOX_CONTROLLER_PATH))
        gamepad_path = DEFAULT_XBOX_CONTROLLER_PATH

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", PORT))
    s.setblocking(0)
    print("[*] Created UDP socket")


    xbox = InputDevice(gamepad_path)
    while True:
        try:
            data = s.recv(1024)
            break
        except:
            pass

    print("[*] Waiting for input")
    while True:
        try:
            newdata = s.recv(1024)
            data = newdata
        except:
            pass

        (speed, handbrake, clutch, brakes, accelerator, steering_angle) = parse_data(data)
        if handbrake:
            xbox.write(e.EV_KEY, HANDBRAKE_BUTTON, 1)
        else:
            xbox.write(e.EV_KEY, HANDBRAKE_BUTTON, 0)
        xbox.write_event(InputEvent(1334414993, 274296, e.EV_SYN, 0, 0))

        xbox.write(e.EV_ABS, STEERING_BUTTON, steering_angle)
        xbox.write_event(InputEvent(1334414993, 274296, e.EV_SYN, 0, 0))
        xbox.write(e.EV_ABS, ACCELERATOR_BUTTON, accelerator)
        xbox.write_event(InputEvent(1334414993, 274296, e.EV_SYN, 0, 0))
        xbox.write(e.EV_ABS, BRAKES_BUTTON, brakes)
        xbox.write_event(InputEvent(1334414993, 274296, e.EV_SYN, 0, 0))

        if VERBOSE:
            print(handbrake, brakes, accelerator, steering_angle)
except Exception as e:
    print(e)
    pass

