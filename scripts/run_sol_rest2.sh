#!/bin/bash
# Sol remaining work. Pass 1 is already complete (4,760 rows); no wait loop --
# the previous one matched the Sonnet judge processes by pattern and hung.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
CORPUS=archive/data/canonical/merged_validated_cusp_fixed.jsonl
VAR=results_sol_run1/variance_subsample_ids.txt
IDS=results_sonnet5_run1/subset500_ids.txt
OUT=results_sol_run1/raw
go () {
  local tag="$1" cond="$2" idx="$3" conc="$4"; shift 4
  echo "=== $(date +%H:%M:%S) start $tag ==="
  $PY scripts/run_cusp.py --input "$CORPUS" --output "$OUT/$tag.jsonl" \
      --provider OPENAI --model gpt-5.6-sol --condition "$cond" --run-index "$idx" \
      --effort medium --max-tokens 2048 --frq-max-tokens 2048 \
      --concurrency "$conc" --resume "$@" >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$OUT/$tag.jsonl") rows ==="
}
go base_medium_run2 base      2 16 --ids-file "$VAR"
go base_medium_run3 base      3 16 --ids-file "$VAR"
go ws_cutoff_500    ws_cutoff 1  6 --ids-file "$IDS" --ws-cutoff 2026-02
go ws_500           ws        1  6 --ids-file "$IDS"
echo "=== $(date +%H:%M:%S) SOL INFERENCE COMPLETE ==="
