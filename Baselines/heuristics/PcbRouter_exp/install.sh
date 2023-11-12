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

# install
for serv in ${servers[@]}; do

ssh -t -p 22 $serv << EOF
	sudo apt-get -y install cmake
	sudo apt-get install swig3.0
	sudo apt-get install libboost-all-dev

	git clone --recurse-submodules https://github.com/The-OpenROAD-Project/PcbRouter.git
	cd PcbRouter
	mkdir build
	cd build
	cmake ..
	make
	cd
	mkdir output
	mkdir logs
	exit
EOF
done