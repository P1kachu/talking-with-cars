import uinput
import time
import random

CONTROLLER = "Microsoft X-Box 360 pad - P1ka"
VENDOR = 0x45e
PRODUCT = 0x28e
VERSION = 101

def main():
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

    array = [
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
        ]

    with uinput.Device(events,
                       name=CONTROLLER,
                       vendor=VENDOR,
                       product=PRODUCT,
                       bustype=3,
                       version=VERSION,
                       ) as device:
        print("Device created")
        time.sleep(1)
        device.emit_click(uinput.BTN_MODE)
        for i in range(200000):
            print(i)
            r1 = random.randint(-32767, 32767)
            r2 = random.randint(-32767, 32767)
            r3 = random.randint(-32767, 32767)
            device.emit(uinput.ABS_X, r1, syn=False)
            device.emit(uinput.ABS_GAS, r2, syn=False)
            device.emit(uinput.ABS_BRAKE, r3, syn=False)
            device.emit_click(array[i % (len(array) - 1)], syn=True)
            time.sleep(0.3)

if __name__ == "__main__":
    main()
