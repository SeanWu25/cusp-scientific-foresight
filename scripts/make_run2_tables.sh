#!/bin/bash
# Regenerate every run-2 table into results_extension_run2/tables/.
# Reads stored predictions and judgements only -- no inference, no API calls.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
R=results_extension_run2/reports
T=results_extension_run2/tables
mkdir -p "$T"

echo "### 1. extension panel, extension-vs-original, date baseline, FRQ, cost"
$PY run_evaluation/extension_tables.py > "$T/01_extension_panel.txt" 2>&1

echo "### 2. full corpus (original + extension) per model"
$PY run_evaluation/full_corpus_tables.py --out "$T/02_full_corpus.json" \
    > "$T/02_full_corpus.txt" 2>&1

echo "### 3. binary bias / calibration on the extension"
$PY run_evaluation/binary_extended.py --benchmark "$EXT" --results /dev/null \
  --extra "GPT-4o=2023-10=$R/gpt4o_base.json" \
  --extra "LLaMA 3.3 70B=2023-12=$R/llama33_base.json" \
  --extra "GPT-OSS 20B=2024-06=$R/gptoss20b_base.json" \
  --extra "Claude S4.5=2025-01=$R/sonnet45_base.json" \
  --extra "GPT-5.4=2025-08=$R/gpt54_base.json" \
  --extra "Claude Sonnet 5=2026-01=$R/sonnet5_base_run1.json" \
  --extra "GPT-5.6 Sol=2026-02=$R/sol_base.json" \
  --extra "DeepSeek-V4-Pro=2026-04=$R/deepseekv4pro_base.json" \
  --out "$T/03_binary_bias.json" > "$T/03_binary_bias.txt" 2>&1

echo "### 4. horizon-stratified, extension"
$PY run_evaluation/horizon_stratified.py --benchmark "$EXT" --results /dev/null --min-n 20 \
  --extra "GPT-4o=2023-10=$R/gpt4o_base.json" \
  --extra "LLaMA 3.3 70B=2023-12=$R/llama33_base.json" \
  --extra "GPT-OSS 20B=2024-06=$R/gptoss20b_base.json" \
  --extra "Claude S4.5=2025-01=$R/sonnet45_base.json" \
  --extra "GPT-5.4=2025-08=$R/gpt54_base.json" \
  --extra "Claude Sonnet 5=2026-01=$R/sonnet5_base_run1.json" \
  --extra "GPT-5.6 Sol=2026-02=$R/sol_base.json" \
  --extra "DeepSeek-V4-Pro=2026-04=$R/deepseekv4pro_base.json" \
  --out "$T/04_horizon.json" > "$T/04_horizon.txt" 2>&1

echo "### 5. web-search ablation (S2/S3) on the extension"
$PY run_evaluation/web_search_block.py \
  --base "$R/sonnet5_base_run1.json" --wscut "$R/sonnet5_ws_cutoff.json" --ws "$R/sonnet5_ws.json" \
  --label "Claude Sonnet 5 (extension WS subset)" --benchmark "$EXT" --cutoff 2026-01 \
  --out "$T/05_web_search.json" > "$T/05_web_search.txt" 2>&1

echo "### 6. delta decomposition on the extension"
$PY run_evaluation/gap_decomposition.py --benchmark "$EXT" --min-n 20 \
  --extra "Claude Sonnet 5 (ext)=2026-01=$R/sonnet5_base_run1.json=$R/sonnet5_ws.json=$R/sonnet5_ws_cutoff.json" \
  --out "$T/06_gap.json" > "$T/06_gap.txt" 2>&1

echo "### 7. refusals, sensitivity, run-to-run variance, cost"
$PY run_evaluation/run2_diagnostics.py --out "$T/07_diagnostics.json" \
    > "$T/07_diagnostics.txt" 2>&1

echo
echo "wrote:"; ls -la "$T" | awk 'NR>3{print "  ",$5,$9}'
