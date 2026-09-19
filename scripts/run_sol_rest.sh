#!/bin/bash
# GPT-5.6 Sol, remaining passes.
#   pass 1        : full corpus (already in flight)
#   passes 2 & 3  : 1,000-event variance subsample, NOT the full corpus.
#                   Run-to-run variance on Sonnet 5 came out at sd 0.003-0.004,
#                   an order of magnitude under the CIs. A 1,000-event sample
#                   that already contains EVERY post-cutoff event estimates that
#                   quantity just as tightly, for a third of the wall clock.
#   conditions    : WS+Cutoff and WS over the pinned 500-event subset.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
CORPUS=archive/data/canonical/merged_validated_cusp_fixed.jsonl
VAR=results_sol_run1/variance_subsample_ids.txt
IDS=results_sonnet5_run1/subset500_ids.txt
OUT=results_sol_run1/raw
M=gpt-5.6-sol

go () {
  local tag="$1" cond="$2" idx="$3" conc="$4"; shift 4
  echo "=== $(date +%H:%M:%S) start $tag ==="
  $PY scripts/run_cusp.py --input "$CORPUS" --output "$OUT/$tag.jsonl" \
      --provider OPENAI --model "$M" --condition "$cond" --run-index "$idx" \
      --effort medium --max-tokens 2048 --frq-max-tokens 2048 \
      --concurrency "$conc" --resume "$@" >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$OUT/$tag.jsonl") rows ==="
}

while pgrep -f "base_medium_run1" >/dev/null; do sleep 30; done
echo "=== $(date +%H:%M:%S) pass1 done: $(wc -l < $OUT/base_medium_run1.jsonl) rows ==="
go base_medium_run2 base      2 16 --ids-file "$VAR"
go base_medium_run3 base      3 16 --ids-file "$VAR"
go ws_cutoff_500    ws_cutoff 1  6 --ids-file "$IDS" --ws-cutoff 2026-02
go ws_500           ws        1  6 --ids-file "$IDS"
echo "=== $(date +%H:%M:%S) SOL COMPLETE ==="
