import can

'''

    Send all data to the specified CAN BUS
    does not do any computations

'''

class CanSink():
    def __init__(self, interface, known_fields = {}):
        self.bus = can.interface.Bus(channel=interface, bustype='socketcan_native')

    def register_message(self, can_message):
        self.bus.send(can_message)
