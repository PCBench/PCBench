#!/bin/bash

# folder="../../PCBs/*"
# for pcb in $folder; do
#     echo "Processing $pcb"
#     n=$(echo "$pcb" | cut -d "/" -f 4)
#     python3 trainer.py $pcb &>> run_log_$n.txt &
# done

input="./pcb_names_$1.txt"
while IFS= read -r line
do
    echo "Processing $line"
    python3 agent.py "../../PCBs/$line" &>> run_log_$line.txt &
done < "$input"