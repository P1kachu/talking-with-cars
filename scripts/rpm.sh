#!/bin/bash

dump_to_rpm()
{
	cansend can0 7df#02010c0000000000
	while read data; do
		#echo $data
		value=$(echo $data | grep RX | cut -d' ' -f10-11);
		x=$(echo $value | cut -d' ' -f1);
		y=$(echo $value | cut -d' ' -f2);
		if [[ -z $x ]]; then continue 2; fi
		x=$((16#$x))
		y=$((16#$y))
		final=$(echo "$(($(($((256 * $x + $y)) / 4))/20))")
		python -c "print('.' * $final)";
		cansend can0 7df#02010c0000000000
	done
}

candump -a -d -e -x can0 | dump_to_rpm
