#!/usr/bin/env python3

import curses
import can
import datetime

# curses parameters
nb_elts = 8
y_pad = 2
x_pad = 2
max_rpm = 6000  # In practice, not in theory
max_speed = 130 # Same ^

# CAN parameters
INTERFACE='can0'
can_11bits_diagnostic_id = 0x7df      # Classic 11bits CAN ID
#can_29bits_diagnostic_id = 0xBE3EB811 # FIAT 500 (29bits) CAN ID
#can_29bits_diagnostic_id = 0x80022000 # FIAT 500 (29bits) CAN ID
#can_29bits_diagnostic_id = 0xC0C00000 # FIAT 500 (29bits) CAN ID
diagnostic_id = can_11bits_diagnostic_id

def _is_answer(answer, data):
    '''
    Check if the message received answers our query
    '''
    ret = True

    ret &= (answer.data[1] == data[1] + 0x40) # REQUEST MODE
    ret &= (answer.data[2] == data[2])        # REQUEST PID

    return ret

def can_xchg(bus, arb_id, data, ext=False):
    '''
    Noise proof
    '''
    msg = can.Message(arbitration_id=arb_id,
            data=data,
            extended_id=ext)

    bus.send(msg)

    answer = bus.recv()
    while not _is_answer(answer, data):
        answer = bus.recv()

    return answer

def get_coolant_temp(bus):
    answer = can_xchg(bus, diagnostic_id, [2, 1, 5, 0, 0, 0, 0, 0])
    return answer.data[3] - 40

def get_rpm(bus):
    answer = can_xchg(bus, diagnostic_id, [2, 1, 0xc, 0, 0, 0, 0, 0])
    return int((answer.data[3] * 256 + answer.data[4])/4)

def get_speed(bus):
    answer = can_xchg(bus, diagnostic_id, [2, 1, 0xd, 0, 0, 0, 0, 0])
    return answer.data[3]

def get_throttle_pos(bus):
    answer = can_xchg(bus, diagnostic_id, [2, 1, 0x11, 0, 0, 0, 0, 0])
    return int(100 * answer.data[3] / 255)

def get_accel_pos(bus):
    #0x49 0x4a 0x4b
    answer = can_xchg(bus, diagnostic_id, [2, 1, 0x49, 0, 0, 0, 0, 0])
    return int(100 * answer.data[3] / 255)

def get_elapsed_time(bus):
    answer = can_xchg(bus, diagnostic_id, [2, 1, 0x1f, 0, 0, 0, 0, 0])
    return int(256 * answer.data[3] + answer.data[4])

def print_graph(stdscr, win, value, max_value):
    h,w = win.getmaxyx()
    percent = value/max_value

    # Get current value regarding the screen height
    current_top = max(int(h - (h * percent)), 0)

    # Get color based on percentage
    color = curses.color_pair(int(3 * percent + 1))
    font = curses.color_pair(int(3 * percent + 1) + 4)

    win.clear()

    try:
        length = len(str(value))
        maxi = max(current_top - 1, 0)
        win.addstr(maxi, int(w / 2 - length / 2), str(value), font)
    except:
        clean(stdscr)
        exit()

    try:
        for y in range(current_top, h - 1):
            win.addstr(y, 0, "_" * w, color)
    except:
        clean(stdscr)
        exit()

    stdscr.move(0,0)
    win.refresh()


def init():
    stdscr = curses.initscr()
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    return stdscr

def clean(stdscr):
    curses.nocbreak();
    stdscr.keypad(0);
    curses.echo()
    curses.endwin()


if __name__ in "__main__":

    bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan_native')
    stdscr = init()
    (h, w) = stdscr.getmaxyx()

    # Info, half the screen (left)
    left  = curses.newwin(h, int(w * 2 / 4), 0, 0)

    # Speed (1/4th of the screen, middle)
    middle = curses.newwin(h, int(w / 4) - 3, 0, int(2 / 4 * w))

    # RPM (1/4th of the screen, right)
    right = curses.newwin(h, int(w / 4) - 3, 0, int(3 / 4 * w))

    tmp_inc = 0
    engine_coolant = 0
    coolant_str = ""
    elapsed_time_str = ""

    while 1:
        try:

            # RPM
            rpm = get_rpm(bus)
            rpm_str = "RPM:  {0}".format(str(rpm).rjust(4))

            # Vehicle speed
            speed = get_speed(bus)
            speed_str = "Speed: {0} km/h".format(str(speed).rjust(3))

            # Throttle position
            throttle_pos = get_throttle_pos(bus)
            throttle_str = "Throttle position: {0}%".format(str(throttle_pos).rjust(3))

            # Accelerator pedal position
            accel_pos = get_accel_pos(bus)
            accel_str = "Accelerator pedal position: {0}%".format(str(accel_pos).rjust(3))

            if tmp_inc % 60 == 0:
                # Engine coolant temperature
                engine_coolant = get_coolant_temp(bus)
                coolant_str = "Engine coolant temperature: {0}ºC".format(str(engine_coolant).rjust(2))

                # Elapsed time since engine started
                elapsed_time = get_elapsed_time(bus)
                elapsed_time = str(datetime.timedelta(seconds=elapsed_time))
                elapsed_time_str = "Elapsed time since engine started: {0}".format(str(elapsed_time).rjust(6))

                tmp_inc = 0
            tmp_inc += 1

            elt = 0
            left.clear()
            left.addstr(int(y_pad + elt * h/nb_elts), x_pad, rpm_str); elt += 1
            left.addstr(int(y_pad + elt * h/nb_elts), x_pad, speed_str); elt += 1
            left.addstr(int(y_pad + elt * h/nb_elts), x_pad, coolant_str); elt += 1
            left.addstr(int(y_pad + elt * h/nb_elts), x_pad, throttle_str); elt += 1
            left.addstr(int(y_pad + elt * h/nb_elts), x_pad, accel_str); elt += 1
            left.addstr(int(y_pad + elt * h/nb_elts), x_pad, elapsed_time_str); elt += 1
            left.refresh()

            print_graph(stdscr, middle, speed, max_speed)
            print_graph(stdscr, right, rpm, max_rpm)

        except Exception as e:
            print(e)
            #break

    clean(stdscr)
