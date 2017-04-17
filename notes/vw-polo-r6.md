## Wolkswagen Polo R6

> ssp444-vw-polo-2010.pdf
> SPP_238.pdf

### Transfer speed
CAN bus drive:                       500 kbit/s
CAN bus diagnosis:                   500 kbit/s
CAN bus led lights:                  500 kbit/s
CAN bus system Comfort/Infotainment: 100 kbit/s
LIN bus:                             19.2 kbit/s

### Fuzzing

> Messages obtained while fuzzing the car

#### Notes

|       ID        |    Communicates with    |    Triggering data    |
---------------------------------------------------------------------
| 0x711           |  0x77B                  | [[0-31], X, X, ... ]  |
| 0x76c           |  0x7D6                  | [[0-31], X, X, ... ]  |

#### KWP Session request ID bruteforcing

can0  TX - -  70A   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  774   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  711   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  77B   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  713   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  77D   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  714   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  77E   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  715   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  77F   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  7F1   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  7F9   [8]  03 7F 01 11 AA AA AA AA   '........'

// Actual request sent from 0xF0x

can0  TX - -  70A   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  774   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  711   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  77B   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  713   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  77D   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  714   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  77E   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  715   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  77F   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  751   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  7BB   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  76C   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  7D6   [8]  03 7F 01 11 AA AA AA AA   '........'

can0  TX - -  7F1   [8]  07 01 C0 00 10 00 03 01   '........'
can0  RX - -  7F9   [8]  03 7F 01 11 AA AA AA AA   '........'

#### Tests

- See can
