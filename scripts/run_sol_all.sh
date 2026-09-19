#!/bin/bash
# GPT-5.6 Sol: three repeated full-corpus passes, then the two web-search
# conditions over the pinned 500-event subset.
#   reasoning_effort=medium  (the model's default; also suppresses the
#                             temperature argument, which this model rejects)
#   FRQ max_tokens=2048      (what the five published OpenAI models used; the
#                             cap covers reasoning tokens on this model, so a
#                             smaller cap returns empty text)
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
CORPUS=archive/data/canonical/merged_validated_cusp_fixed.jsonl
IDS=results_sonnet5_run1/subset500_ids.txt
OUT=results_sol_run1/raw
M=gpt-5.6-sol

pass () {
  local idx="$1" tag="$2"
  echo "=== $(date +%H:%M:%S) start $tag ==="
  $PY scripts/run_cusp.py --input "$CORPUS" --output "$OUT/$tag.jsonl" \
      --provider OPENAI --model "$M" --condition base --run-index "$idx" \
      --effort medium --max-tokens 2048 --frq-max-tokens 2048 \
      --concurrency 16 --resume >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$OUT/$tag.jsonl") rows ==="
}
sub () {
  local cond="$1" tag="$2"; shift 2
  echo "=== $(date +%H:%M:%S) start $tag ==="
  $PY scripts/run_cusp.py --input "$CORPUS" --ids-file "$IDS" --output "$OUT/$tag.jsonl" \
      --provider OPENAI --model "$M" --condition "$cond" --run-index 1 \
      --effort medium --max-tokens 2048 --frq-max-tokens 2048 \
      --concurrency 6 --resume "$@" >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$OUT/$tag.jsonl") rows ==="
}
pass 1 base_medium_run1
pass 2 base_medium_run2
pass 3 base_medium_run3
sub ws_cutoff ws_cutoff_500 --ws-cutoff 2026-02
sub ws        ws_500
echo "=== $(date +%H:%M:%S) GPT-5.6 SOL ALL PASSES COMPLETE ==="
