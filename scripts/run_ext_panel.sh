#!/bin/bash
# Full panel on the Apr-Aug 2026 extension. Cheapest / open-weight first so
# failures surface before the expensive models.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
WS=results_extension_run2/ws_subset_ids.txt
OUT=results_extension_run2/raw
set -a; . ./.env; set +a
AZ_EP="$AZURE_OPENAI_ENDPOINT"; AZ_KEY="$AZURE_OPENAI_KEY"
OAI_KEY="$OPENAI_API_KEY"

# azure_run <tag> <deployment> [extra run_cusp args...]
azure_run () {
  local tag="$1" dep="$2"; shift 2
  echo "=== $(date +%H:%M:%S) start $tag ($dep via azure) ==="
  OPENAI_API_BASE="$AZ_EP" OPENAI_API_KEY="$AZ_KEY" \
  $PY scripts/run_cusp.py --input "$EXT" --output "$OUT/$tag.jsonl" \
      --provider OPENAI --model "$dep" --condition base --run-index 1 \
      --temperature 0.0 --max-tokens 2048 --frq-max-tokens 2048 \
      --concurrency 8 --resume "$@" >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$OUT/$tag.jsonl" 2>/dev/null || echo 0) rows ==="
}
# oai_run <tag> <model> <effort-or-temp mode> [extra...]
oai_run () {
  local tag="$1" m="$2" mode="$3"; shift 3
  echo "=== $(date +%H:%M:%S) start $tag ($m via openai) ==="
  local extra=()
  if [ "$mode" = "effort" ]; then extra=(--effort medium); else extra=(--temperature 0.0); fi
  OPENAI_API_BASE="https://api.openai.com/v1" OPENAI_API_KEY="$OAI_KEY" \
  $PY scripts/run_cusp.py --input "$EXT" --output "$OUT/$tag.jsonl" \
      --provider OPENAI --model "$m" --condition base --run-index 1 \
      "${extra[@]}" --max-tokens 2048 --frq-max-tokens 2048 \
      --concurrency 10 --resume "$@" >> "$OUT/$tag.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $tag: $(wc -l < "$OUT/$tag.jsonl" 2>/dev/null || echo 0) rows ==="
}

azure_run llama33_base       Llama-3.3-70B-Instruct
azure_run deepseekv4pro_base DeepSeek-V4-Pro
oai_run   gpt4o_base         gpt-4o        temp
oai_run   gpt54_base         gpt-5.4       effort
oai_run   sol_base           gpt-5.6-sol   effort
echo "=== $(date +%H:%M:%S) PANEL (api models) COMPLETE ==="
