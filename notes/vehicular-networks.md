## Vehicular Networks

> vehicular-networks.pdf
> can-based-hlp.pdf
> http://jazdw.net/tp20

### OSI Model
Different configuration possible, but we are interested in this one:

- Application:  KWP2000
- Presentation:
- Session:
- Transport:    VW TP 2.0
- Network:
- Data Link:    CAN
- Physical:     CAN


### K-Line Bus
- Standard in the 80s - Bidirectional bus, communicating over 1 wire (K Line)
- KWP 2000 (Keyword Protocol)
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

CAN allows for data packets with a payload of up to 8 bytes, to send messages
longer than 8 bytes it is necessary to use a transport protocol. The OBD-II
specification for example makes use of ISO-TP (ISO 15765-2). Volkswagen however
uses it's own transport protocol in its vehicles, known as VW TP 2.0.

#### ISO-TP

#### TP 2.0
- Application layer: KWP2000
- Opens data "channels" between two communicating devices.
- 4 message types

##### Broadcast
- Fixed length of 7 bytes
- Sent 5 times in case of data loss
>  0       1      [2 - 4]       5          6
> Dest | Opcode | KWP Data | Resp Req | Resp Req
- Fields:
    - Dest:     Logical address of destination module, (like 0x01 for the ECU)
    - Opcode:   0x23 for broadcast request - 0x24 for broadcast response
    - KWP Data: KWP2000 SID and parameters
    - Resp Req: 0x00 for response expected, else 0x55 or 0xAA

##### Channel setup
- Fixed length of 7 bytes
- Establishes a data channel between two devices:
    - Request should be sent from 0x200
    - Response sent with 0x200 + dest logical address (like 0x201 for ECU)
    - Communication then switches to CAN IDs negotiated during setup
>  0       1         2         3         4         5        6
> Dest | Opcode | RX ID V | RX Pref | TX ID V | TX Pref |  App
- Fields:
    - Dest:    Logical address of destination module
    - Opcode:  Setup req (0xC0) - Positive Resp (0xD0) - Negative Resp (0xD6...0xD8)
    - RX ID:   Tells destination module which ID to listen to
    - RX Pref: RX ID prefix
    - TX ID:   Tells destination module which ID to transmit to
    - TX Pref: TX ID prefix
    - V:       Is CAN ID valid
    - App:     Application type (seems to be always 1 for KWP)

"You should request the destination module to transmit using CAN ID 0x300 to
0x310 and set the validity nibble for RX ID to invalid. The VW modules seem to
respond that you should transmit using CAN ID 0x740."

##### Channel parameters
// TODO

##### Channel transmission
// TODO

### LIN
// TODO

