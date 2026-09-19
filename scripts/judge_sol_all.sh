#!/bin/bash
# Stage-1 leakage only for GPT-5.6 Sol. Stage 2 is deferred (rubric under
# revision); stage 1 runs now because it depends on live web search.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
OUT=results_sol_run1/judgements
mkdir -p "$OUT"
# wait for the Sonnet leakage re-run to release the Azure judge quota
while pgrep -f "leakage_with_evidence_run1" >/dev/null; do sleep 30; done
for t in base_medium_run1 ws_cutoff_500 ws_500; do
  # wait for the inference file to be finished if it is still being written
  while pgrep -f "run_cusp.py.*results_sol_run1/raw/$t.jsonl" >/dev/null; do sleep 30; done
  echo "=== $(date +%H:%M:%S) leakage: $t ==="
  $PY scripts/judge_frq.py --predictions "results_sol_run1/raw/$t.jsonl" \
      --output "$OUT/leakage_$t.jsonl" --stage leakage \
      --endpoint azure --concurrency 3 --resume 2>&1 | grep -E "^  [0-9]+/|DONE|judging"
done
echo "=== $(date +%H:%M:%S) SOL LEAKAGE JUDGING COMPLETE ==="
