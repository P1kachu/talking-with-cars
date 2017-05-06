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


