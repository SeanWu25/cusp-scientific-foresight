#!/bin/bash
# Judge FRQ for original-design runs that have already finished (no transport errors), while slower runs continue.
# Same command as a43_ext_original_finish.sh (resumable by id), so the finish step skips these rows later.
set -u; cd /home/seanwu/FutureScience; PY=/home/seanwu/miniconda3/bin/python3
D=results/A4_retrieval/A4_3_fixed_queries/ext500; O=$D/original; R=$O/judgements_rubric; L=$O/logs; mkdir -p $R
pred () { [ -f $O/raw/$1.adapted.jsonl ] && echo $O/raw/$1.adapted.jsonl || echo $O/raw/$1.jsonl; }
judge () { $PY scripts/judge_frq.py --predictions $(pred $1) --benchmark $D/benchmark_ext500.jsonl --output $R/rubric_$1.jsonl --stage rubric --endpoint azure --concurrency 2 --resume > $L/rubric_$1.log 2>&1; echo "=== $(date +%T) judged $1: $(wc -l < $R/rubric_$1.jsonl)"; }
throttle () { while [ "$(jobs -rp | wc -l)" -ge 2 ]; do wait -n; done; }
for k in "$@"; do throttle; judge $k & done; wait; echo "=== $(date +%T) EARLY JUDGING DONE"
