#!/bin/bash
# A4.3 chain: fixed queries (Opus 4.8) -> You.com evidence for every bound -> 6 models x 2 conditions,
# grouped by provider so groups run in parallel and each provider sees one job at a time.
set -u; cd /home/seanwu/FutureScience; PY=/home/seanwu/miniconda3/bin/python3; S=results/A4_retrieval/scripts; L=results/A4_retrieval/A4_3_fixed_queries/logs; mkdir -p $L
echo "=== $(date +%H:%M:%S) queries ==="; $PY $S/a43_queries.py --query-model claude-opus-4-8 --concurrency 4 2>&1 | tail -2
echo "=== $(date +%H:%M:%S) evidence ==="; $PY $S/a43_evidence.py --concurrency 4 2>&1 | tail -8
run_group () { for spec in "$@"; do m=${spec%%:*}; c=${spec##*:}; echo "=== $(date +%H:%M:%S) start $m $c ==="; $PY $S/a43_run.py --model $m --condition $c --concurrency 6 > $L/${m}_${c}.log 2>&1; tail -1 $L/${m}_${c}.log; done; }
run_group gpt4o:fixed_ws_cutoff gpt4o:fixed_ws gpt54:fixed_ws_cutoff gpt54:fixed_ws > $L/group_azure.log 2>&1 &
run_group claude45:fixed_ws_cutoff claude45:fixed_ws sonnet5:fixed_ws_cutoff sonnet5:fixed_ws > $L/group_anthropic.log 2>&1 &
run_group sol:fixed_ws_cutoff sol:fixed_ws > $L/group_openai.log 2>&1 &
run_group llama33:fixed_ws_cutoff llama33:fixed_ws > $L/group_foundry.log 2>&1 &
wait
echo "=== $(date +%H:%M:%S) A43 MODEL RUNS DONE ==="
