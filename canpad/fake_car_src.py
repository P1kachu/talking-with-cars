import math
import time
import can_helpers
import can

class FakeCarSrc:
    ENGINE_POWER = 2500
    ENGINE_TARGET_RPM = 3500
    ENGINE_FRICTION = 0.01
    ENGINE_CONST = 150.0
    ENGINE_REV_GEAR_UP = 1000
    ENGINE_REV_GEAR_DOWN = 3400

    SPEED_INC = 250
    MAX_SPEED = 160
    MASS = 800
    TORQUE_CONST = 3140
    BRAKE_DURATION = 3
    BRAKE_INTERVAL = 10
    BRAKE_POWER = 3000

    def __init__(self, sink, known_fields, print_debug=True):
        self.speed = 0
        self.engine_rev = 0
        self.brake = 0
        self.ramp = 0
        self.last_brake = time.time()
        self.braking = False
        self.last_tick = time.time()
        self.gear_mult = 1.0

        self.known_fields = known_fields
        self.print_debug = print_debug
        self.sink = sink

    def gear_up(self):
        if self.gear_mult < 5:
            self.gear_mult += 1.0
            self.engine_rev = self.ENGINE_REV_GEAR_UP

    def gear_down(self):
        if self.gear_mult > 1:
            self.gear_mult -= 1.0
            self.engine_rev = self.ENGINE_REV_GEAR_DOWN

    def listen(self):
        time.sleep(0.1)
        now = time.time()
        deltatime = now - self.last_tick
        self.last_tick = now

        if now - self.last_brake > self.BRAKE_INTERVAL + self.BRAKE_DURATION:
            self.braking = True
            self.last_brake = now
        elif now - self.last_brake > self.BRAKE_DURATION:
            self.braking = False


        self.engine_rev *= 1.0 - self.ENGINE_FRICTION * deltatime
        engine_inc = self.ENGINE_POWER \
            * (1.0 - (max(1, self.engine_rev) / self.ENGINE_TARGET_RPM))
        engine_inc *= deltatime

        power_required = self.MASS * self.speed ** 2 / self.gear_mult
        power_produced = self.engine_rev * self.ENGINE_CONST * self.gear_mult
        power_left = power_produced - power_required

        braking_power = 0
        if self.braking:
            energy = self.MASS * self.speed ** 2
            braking_power = min(energy, self.BRAKE_POWER * deltatime)
        power_left = power_left - braking_power
        self.engine_rev = max(0, self.engine_rev - braking_power)

        speed_delta = 0
        if power_left > 0:
            speed_delta = math.sqrt(power_left / self.MASS)
        else:
            speed_delta = -math.sqrt(-power_left / self.MASS)
        speed_delta *= deltatime * self.gear_mult

        if self.engine_rev >= self.ENGINE_TARGET_RPM - 200:
            self.gear_up()
        elif self.engine_rev <= 900:
            self.gear_down()

        self.engine_rev += engine_inc
        self.speed += speed_delta

        if self.print_debug:
            print("Engine: %6.2f" % self.engine_rev)
            print("Speed %5.2f" % self.speed)
            print("Brake %s" % self.braking)
            print("Gear mult %d" % self.gear_mult)
            print("\b\r\b\r\b\r\b\r", end="")

        return True

    def find_can_message_info(self, key):
        for k in self.known_fields:
            fields = self.known_fields[k]
            for f in fields:
                if f.name != key:
                    continue
                return (k, f)
        return None, None

    '''
        This function let you choose which value to send on which known field

        By example, I have the following known values:

        {
            0x0b0, [ 'wheel', 0, 16 ],
            0x0b4: [ [ "speed",         40, 16, speed_recv, speed_send ], ],
        }

        If I want to show fakeCar.speed and fakeCar.engine_rev on the can bus, I can do:

        {
            "speed": fakeCar.speed,
            "wheel": fakeCar.engine_rev
        }

        Proper CAN messages will be crafted and sent to the sink
    '''
    def send_values(self, values = {}):
        messages = { }

        for v in values:
            can_id, descriptor = self.find_can_message_info(v)
            if can_id == None:
                print("Unknown key %s" % v)
                return False

            payload = values[v]

            if descriptor.send_function != None:
                payload = descriptor.send_function(payload)
            payload = int(payload)

            if can_id in messages:
                data = messages[can_id]
            else:
                data = [ 0 ] * 8

            if not can_helpers.insert_value( descriptor.bit_start,
                                             descriptor.bit_count, payload, data):
                print("Failed to add entry to key %s (%s)", (v, str(payload)))

            messages[can_id] = data

        for m in messages:
            msg = can.Message(arbitration_id=m, data=messages[m])
            self.sink.register_message(msg)
