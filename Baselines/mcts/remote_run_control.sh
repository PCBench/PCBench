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

declare -i idx=0
for serv in ${servers[@]}; do
	echo -e "copy $idx folder to $serv"
    # scp -r mul_run.py "$serv:~/PCBench/Baselines/mcts/"
    scp -r run.sh "$serv:~/PCBench/Baselines/mcts/"
	# scp -r ../RL/models_$idx "$serv:~/PCBench/Baselines/RL/"

	idx=$(( idx + 1 ))
done