#!/bin/bash
# Stage-1 leakage then stage-2 rubric for every judged Claude Opus 4.8 file.
# Same judge, same rubric (fc24e69d...), same throughput discipline as before:
# stage 1 at 3 concurrent files x concurrency 3; stage 2 at 2 files x concurrency 2
# (the measured knee; more only adds failures). Files that do not exist yet are
# skipped, so this can be run as soon as the first raw file lands and re-run later.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
ORIG=archive/data/canonical/merged_validated_cusp_fixed.jsonl
E=results_extension_run2; OP=results_opus48_run1
LOG=$E/raw/rubric_logs; mkdir -p "$LOG" $E/judgements $E/judgements_rubric $OP/judgements $OP/judgements_rubric
# name | raw | benchmark | leakage out | rubric out
JOBS=(
 "opus48_base_run1|$E/raw/opus48_base_run1.jsonl|$EXT|$E/judgements/leakage_opus48_base_run1.jsonl|$E/judgements_rubric/rubric_opus48_base_run1.jsonl"
 "opus48_ws|$E/raw/opus48_ws.jsonl|$EXT|$E/judgements/leakage_opus48_ws.jsonl|$E/judgements_rubric/rubric_opus48_ws.jsonl"
 "opus48_ws_cutoff|$E/raw/opus48_ws_cutoff.jsonl|$EXT|$E/judgements/leakage_opus48_ws_cutoff.jsonl|$E/judgements_rubric/rubric_opus48_ws_cutoff.jsonl"
 "opus48_orig|$OP/raw/base_medium_run1.jsonl|$ORIG|$OP/judgements/leakage_base_medium_run1.jsonl|$OP/judgements_rubric/rubric_opus48_orig.jsonl"
 "opus48_ws_500|$OP/raw/ws_500.jsonl|$ORIG|$OP/judgements/leakage_ws_500.jsonl|$OP/judgements_rubric/rubric_opus48_ws_500.jsonl"
 "opus48_ws_cutoff_500|$OP/raw/ws_cutoff_500.jsonl|$ORIG|$OP/judgements/leakage_ws_cutoff_500.jsonl|$OP/judgements_rubric/rubric_opus48_ws_cutoff_500.jsonl"
)
stage() {  # stage par conc outfield
  local st=$1 par=$2 conc=$3 field=$4
  for spec in "${JOBS[@]}"; do
    IFS="|" read -r nm raw bench lk rb <<< "$spec"
    [ -s "$raw" ] || { echo "  skip $nm ($st): raw not present"; continue; }
    out=$lk; [ "$field" = rubric ] && out=$rb
    while [ "$(jobs -rp | wc -l)" -ge "$par" ]; do wait -n; done
    ( $PY scripts/judge_frq.py --predictions "$raw" --benchmark "$bench" --output "$out" \
          --stage "$st" --endpoint azure --concurrency "$conc" --resume > "$LOG/${st}_$nm.log" 2>&1
      echo "=== $(date +%H:%M:%S) done $st $nm: $(wc -l < "$out" 2>/dev/null || echo 0)" ) &
  done
  wait
}
echo "=== $(date +%H:%M:%S) OPUS 4.8 STAGE 1 (leakage) ==="; stage leakage 3 3 leakage
echo "=== $(date +%H:%M:%S) OPUS 4.8 STAGE 2 (rubric) ===";  stage rubric  2 2 rubric
echo "=== $(date +%H:%M:%S) OPUS 4.8 JUDGING COMPLETE ==="
