#!/bin/bash
# DeepSeek-V4-Pro on the ORIGINAL corpus, so it has a row over the full dataset.
# Waits for the extension panel to finish so the two do not contend for Azure.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
set -a; . ./.env; set +a
while pgrep -f "run_ext_panel" >/dev/null; do sleep 60; done
mkdir -p results_dsv4pro_run1/raw results_dsv4pro_run1/reports
echo "=== $(date +%H:%M:%S) start deepseek-v4-pro on the original corpus ==="
OPENAI_API_BASE="$AZURE_OPENAI_ENDPOINT" OPENAI_API_KEY="$AZURE_OPENAI_KEY" \
$PY scripts/run_cusp.py \
    --input archive/data/canonical/merged_validated_cusp_fixed.jsonl \
    --output results_dsv4pro_run1/raw/base_run1.jsonl \
    --provider OPENAI --model DeepSeek-V4-Pro --condition base --run-index 1 \
    --temperature 0.0 --max-tokens 2048 --frq-max-tokens 2048 \
    --concurrency 8 --resume >> results_dsv4pro_run1/raw/base_run1.log 2>&1
echo "=== $(date +%H:%M:%S) done: $(wc -l < results_dsv4pro_run1/raw/base_run1.jsonl) rows ==="
