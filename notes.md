Playing with CAN
================

- PiCan2
- 2012/2013 Volkswagen Polo R6

# Notes and documentation

## Vehicular Networks

> vehicular-networks.pdf
> can-based-hlp.pdf
> http://jazdw.net/tp20

### K-Line Bus
- Standard in the 80s - Bidirectional bus, communicating over 1 wire (K Line)
- KWP 2000 (Keyword Protocol) - Layers 1 & 2
- Protocol slides 4 to 7

### CAN Bus
- Controller Area Network ('86) - Layers 1 & 2
- Two signal levels (low == dominant/high == recessive)
- Up to 110 nodes
- CSMA/CA with Bus arbitration based on ID
  Avoids collisions by priority-controlled bus access
  Bit stuffing: after 5 identical Bits one inverted Stuff-Bit is inserted
  (ignored by receiver)
  When no station is sending the bus reads “1” (recessive state)
  Synchronization happens on bit level, by detecting start bit of sending
  station
  End of current transmission: wait for 6 consecutive recessive bits (1)
  Watch for mismatch between transmitted/detected signal level, meaning that
  a collision with a higher priority message occured, back off and retry later.
- Do not use destination addresses, implicit broadcast/multicast.
  Address-less communication, messages carry 11/29 bits message ID.
  Stations use message identifier to decide whether a message is meant
  for them.
  Acceptance of messages determined using two registers: Acceptance Code (AC,
  bit pattern to filter on) and Acceptance Mask (AM, "0" marks relevant bits
  in AC)
- 4 frame formats: Data, Remote (request), Error, Overload (flow control)
- Time-Triggered CAN (TTCAN) slides 24/25 (smarter way of choosing IDs)
- Data format slides 27 to 29
- Error detection: sender checks for unexpected signal levels on bus, all nodes
  check protocol conformance of message and bit stuffing, receiver checks CRC
  If any node detects error, error message (not conform, 6 dominant bits with no
  stuffing)
  All nodes dectect error and discard message
  Sender checks for ACK (receiver send back message with 0 in ACK field)
  Sender resend if not ACK
  If too many error from a receiver, it stops itself temporarily

### ISO-TP and TP 2.0
// TODO IMPORTANT

### LIN
// TODO


## Wolkswagen Polo R6

> ssp444-vw-polo-2010.pdf
> SPP_238.pdf

### Transfer speed
CAN bus drive:                       500 kbit/s
CAN bus diagnosis:                   500 kbit/s
CAN bus led lights:                  500 kbit/s
CAN bus system Comfort/Infotainment: 100 kbit/s
LIN bus:                             19.2 kbit/s


## Links
- https://hackaday.io/project/6288/logs
- http://jazdw.net/tp20
- docs/
