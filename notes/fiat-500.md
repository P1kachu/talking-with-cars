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
0218a006:
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

------

0810a000[2] => Rises with force applied on breaks

------

0a18a000[0]:
0a18a000[6]:
  0x00 = 0b00000000 => Handbrake off
  0x20 = 0b00100000 => Handbrake on
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

0a18a000[7]:
 Increments on 8 bits

------

0a18a001[4:5]: rises when electrical components are used (?)

------

0a28a006[2] == 0a28a000[0] => Speed1
0a28a006[3] == 0a28a000[1] => Speed2

------

0a28a000[0] => Speed1
0a28a000[1] => Speed2
0a28a000[3] ?= 0a18a000[7] => Increments on 8 bits

------

0c1ca000[2]:
  0x28 = 0b00101000 => Any front door opened, contact on, Start&Stop unavailable
  0x2C = 0b00101100 => All front door closed, contact on, Start&Stop unavailable
  0xC8 = 0b11001000 => Any front door opened, contact on, Start&Stop off
  0xCC = 0b11001100 => All front door closed, contact on, Start&Stop off
  0xE8 = 0b11101000 => Any front door opened, contact on, Start&Stop on
  0xEC = 0b11101100 => All front door closed, contact on, Start&Stop on
                ^-------- 2: All front door closed
             ^----------- 5: Start&Stop on
            ^------------ 6: Start&Stop available

------

0c28a000
  Date readeable in hexadecimal
  0c28a000[0]: Hour
  0c28a000[1]: Minute
  0c28a000[2]: Day
  0c28a000[3]: Month
  0c28a000[4]: Year1
  0c28a000[5]: Year2
