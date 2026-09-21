#!/bin/bash
# Fill-in chain: refused queries (gpt-5.4-mini) -> evidence for missing ids -> re-run every model x condition for
# missing/purged ids (resumable), provider groups in parallel -> inclusion for new packets -> gaps.
set -u; cd /home/seanwu/FutureScience; PY=/home/seanwu/miniconda3/bin/python3; S=results/A4_retrieval/scripts; D=results/A4_retrieval/A4_3_fixed_queries; L=$D/logs
echo "=== $(date +%H:%M:%S) fallback queries (gpt-5.4-mini) ==="; $PY $S/a43_queries.py --query-model gpt-5.4-mini --concurrency 3 2>&1 | tail -1
echo "=== $(date +%H:%M:%S) evidence for missing ids ==="; $PY $S/a43_evidence.py --concurrency 4 2>&1 | tail -7
run_group () { for spec in "$@"; do m=${spec%%:*}; c=${spec##*:}; echo "=== $(date +%H:%M:%S) rerun $m $c ==="; $PY $S/a43_run.py --model $m --condition $c --concurrency 5 > $L/rerun_${m}_${c}.log 2>&1; tail -1 $L/rerun_${m}_${c}.log; done; }
run_group gpt4o:fixed_ws_cutoff gpt4o:fixed_ws > $L/rerun_group_gpt4o.log 2>&1 &
run_group gpt54:fixed_ws_cutoff gpt54:fixed_ws > $L/rerun_group_gpt54.log 2>&1 &
run_group llama33:fixed_ws_cutoff llama33:fixed_ws > $L/rerun_group_llama.log 2>&1 &
run_group claude45:fixed_ws_cutoff claude45:fixed_ws sonnet5:fixed_ws_cutoff sonnet5:fixed_ws > $L/rerun_group_anthropic.log 2>&1 &
run_group sol:fixed_ws_cutoff sol:fixed_ws > $L/rerun_group_sol.log 2>&1 &
wait
echo "=== $(date +%H:%M:%S) inclusion for new packets ==="; $PY $S/a43_inclusion.py --concurrency 3 2>&1 | tail -1
echo "=== $(date +%H:%M:%S) gaps ==="; $PY $S/a43_gaps.py 2>&1 | grep -v "^  report" | head -3; $PY $S/a43_inclusion_summary.py > /dev/null 2>&1
echo "=== $(date +%H:%M:%S) A43 FOLLOWUP DONE ==="
