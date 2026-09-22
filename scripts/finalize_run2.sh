#!/bin/bash
# Final run-2 pass. Reads stored predictions and judgements only -- no inference.
#   1. dedupe judgements (two drivers briefly shared an output file)
#   2. triage every leakage 'fail'
#   3. merge split judgement files (leakage in one file, rubric in another)
#      field-by-field, one row per event  -- scripts/merge_judgements.py
#   4. rebuild reports with leakage verdicts AND rubric scores joined in,
#      for the extension runs and the three new original-corpus runs
#   5. build the refusals-as-wrong variants the sensitivity block needs
#   6. regenerate every table, with FRQ quality reported
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
RAW=results_extension_run2/raw
JUD=results_extension_run2/judgements
REP=results_extension_run2/reports
T=results_extension_run2/tables
ALT=results_extension_run2/reports_refusals_as_wrong
mkdir -p "$T" "$ALT"

echo "### 1. dedupe judgements"
for f in "$JUD"/*.jsonl; do
  [ -f "$f" ] && $PY scripts/dedupe_judgements.py --in-place "$f" 2>&1 \
    | grep -E "unique events|self-consistency" | sed "s|^|  $(basename "$f" .jsonl): |"
done

echo "### 2. triage leakage failures"
$PY scripts/triage_leakage.py --out "$T/08_leakage_triage.json" \
  | tee "$T/08_leakage_triage.txt" | head -12

echo "### 2b. residual-gap sweep (re-grade null-score leftovers; safe to re-run)"
bash scripts/run_frq_sweep.sh | tail -3 | sed 's/^/  /'

echo "### 3. merge split judgement files, one row per event"
RUB=results_extension_run2/judgements_rubric
MRG=results_extension_run2/judgements_merged
mkdir -p "$MRG" results_sonnet5_run1/judgements_merged results_sol_run1/judgements_merged \
         results_dsv4pro_run1/judgements_merged
# extension: leakage file + rubric file (+ todo-based rubric for the WS pair)
for t in sonnet5_base_run1 sonnet5_ws sonnet5_ws_cutoff llama33_base sonnet45_base \
         deepseekv4pro_base gpt4o_base gpt54_base sol_base gptoss20b_base \
         opus48_base_run1 opus48_ws opus48_ws_cutoff; do
  parts=""
  [ -f "$JUD/leakage_$t.jsonl" ] && parts="$parts $JUD/leakage_$t.jsonl"
  [ -f "$RUB/rubric_$t.jsonl" ]  && parts="$parts $RUB/rubric_$t.jsonl"
  [ -f "$RUB/rubric_${t}_sweep.jsonl" ] && parts="$parts $RUB/rubric_${t}_sweep.jsonl"
  [ -n "$parts" ] && $PY scripts/merge_judgements.py $parts --out "$MRG/$t.jsonl" | sed 's/^/  /'
done
# merge helper: pass any number of files; missing ones are skipped
mj() { out="$1"; shift; parts=""; for f in "$@"; do [ -f "$f" ] && parts="$parts $f"; done
       [ -n "$parts" ] && $PY scripts/merge_judgements.py $parts --out "$out" | sed 's/^/  /'; }
# original corpus: pre-deferral Sonnet 5 grading + its gap fill; Sol WS subsets; new base runs
S5=results_sonnet5_run1; SO=results_sol_run1; DS=results_dsv4pro_run1
mj $S5/judgements_merged/base_medium_run1.jsonl $S5/raw/judged_base_medium_run1.jsonl $S5/judgements_rubric/rubric_sonnet5_orig_gaps.jsonl $S5/judgements_rubric/rubric_sonnet5_orig_gaps_sweep.jsonl
mj $S5/judgements_merged/ws_500.jsonl $S5/raw/judged_ws_500.jsonl $S5/judgements_rubric/rubric_sonnet5_ws_500.jsonl $S5/judgements_rubric/rubric_sonnet5_ws_500_sweep.jsonl
mj $S5/judgements_merged/ws_cutoff_500.jsonl $S5/raw/judged_ws_cutoff_500.jsonl $S5/judgements_rubric/rubric_sonnet5_ws_cutoff_500.jsonl $S5/judgements_rubric/rubric_sonnet5_ws_cutoff_500_sweep.jsonl
mj $SO/judgements_merged/base_medium_run1.jsonl $SO/judgements/leakage_base_medium_run1.jsonl $SO/judgements_rubric/rubric_sol_orig.jsonl $SO/judgements_rubric/rubric_sol_orig_sweep.jsonl
mj $SO/judgements_merged/ws_500.jsonl $SO/judgements/leakage_ws_500.jsonl $SO/judgements_rubric/rubric_sol_ws_500.jsonl $SO/judgements_rubric/rubric_sol_ws_500_sweep.jsonl
mj $SO/judgements_merged/ws_cutoff_500.jsonl $SO/judgements/leakage_ws_cutoff_500.jsonl $SO/judgements_rubric/rubric_sol_ws_cutoff_500.jsonl $SO/judgements_rubric/rubric_sol_ws_cutoff_500_sweep.jsonl
OP=results_opus48_run1; mkdir -p $OP/judgements_merged
mj $OP/judgements_merged/base_medium_run1.jsonl $OP/judgements/leakage_base_medium_run1.jsonl $OP/judgements_rubric/rubric_opus48_orig.jsonl $OP/judgements_rubric/rubric_opus48_orig_sweep.jsonl
mj $OP/judgements_merged/ws_500.jsonl $OP/judgements/leakage_ws_500.jsonl $OP/judgements_rubric/rubric_opus48_ws_500.jsonl $OP/judgements_rubric/rubric_opus48_ws_500_sweep.jsonl
mj $OP/judgements_merged/ws_cutoff_500.jsonl $OP/judgements/leakage_ws_cutoff_500.jsonl $OP/judgements_rubric/rubric_opus48_ws_cutoff_500.jsonl $OP/judgements_rubric/rubric_opus48_ws_cutoff_500_sweep.jsonl
mj $DS/judgements_merged/base_run1.jsonl $DS/judgements_rubric/rubric_dsv4pro_orig.jsonl $DS/judgements_rubric/rubric_dsv4pro_orig_sweep.jsonl

echo "### 4. rebuild reports with leakage AND rubric scores joined in"
ORIG=archive/data/canonical/merged_validated_cusp_fixed.jsonl
for t in sonnet5_base_run1 sonnet5_base_run2 sonnet5_base_run3 sonnet5_ws sonnet5_ws_cutoff \
         llama33_base sonnet45_base deepseekv4pro_base gpt4o_base gpt54_base sol_base gptoss20b_base \
         opus48_base_run1 opus48_base_run2 opus48_base_run3 opus48_ws opus48_ws_cutoff; do
  [ -f "$RAW/$t.jsonl" ] || continue
  J=""; [ -f "$MRG/$t.jsonl" ] && J="--judged $MRG/$t.jsonl --frq-scores include"
  $PY scripts/build_report.py --predictions "$RAW/$t.jsonl" --benchmark "$EXT" \
      $J --out "$REP/$t.json" >/dev/null 2>&1 && echo "  ok $t" || echo "  FAIL $t"
done
# the three original-corpus runs that were graded in this pass
for spec in \
  "$S5/raw/base_medium_run1.jsonl|$S5/judgements_merged/base_medium_run1.jsonl|$S5/reports/base_medium_run1.json" \
  "$S5/raw/ws_500.jsonl|$S5/judgements_merged/ws_500.jsonl|$S5/reports/ws_500.json" \
  "$S5/raw/ws_cutoff_500.jsonl|$S5/judgements_merged/ws_cutoff_500.jsonl|$S5/reports/ws_cutoff_500.json" \
  "$SO/raw/base_medium_run1.jsonl|$SO/judgements_merged/base_medium_run1.jsonl|$SO/reports/base_medium_run1.json" \
  "$SO/raw/ws_500.jsonl|$SO/judgements_merged/ws_500.jsonl|$SO/reports/ws_500.json" \
  "$SO/raw/ws_cutoff_500.jsonl|$SO/judgements_merged/ws_cutoff_500.jsonl|$SO/reports/ws_cutoff_500.json" \
  "$DS/raw/base_run1.jsonl|$DS/judgements_merged/base_run1.jsonl|$DS/reports/base_run1.json" \
  "$OP/raw/base_medium_run1.jsonl|$OP/judgements_merged/base_medium_run1.jsonl|$OP/reports/base_medium_run1.json" \
  "$OP/raw/ws_500.jsonl|$OP/judgements_merged/ws_500.jsonl|$OP/reports/ws_500.json" \
  "$OP/raw/ws_cutoff_500.jsonl|$OP/judgements_merged/ws_cutoff_500.jsonl|$OP/reports/ws_cutoff_500.json"; do
  IFS="|" read -r raw jud rep <<< "$spec"
  [ -f "$raw" ] && [ -f "$jud" ] || continue
  $PY scripts/build_report.py --predictions "$raw" --benchmark "$ORIG" \
      --judged "$jud" --frq-scores include --out "$rep" >/dev/null 2>&1 \
      && echo "  ok $(basename $rep .json) [orig]" || echo "  FAIL $rep"
done

echo "### 5. refusals-as-wrong variants"
for t in sonnet45_base sonnet5_base_run1 sol_base gpt54_base opus48_base_run1; do
  [ -f "$RAW/$t.jsonl" ] || continue
  $PY scripts/build_report.py --predictions "$RAW/$t.jsonl" --benchmark "$EXT" \
      --score-refusals-as-wrong --out "$ALT/$t.json" >/dev/null 2>&1 && echo "  ok $t"
done

echo "### 6. tables (FRQ quality reported)"
$PY run_evaluation/extension_tables.py --frq report > "$T/01_extension_panel.txt" 2>&1
$PY run_evaluation/full_corpus_tables.py --out "$T/02_full_corpus.json" \
                                                 > "$T/02_full_corpus.txt" 2>&1
$PY run_evaluation/run2_diagnostics.py --refusals-as-wrong-dir "$ALT" \
    --out "$T/07_diagnostics.json"               > "$T/07_diagnostics.txt" 2>&1
R=$REP
$PY run_evaluation/binary_extended.py --benchmark "$EXT" --results /dev/null \
  --extra "GPT-4o=2023-10=$R/gpt4o_base.json" \
  --extra "LLaMA 3.3 70B=2023-12=$R/llama33_base.json" \
  --extra "GPT-OSS 20B=2024-06=$R/gptoss20b_base.json" \
  --extra "Claude S4.5=2025-01=$R/sonnet45_base.json" \
  --extra "GPT-5.4=2025-08=$R/gpt54_base.json" \
  --extra "Claude Sonnet 5=2026-01=$R/sonnet5_base_run1.json" \
  --extra "GPT-5.6 Sol=2026-02=$R/sol_base.json" \
  --extra "DeepSeek-V4-Pro=2026-04=$R/deepseekv4pro_base.json" \
  --out "$T/03_binary_bias.json"                 > "$T/03_binary_bias.txt" 2>&1
$PY run_evaluation/horizon_stratified.py --benchmark "$EXT" --results /dev/null --min-n 20 \
  --extra "GPT-4o=2023-10=$R/gpt4o_base.json" \
  --extra "LLaMA 3.3 70B=2023-12=$R/llama33_base.json" \
  --extra "GPT-OSS 20B=2024-06=$R/gptoss20b_base.json" \
  --extra "Claude S4.5=2025-01=$R/sonnet45_base.json" \
  --extra "GPT-5.4=2025-08=$R/gpt54_base.json" \
  --extra "Claude Sonnet 5=2026-01=$R/sonnet5_base_run1.json" \
  --extra "GPT-5.6 Sol=2026-02=$R/sol_base.json" \
  --extra "DeepSeek-V4-Pro=2026-04=$R/deepseekv4pro_base.json" \
  --out "$T/04_horizon.json"                     > "$T/04_horizon.txt" 2>&1
$PY run_evaluation/web_search_block.py \
  --base "$R/sonnet5_base_run1.json" --wscut "$R/sonnet5_ws_cutoff.json" --ws "$R/sonnet5_ws.json" \
  --label "Claude Sonnet 5 (extension WS subset)" --benchmark "$EXT" --cutoff 2026-01 \
  --out "$T/05_web_search.json"                  > "$T/05_web_search.txt" 2>&1
$PY run_evaluation/gap_decomposition.py --benchmark "$EXT" --min-n 20 \
  --extra "Claude Sonnet 5 (ext)=2026-01=$R/sonnet5_base_run1.json=$R/sonnet5_ws.json=$R/sonnet5_ws_cutoff.json" \
  --out "$T/06_gap.json"                         > "$T/06_gap.txt" 2>&1

echo; echo "wrote:"; ls -la "$T" | awk 'NR>3{printf "  %8s  %s\n",$5,$9}'
echo; echo "raw prediction hashes (not in git):"
md5sum "$RAW"/*.jsonl results_dsv4pro_run1/raw/*.jsonl 2>/dev/null | sed 's|  .*/|  |'

echo "### 7. prove binary answers are untouched (study A2 reads these reports)"
$PY scripts/verify_binary_answers_unchanged.py | sed 's/^/  /' \
  || echo "  !! binary answer counts changed -- tell the A2 session (CUSP DATASET CHECK) to re-run analyse"

echo "### 8. re-freeze raw-artifact hashes (keeps superseded hashes for provenance)"
$PY scripts/refreeze_raw_hashes.py results_sol_run1 \
   --note "ws_500 and ws_cutoff_500 regenerated 2026-09-20 after the scripts/web_search.py fix; originals kept as *.FAILED_no_context.*" | sed 's/^/  /'
$PY scripts/refreeze_raw_hashes.py results_sonnet5_run1   --note "run-2 finalize" | sed 's/^/  /'
$PY scripts/refreeze_raw_hashes.py results_extension_run2 --note "run-2 finalize" | sed 's/^/  /'
$PY scripts/refreeze_raw_hashes.py results_dsv4pro_run1   --note "run-2 finalize" | sed 's/^/  /'
[ -d results_opus48_run1/raw ] && $PY scripts/refreeze_raw_hashes.py results_opus48_run1 --note "run-2 finalize" | sed 's/^/  /'
