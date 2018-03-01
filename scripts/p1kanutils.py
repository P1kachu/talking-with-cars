'''
Random utils for CAN analysis
'''

import can

def _is_answer(answer, data):
    '''
    Check if the message received answers our query
    '''
    if len(answer.data) < 3:
    	return False

    if (answer.data[1] != data[1] + 0x40) and (answer.data[1] != 0x7f):
    # REQUEST MODE
    	return False

    if (answer.data[2] != data[2]) and (answer.data[2] != data[1]):
        # REQUEST PID
        return False

    return True

def can_xchg(bus, arb_id, data, ext=False):
    '''
    Noise proof
    '''
    msg = can.Message(arbitration_id=arb_id,
            data=data,
            extended_id=ext)

    answer = None
    bus.send(msg)
    while not answer or not _is_answer(answer, data):
        # 29bits CAN requires to resend the message until
        # the answer is received.
        try:
            answer = bus.recv(0.05)
        except:
            pass

    return answer

