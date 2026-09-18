#!/bin/bash
# Condition A: full corpus, three repeated passes at the frozen settings,
# plus one low-effort pass as the effort-sensitivity check.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
CORPUS=archive/data/canonical/merged_validated_cusp_fixed.jsonl
OUT=results_sonnet5_run1/raw

run () {  # run <run_index> <effort> <tag>
  local idx="$1" eff="$2" tag="$3"
  echo "=== $(date +%H:%M:%S) starting $tag (run_index=$idx effort=$eff) ==="
  $PY scripts/run_cusp.py \
      --input "$CORPUS" --output "$OUT/$tag.jsonl" \
      --provider ANTHROPIC --model claude-sonnet-5 \
      --condition base --run-index "$idx" --effort "$eff" \
      --frq-max-tokens 384 --concurrency 16 --resume \
      >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) finished $tag: $(wc -l < "$OUT/$tag.jsonl") rows ==="
}

# run 1 is already in flight; wait for it to drain before starting run 2
while pgrep -f "run_cusp.py.*base_medium_run1" >/dev/null; do sleep 30; done
echo "=== $(date +%H:%M:%S) run1 complete: $(wc -l < $OUT/base_medium_run1.jsonl) rows ==="

run 2 medium base_medium_run2
run 3 medium base_medium_run3
run 1 low    base_low_run1
echo "=== $(date +%H:%M:%S) ALL CONDITION A PASSES COMPLETE ==="
