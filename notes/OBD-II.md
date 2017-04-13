## OBD-II

> https://en.wikipedia.org/wiki/OBD-II_PIDs
> http://www.eaa-phev.org/wiki/Escape_PHEV_TechInfo#PIDs (Ford Hybrid)

On-board diagnostics (OBD) is an automotive term referring to a vehicle's
self-diagnostic and reporting capability

### Modes of operation

There are 10 modes of operation described in the latest OBD-II standard SAE
J1979. They are as follows:
- 01: Show current data
- 02: Show freeze frame data
- 03: Show stored Diagnostic Trouble Codes
- 04: Clear Diagnostic Trouble Codes and stored values
- 05: Test results, oxygen sensor monitoring (non CAN only)
- 06: Test results, other component/system monitoring (Test results, oxygen sensor monitoring for CAN only)
- 07: Show pending Diagnostic Trouble Codes (detected during current or last driving cycle)
- 08: Control operation of on-board component/system
- 09: Request vehicle information
- 0A: Permanent Diagnostic Trouble Codes (DTCs) (Cleared DTCs)

Vehicle manufacturers are not required to support all modes. Each manufacturer
may define additional modes above #9 (e.g.: mode 22 as defined by SAE J2190 for
Ford/GM, mode 21 for Toyota) for other information e.g. the voltage of the
traction battery in a hybrid electric vehicle (HEV).

### CAN (11-bit) bus format

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

### Non-standard PIDs
- Majority of all OBD-II PIDs are non-standard
- Minor overlap between vehicle manufacturers
- Very limited information available in the public domain. The primary source
  of information is maintained by the Equipment and Tool Institute (ETI), and
  available only to members. The price of ETI membership for access to scan
  codes varies based on annual sales of automotive tools and equipement in North
  America:

> | Annual Sales in North America | Annual Dues |
>  ---------------------------------------------
> | Under $10,000,000             | $5,000      |
> | $10,000,000 - $50,000,000     | $7,500      |
> | Over $50,000,000              | $10,000     |


