#!/bin/bash
# Stage-2 FRQ rubric grading (judge_frq_combined, sha256 fc24e69d..., 4 dims).
# Same judge and dimensions as the six published models -- nothing revised.
#
# Stage 2 is NOT stage 1. judge_frq_combined sends a 2,697-char rubric plus the
# full FRQ response and returns four scored dimensions, so it burns several
# times the tokens per call. The deployment is token-bound, not request-bound,
# and the throughput curve has a sharp knee -- measured, 5-minute windows:
#
#     slots   throughput   errors   retry rate
#       2       7.6/min      0%        30%
#       4      11.4/min      0%        50%     <- operating point
#       6      11.6/min      5%         -      (no gain, failures return)
#       9       5.6/min     16%        57%     (past the knee: strictly worse)
#
# Past the knee retries eat the quota that would otherwise serve first attempts,
# so pushing harder is worse on BOTH throughput and completeness. 2 files x
# concurrency 2 = 4 slots.
#
# Three kinds of work, in this order:
#   1. GAP FILLS. Runs that already carry rubric scores for most events (the
#      pre-deferral Sonnet 5 grading, the Sol/Sonnet 5 web-search subsets). The
#      rubric hash is unchanged, so those scores stand; only the missing ones
#      are graded, from a todo subset (scripts/frq_todo.py), into a fresh file.
#      --resume cannot do this itself: it treats any id present in the output
#      as done, and the gap rows ARE present -- with a null score.
#   2. Extension base runs, all 8 models, fresh files, resume by id.
#   3. Original-corpus base runs for GPT-5.6 Sol and DeepSeek-V4-Pro, which
#      have no rubric scores at all (~4,100 each).
#
# Covers the three Claude runs whose FRQ responses are truncated at their token
# caps (ext sonnet45 99.6%, ext sonnet5 97.4%, orig sonnet5 96.3%), by explicit
# decision. Their scores are computed on text cut off mid-sentence while the
# rest of the panel answered to completion. Footnote that asymmetry wherever
# the numbers appear -- but do not assert its direction: on the original corpus
# Sonnet 5 scores specificity 5.40 despite 96% truncation, second in the panel.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
ORIG=archive/data/canonical/merged_validated_cusp_fixed.jsonl
LOG=results_extension_run2/raw/rubric_logs
mkdir -p "$LOG" results_extension_run2/judgements_rubric \
         results_sol_run1/judgements_rubric results_dsv4pro_run1/judgements_rubric \
         results_sonnet5_run1/judgements_rubric
PAR=${PAR:-2}

judge() {  # name predictions benchmark outdir
  [ -s "$2" ] || { echo "=== skip $1: nothing to grade"; return; }
  $PY scripts/judge_frq.py --predictions "$2" --benchmark "$3" \
      --output "$4/rubric_$1.jsonl" --stage rubric --endpoint azure \
      --concurrency 2 --resume > "$LOG/$1.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $1: $(wc -l < "$4/rubric_$1.jsonl" 2>/dev/null || echo 0)"
}
throttle() { while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n; done; }

# ---- 1. gap fills (657 items total; cheap, and they complete the WS block) ----
S5=results_sonnet5_run1/judgements_rubric
SO=results_sol_run1/judgements_rubric
EX=results_extension_run2/judgements_rubric
for spec in \
  "sonnet5_orig_gaps|$S5/todo_base_medium_run1.jsonl|$ORIG|$S5" \
  "sol_ws_500|$SO/todo_ws_500.jsonl|$ORIG|$SO" \
  "sol_ws_cutoff_500|$SO/todo_ws_cutoff_500.jsonl|$ORIG|$SO" \
  "sonnet5_ws_500|$S5/todo_ws_500.jsonl|$ORIG|$S5" \
  "sonnet5_ws_cutoff_500|$S5/todo_ws_cutoff_500.jsonl|$ORIG|$S5" \
  "sonnet5_ws|$EX/todo_sonnet5_ws.jsonl|$EXT|$EX" \
  "sonnet5_ws_cutoff|$EX/todo_sonnet5_ws_cutoff.jsonl|$EXT|$EX"; do
  IFS="|" read -r nm pred bench out <<< "$spec"
  throttle; judge "$nm" "$pred" "$bench" "$out" &
done

# ---- 2. extension base runs ----
for t in gpt4o_base llama33_base gptoss20b_base gpt54_base sol_base deepseekv4pro_base \
         sonnet5_base_run1 sonnet45_base; do
  throttle; judge "$t" "results_extension_run2/raw/$t.jsonl" "$EXT" "$EX" &
done
wait
echo "=== $(date +%H:%M:%S) GAP FILLS + EXTENSION RUBRIC DONE ==="

# ---- 3. original-corpus base runs with no rubric scores at all ----
for spec in \
  "sol_orig|results_sol_run1/raw/base_medium_run1.jsonl|$SO" \
  "dsv4pro_orig|results_dsv4pro_run1/raw/base_run1.jsonl|results_dsv4pro_run1/judgements_rubric"; do
  IFS="|" read -r nm raw out <<< "$spec"
  throttle; judge "$nm" "$raw" "$ORIG" "$out" &
done
wait
echo "=== $(date +%H:%M:%S) ALL RUBRIC GRADING COMPLETE ==="
