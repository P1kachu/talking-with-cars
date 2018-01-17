import can_helpers

class ToyotaYaris:
    def speed_recv(value):
        return value * 0.01

    def speed_send(value):
        return int(value * 100.0)

    def steering_recv(value):
        return 0

    def steering_send(value):
        return 0

    def get_known_fields():
        return can_helpers.dict_to_fields(ToyotaYaris.fields)

    fields = {
        0x0b4: [ [ "speed",         40, 16, speed_recv, speed_send ], ],
        0x0b0: [ [ "wheel-fl",      0,  16 ], \
                 [ "wheel-fr",      16, 16 ], ],
        0x0b2: [ [ "wheel-bl",      0,  16 ], \
                 [ "wheel-br",      16, 16 ], ],
        0x224: [ [ "brake-b",       2,  1  ], ],
        0x260: [ [ "steering",      40, 24, steering_recv, steering_send ], ],
        0x2c4: [ [ "engine-rev-a",  0,  16 ], \
                 [ "unknown 2",  54,  8 ], ],
        0x3b3: [ [ "engine-rev-b",  0,  16 ], ],
        0x3b4: [ [ "brake-a",       39, 1  ], ],
        0x610: [ [ "speed-b",       8,  16 ], ],
        0x611: [ [ "km-count",      40, 24 ], ],
        0x620: [ [ "door-rl+rr",    44, 2  ], \
                 [ "door-fr",       43, 1  ], \
                 [ "door-fl",       42, 1  ], \
                 [ "door-trunk",    46, 1  ], \
                 [ "parking-brake", 59, 1  ]  ],
        0x621: [ [ "lock-trig",     8,  1 ], \
                 [ "lock-err",     16,  1 ], ],
        0x398: [ [ "throttle slow", 0,  16 ], ],
        0x638: [ [ "door unlocked",  19,  1 ], ],
    }

    '''
    Need to  find how to compute these values
        0x2c1: an accelerator related value
        0x3b3: an accelerator related value too
        steering: find correct constants
    '''

class Peugeot207_2008_diesel:
    fields = {
        0x208: [ [ "throttle-a", 32, 8], ],
        0x228: [ [ "throttle-b", 16, 8], ],
        0x50d: [ [ "brake", 47, 1], ],
        0x412: [ [ "parking-brake", 4, 1], ],
    }

    def get_known_fields():
        return can_helpers.dict_to_fields(Peugeot207_2008_diesel.fields)
