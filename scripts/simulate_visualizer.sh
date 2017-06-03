#!/bin/sh

INTERFACE=vcan0
ID=18DB33F1

while true; do
	cansend $INTERFACE $ID#02410540     	   # Coolant
	cansend $INTERFACE $ID#04410C4040   	   # RPM
	cansend $INTERFACE $ID#04410D40     	   # Speed
	cansend $INTERFACE $ID#04411140     	   # Throttle
	cansend $INTERFACE $ID#04414940     	   # Accelerator

	cansend $INTERFACE 0a18a000#20AA20         # Handbrake, Misc1
	cansend $INTERFACE 0c1ca000#AAAAAA         # Misc2
	cansend $INTERFACE 0628a001#AAAAAAAAAA10   # Clutch
	cansend $INTERFACE 0810a000#AAAA20         # Brakes
	cansend $INTERFACE $ID#04414940     	   # Accelerator
	sleep 0.2
done
