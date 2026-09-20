#!/bin/bash
# Final run-2 pass. Reads stored predictions and judgements only -- no inference.
#   1. dedupe judgements (two drivers briefly shared an output file)
#   2. triage every leakage 'fail'
#   3. rebuild reports with leakage verdicts joined in
#   4. build the refusals-as-wrong variants the sensitivity block needs
#   5. regenerate every table
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

echo "### 3. rebuild reports with leakage verdicts"
for t in sonnet5_base_run1 sonnet5_base_run2 sonnet5_base_run3 sonnet5_ws sonnet5_ws_cutoff \
         llama33_base sonnet45_base deepseekv4pro_base gpt4o_base gpt54_base sol_base gptoss20b_base; do
  [ -f "$RAW/$t.jsonl" ] || continue
  J=""; [ -f "$JUD/leakage_$t.jsonl" ] && J="--judged $JUD/leakage_$t.jsonl"
  $PY scripts/build_report.py --predictions "$RAW/$t.jsonl" --benchmark "$EXT" \
      $J --out "$REP/$t.json" >/dev/null 2>&1 && echo "  ok $t" || echo "  FAIL $t"
done

echo "### 4. refusals-as-wrong variants"
for t in sonnet45_base sonnet5_base_run1 sol_base gpt54_base; do
  [ -f "$RAW/$t.jsonl" ] || continue
  $PY scripts/build_report.py --predictions "$RAW/$t.jsonl" --benchmark "$EXT" \
      --score-refusals-as-wrong --out "$ALT/$t.json" >/dev/null 2>&1 && echo "  ok $t"
done

echo "### 5. tables"
$PY run_evaluation/extension_tables.py           > "$T/01_extension_panel.txt" 2>&1
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
