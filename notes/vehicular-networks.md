## Vehicular Networks

> vehicular-networks.pdf
> can-based-hlp.pdf
> http://jazdw.net/tp20
> http://marco.guardigli.it/2010/10/hacking-your-car.html

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

#### CAN (11-bit) bus packets
> https://en.wikipedia.org/wiki/OBD-II_PIDs#CAN_.2811-bit.29_bus_format
> https://en.wikipedia.org/wiki/OBD-II_PIDs#Mode_01

- The diagnostic reader initiates a query using CAN ID 7DFh, which acts as a
  broadcast address, and accepts responses from any ID in the range 7E8h to 7EFh.
  ECUs that can respond to OBD queries listen both to the functional broadcast ID
  of 7DFh and one assigned ID in the range 7E0h to 7E7h. Their response has an ID
  of their assigned ID plus 8 e.g. 7E8h through 7EFh. This approach allows up
  to eight ECUs, each independently responding to OBD queries.

Transmission example (SAE standard):

> Interface |  Pin   |   ID   |  Length  |      Data         |
>
> can0         TX - -    7DF      [8]    02 01 05 00 00 00 00 00
>
> can0         RX - -    7E8      [8]    03 41 05 82 AA AA AA AA

- The first line is the request (TX). The ID 7DF is the diagnostic reader.
  It sends 8 bytes of data: The first one is the number of additionnal data
  bytes (here 2), the second is the mode (here, show current data) and the
  third is the PID code (05 = Engine coolant temperature).
- The second line is the answer. The vehicle responds to the PID query on the
  CAN bus with message IDs that depend on which module responded. The engine
  or main ECU is typically 7E8h.
  The data can be read as:
  - Byte 0: Number of additionnal data bytes
  - Byte 1: Custom mode (mode + 40h) here is show current data
  - Byte 2: PID code
  - Byte 3: Byte 0 of the specified parameter
  - Byte 4: Byte 1 of the specified parameter (optional)
  - Byte 5: Byte 2 of the specified parameter (optional)
  - Byte 6: Byte 3 of the specified parameter (optional)
  - Byte 7: Not used (0x00 || 0x55 || 0xAA)

- So, in our previous example, we (7DFh) send a message containing 3 bytes of
  data, asking for the current value of the engine coolant temperature. The ECU
  (7E8h) answers with 4 bytes of data, the final byte being the temperature.
  Following the explanation from wikipedia (second link in sources above), we
  can determine that the temperature is (0x82 - 40) degrees.


### ISO-TP and TP 2.0

Pure CAN cannot satisfy the requirements that have to be fulfilled within
large, extendable, interconnected networks from different manufacturers.
Higher Layer Protocols (HLP) enables the interconnection of these networks.
CAN allows for data packets with a payload of up to 8 bytes, to send messages
longer than 8 bytes it is necessary to use a transport protocol. The OBD-II
specification for example makes use of ISO-TP (ISO 15765-2). Volkswagen however
uses it's own transport protocol in its vehicles, known as VW TP 2.0.

#### ISO-TP - ISO-14229 - UDS

> https://en.wikipedia.org/wiki/Unified_Diagnostic_Services
> Adventures in Automotive Networks and Control Units - Miller & Valasek
> https://automotive.wiki/index.php/ISO_14229

- Unified Diagnostic Services (UDS) is a diagnostic communication protocol ECU
  environment within the automotive electronics, which is specified in the ISO
  14229-1 It is derived from ISO 14230-3 (KWP2000) and ISO 15765-3 (Diagnostic
  Communication over Controller Area Network (DoCAN)).

##### Service IDs

> 0x10 	Diagnostic Session Control
> 0x11 	ECU Reset
> 0x14 	Clear Diagnostic Information
> 0x19 	Read DTC Information
> 0x22 	Read Data By Identifier
> 0x23 	Read Memory By Address
> 0x27 	Security Access
> 0x28 	Communication Control
> 0x2E 	Write Data By Identifier
> 0x2F 	Input Output Control By Identifier
> 0x31 	Routine Control
> 0x34 	Request Download
> 0x35 	Request Upload
> 0x36 	Transfer Data
> 0x37 	Transfer Exit
> 0x3D 	Write Memory By Address
> 0x3E 	Tester Present
> 0x85 	Control DTC Setting

##### Negative Response Codes (NRCs)

- The negative response codes (NRC) are divided into 3 ranges:
    - 0x00: positiveResponse parameter value for server internal implementation,
    - 0x01 – 0x7F: communication related negative response codes,
    - 0x80 – 0xFF: negative response codes for specific conditions that are not
      correct at the point in time the request is received by the server. These
      response codes may be utilized whenever response code 0x22
      (conditionsNotCorrect) is listed as valid in order to report more
      specifically why the requested action can not be taken.

> 0x00:      positiveResponse
> 0x01-0x0F: ISOSAEReserved
> 0x10:      generalReject
> 0x11:      serviceNotSupported
> 0x12:      subFunctionNotSupported
> 0x13:      incorrectMessageLengthOrInvalidFormat
> 0x14:      responseTooLong
> 0x15-0x20: ISOSAEReserved
> 0x21:      busyRepeatReques
> 0x22:      conditionsNotCorrect
> 0x23:      ISOSAEReserved
> 0x24:      requestSequenceError
> 0x25-0x30: ISOSAEReserved
> 0x31:      requestOutOfRange
> 0x32:      ISOSAEReserved
> 0x33:      securityAccessDenied
> 0x34:      ISOSAEReserved
> 0x35:      invalidKey
> 0x36:      exceedNumberOfAttempts
> 0x37:      requiredTimeDelayNotExpired
> 0x38-0x4F: reservedByExtendedDataLinkSecurityDocument
> 0x50-0x6F: ISOSAEReserved
> 0x70:      uploadDownloadNotAccepted
> 0x71:      transferDataSuspended
> 0x72:      generalProgrammingFailure
> 0x73:      wrongBlockSequenceCounter
> 0x74-0x77: ISOSAEReserved
> 0x78:      requestCorrectlyReceived-ResponsePending
> 0x79-0x7D: ISOSAEReserved
> 0x7E:      subFunctionNotSupportedInActiveSession
> 0x7F:      serviceNotSupportedInActiveSession
> 0x80:      ISOSAEReserved
> 0x81:      rpmTooHigh
> 0x82:      rpmTooLow
> 0x83:      engineIsRunning
> 0x84:      engineIsNotRunning
> 0x85:      engineRunTimeTooLow
> 0x86:      temperatureTooHigh
> 0x87:      temperatureTooLow
> 0x88:      vehicleSpeedTooHigh
> 0x89:      vehicleSpeedTooLow
> 0x8A:      throttle/PedalTooHigh
> 0x8B:      throttle/PedalTooLow
> 0x8C:      transmissionRangeNotInNeutral
> 0x8D:      transmissionRangeNotInGear
> 0x8E:      ISOSAEReserved
> 0x8F:      brakeSwitch(es)NotClosed
> 0x90:      shifterLeverNotInPark
> 0x91:      torqueConverterClutchLocked
> 0x92:      voltageTooHigh
> 0x93:      voltageTooLow
> 0x94-0xFE: reservedForSpecificConditionsNotCorrect
> 0xFF:      ISOSAEReserved

- See ../scripts/iso_tp.py for examples

// TODO

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
>  0       1         2         3          4          5          6
> Dest | Opcode | RX ID | RX Pref + V | TX ID | TX Pref + V |  App
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

- See ../scripts/vw_kwp.py for examples

##### Channel parameters
- 1 to 6 bytes
- Setup parameters for an open channel or send test/break/disconnect signals
- Request should be send straight after channel setup
> 0      [ 1   2  3  4  5 ]
> Opcode [ BS T1 T2 T3 T4 ]
- Fields:
    - Opcode:
        - 0xA0: Parameters request, used for destination module to initiator
          (6 byte)
        - 0xA1: Parameters response, used for initiator to destination module
          (6 byte)
        - 0xA3: Channel test, response is same as parameters response. Used to
          keep channel alive. (1 byte)
        - 0xA4: Break, receiver discards all data since last ACK (1 byte)
        - 0xA8: Disconnect, channel is no longer open. Receiver should reply
          with a disconnect (1 byte)
    - BS: Block size (number of packets to send before expecting a ACK)
    - T1: Timing param 1, time to wait for ACK (T1 > (4 * T3))
    - T2: Timing param 2, always 0xff
    - T3: Timing param 3, interval between two packets
    - T4: Timing param 4, always 0xff

- See http://jazdw.net/tp20 for timing parameters format

##### Channel transmission
- 2 to 8 bytes
- Used for actual transmissions (after channel setup)
>      0            1234567
> Opcode + Seq    KWP payload
- Fields:
    - Opcode:
        - 0x0: Waiting for ACK, more packets to follow
        - 0x1: Waiting for ACK, this is the last packet
        - 0x2: Not waiting for ACK, more packets to follow
        - 0x3: Not waiting for ACK, this is the last packet
        - 0x9: ACK, not ready for next packet
        - 0xB: ACK, ready for next packet
   - Seq: Sequence number, increments up to 0xF, then loop
   - Payload: KWP2000 payload. The first 2 bytes of the first packet contains
     the total length.

##### Example
See http://jazdw.net/tp20 for a working example

### LIN
// TODO

