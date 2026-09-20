#!/bin/bash
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
WS=results_extension_run2/ws_subset_ids.txt
OUT=results_extension_run2/raw
go () {
  local tag="$1" cond="$2" idx="$3" conc="$4"; shift 4
  echo "=== $(date +%H:%M:%S) start $tag ==="
  $PY scripts/run_cusp.py --input "$EXT" --output "$OUT/$tag.jsonl" \
      --provider ANTHROPIC --model claude-sonnet-5 --condition "$cond" --run-index "$idx" \
      --effort medium --frq-max-tokens 384 --concurrency "$conc" --resume "$@" \
      >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$OUT/$tag.jsonl") rows ==="
}
go sonnet5_base_run1 base 1 14
go sonnet5_base_run2 base 2 14
go sonnet5_ws_cutoff ws_cutoff 1 6 --ids-file "$WS" --ws-cutoff 2026-01
go sonnet5_ws        ws        1 6 --ids-file "$WS"
echo "=== $(date +%H:%M:%S) SONNET 5 EXTENSION COMPLETE ==="
