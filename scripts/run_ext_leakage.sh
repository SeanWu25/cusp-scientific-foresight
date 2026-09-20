#!/bin/bash
# Stage-1 leakage judging for every completed extension run.
# Runs against the Azure gpt-4o judge deployment, which is a different
# deployment from DeepSeek-V4-Pro, so it does not share that quota.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
OUT=results_extension_run2/raw
JUD=results_extension_run2/judgements
mkdir -p "$JUD"
for t in sonnet5_base_run1 sonnet5_ws_cutoff sonnet5_ws llama33_base sonnet45_base \
         deepseekv4pro_base gpt4o_base gpt54_base sol_base; do
  [ -f "$OUT/$t.jsonl" ] || { echo "skip $t (no raw)"; continue; }
  echo "=== $(date +%H:%M:%S) leakage: $t ==="
  $PY scripts/judge_frq.py --predictions "$OUT/$t.jsonl" \
      --benchmark "$EXT" --output "$JUD/leakage_$t.jsonl" --stage leakage \
      --endpoint azure --concurrency 3 --resume 2>&1 | grep -E "^  [0-9]+/|DONE|judging"
  echo "=== $(date +%H:%M:%S) done $t: $(wc -l < "$JUD/leakage_$t.jsonl" 2>/dev/null || echo 0) verdicts ==="
done
echo "=== $(date +%H:%M:%S) EXTENSION LEAKAGE COMPLETE ==="
