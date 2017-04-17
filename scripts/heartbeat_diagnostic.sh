#!/bin/sh

# Used to tell the car to stay in diagnostic mode

while :
do
        cansend can0 7df#013e
        sleep 1
done
