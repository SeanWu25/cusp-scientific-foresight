#!/bin/bash
# A4.3 ext500 — wait for the running model jobs, then up to 3 rounds of (purge API-error records -> re-run missing ids),
# then the rest of a43_ext_pipeline.sh (its query/evidence/model steps are resumable no-ops once complete).
set -u; cd /home/seanwu/FutureScience; PY=/home/seanwu/miniconda3/bin/python3; S=results/A4_retrieval/scripts; D=results/A4_retrieval/A4_3_fixed_queries/ext500; L=$D/logs
# wait for the orphaned provider-group subshells of the stopped first pipeline (PIDs passed as args), then for any a43_run left
for pid in "$@"; do while kill -0 $pid 2>/dev/null; do sleep 30; done; done
while pgrep -f "a43_run.py --set ext500" > /dev/null; do sleep 30; done
echo "=== $(date +%F' '%T) first-pass model runs finished ==="
run_group () { for spec in "$@"; do m=${spec%%:*}; c=${spec##*:}; $PY $S/a43_run.py --set ext500 --model $m --condition $c --concurrency 3 > $L/rerun_${m}_${c}.log 2>&1; echo "  rerun $m $c: $(tail -1 $L/rerun_${m}_${c}.log)"; done; }
for round in 1 2 3; do
  out=$($PY $S/a43_purge_errors.py --set ext500); echo "=== round $round: $out"
  case "$out" in "purged 0 records"*) [ $round -gt 1 ] && break;; esac
  run_group gpt4o:fixed_ws_cutoff gpt4o:fixed_ws gpt54:fixed_ws_cutoff gpt54:fixed_ws &
  run_group claude45:fixed_ws_cutoff claude45:fixed_ws sonnet5:fixed_ws_cutoff sonnet5:fixed_ws &
  run_group sol:fixed_ws_cutoff sol:fixed_ws &
  run_group llama33:fixed_ws_cutoff llama33:fixed_ws &
  wait
done
$PY - <<'PY'
import json,collections
c=collections.Counter()
for l in open("results/A4_retrieval/A4_3_fixed_queries/ext500/model_outputs.jsonl"): r=json.loads(l); c[(r["model_key"],r["condition"])]+=1
print("records per model x condition:", dict(sorted(c.items())))
PY
echo "=== $(date +%F' '%T) continuing with a43_ext_pipeline.sh ==="
bash $S/a43_ext_pipeline.sh
