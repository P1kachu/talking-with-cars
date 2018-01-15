class CanField():

    def __init__(self, can_id, name, bit_start, bit_count = 8,
                 recv_function = None, send_function = None):
        self.can_id = can_id
        self.name = name
        self.bit_start = bit_start
        self.bit_count = bit_count
        self.recv_function = recv_function
        self.send_function = send_function
        self.value = 0
        self.min_value = 0
        self.max_value = 1

    def recv(self, value):
        if self.recv_function:
            self.value = self.recv_function(value)
        else:
            self.value = value

        self.min_value = min(self.value, self.min_value)
        self.max_value = max(self.value, self.max_value)

    def send(self):
        if self.send_function:
            return self.send_function(self.value)
        return self.value

    def __str__(self):
        return format("[0x%x]\t'%s' (%d@%d): %d \n\tsend=%s\n\trecv=%s" % \
            (self.can_id, self.name, self.bit_count, self.bit_start, self.value,
             self.recv_function, self.send_function))

def insert_value(bit_start, bit_count, payload, data):
    while bit_count > 0:
        bit_end = bit_start + bit_count

        bits_to_write = bit_end % 8
        byte_to_write = bit_end // 8

        if bits_to_write == 0 and bit_count > 0:
            bits_to_write = 8
            byte_to_write -= 1
            if byte_to_write < 0:
                return False

        mask = (0xFF >> (8 - bits_to_write)) << (8 - bits_to_write)
        inc = (payload << (8 - bits_to_write)) & mask

        data[byte_to_write] |= inc & mask

        payload >>= bits_to_write
        bit_count -= bits_to_write
    return True


def extract_value(bit_start, bit_count, data):
    value = 0

    while bit_count > 0:
        bit_pos = bit_start % 8
        bit_to_read = min(bit_count, 8 - bit_pos)
        byte_pos = bit_start // 8

        mask = (0xFF >> (8 - bit_to_read)) << (8 - bit_to_read)
        mask >>= bit_pos
        mask &= 0xFF

        if len(data) > byte_pos:
            value |= data[byte_pos] & mask

        bit_count -= 8 - bit_pos
        bit_start += 8 - bit_pos

        if bit_count > 0:
            value <<= 8 - bit_pos

    return value

def dict_to_fields(known_values):
    out = {}

    for k in known_values:
        for f in known_values[k]:
            name = f[0]
            bit_start = f[1]
            bit_count = f[2]
            recv_func = f[3] if len(f) >= 4 else None
            send_func = f[4] if len(f) >= 5 else None

            field = CanField(k, name, bit_start, bit_count, recv_func, send_func)
            if k in out:
                out[k].append(field)
            else:
                out[k] = [ field ]
    return out
