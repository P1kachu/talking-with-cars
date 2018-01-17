# Toyota Yaris

These are only "listen-only" fetched CAN messages. \
I did not had the permisson to send any CAN packet :(

|Designation|ID|bit-start| bit-count |
|-|-|-|-|
| name of the guessed field | Can ID | bit from which the data starts | bit length of the data |


## Speed

|Designation|ID|bit-start| bit-count |
|-|-|-|-|
|speed (high refresh)|0x0b4|40|16|
|speed (low refresh)|0x610|8|16|

speed must be multiplied by 100.0 to get the real value. (Fixed point storage)

## Wheels

Warning: front and left might be inverted. Only left-right is guarenteed

|Designation|ID|bit-start| bit-count |
|-|-|-|-|
|wheel-front-left|0x0b0|0|16|
|wheel-front-right|0x0b0|16|16|
|wheel-back-left|0x0b2|0|16|
|wheel-back-right|0x0b2|16|16|

On the bits from 24 to 32, there is a value ALWAYS updating, and cycling on the byte. \
Maybe some type on alive-check ? \
Also byte 16 to 24 (the third one) os always at 0x11

## Controls

|Designation|ID|bit-start| bit-count |
|-|-|-|-|
|brake-a|0x3b4|39|1|
|brake-b|0x224|2|1|
|steering|0x260|40|24|
|parking-brake|0x620|59|1|


## Engine

|Designation|ID|bit-start| bit-count |
|-|-|-|-|
|engine-rev (high refresh)|0x2c4|0|16|
|unknown 1|0x2c4|54|8|
|engine-rev (low refresh)|0x3b3|0|16|
|throttle slow|0x398|0|16|

## Misc

|Designation|ID|bit-start| bit-count |
|-|-|-|-|
|km-count|0x620|40|24|
|door-rear-open|0x620|44|2|
|door-front-left-open|0x620|43|1|
|door-front-right-open|0x620|42|1|
|door-trunk|0x620|46|1|
|lock-trigger|0x621|8|1|
|lock-error|0x621|16|1|
|door-unlocked|0x638|19|1|

Despite being on 2 bits, rear doors are not distinct. \
Lock-error in set ONLY when the driver-side door is left open upon locking. \
Driver-side door is the only one which will unlock the vehicle once opened.
