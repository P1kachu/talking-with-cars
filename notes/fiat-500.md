FIAT 500 Nuova 500C 1.2 MPi Cabriolet S&S 69 cv
===============================================

> http://www.lacentrale.fr/fiche-technique-voiture-fiat-500-ii+c+1.2+8v+69+s%5Es+lounge-2010.html
> http://www.outilsobdfacile.com/vehicle-list-compatible-obd2/fiat
> http://www.obdtester.com/ficom
> http://www.mp3car.com/forum/mp3car-technical-hardware/engine-management-obd-ii-engine-diagnostics-etc/151698-does-anyone-know-what-is-obd-ii-protocol-for-2010-s-hondas
> http://multiplex-engineering.com/tutorials/
> https://www.scantool.net/scantool/downloads/64/ecusim_5100-ug.pdf
> https://github.com/kipyegonmark/mechanic/issues/6
> https://www.dgtech.com/wp-content/uploads/2016/07/DGDiagOBDII-manual.pdf


- Uses 29bits (Extended) CAN BUS
- 500kb/s
- Debug arbitration ID: 0x18DB33F1

## Reverse engineering broadcast message

Here are the different values observed during daily usage of the car, and some
of their meanings. Output example can be found in
../can_logs/test_canmonitor_fiat500_reverse.log

Terms used here:
  - RWH: Rear window heater (defogger)
  - SS: Start&Stop
  - SB: Driver's seatbelt
  - Speed:
    Speed1: High byte of speed (>= 0x10)
    Speed2: Low byte of speed (< 0x10, and one digit after coma)
    Example: '01 67' means 16,7 km/h (hex) => 22 km/h (dec)

### 0210a006
0210a006[4:5]: Rises with speed. Real meaning still unknown

### 0218a006
Gives speed at 4 different but close moments if the car is running. If the
car's speed is less than 3 km/h, it gives 4 times '00 2C'

0218a006[0] => Speed1
0218a006[1] => Speed2
0218a006[2] => Speed1
0218a006[3] => Speed2
0218a006[4] => Speed1
0218a006[5] => Speed2
0218a006[6] => Speed1
0218a006[7] => Speed2

### 0618a001

> Suppositions, need to be verified

Gas consumption ?

0618a001[5]:
  0x23 = 0b100011 => RWH off, both windows opened, radio off
  0x24 = 0b100100 => RWH off, both windows closed, radio off
  0x25 = 0b100101 => RWH off, both windows closed, radio on
  0x2C = 0b101100 => RWH on, both windows closed, radio off
                ^------ 0: Windows opened (Left)
               ^------- 1: Windows opened (Right)
              ^-------- 2: Both windows closed ?
             ^--------- 3: RWH on


### 0810a000
0810a000[2] => Rises with force applied on brakes. Real meaning unknown
0810a000[2]:
  0x1x: Brakes pedal released
  0x3x: Brakes pedal being released
  0x7x: Brakes pedal being depressed

### 0a18a000
Seems to convey status bitfields

0a18a000[0]:
  0x00 = 0b00000000 => Handbrake off, RWH off
  0x20 = 0b00100000 => Handbrake on, RWH off
             ^----------- 5: Handbrake on

0a18a000[2]:
  0x10 = 0b00010000 => Left front door closed, contact off
  0x18 = 0b00011000 => Left front door opened, contact off
  0x40 = 0b01000000 => Left front door closed, contact on
  0x48 = 0b01001000 => Left front door opened, contact on
  0xC0 = 0b11000000 => Left front door closed, Ignition
  0xC8 = 0b11001000 => Left front door opened, Ignition
               ^--------- 3: Left front door opened
              ^---------- 4: ?
            ^------------ 6: Contact on
           ^------------- 7: Ignition

0a18a000[6]:
  0x00 = 0b00000000 => Handbrake off, RWH off
  0x20 = 0b00100000 => Handbrake on, RWH off
  0x30 = 0b00110000 => Handbrake on, RWH on
              ^---------- 4: RWH on
             ^----------- 5: Handbrake on

0a18a000[7]:
  Increments on 8 bits when the wheels are turning

### 0a18a001
0a18a001[4:5]: Seems to rise when electrical components are used. Real meaning
unkown

### 0a181006
0a181006[0] => 00 when engine is off, 01 otherwise (seems)
0a181006[1] => Always 00. Real meaning unknown
0a181006[2] => Speed1
0a181006[3] => Speed2
0a181006[4:5] => Loops from 0x0000 to 0x1fff when car is running. Real meaning
0a181006[6:7] => unknown

### 0a28a000
0a28a000[0] => Speed1
0a28a000[1] => Speed2
0a28a000[3] ?= 0a18a000[7] => Increments on 8 bits when wheels are turning

### 0628a001
0628a001[5]:
  0x00 = 0b000000 => Clutch pedal released, Gearbox in neutral
  0x10 = 0b010000 => Clutch pedal released, some gear engaged
  0x20 = 0b100000 => Depressing clutch pedal
  0x30 = 0b110000 => Releasing clutch pedal

### 0a28a006
0a28a006[2] => Speed1
0a28a006[3] => Speed2

### 0c1ca000
0c1ca000[2]:
  0x28 = 0b00101000 => Any front door opened and SB disengaged, SS unavailable
  0x2C = 0b00101100 => All front door closed or  SB    engaged, SS unavailable
  0xC8 = 0b11001000 => Any front door opened and SB disengaged, SS off
  0xCC = 0b11001100 => All front door closed or  SB    engaged, SS off
  0xE8 = 0b11101000 => Any front door opened and SB disengaged, SS on
  0xEC = 0b11101100 => All front door closed or  SB    engaged, SS on
                ^-------- 2: All front door closed or SB engaged
             ^----------- 5: SS on
            ^------------ 6: SS available (?)
           ^------------- 7: SS available (?)


### 0c28a000
Date readeable in hexadecimal
0c28a000[0]: Hour
0c28a000[1]: Minute
0c28a000[2]: Day
0c28a000[3]: Month
0c28a000[4]: Year1
0c28a000[5]: Year2

Example:
> 0c28a000     21 02 24 05 20 17
> May, 24th 2017 - 9:02PM
