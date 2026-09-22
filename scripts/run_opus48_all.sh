#!/bin/bash
# Claude Opus 4.8 -- the full treatment the other new models got.
#
# Decoding mirrors Claude Sonnet 5 exactly (same cutoff month, same API family):
# no sampling params (the API rejects temperature with 400), effort=medium,
# max_tokens 2048, FRQ cap 384. Repeated passes on the extension bound the
# non-determinism that the missing temperature control leaves.
#
# Order: cheap and informative first.
#   1. extension base x3          (815 events each)   -> extension table + variance
#   2. extension WS pair          (86-event subset)   -> S2/S3 on unseen material
#   3. original-corpus WS pair    (pinned 500 subset) -> published S2/S3 comparison
#   4. original-corpus base x1    (4,760 events)      -> full-dataset row, pre/post
# All Anthropic API; no contention with the Azure judge.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
set -a; . ./.env; set +a
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
ORIG=archive/data/canonical/merged_validated_cusp_fixed.jsonl
EOUT=results_extension_run2/raw
OOUT=results_opus48_run1/raw
WS_EXT=results_extension_run2/ws_subset_ids.txt
WS_500=results_sonnet5_run1/subset500_ids.txt
CUT=2026-01
MODEL=claude-opus-4-8
CONC=${CONC:-8}
mkdir -p "$OOUT" results_opus48_run1/reports
LOG=results_opus48_run1/driver.log

run() {  # tag input output condition run_index [extra args...]
  local tag=$1 input=$2 output=$3 cond=$4 idx=$5; shift 5
  echo "=== $(date +%H:%M:%S) start $tag ===" | tee -a "$LOG"
  $PY scripts/run_cusp.py --input "$input" --output "$output" \
      --provider ANTHROPIC --model "$MODEL" --condition "$cond" --run-index "$idx" \
      --effort medium --frq-max-tokens 384 --concurrency "$CONC" --resume "$@" \
      >> "${output%.jsonl}.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$output" 2>/dev/null || echo 0) rows (exit $?) ===" | tee -a "$LOG"
}

# 1. extension base x3
run opus48_base_run1 "$EXT" "$EOUT/opus48_base_run1.jsonl" base 1
run opus48_base_run2 "$EXT" "$EOUT/opus48_base_run2.jsonl" base 2
run opus48_base_run3 "$EXT" "$EOUT/opus48_base_run3.jsonl" base 3
# 2. extension WS pair (same 86-event subset as Sonnet 5)
run opus48_ws_cutoff "$EXT" "$EOUT/opus48_ws_cutoff.jsonl" ws_cutoff 1 --ids-file "$WS_EXT" --ws-cutoff "$CUT"
run opus48_ws        "$EXT" "$EOUT/opus48_ws.jsonl"        ws        1 --ids-file "$WS_EXT"
# 3. original-corpus WS pair (pinned 500 subset)
run ws_cutoff_500 "$ORIG" "$OOUT/ws_cutoff_500.jsonl" ws_cutoff 1 --ids-file "$WS_500" --ws-cutoff "$CUT"
run ws_500        "$ORIG" "$OOUT/ws_500.jsonl"        ws        1 --ids-file "$WS_500"
# 4. original-corpus base
run base_medium_run1 "$ORIG" "$OOUT/base_medium_run1.jsonl" base 1
echo "=== $(date +%H:%M:%S) OPUS 4.8 INFERENCE COMPLETE ===" | tee -a "$LOG"
