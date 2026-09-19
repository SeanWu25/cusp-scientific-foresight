#!/bin/bash
# Fable 5: after run 1, the two web-search conditions on the pinned 500 only.
# Repeat passes are deliberately NOT queued: Fable 5 declines ~1/3 of the corpus,
# so paying for run-to-run variance on it is poor value until that is settled.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
CORPUS=archive/data/canonical/merged_validated_cusp_fixed.jsonl
IDS=results_sonnet5_run1/subset500_ids.txt
OUT=results_fable5_run1/raw
sub () {
  local cond="$1" tag="$2"; shift 2
  echo "=== $(date +%H:%M:%S) start $tag ==="
  $PY scripts/run_cusp.py --input "$CORPUS" --ids-file "$IDS" --output "$OUT/$tag.jsonl" \
      --provider ANTHROPIC --model claude-fable-5 --condition "$cond" --run-index 1 \
      --effort medium --frq-max-tokens 384 --concurrency 6 --resume "$@" \
      >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$OUT/$tag.jsonl") rows ==="
}
while pgrep -f "run_cusp.py.*results_fable5_run1/raw/base_medium_run1" >/dev/null; do sleep 30; done
echo "=== $(date +%H:%M:%S) run1 done: $(wc -l < $OUT/base_medium_run1.jsonl) rows ==="
sub ws_cutoff ws_cutoff_500 --ws-cutoff 2026-01
sub ws        ws_500
echo "=== $(date +%H:%M:%S) FABLE 5 RUN1 + CONDITIONS COMPLETE ==="
