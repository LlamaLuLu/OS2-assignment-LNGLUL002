#!/bin/bash

mkdir -p results

PATRONS=(10 30 50)
SEEDS=(42 123 999)
SCHEDS=(1 2 3 4)

for n in "${PATRONS[@]}"; do
    for seed in "${SEEDS[@]}"; do
        for sched in "${SCHEDS[@]}"; do
            echo "Running: patrons=$n sched=$sched seed=$seed"
            make run ARGS="$n $sched 0 $seed" > /dev/null
        done
    done
done

echo "All runs complete. Results in results/"
