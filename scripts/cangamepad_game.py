#!/usr/bin/env python3
import foohid
import struct
import random
import time
import socket


PORT=12345
DEVICE_NAME="FooHID CAN Joypad"

xbox = (
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x05,        # Usage (Game Pad)
    0xA1, 0x01,        # Collection (Application)

    0x05, 0x01,        #    Usage Page (Generic Desktop)
    0x09, 0x3A,        #    Usage (Counted Buffer)      #XXX
    0xA1, 0x02,        #    Collection (Logical)

                       # padding
    0x75, 0x08,        #       Report Size (8)
    0x95, 0x01,        #       Report Count (1)
    0x81, 0x01,        #       Input (Constant)

                       # byte count
    0x75, 0x08,        #       Report Size (8)
    0x95, 0x01,        #       Report Count (1)
    0x05, 0x01,        #       Usage Page (Generic Desktop)
    0x09, 0x3B,        #       Usage (Byte Count)      #XXX
    0x81, 0x01,        #       Input (Constant)

                       # D-pad
    0x05, 0x01,        #       Usage Page (Generic Desktop)
    0x09, 0x01,        #       Usage (Pointer)
    0xA1, 0x00,        #       Collection (Physical)
    0x75, 0x01,        #          Report Size (1)
    0x15, 0x00,        #          Logical Minimum (0)
    0x25, 0x01,        #          Logical Maximum (1)
    0x35, 0x00,        #          Physical Minimum (0)
    0x45, 0x01,        #          Physical Maximum (1)
    0x95, 0x04,        #          Report Count (4)
    0x05, 0x01,        #          Usage Page (Generic Desktop)
    0x09, 0x90,        #          Usage (D-pad Up)
    0x09, 0x91,        #          Usage (D-pad Down)
    0x09, 0x93,        #          Usage (D-pad Left)
    0x09, 0x92,        #          Usage (D-pad Right)
    0x81, 0x02,        #          Input (Data,Variable,Absolute)
    0xC0,              #        End Collection

                       # start, back, stick press
    0x75, 0x01,        #       Report Size (1)
    0x15, 0x00,        #       Logical Minimum (0)
    0x25, 0x01,        #       Logical Maximum (1)
    0x35, 0x00,        #       Physical Minimum (0)
    0x45, 0x01,        #       Physical Maximum (1)
    0x95, 0x04,        #       Report Count (4)
    0x05, 0x09,        #       Usage Page (Button)
    0x19, 0x07,        #       Usage Minimum (Button 7)
    0x29, 0x0A,        #       Usage Maximum (Button 10)
    0x81, 0x02,        #       Input (Data,Variable,Absolute)

                       # reserved
    0x75, 0x01,        #       Report Size (1)
    0x95, 0x08,        #       Report Count (8)
    0x81, 0x01,        #       Input (Constant)

                       # analog buttons
    0x75, 0x08,        #       Report Size (8)
    0x15, 0x00,        #       Logical Minimum (0)
    0x26, 0xFF, 0x00,  #       Logical Maximum (255)
    0x35, 0x00,        #       Physical Minimum (0)
    0x46, 0xFF, 0x00,  #       Physical Maximum (255)
    0x95, 0x06,        #       Report Count (6)
    0x05, 0x09,        #       Usage Page (Button)
    0x19, 0x01,        #       Usage Minimum (Button 1)
    0x29, 0x06,        #       Usage Minimum (Button 6)
    0x81, 0x02,        #       Input (Data,Variable,Absolute)

                       # triggers
    0x75, 0x08,        #       Report Size (8)
    0x15, 0x00,        #       Logical Minimum (0)
    0x26, 0xFF, 0x00,  #       Logical Maximum (255)
    0x35, 0x00,        #       Physical Minimum (0)
    0x46, 0xFF, 0x00,  #       Physical Maximum (255)
    0x95, 0x02,        #       Report Count (2)
    0x05, 0x01,        #       Usage Page (Generic Desktop)
    0x09, 0x32,        #       Usage (Z)
    0x09, 0x35,        #       Usage (Rz)
    0x81, 0x02,        #       Input (Data,Variable,Absolute)

                       # sticks
    0x75, 0x10,        #       Report Size (16)
    0x16, 0x00, 0x80,  #       Logical Minimum (-32768)
    0x26, 0xFF, 0x7F,  #       Logical Maximum (32767)
    0x36, 0x00, 0x80,  #       Physical Minimum (-32768)
    0x46, 0xFF, 0x7F,  #       Physical Maximum (32767)

    0x05, 0x01,        #       Usage Page (Generic Desktop)
    0x09, 0x01,        #       Usage (Pointer)
    0xA1, 0x00,        #       Collection (Physical)
    0x95, 0x02,        #          Report Count (2)
    0x05, 0x01,        #          Usage Page (Generic Desktop)
    0x09, 0x30,        #          Usage (X)
    0x09, 0x31,        #          Usage (Y)         #north positive
    0x81, 0x02,        #          Input (Data,Variable,Absolute)
    0xC0,              #        End Collection

    0x05, 0x01,        #       Usage Page (Generic Desktop)
    0x09, 0x01,        #       Usage (Pointer)
    0xA1, 0x00,        #       Collection (Physical)
    0x95, 0x02,        #          Report Count (2)
    0x05, 0x01,        #          Usage Page (Generic Desktop)
    0x09, 0x33,        #          Usage (Rx)
    0x09, 0x34,        #          Usage (Ry)         #north positive
    0x81, 0x02,        #          Input (Data,Variable,Absolute)
    0xC0,              #        End Collection

    0xC0,              #     End Collection

    0x05, 0x01,        #    Usage Page (Generic Desktop)
    0x09, 0x3A,        #    Usage (Counted Buffer)      #XXX
    0xA1, 0x02,        #    Collection (Logical)

                       # padding
    0x75, 0x08,        #       Report Size (8)
    0x95, 0x01,        #       Report Count (1)
    0x91, 0x01,        #       Output (Constant)

                       # byte count
    0x75, 0x08,        #       Report Size (8)
    0x95, 0x01,        #       Report Count (1)
    0x05, 0x01,        #       Usage Page (Generic Desktop)
    0x09, 0x3B,        #       Usage (Byte Count)      #XXX
    0x91, 0x01,        #       Output (Constant)

                       # padding
    0x75, 0x08,        #       Report Size (8)
    0x95, 0x01,        #       Report Count (1)
    0x91, 0x01,        #       Output (Constant)

                       # left actuator
    0x75, 0x08,        #       Report Size (8)
    0x15, 0x00,        #       Logical Minimum (0)
    0x26, 0xFF, 0x00,  #       Logical Maximum (255)
    0x35, 0x00,        #       Physical Minimum (0)
    0x46, 0xFF, 0x00,  #       Physical Maximum (255)
    0x95, 0x01,        #       Report Count (1)
    0x06, 0x00, 0xFF,  #       Usage Page (vendor-defined)
    0x09, 0x01,        #       Usage (1)
    0x91, 0x02,        #       Output (Data,Variable,Absolute)

                       # padding
    0x75, 0x08,        #       Report Size (8)
    0x95, 0x01,        #       Report Count (1)
    0x91, 0x01,        #       Output (Constant)

                       # right actuator
    0x75, 0x08,        #       Report Size (8)
    0x15, 0x00,        #       Logical Minimum (0)
    0x26, 0xFF, 0x00,  #       Logical Maximum (255)
    0x35, 0x00,        #       Physical Minimum (0)
    0x46, 0xFF, 0x00,  #       Physical Maximum (255)
    0x95, 0x01,        #       Report Count (1)
    0x06, 0x00, 0xFF,  #       Usage Page (vendor-defined)
    0x09, 0x02,        #       Usage (2)
    0x91, 0x02,        #       Output (Data,Variable,Absolute)

    0xC0,              #     End Collection

    0xC0,              #  End Collection
        )

def convert(data):
    return struct.unpack_from("B?BBBI", data)

def get_steering(steering_angle):
    return steering_angle

def create_output_report(data):
    speed, handbrake, clutch, brakes, accelerator, steering_angle = convert(data)
    print(speed, handbrake, clutch, brakes, accelerator, steering_angle)
    steering = get_steering(steering_angle)
    return struct.pack('12B4H',
            0, 0x14, 0, 0,       # 0, sizeof(report), digital buttons, reserved
            handbrake,           # A button
            0, 0, 0, 0, 0,       # B, X, y, Black, White
            brakes, accelerator, # Left and Right triggers
            steering, 0,         # Left stick X and Y axis
            0, 0)                # Right stick X and Y axis


try:
    foohid.destroy(DEVICE_NAME)
except:
    pass
foohid.create(DEVICE_NAME,
        struct.pack('{0}B'.format(len(xbox)), *xbox),
        "SN 123",
        2,
        3)
print("Created device")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", PORT))
    print("Created socket")

    while True:
        data = s.recv(1024)
        #print("Received {0}".format(data))
        out_report = create_output_report(data)
        foohid.send(DEVICE_NAME, out_report)

except KeyboardInterrupt:
    foohid.destroy(DEVICE_NAME)
