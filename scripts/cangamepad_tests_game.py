#!/usr/bin/env python3
import foohid
import struct
import random
import time
import socket


PORT=12345
DEVICE_NAME="FooHID CAN Joypad"
STEERING_MAX_ABS_CNST = 0x450 * 2

keyboard = (
    0x05, 0x01,
    0x09, 0x06,
    0xa1, 0x01,
    0x05, 0x07,
    0x19, 0xe0,
    0x29, 0xe7,
    0x15, 0x00,
    0x25, 0x01,
    0x75, 0x01,
    0x95, 0x08,
    0x81, 0x02,
    0x95, 0x01,
    0x75, 0x08,
    0x81, 0x01,
    0x95, 0x05,
    0x75, 0x01,
    0x05, 0x08,
    0x19, 0x01,
    0x29, 0x05,
    0x91, 0x02,
    0x95, 0x01,
    0x75, 0x03,
    0x91, 0x01,
    0x95, 0x06,
    0x75, 0x08,
    0x15, 0x00,
    0x25, 0x65,
    0x05, 0x07,
    0x19, 0x00,
    0x29, 0x65,
    0x81, 0x00,
    0x09, 0x00,
    0x75, 0x08,
    0x95, 0x01,
    0x15, 0x00,
    0x25, 0x7f,
    0xb1, 0x02,
    0xc0
)

def convert(data):
    return struct.unpack_from("BBBBBI", data)

def get_steering(steering_angle):
    steering_angle = int((steering_angle / STEERING_MAX_ABS_CNST) * 255)
    return steering_angle

def create_output_report(data):
    speed, handbrake, clutch, brakes, accelerator, steering_angle = convert(data)
    print(speed, handbrake, clutch, brakes, accelerator, steering_angle)
    steering = get_steering(steering_angle)
    return (speed, handbrake, clutch, brakes, accelerator, steering)

try:
    foohid.send("FooHID simple keyboard", struct.pack('8B', 0, 0, 0, 0, 0, 0, 0, 0))
    foohid.destroy("FooHID simple keyboard")
except:
    pass

try:
    foohid.create("FooHID simple keyboard",
            struct.pack('{0}B'.format(len(keyboard)), *keyboard),
            "SN 123",
            2,
            3)
except:
    foohid.send("FooHID simple keyboard", struct.pack('8B', 0, 0, 80, 0, 0, 0, 0, 0))
    exit(0)

print("Created device")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", PORT))
print("Created socket")

accel = 20
steering = 127

keys = [0,0,0,0]
tmp_keys = [0,0,0,0]
try:
    while True:
        if 0: # DEBUG
            accel -= 1
            if accel == -20:
                accel = 20
            accelerator = accel
            brakes = (accel < - 10)
            handbrake = (accel < - 15)
            steering += 1
            if steering >= 255:
                steering = 0
        else:
            data = s.recv(1024)
            speed, handbrake, clutch, brakes, accelerator, steering = create_output_report(data)

        keys[0] = 0
        keys[1] = 0
        keys[2] = 0
        keys[3] = 0

        if handbrake:
            keys[0] = 0x2c
        if accelerator > 0:
            keys[1] = 0x52
        if steering < 100:
            keys[2] = 0x50
        elif steering > 154:
            keys[2] = 0x4f
        else:
            keys[2] = 0
        if brakes:
            keys[3] = 0x51

        reset = False
        for i in range(4):
            if keys[i] != tmp_keys[i]:
                reset = True
                #print("Reset")
            tmp_keys[i] = keys[i]

        if reset:
            #foohid.send("FooHID simple keyboard", struct.pack('8B', 0, 0, 0, 0, 0, 0, 0, 0))
            #time.sleep(1)
            pass
        else:
            time.sleep(0.2)

        foohid.send("FooHID simple keyboard",
                    struct.pack('8B',
                        0,
                        0,
                        keys[0],
                        keys[1],
                        keys[2],
                        keys[3],
                        0,
                        0)
                    )

except Exception as e:
    print(e)
    # make sure key is unpressed before exiting
    foohid.send("FooHID simple keyboard", struct.pack('8B', 0, 0, 0, 0, 0, 0, 0, 0))
    foohid.destroy("FooHID simple keyboard")

