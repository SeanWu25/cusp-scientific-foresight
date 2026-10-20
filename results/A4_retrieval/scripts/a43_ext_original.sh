#!/bin/bash
# A4.3 extension — ORIGINAL design (each model writes its own query) on the 500 added events, so the
# original-vs-fixed comparison (response Tables 20-23) can use all 1,000 events.
# Each model uses the harness and settings of its original retrieval run (results/A4_retrieval/A4_1_pipeline/pipeline_description.md):
#   GPT-4o, GPT-5.4, Claude S4.5: test_LLM.py as of 2026-05-08 (ext500/original/harness/, copied from the backup tree, SHA256SUMS);
#     WS+Cutoff = You.com pipeline with the model cutoff; WS = OpenAI Responses web_search tool (GPT-4o, GPT-5.4) or
#     You.com bounded at the run month (Claude S4.5, as its original run). Temperature 0; FRQ cap 2048 (OpenAI) / 250 (Anthropic).
#     The retired Azure OpenAI deployments are replaced by the Azure AI Foundry endpoint (same as the fixed-packet runs).
#   Claude Sonnet 5, LLaMA 3.3 70B and GPT-5.6 Sol (run after the Anthropic and OpenAI keys were replaced on 2026-10-19): scripts/run_cusp.py, same args as their original runs.
# Usage: bash a43_ext_original.sh [group ...]   groups: openai_old anthropic_old sonnet5 llama33 sol
set -u; cd /home/seanwu/FutureScience; PY=/home/seanwu/miniconda3/bin/python3
D=results/A4_retrieval/A4_3_fixed_queries/ext500; O=$D/original; R=$O/raw; L=$O/logs; mkdir -p $R $L
BENCH=$(pwd)/$D/benchmark_ext500.jsonl; IDS=$D/subset_ext500_ids.txt
set -a; source .env; set +a
FOUNDRY=https://bascolm.services.ai.azure.com/openai/v1
old () {  # key model cond provider extra...
  local k=$1 m=$2 c=$3 p=$4; shift 4; local out=$(pwd)/$R/${k}_${c}; mkdir -p $out
  local res=""; f=$(ls $out/predictions_*.jsonl 2>/dev/null | head -1); [ -n "$f" ] && res="--resume $f"
  echo "=== $(date +%T) start $k $c"
  ( cd $O/harness && OPENAI_API_BASE=$FOUNDRY OPENAI_API_KEY=$AZURE_OPENAI_KEY $PY -u test_LLM.py --input $BENCH --output-dir $out \
      --provider $p --model $m --temperature 0 $res "$@" > $(pwd)/../logs/${k}_${c}.log 2>&1 )
  echo "=== $(date +%T) done $k $c: $(cat $out/predictions_*.jsonl 2>/dev/null | wc -l) rows"
}
new () {  # key model cond provider extra...
  local k=$1 m=$2 c=$3 p=$4; shift 4
  echo "=== $(date +%T) start $k $c"
  $PY scripts/run_cusp.py --input $BENCH --ids-file $IDS --output $R/${k}_${c}.jsonl --provider $p --model $m --condition $c \
      --run-index 1 --max-tokens 2048 --seed 42 --concurrency 4 --resume "$@" > $L/${k}_${c}.log 2>&1
  echo "=== $(date +%T) done $k $c: $(wc -l < $R/${k}_${c}.jsonl) rows"
}
group () {
  case $1 in
    openai_old)    old gpt4o gpt-4o ws_cutoff OPENAI --web-search --ws-cutoff 2023-10 & old gpt54 gpt-5.4 ws_cutoff OPENAI --web-search --ws-cutoff 2025-08 & wait
                   old gpt4o gpt-4o ws OPENAI --native-web-search & old gpt54 gpt-5.4 ws OPENAI --native-web-search & wait ;;
    anthropic_old) old claude45 claude-sonnet-4-5-20250929 ws_cutoff ANTHROPIC --web-search --ws-cutoff 2025-01
                   old claude45 claude-sonnet-4-5-20250929 ws ANTHROPIC --web-search --ws-cutoff 2026-10 ;;
    sonnet5)       new sonnet5 claude-sonnet-5 ws_cutoff ANTHROPIC --ws-cutoff 2026-01 --effort medium --frq-max-tokens 384
                   new sonnet5 claude-sonnet-5 ws ANTHROPIC --effort medium --frq-max-tokens 384 ;;
    llama33)       OPENAI_API_BASE=$FOUNDRY OPENAI_API_KEY=$AZURE_OPENAI_KEY new llama33 Llama-3.3-70B-Instruct ws_cutoff OPENAI --ws-cutoff 2023-12 --temperature 0 --frq-max-tokens 2048
                   OPENAI_API_BASE=$FOUNDRY OPENAI_API_KEY=$AZURE_OPENAI_KEY new llama33 Llama-3.3-70B-Instruct ws OPENAI --temperature 0 --frq-max-tokens 2048 ;;
    sol)           new sol gpt-5.6-sol ws_cutoff OPENAI --ws-cutoff 2026-02 --effort medium --frq-max-tokens 2048
                   new sol gpt-5.6-sol ws OPENAI --effort medium --frq-max-tokens 2048 ;;
  esac
}
for g in "${@:-openai_old anthropic_old sonnet5 llama33}"; do for gg in $g; do group $gg > $L/group_$gg.log 2>&1 & done; done
wait; echo "=== $(date +%F' '%T) ORIGINAL-DESIGN RUNS DONE"
