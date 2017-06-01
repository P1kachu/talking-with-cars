#!/usr/bin/env python3

import curses
import can
import datetime
from math import floor

# Constants
nb_elts = 16
y_pad = 2
x_pad = 2
max_rpm = 6000  # In practice, not in theory
max_speed = 130 # Same ^
can_11bits_diagnostic_id = 0x7df      # Classic 11bits CAN ID
can_29bits_diagnostic_id = 0x18DB33F1 # FIAT 500 (29bits) CAN ID

# CAN parameters
INTERFACE='vcan0'
diagnostic_id = can_29bits_diagnostic_id # 29bits -> Fiat 500 / 11bits -> VW Polo
extended = (diagnostic_id == can_29bits_diagnostic_id)

def _is_answer(answer, data):
    '''
    Check if the message received answers our query
    '''
    ret = True

    if len(answer.data) < 3:
        return False

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

    answer = None
    while not answer or not _is_answer(answer, data):
        # 29bits CAN requires to resend the message until
        # the answer is received.
        try:
            bus.send(msg)
            answer = bus.recv(0.1)
        except:
            pass

    return answer

def can29_recv(bus, arb_id, byte_nb):
    answer = bus.recv(0.1)

    while not answer or answer.arbitration_id != arb_id or len(answer.data) <= byte_nb:
        answer = bus.recv(0.1)

    return answer.data[byte_nb]

def get_coolant_temp(bus):
    answer = can_xchg(bus, diagnostic_id, [2, 1, 5, 0, 0, 0, 0, 0], extended)
    if answer is None:
        return 0
    return answer.data[3] - 40

def get_rpm(bus):
    answer = can_xchg(bus, diagnostic_id, [2, 1, 0xc, 0, 0, 0, 0, 0], extended)
    if answer is None:
        return 0
    return (answer.data[3], answer.data[4])

def get_speed(bus):
    answer = can_xchg(bus, diagnostic_id, [2, 1, 0xd, 0, 0, 0, 0, 0], extended)
    if answer is None:
        return 0
    return answer.data[3]

def get_throttle_pos(bus):
    answer = can_xchg(bus, diagnostic_id, [2, 1, 0x11, 0, 0, 0, 0, 0], extended)
    if answer is None:
        return 0
    return answer.data[3]

def get_accel_pos(bus):
    #0x49 0x4a 0x4b
    answer = can_xchg(bus, diagnostic_id, [2, 1, 0x49, 0, 0, 0, 0, 0], extended)
    if answer is None:
        return 0
    return answer.data[3]

def get_elapsed_time(bus):
    # 29bits CAN doesn't answer this query. Don't know why
    if diagnostic_id == can_29bits_diagnostic_id:
        return "N/A"

    answer = can_xchg(bus, diagnostic_id, [2, 1, 0x1f, 0, 0, 0, 0, 0], extended)
    if answer is None:
        return "N/A"

    elapsed_time = int(256 * answer.data[3] + answer.data[4])
    return str(datetime.timedelta(seconds=elapsed_time))

def get_fiat_status(bus):
    handbrake = "Up" if can29_recv(bus, 0x0a18a000, 0) else "Down"
    misc = can29_recv(bus, 0x0a18a000, 2)
    misc2 = can29_recv(bus, 0x0c1ca000, 2)

    engine = "Ignition" if (misc >> 7) else ("On" if (misc >> 6) else "Off")
    start_stop = "unavailable" if not ((misc2 >> 6) & 1) else ("activated" if (misc2 >> 5) & 1 else "deactivated")
    doors = ""

    if not (misc2 >> 2) & 1:
        if (misc >> 3) & 1:
            doors = "Left door opened"
        else:
            doors = "Right or both doors opened" # Or maybe both, check that
    else:
        doors = "Doors closed"

    return (handbrake, engine, start_stop, doors)


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

def fiat_print_pedals(stdscr, win, bus):
    h,w = win.getmaxyx()
    y,x = win.getbegyx()
    max_pedal_width = int(w / 3 - 1)

    win.clear()
    pedals_str = " Pedals "
    padding = int(w / 2 - len(pedals_str) / 2)
    font = curses.color_pair(0)
    win.addstr(0, 0, "*" * padding + pedals_str + "*" * padding, font)


    left_pad = int(w / 15)
    # Clutch pedal byte can have values 0x00, 0x10, 0x20, 0x30
    # We are only interested in the 0x00 and 0x20
    clutch_p = can29_recv(bus, 0x0628a001, 5)
    clutch_p = min(int(clutch_p / 0x10), 2) & 0b10
    try:
        color = curses.color_pair(clutch_p)
        for str_y in range(2, y - h - 5):
            win.addstr(str_y + 1, left_pad, "*" * int(max_pedal_width / 2), color)
    except Exception as e:
        clean(stdscr)
        print(e)
        exit()

    # Brake pedal byte can have values:
    #   0b001xxxx
    #   0b011xxxx
    #   0b111xxxx
    brake_p = can29_recv(bus, 0x0810a000, 2)
    brake_p = bin(brake_p >> 4).count("1") - 1
    try:
        color = curses.color_pair(brake_p)
        for str_y in range(2, y - h - 4):
            win.addstr(str_y + 1, max_pedal_width + left_pad, "*" * int(max_pedal_width * 2/3 - 2), color)
    except Exception as e:
        clean(stdscr)
        print(e)
        exit()

    # Accelerator pedal value in percents
    accel_p = get_accel_pos(bus)
    accel_p = accel_p / 255
    try:
        color = curses.color_pair(min(int(4 * accel_p + 0), 4))
        for str_y in range(2, y - h - 2):
            win.addstr(str_y + 1, 2 * max_pedal_width + left_pad, "*" * int(max_pedal_width* 2/3 - 2), color)
    except Exception as e:
        clean(stdscr)
        print(e)
        exit()


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

    #                    height, width, y, x
    left = curses.newwin(h, int(w / 4) - 3, 0, 0)

    infos_win = curses.newwin(int(h * 2 / 3) - 3, int(w / 2) - 4, 0, int(w / 4) + 2)
    pedals_win = curses.newwin(int(h / 3), int(w / 2) - 4, int(h * 2 / 3), int(w / 4) + 2)

    right = curses.newwin(h, int(w / 4) - 3, 0, int(w * 3 / 4))

    tmp_inc = 0
    engine_coolant = 0
    coolant_str = ""
    elapsed_time_str = ""
    fiat_status_str = ""
    fiat_status2_str = ""

    while 1:
        try:

            # RPM
            byte_3, byte_4 = get_rpm(bus)
            rpm = int((byte_3 * 256 + byte_4)/4)
            rpm_str = "RPM:  {0}".format(str(rpm).rjust(4))
            rpm_str += " ({:02x} {:02x})".format(byte_3, byte_4) # DEBUG

            # Vehicle speed
            speed = get_speed(bus)
            speed_str = "Speed: {0} km/h".format(str(speed).rjust(3))
            speed_str += " ({:02x})".format(speed) # DEBUG

            # Throttle position
            byte_3 = get_throttle_pos(bus)
            throttle_pos = int(100 * byte_3 / 255)
            throttle_str = "Throttle position: {0}%".format(str(throttle_pos).rjust(3))
            throttle_str += " ({:02x})".format(byte_3) # DEBUG

            # Accelerator pedal position
            byte_3 = get_accel_pos(bus)
            accel_pos = int(100 * byte_3 / 255)
            accel_str = "Accelerator pedal position: {0}%".format(str(accel_pos).rjust(3))
            accel_str += " ({:02x})".format(byte_3) # DEBUG

            if tmp_inc % 60 == 0:
                # Engine coolant temperature
                engine_coolant = get_coolant_temp(bus)
                coolant_str = "Engine coolant temperature: {0}ºC".format(str(engine_coolant).rjust(2))
                coolant_str += " ({:02x})".format(engine_coolant) # DEBUG

                # Elapsed time since engine started
                elapsed_time = get_elapsed_time(bus)
                elapsed_time_str = "Elapsed time since engine started: {0}".format(str(elapsed_time).rjust(6))

                tmp_inc = 0

            if diagnostic_id == can_29bits_diagnostic_id: # Fiat 500 only
                if tmp_inc % 5 == 0:
                    handbrake_sts, engine_sts, start_stop_sts, doors_sts = get_fiat_status(bus)
                    fiat_status_str = ""
                    fiat_status2_str = ""
                    fiat_status_str += "Handbrake: {0} - ".format(handbrake_sts)
                    fiat_status_str += "Start&Stop {0}".format(start_stop_sts)
                    fiat_status2_str += "Engine: {0} - ".format(engine_sts)
                    fiat_status2_str += "{0}".format(doors_sts)
                fiat_print_pedals(stdscr, pedals_win, bus)


            tmp_inc += 1

            i = 0
            infos_win.clear()
            infos_win.addstr(int(y_pad + i * floor(h/nb_elts)), x_pad, rpm_str); i += 1
            infos_win.addstr(int(y_pad + i * floor(h/nb_elts)), x_pad, speed_str); i += 1
            infos_win.addstr(int(y_pad + i * floor(h/nb_elts)), x_pad, coolant_str); i += 1
            infos_win.addstr(int(y_pad + i * floor(h/nb_elts)), x_pad, throttle_str); i += 1
            infos_win.addstr(int(y_pad + i * floor(h/nb_elts)), x_pad, accel_str); i += 1
            infos_win.addstr(int(y_pad + i * floor(h/nb_elts)), x_pad, elapsed_time_str); i += 1
            infos_win.addstr(int(y_pad + i * floor(h/nb_elts)), x_pad, fiat_status_str); i += 1
            infos_win.addstr(int(y_pad + i * floor(h/nb_elts)), x_pad, fiat_status2_str); i += 1
            infos_win.refresh()

            print_graph(stdscr, left, speed, max_speed)
            print_graph(stdscr, right, rpm, max_rpm)

        except Exception as e:
            print(e)
            while (1):
                pass
            break

    clean(stdscr)
