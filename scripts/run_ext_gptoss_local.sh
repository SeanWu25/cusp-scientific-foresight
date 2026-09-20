#!/bin/bash
# GPT-OSS 20B on the extension, served locally by vLLM on GPUs 0-3.
# The published original-corpus row for this model used an HF transformers
# pipeline on a different host; that checkpoint is not available here and the
# Azure deployment no longer exists. Serving stack is therefore NOT identical
# to the published row -- this is recorded in the outputs.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
OUT=results_extension_run2/raw
echo "=== $(date +%H:%M:%S) start gptoss20b_base (local vLLM) ==="
OPENAI_API_BASE="http://127.0.0.1:8077/v1" OPENAI_API_KEY="local-vllm" \
$PY scripts/run_cusp.py --input "$EXT" --output "$OUT/gptoss20b_base.jsonl" \
    --provider OPENAI --model gpt-oss-20b --condition base --run-index 1 \
    --temperature 0.0 --max-tokens 2048 --frq-max-tokens 2048 \
    --concurrency 16 --resume >> "$OUT/gptoss20b_base.log" 2>&1
echo "=== $(date +%H:%M:%S) done: $(wc -l < "$OUT/gptoss20b_base.jsonl" 2>/dev/null || echo 0) rows ==="
