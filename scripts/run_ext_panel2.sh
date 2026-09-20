#!/bin/bash
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
OUT=results_extension_run2/raw
set -a; . ./.env; set +a
# Claude Sonnet 4.5 runs on the Anthropic API, so no contention with the Azure
# panel driver; it starts immediately.
echo "=== $(date +%H:%M:%S) start sonnet45_base ==="
$PY scripts/run_cusp.py --input "$EXT" --output "$OUT/sonnet45_base.jsonl" \
    --provider ANTHROPIC --model claude-sonnet-4-5 --condition base --run-index 1 \
    --temperature 0.0 --frq-max-tokens 250 --concurrency 12 --resume \
    >> "$OUT/sonnet45_base.log" 2>&1
echo "=== $(date +%H:%M:%S) done sonnet45_base: $(wc -l < "$OUT/sonnet45_base.jsonl" 2>/dev/null || echo 0) rows ==="
# gpt-oss-20b waits for the Azure panel driver to finish so they don't contend
while pgrep -f run_ext_panel.sh >/dev/null; do sleep 30; done
echo "=== $(date +%H:%M:%S) start gptoss20b_base ==="
OPENAI_API_BASE="$AZURE_OPENAI_ENDPOINT" OPENAI_API_KEY="$AZURE_OPENAI_KEY" \
$PY scripts/run_cusp.py --input "$EXT" --output "$OUT/gptoss20b_base.jsonl" \
    --provider OPENAI --model gpt-oss-20b --condition base --run-index 1 \
    --temperature 0.0 --max-tokens 2048 --frq-max-tokens 2048 \
    --concurrency 8 --resume >> "$OUT/gptoss20b_base.log" 2>&1
echo "=== $(date +%H:%M:%S) done gptoss20b_base: $(wc -l < "$OUT/gptoss20b_base.jsonl" 2>/dev/null || echo 0) rows ==="
echo "=== $(date +%H:%M:%S) PANEL 2 COMPLETE ==="
