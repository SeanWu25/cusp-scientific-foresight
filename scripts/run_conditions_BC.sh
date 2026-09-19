#!/bin/bash
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
CORPUS=archive/data/canonical/merged_validated_cusp_fixed.jsonl
IDS=results_sonnet5_run1/subset500_ids.txt
OUT=results_sonnet5_run1/raw

run () {  # run <condition> <tag> [extra args...]
  local cond="$1" tag="$2"; shift 2
  echo "=== $(date +%H:%M:%S) starting $tag ==="
  $PY scripts/run_cusp.py \
      --input "$CORPUS" --ids-file "$IDS" --output "$OUT/$tag.jsonl" \
      --provider ANTHROPIC --model claude-sonnet-5 \
      --condition "$cond" --run-index 1 --effort medium \
      --frq-max-tokens 384 --concurrency 6 --resume "$@" \
      >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) finished $tag: $(wc -l < "$OUT/$tag.jsonl") rows ==="
}

run ws_cutoff ws_cutoff_500 --ws-cutoff 2026-01
run ws        ws_500
echo "=== $(date +%H:%M:%S) CONDITIONS B AND C COMPLETE ==="
