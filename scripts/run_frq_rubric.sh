#!/bin/bash
# Stage-2 FRQ rubric grading (judge_frq_combined, sha256 fc24e69d..., 4 dims).
# Same judge and dimensions as the six published models -- nothing revised.
#
# Throughput is the same ~18 judgements/min ceiling as stage 1: judge_frq_combined
# is also a single LLM+web-search call against the same Azure deployment. So the
# same 3-concurrent-files limit applies; more only adds retries and hard failures.
#
# Covers every run, INCLUDING the three Claude ones whose FRQ responses are
# truncated at their token caps (ext sonnet45 99.6%, ext sonnet5 97.4%, orig
# sonnet5 96.3%). Grading them was an explicit decision. Their specificity and
# alignment scores are computed on text cut off mid-sentence while the rest of
# the panel answered to completion, and that asymmetry is invisible in the
# numbers themselves -- footnote it wherever these FRQ scores appear.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
ORIG=archive/data/canonical/merged_validated_cusp_fixed.jsonl
LOG=results_extension_run2/raw/rubric_logs
mkdir -p "$LOG" results_extension_run2/judgements_rubric \
         results_sol_run1/judgements_rubric results_dsv4pro_run1/judgements_rubric
PAR=${PAR:-3}

judge() {  # name raw benchmark outdir
  $PY scripts/judge_frq.py --predictions "$2" --benchmark "$3" \
      --output "$4/rubric_$1.jsonl" --stage rubric --endpoint azure \
      --concurrency 3 --resume > "$LOG/$1.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $1: $(wc -l < "$4/rubric_$1.jsonl" 2>/dev/null || echo 0)"
}

# extension first: smaller, completes the panel sooner
for t in gpt4o_base llama33_base gptoss20b_base gpt54_base sol_base deepseekv4pro_base \
         sonnet5_base_run1 sonnet45_base; do
  while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n; done
  judge "$t" "results_extension_run2/raw/$t.jsonl" "$EXT" \
        "results_extension_run2/judgements_rubric" &
done
wait
echo "=== $(date +%H:%M:%S) EXTENSION RUBRIC DONE (8 models) ==="

# then the two untruncated original-corpus runs
mkdir -p results_sonnet5_run1/judgements_rubric
for spec in "sol_orig|results_sol_run1/raw/base_medium_run1.jsonl|results_sol_run1/judgements_rubric" \
            "dsv4pro_orig|results_dsv4pro_run1/raw/base_run1.jsonl|results_dsv4pro_run1/judgements_rubric" \
            "sonnet5_orig|results_sonnet5_run1/raw/base_medium_run1.jsonl|results_sonnet5_run1/judgements_rubric"; do
  IFS="|" read -r nm raw out <<< "$spec"
  while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n; done
  judge "$nm" "$raw" "$ORIG" "$out" &
done
wait
echo "=== $(date +%H:%M:%S) ALL RUBRIC GRADING COMPLETE ==="
