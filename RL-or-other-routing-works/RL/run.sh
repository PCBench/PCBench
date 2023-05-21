folder="../../PCBs/*"
for pcb in $folder; do
    echo "Processing $pcb" &>> run_log.txt
    python trainer.py $pcb &>> run_log.txt
done