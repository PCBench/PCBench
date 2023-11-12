#!/bin/bash

servers=(Ybiao@c220g1-030611.wisc.cloudlab.us
		Ybiao@c220g1-030605.wisc.cloudlab.us
		Ybiao@c220g1-030608.wisc.cloudlab.us
		Ybiao@c220g1-030607.wisc.cloudlab.us
		Ybiao@c220g1-030621.wisc.cloudlab.us
		Ybiao@c220g2-011321.wisc.cloudlab.us
		Ybiao@c220g1-030613.wisc.cloudlab.us
		Ybiao@c220g1-030629.wisc.cloudlab.us
		Ybiao@c220g2-011322.wisc.cloudlab.us
		Ybiao@c220g1-030614.wisc.cloudlab.us)

declare -i idx=50
for serv in ${servers[@]}; do
ssh -t -p 22 $serv << EOF
	cd ~/PCBench/Baselines/RL
	rm -r logs
	rm -r models
	rm -r run_log*
	bash run.sh $idx
	exit
EOF
idx=$(( idx + 1 ))
done