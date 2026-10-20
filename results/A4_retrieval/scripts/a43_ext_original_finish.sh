#!/bin/bash
# A4.3 extension, original design: after a43_ext_original.sh — up to 3 rounds of (purge transport errors -> resume),
# then reports, stage-2 FRQ rubric (same judge/rubric as every A4.3 run), sweep, merge, reports with FRQ, and the
# 1,000-event pre/post + agreement tables (A43_EVENTS=1000 a43_pre_post_correlation.py).
# Usage: bash a43_ext_original_finish.sh "<groups>" [pids-to-wait-for ...]
set -u; cd /home/seanwu/FutureScience; PY=/home/seanwu/miniconda3/bin/python3; S=results/A4_retrieval/scripts
D=results/A4_retrieval/A4_3_fixed_queries/ext500; O=$D/original; L=$O/logs; R=$O/judgements_rubric; M=$O/judgements_merged; mkdir -p $R $M
RUN_GROUPS="$1"; shift; for pid in "$@"; do while kill -0 $pid 2>/dev/null; do sleep 60; done; done
echo "=== $(date +%F' '%T) runs finished"
for round in 1 2 3; do
  out=$($PY $S/a43_ext_original_reports.py purge); echo "=== round $round: $(echo $out | tr '\n' ' ')"
  echo "$out" | grep -qv "^purged 0 " || { [ $round -gt 1 ] && break; }
  bash $S/a43_ext_original.sh "$RUN_GROUPS"
done
$PY $S/a43_ext_original_reports.py build
BENCH=$D/benchmark_ext500.jsonl
pred () { [ -f $O/raw/$1.adapted.jsonl ] && echo $O/raw/$1.adapted.jsonl || echo $O/raw/$1.jsonl; }
judge () { $PY scripts/judge_frq.py --predictions $(pred $1) --benchmark $BENCH --output $R/rubric_$1.jsonl --stage rubric --endpoint azure --concurrency 2 --resume > $L/rubric_$1.log 2>&1; echo "=== $(date +%T) judged $1: $(wc -l < $R/rubric_$1.jsonl)"; }
throttle () { while [ "$(jobs -rp | wc -l)" -ge 2 ]; do wait -n; done; }
KEYS=$($PY -c "import sys; sys.path.insert(0,'$S'); import a43_ext_original_reports as X; print(' '.join(k for k,_,_ in X.runs()))"); echo "runs to judge: $KEYS"
for k in $KEYS; do throttle; judge $k & done; wait
for k in $KEYS; do
  todo=$R/sweep_todo_$k.jsonl; ex="--existing $R/rubric_$k.jsonl"; [ -f $R/rubric_${k}_sweep.jsonl ] && ex="$ex --existing $R/rubric_${k}_sweep.jsonl"
  $PY scripts/frq_todo.py --predictions $(pred $k) $ex --out $todo | sed 's/^/  /'
  [ "$(wc -l < $todo)" -gt 0 ] && $PY scripts/judge_frq.py --predictions $todo --benchmark $BENCH --output $R/rubric_${k}_sweep.jsonl --stage rubric --endpoint azure --concurrency 2 --resume > $L/sweep_$k.log 2>&1
  rm -f $todo; files=$R/rubric_$k.jsonl; [ -f $R/rubric_${k}_sweep.jsonl ] && files="$files $R/rubric_${k}_sweep.jsonl"
  $PY scripts/merge_judgements.py $files --out $M/$k.jsonl
done
$PY $S/a43_ext_original_reports.py build
A43_EVENTS=1000 $PY $S/a43_pre_post_correlation.py > /dev/null && echo "1000-event tables ok"
echo "=== $(date +%F' '%T) ORIGINAL-DESIGN FINISH DONE"
