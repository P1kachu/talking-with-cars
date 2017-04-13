#!/usr/bin/env python3

import curses
import can

nb_elts = 10
y_pad = 2
x_pad = 2
#max_rpm = 8000
max_rpm = 4000
max_speed = 255

def can_xchg(bus, arb_id, data, ext=False):
    msg = can.Message(arbitration_id=arb_id,
            data=data,
            extended_id=ext)
    bus.send(msg)
    return bus.recv()

def get_coolant_temp(bus):
    answer = can_xchg(bus, 0x7df, [2, 1, 5, 0, 0, 0, 0, 0])
    return answer.data[3] - 40

def get_rpm(bus):
    answer = can_xchg(bus, 0x7df, [2, 1, 0xc, 0, 0, 0, 0, 0])
    return int((answer.data[3] * 256 + answer.data[4])/4)

def get_speed(bus):
    answer = can_xchg(bus, 0x7df, [2, 1, 0xd, 0, 0, 0, 0, 0])
    return answer.data[3]

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
        print("current_top={0} - y={1} - h={1}".format(y, current_top, h-1))
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

    bus = can.interface.Bus(channel="can0", bustype='socketcan_native')
    stdscr = init()
    (h, w) = stdscr.getmaxyx()

    # Info, half the screen (left)
    winleft  = curses.newwin(h, int(w * 2 / 4), 0, 0)

    # Speed (1/4th of the screen, middle)
    winmiddle = curses.newwin(h, int(w / 4) - 3, 0, int(2 / 4 * w))

    # RPM (1/4th of the screen, right)
    winright = curses.newwin(h, int(w / 4) - 3, 0, int(3 / 4 * w))

    tmp_inc = 0
    engine_coolant = 0
    coolant_string = ""

    while 1:
        try:
            rpm = get_rpm(bus)
            speed = get_speed(bus)

            rpm_string = "RPM:  {0}".format(str(rpm).rjust(4))
            speed_string = "Speed: {0} km/h".format(str(speed).rjust(3))
        
            if tmp_inc % 20 == 0:
                engine_coolant = get_coolant_temp(bus)
                coolant_string = "Engine coolant temperature: {0}ºC".format(str(engine_coolant).rjust(2))
                tmp_inc = 0
            tmp_inc += 1

            elt = 0
            winleft.clear()
            winleft.addstr(int(y_pad + elt * h/nb_elts), x_pad, rpm_string); elt += 1
            winleft.addstr(int(y_pad + elt * h/nb_elts), x_pad, speed_string); elt += 1
            winleft.addstr(int(y_pad + elt * h/nb_elts), x_pad, coolant_string); elt += 1
            winleft.refresh()

            print_graph(stdscr, winmiddle, speed, max_speed)
            print_graph(stdscr, winright, rpm, max_rpm)

        except Exception as e:
            print(e)
            #break

    clean(stdscr)
