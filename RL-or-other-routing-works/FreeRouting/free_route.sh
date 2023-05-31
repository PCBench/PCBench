#!/bin/bash

freerouting_exe=./freerouting-1.7.0.jar
circuit_folder=./unrouted/

for cir_file in "$circuit_folder"*.dsn
do
	out_extension=.ses
	out_file=${cir_file/.dsn/"$out_extension"}
	if test -f "$out_file"; then
		echo "$out_file exists."
		continue
	fi
	timeout 10m java -jar $freerouting_exe -de $cir_file -do $out_file -mp 100
done