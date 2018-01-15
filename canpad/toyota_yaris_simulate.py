#!/usr/bin/python3

import fake_car_src
import can_sink
import can_helpers
import car_library

'''
This file shows you am example of a FakeCarSrc.
When launched, this script will simulate a basic
car output on the specified can bus

This file is setup to simulate a Toyota Yaris output.
You can change it to any car already added in the library.

'''


# Interface selection
interface = "vcan0"

# Change the car here
known_fields = car_library.ToyotaYaris.get_known_fields()

sink = can_sink.CanSink(interface, known_fields)
src = fake_car_src.FakeCarSrc(sink, known_fields)

while src.listen():
    values = {
        "speed": src.speed,
        "engine-rev-a": src.engine_rev,
    }

    src.send_values(values)
