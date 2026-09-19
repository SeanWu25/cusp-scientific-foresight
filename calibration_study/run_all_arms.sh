#!/bin/bash
# Usage: run_all_arms.sh <model> <concurrency>   — arms B1, B2, E at T=0; D at T=1.0. Resumable.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
M=$1; CONC=$2
for arm in B1 B2 E; do
  echo "=== $(date +%H:%M:%S) start $M $arm ==="
  $PY calibration_study/run_arm.py --model $M --arm $arm --temperature 0 --concurrency $CONC
done
echo "=== $(date +%H:%M:%S) start $M D ==="
$PY calibration_study/run_arm.py --model $M --arm D --temperature 1.0 --concurrency $CONC
echo "=== $(date +%H:%M:%S) ALL ARMS DONE $M ==="
