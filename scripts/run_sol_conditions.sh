#!/bin/bash
# GPT-5.6 Sol: the two retrieval conditions over the pinned 500-event subset.
# Passes 1-3 are already complete.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
CORPUS=archive/data/canonical/merged_validated_cusp_fixed.jsonl
IDS=results_sonnet5_run1/subset500_ids.txt
OUT=results_sol_run1/raw
go () {
  local tag="$1" cond="$2"; shift 2
  echo "=== $(date +%H:%M:%S) start $tag ==="
  $PY scripts/run_cusp.py --input "$CORPUS" --ids-file "$IDS" --output "$OUT/$tag.jsonl" \
      --provider OPENAI --model gpt-5.6-sol --condition "$cond" --run-index 1 \
      --effort medium --max-tokens 2048 --frq-max-tokens 2048 \
      --concurrency 6 --resume "$@" >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$OUT/$tag.jsonl") rows ==="
}
go ws_cutoff_500 ws_cutoff --ws-cutoff 2026-02
go ws_500        ws
echo "=== $(date +%H:%M:%S) SOL INFERENCE COMPLETE ==="
