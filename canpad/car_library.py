import can_helpers

'''
    How to add a car:

    A valid class has a get_known_fields function.
    This function return the 'fields' attribute modified by
    can_helpers.dict_to_fields.

    the field attribute:

    {
        can-id-a: [ [ field-a ], [ field-b], ... ],
        can-id-b: [ [ field-a ], [ field-b], ... ],
        ...
    }

    Each field represents a guessed value.
    can-id-X is the can-message ID we are interested in.

    Each field is a array of 3 + 2 values.

    [ name, bit_start, bit_length, recv_func, send_func ]

    name: the name of the guessed field
    bit-start: bit from which the data starts
    bit-count: the lenght of our field in bits
    recv_func: a function called to tweak our value on reception
    send_func: a function called to tweak our value before emission

    Example:
        0x0b4: [ [ "speed",         40, 16, speed_recv, speed_send ], ],
        0x0C0: [ [ "value-b",         0, 8 ], ],

        On a CAN message with the ID 0x0b4, we have one interesting field:
            the field "speed", starting at the bit 40, with a length of 16 bits.
            The value cannot be used directly, so we provide two functions:
            speed_recv and speed_send.

            speed_recv will divide it by 100 (Fixed point value)
            and speed_send will multiply it by 100 and convert it to an integer.

        On a CAN message with the ID 0xC0, we have a field 'value-b'.
            Starting at the bit 0, for 8 bits.
            The value can be used directly, so no send/recv function is given.

'''
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
