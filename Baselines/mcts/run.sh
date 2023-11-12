declare -i idx=$1
for i in {0..19}
do
    python3 mul_run.py ../RL/models_$idx $
    sleep 1800
done