#!/usr/bin/python3

import can
import math
import os
import random
import signal
import sys
import threading
import time
import can_helpers

'''

    This sink allows you to display both raw values and known values.
    Raw values will be displayed in an array. All changing values will be marked red.

    The known values will be displayed in a graph, from MIN to MAX.
    MIN and MAX values are recomputed each time we get a new value.

'''

class TerminalSink(threading.Thread):

    # For now I do not get the real size of the terminal. FIXME
    SCREEN_HEIGHT = 56
    SCREEN_WIDTH = 80

    def __init__(self, known_fields):
        threading.Thread.__init__(self)

        self.known_fields = known_fields
        self.graphs = {}
        self.mcus = {}

    def line_graph(self, name, value, mini, maxi):
        percent = (value - mini) / (maxi - mini)
        percent = min(1.0, max(0.0, percent))

        sharp_count = math.ceil(percent * (self.SCREEN_WIDTH - 25))
        line = format("%16s %08.2f: %s" % (name, value, "#" * sharp_count))
        return line

    def draw_graphs(self, lines):
        for can_id in self.known_fields:
            for field in self.known_fields[can_id]:
                lines.append(self.line_graph(field.name, field.value, field.min_value, \
                    field.max_value))

    def show_gui(self):
        lines = []
        lines.append("Terminal-Sink")

        self.draw_graphs(lines)

        dic = {**self.mcus}

        for key in dic:
            l = format("%03x | " % key)

            data = dic[key]
            for j in range(0, 8):
                if j >= len(data):
                    l += format("00 ")
                elif data[j][1] > 0:
                    l += format("%s%02x%s " % ('\033[41m', data[j][0], '\033[0m'))
                    data[j] = (data[j][0], 0)
                else:
                    l += format("%02x " % data[j][0])
            dic[key] = data

            lines.append(l)

        if len(lines) < self.SCREEN_HEIGHT:
            lines += [""] * (self.SCREEN_HEIGHT - len(lines))
        lines = lines[:self.SCREEN_HEIGHT]

        print("\n".join(lines))

    def run(self):
        while True:
            self.show_gui()
            time.sleep(0.1)

    '''
        When a message is received, we will first save it in a generic array,
        used to display raw values with HITS.

        Then we will see if we know the key, and extract the interecting part
        to display it in a graph.

    '''
    def register_message(self, can_message):

        can_id = can_message.arbitration_id

        if can_id not in self.mcus:
            data = []
            for d in can_message.data:
                data += [ (d, 0)]
            data += [ (0, 0) ] * (8 - len(data))
            self.mcus[can_id] = data
            return

        data = self.mcus[can_id]

        for i in range(0, 8):
            old_value = data[i][0]
            new_value = old_value

            if len(can_message.data) > i:
                new_value = can_message.data[i]

            # Mark an HIT
            data[i] = (new_value, new_value != old_value)
        self.mcus[can_id] = data

        if can_id not in self.known_fields:
            return

        # If the value is known, we need to extract the interesting parts
        for key in self.known_fields:
            if key != can_id:
                continue

            for f in self.known_fields[key]:
                value = can_helpers.extract_value(f.bit_start, f.bit_count, \
                                                  can_message.data)
                f.recv(value)
            break

