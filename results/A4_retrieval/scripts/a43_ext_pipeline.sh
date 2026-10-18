#!/bin/bash
# A4.3 extension (500 added events, ext500/): same chain as a43_pipeline.sh + FRQ judging + finalize, for the --set ext500 events.
# Opus 4.8 fixed queries -> You.com evidence (7 bounds; the DeepSeek R1 2024-07 bound is skipped, R1 has no fixed-packet run)
# -> 6 models x 2 conditions (one job per provider at a time) -> reports -> stage-2 FRQ rubric (Azure judge, 2 files x conc 2 = 4 slots)
# -> null-score sweep -> merge -> reports with FRQ. Resumable at every step.
set -u; cd /home/seanwu/FutureScience; PY=/home/seanwu/miniconda3/bin/python3; S=results/A4_retrieval/scripts
D=results/A4_retrieval/A4_3_fixed_queries/ext500; L=$D/logs; mkdir -p $L $D/judgements_rubric $D/judgements_merged
$PY $S/a43_ext_reports.py --bench-only; BENCH=$D/benchmark_ext500.jsonl
echo "=== $(date +%F' '%T) queries ==="; $PY $S/a43_queries.py --set ext500 --query-model claude-opus-4-8 --concurrency 4 2>&1 | tail -2
$PY $S/a43_queries.py --set ext500 --query-model gpt-5.4-mini --concurrency 3 2>&1 | tail -1   # events Opus 4.8 refused (None content): gpt-5.4-mini fallback, as for the first 500 (a43_fillin.sh)
echo "=== $(date +%F' '%T) evidence ==="; $PY $S/a43_evidence.py --set ext500 --concurrency 4 --bounds 2023-10-01,2023-12-01,2025-01-01,2025-08-01,2026-01-01,2026-02-01,unrestricted 2>&1 | grep -v Warning | tail -8
run_group () { for spec in "$@"; do m=${spec%%:*}; c=${spec##*:}; echo "=== $(date +%T) start $m $c ==="; $PY $S/a43_run.py --set ext500 --model $m --condition $c --concurrency 6 > $L/${m}_${c}.log 2>&1; tail -1 $L/${m}_${c}.log; done; }
run_group gpt4o:fixed_ws_cutoff gpt4o:fixed_ws gpt54:fixed_ws_cutoff gpt54:fixed_ws > $L/group_azure.log 2>&1 &
run_group claude45:fixed_ws_cutoff claude45:fixed_ws sonnet5:fixed_ws_cutoff sonnet5:fixed_ws > $L/group_anthropic.log 2>&1 &
run_group sol:fixed_ws_cutoff sol:fixed_ws > $L/group_openai.log 2>&1 &
run_group llama33:fixed_ws_cutoff llama33:fixed_ws > $L/group_foundry.log 2>&1 &
wait; echo "=== $(date +%F' '%T) MODEL RUNS DONE ==="
$PY $S/a43_ext_reports.py 2>&1 | tail -12
echo "=== $(date +%F' '%T) FRQ rubric ==="
judge() { $PY scripts/judge_frq.py --predictions "$D/reports/pred_$1.jsonl" --benchmark "$BENCH" --output "$D/judgements_rubric/rubric_$1.jsonl" \
          --stage rubric --endpoint azure --concurrency 2 --resume > "$L/rubric_$1.log" 2>&1; echo "=== $(date +%T) judged $1: $(wc -l < $D/judgements_rubric/rubric_$1.jsonl)"; }
throttle() { while [ "$(jobs -rp | wc -l)" -ge 2 ]; do wait -n; done; }
for m in gpt4o gpt54 llama33 claude45 sonnet5 sol; do for c in fixed_ws_cutoff fixed_ws; do throttle; judge "${m}_${c}" & done; done; wait
echo "=== $(date +%F' '%T) sweep + merge ==="
R=$D/judgements_rubric
for m in gpt4o gpt54 llama33 claude45 sonnet5 sol; do for c in fixed_ws_cutoff fixed_ws; do
  nm="${m}_${c}"; todo="$R/sweep_todo_$nm.jsonl"; ex="--existing $R/rubric_$nm.jsonl"
  [ -f "$R/rubric_${nm}_sweep.jsonl" ] && ex="$ex --existing $R/rubric_${nm}_sweep.jsonl"
  $PY scripts/frq_todo.py --predictions "$D/reports/pred_$nm.jsonl" $ex --out "$todo" | sed 's/^/  /'
  if [ "$(wc -l < $todo)" -gt 0 ]; then $PY scripts/judge_frq.py --predictions "$todo" --benchmark "$BENCH" --output "$R/rubric_${nm}_sweep.jsonl" --stage rubric --endpoint azure --concurrency 2 --resume > "$L/sweep_$nm.log" 2>&1; fi
  rm -f "$todo"; files="$R/rubric_$nm.jsonl"; [ -f "$R/rubric_${nm}_sweep.jsonl" ] && files="$files $R/rubric_${nm}_sweep.jsonl"
  $PY scripts/merge_judgements.py $files --out "$D/judgements_merged/$nm.jsonl"
done; done
$PY $S/a43_ext_reports.py 2>&1 | tail -12
echo "=== $(date +%F' '%T) EXT PIPELINE DONE ==="
