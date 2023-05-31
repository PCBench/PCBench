#!/bin/bash

input="./test.txt"
while IFS= read -r line
do
    echo "Processing $line"
    python3 main_mcts.py "../../PCBs/$line/final.json" "../RL/models/policy_$line" 0.5 &>> run_log_$line.txt
done < "$input"