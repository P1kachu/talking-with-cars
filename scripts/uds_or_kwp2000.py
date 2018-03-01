#!/usr/bin/env python3

import can
from p1kanutils import *

def determine_protocol(bus, arb_id, extended=False):
    '''
    https://automotivetechis.wordpress.com/2012/06/06/kwp2000-and-uds-difference/
    "Error memory management: KWP 2000 contains four services for the management
    of the error memory. These are $14 (clearDiagnosticInformation), $18
    (readDTCByStatus), $17 (readStatusOfDTC), and $12 (readFreezeFrameData).

    In contrast, the UDS standard specifies only two services for the error
    memory management: $14 (clearDiagnosticInformation) and $19
    (readDTCInformation)"
    '''

    kwp_command_check = 0x12
    uds_command_check = 0x19

    kwp_command_success = kwp_command_check + 0x40
    uds_command_success = uds_command_check + 0x40

    command_error = 0x7f

    answer_kwp = can_xchg(bus, arb_id, [01, kwp_command_check], extended_id=extended)
    answer_uds = can_xchg(bus, arb_id, [01, uds_command_check], extended_id=extended)

    if answer_kwp.data[1] == kwp_command_success and answer_uds.data[1] == command_error:
        return "kwp2000"
    elif answer_uds.data[1] == uds_command_success and answer_kwp.data[1] == command_error:
        return "uds"
    else:
        return "cannot determine"

determine_protocol(bus, 0x7e0)

