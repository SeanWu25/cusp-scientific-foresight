#!/bin/bash
# Sonnet 5 third variance pass + stage-1 leakage judging for the extension.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
OUT=results_extension_run2/raw
JUD=results_extension_run2/judgements
mkdir -p "$JUD"
echo "=== $(date +%H:%M:%S) sonnet5 pass 3 ==="
$PY scripts/run_cusp.py --input "$EXT" --output "$OUT/sonnet5_base_run3.jsonl" \
    --provider ANTHROPIC --model claude-sonnet-5 --condition base --run-index 3 \
    --effort medium --frq-max-tokens 384 --concurrency 14 --resume \
    >> "$OUT/sonnet5_base_run3.log" 2>&1
echo "=== $(date +%H:%M:%S) done pass 3: $(wc -l < "$OUT/sonnet5_base_run3.jsonl") rows ==="
# stage-1 leakage for every completed extension run, once the azure panel is idle
while pgrep -f "run_ext_panel" >/dev/null; do sleep 60; done
for t in sonnet5_base_run1 sonnet5_ws_cutoff sonnet5_ws llama33_base sonnet45_base \
         deepseekv4pro_base gpt4o_base gpt54_base sol_base gptoss20b_base; do
  [ -f "$OUT/$t.jsonl" ] || { echo "skip $t (no raw)"; continue; }
  echo "=== $(date +%H:%M:%S) leakage: $t ==="
  $PY scripts/judge_frq.py --predictions "$OUT/$t.jsonl" \
      --benchmark "$EXT" --output "$JUD/leakage_$t.jsonl" --stage leakage \
      --endpoint azure --concurrency 3 --resume 2>&1 | grep -E "^  [0-9]+/|DONE|judging"
done
echo "=== $(date +%H:%M:%S) EXTENSION LEAKAGE COMPLETE ==="
