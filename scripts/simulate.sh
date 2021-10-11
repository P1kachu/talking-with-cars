#!/bin/sh

INTERFACE=vcan0
ID=7E8

if [ "$INTERFACE" = "vcan0" ]; then
        modprobe vcan
        sudo ip link add dev vcan0 type vcan
        sudo ip link set up vcan0
fi


while false; do
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

while true; do
        while read line; do
                echo $line
                id=$(echo $line |cut -d" " -f5)
                data=$(echo $line |cut -d" " -f7-15|sed 's/ //g'|cut -d"'" -f1)
                #echo $INTERFACE $id\#$data
                cansend $INTERFACE $id\#$data
                sleep 0.01
        done <test_nissan_leaf_traffic.log
        echo "Loop back"
done
