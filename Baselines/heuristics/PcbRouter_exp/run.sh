#!/bin/bash

for filename in ./split_unrouted_$1/*.kicad_pcb; do

	read pcbname <<< "${filename##*/}"
	echo "PCB name is: $pcbname"

	if ! test -f ./logs/$pcbname.log; then
		./PcbRouter/bin/pcbrouter $filename > ./logs/$pcbname.log
	fi

	sleep 30
done
