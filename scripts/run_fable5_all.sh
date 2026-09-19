#!/bin/bash
# Fable 5: three repeated full-corpus passes at the frozen settings, then the
# two web-search conditions over the pinned 500-event subset.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
CORPUS=archive/data/canonical/merged_validated_cusp_fixed.jsonl
IDS=results_sonnet5_run1/subset500_ids.txt
OUT=results_fable5_run1/raw
M=claude-fable-5

pass () {  # pass <run_index> <effort> <tag> [extra...]
  local idx="$1" eff="$2" tag="$3"; shift 3
  echo "=== $(date +%H:%M:%S) start $tag ==="
  $PY scripts/run_cusp.py --input "$CORPUS" --output "$OUT/$tag.jsonl" \
      --provider ANTHROPIC --model "$M" --condition base --run-index "$idx" \
      --effort "$eff" --frq-max-tokens 384 --concurrency 16 --resume "$@" \
      >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$OUT/$tag.jsonl") rows ==="
}
sub () {  # sub <condition> <tag> [extra...]
  local cond="$1" tag="$2"; shift 2
  echo "=== $(date +%H:%M:%S) start $tag ==="
  $PY scripts/run_cusp.py --input "$CORPUS" --ids-file "$IDS" --output "$OUT/$tag.jsonl" \
      --provider ANTHROPIC --model "$M" --condition "$cond" --run-index 1 \
      --effort medium --frq-max-tokens 384 --concurrency 6 --resume "$@" \
      >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$OUT/$tag.jsonl") rows ==="
}

while pgrep -f "run_cusp.py.*results_fable5_run1/raw/base_medium_run1" >/dev/null; do sleep 30; done
echo "=== $(date +%H:%M:%S) run1 done: $(wc -l < $OUT/base_medium_run1.jsonl) rows ==="
pass 2 medium base_medium_run2
pass 3 medium base_medium_run3
sub  ws_cutoff ws_cutoff_500 --ws-cutoff 2026-01
sub  ws        ws_500
echo "=== $(date +%H:%M:%S) FABLE 5 ALL PASSES COMPLETE ==="
