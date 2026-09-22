#!/bin/bash
# Residual-gap sweep for stage-2 FRQ grading. Run AFTER run_frq_rubric.sh.
#
# A first pass leaves a few items per run with no score: the judge sometimes
# returns null ("could not assess"), and a small number of calls exhaust their
# retries. --resume never revisits them because their id is already present in
# the output. This recomputes the todo subset for every job from ALL existing
# judgement files and grades just those leftovers into a *_sweep file, which
# finalize_run2.sh merges field-by-field like everything else.
#
# Safe to re-run; each pass only touches what is still unscored.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
ORIG=archive/data/canonical/merged_validated_cusp_fixed.jsonl
E=results_extension_run2; S5=results_sonnet5_run1; SO=results_sol_run1; DS=results_dsv4pro_run1; OP=results_opus48_run1
LOG=$E/raw/rubric_logs; mkdir -p "$LOG"

# name | raw predictions | benchmark | outdir | existing judgement files (space-separated)
JOBS=(
 "gpt4o_base|$E/raw/gpt4o_base.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_gpt4o_base.jsonl"
 "llama33_base|$E/raw/llama33_base.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_llama33_base.jsonl"
 "gptoss20b_base|$E/raw/gptoss20b_base.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_gptoss20b_base.jsonl"
 "gpt54_base|$E/raw/gpt54_base.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_gpt54_base.jsonl"
 "sol_base|$E/raw/sol_base.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_sol_base.jsonl"
 "deepseekv4pro_base|$E/raw/deepseekv4pro_base.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_deepseekv4pro_base.jsonl"
 "sonnet5_base_run1|$E/raw/sonnet5_base_run1.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_sonnet5_base_run1.jsonl"
 "sonnet45_base|$E/raw/sonnet45_base.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_sonnet45_base.jsonl"
 "sonnet5_ws|$E/raw/sonnet5_ws.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_sonnet5_ws.jsonl"
 "sonnet5_ws_cutoff|$E/raw/sonnet5_ws_cutoff.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_sonnet5_ws_cutoff.jsonl"
 "sonnet5_orig_gaps|$S5/raw/base_medium_run1.jsonl|$ORIG|$S5/judgements_rubric|$S5/raw/judged_base_medium_run1.jsonl $S5/judgements_rubric/rubric_sonnet5_orig_gaps.jsonl"
 "sonnet5_ws_500|$S5/raw/ws_500.jsonl|$ORIG|$S5/judgements_rubric|$S5/raw/judged_ws_500.jsonl $S5/judgements_rubric/rubric_sonnet5_ws_500.jsonl"
 "sonnet5_ws_cutoff_500|$S5/raw/ws_cutoff_500.jsonl|$ORIG|$S5/judgements_rubric|$S5/raw/judged_ws_cutoff_500.jsonl $S5/judgements_rubric/rubric_sonnet5_ws_cutoff_500.jsonl"
 "sol_orig|$SO/raw/base_medium_run1.jsonl|$ORIG|$SO/judgements_rubric|$SO/judgements/leakage_base_medium_run1.jsonl $SO/judgements_rubric/rubric_sol_orig.jsonl"
 "sol_ws_500|$SO/raw/ws_500.jsonl|$ORIG|$SO/judgements_rubric|$SO/judgements/leakage_ws_500.jsonl $SO/judgements_rubric/rubric_sol_ws_500.jsonl"
 "sol_ws_cutoff_500|$SO/raw/ws_cutoff_500.jsonl|$ORIG|$SO/judgements_rubric|$SO/judgements/leakage_ws_cutoff_500.jsonl $SO/judgements_rubric/rubric_sol_ws_cutoff_500.jsonl"
 "dsv4pro_orig|$DS/raw/base_run1.jsonl|$ORIG|$DS/judgements_rubric|$DS/judgements_rubric/rubric_dsv4pro_orig.jsonl"
 "opus48_base_run1|$E/raw/opus48_base_run1.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_opus48_base_run1.jsonl"
 "opus48_ws|$E/raw/opus48_ws.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_opus48_ws.jsonl"
 "opus48_ws_cutoff|$E/raw/opus48_ws_cutoff.jsonl|$EXT|$E/judgements_rubric|$E/judgements_rubric/rubric_opus48_ws_cutoff.jsonl"
 "opus48_orig|$OP/raw/base_medium_run1.jsonl|$ORIG|$OP/judgements_rubric|$OP/judgements_rubric/rubric_opus48_orig.jsonl"
 "opus48_ws_500|$OP/raw/ws_500.jsonl|$ORIG|$OP/judgements_rubric|$OP/judgements_rubric/rubric_opus48_ws_500.jsonl"
 "opus48_ws_cutoff_500|$OP/raw/ws_cutoff_500.jsonl|$ORIG|$OP/judgements_rubric|$OP/judgements_rubric/rubric_opus48_ws_cutoff_500.jsonl"
)

total=0
for spec in "${JOBS[@]}"; do
  IFS="|" read -r nm raw bench out existing <<< "$spec"
  [ -f "$raw" ] || continue
  todo="$out/sweep_todo_$nm.jsonl"
  ex_args=""; for f in $existing; do [ -f "$f" ] && ex_args="$ex_args --existing $f"; done
  [ -f "$out/rubric_${nm}_sweep.jsonl" ] && ex_args="$ex_args --existing $out/rubric_${nm}_sweep.jsonl"
  $PY scripts/frq_todo.py --predictions "$raw" $ex_args --out "$todo" | sed 's/^/  /'
  n=$(wc -l < "$todo"); total=$((total+n))
  [ "$n" -gt 0 ] || { rm -f "$todo"; continue; }
  $PY scripts/judge_frq.py --predictions "$todo" --benchmark "$bench" \
      --output "$out/rubric_${nm}_sweep.jsonl" --stage rubric --endpoint azure \
      --concurrency 2 --resume > "$LOG/sweep_$nm.log" 2>&1
  echo "  === swept $nm: $(wc -l < "$out/rubric_${nm}_sweep.jsonl") graded"
done
echo "=== $(date +%H:%M:%S) SWEEP COMPLETE: $total leftovers attempted ==="
