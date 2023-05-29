#!/bin/bash

# folder="../../PCBs/*"
# for pcb in $folder; do
#     echo "Processing $pcb"
#     n=$(echo "$pcb" | cut -d "/" -f 4)
#     python3 trainer.py $pcb &>> run_log_$n.txt &
# done

input="./rerun_pcb.txt"
while IFS= read -r line
do
    echo "Processing $line"
    python3 trainer.py "../../PCBs/$line" &>> run_log_$line.txt
done < "$input"