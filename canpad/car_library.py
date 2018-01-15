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
        0x224: [ [ "brake-b",       5,  1  ], ],
        0x260: [ [ "steering",      40, 24, steering_recv, steering_send ], ],
        0x2c4: [ [ "engine-rev-a",  0,  16 ], ],
        0x3b3: [ [ "engine-rev-b",  0,  16 ], ],
        0x3b4: [ [ "brake-a",       32, 1  ], ],
        0x610: [ [ "speed-b",       8,  16 ], ],
        0x611: [ [ "km-count",      40, 24 ], ],
        0x620: [ [ "door-fl",       45, 1  ], \
                 [ "door-fr",       44, 1  ], \
                 [ "door-rl",       43, 1  ], \
                 [ "door-rr",       42, 1  ], \
                 [ "door-trunk",    41, 1  ], \
                 [ "parking-brake", 60, 8  ]  ],
        0x621: [ [ "lock-trig",     8,  16 ], ],
    }

    '''
    Need to  find how to compute these values
        0x2c1: an accelerator related value
        0x3b3: an accelerator related value too
        steering: find correct constants
    '''
