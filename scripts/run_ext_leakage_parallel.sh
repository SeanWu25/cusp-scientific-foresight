#!/bin/bash
# Stage-1 leakage judging, one process per file so no two ever share an output.
#
# Throughput against the Azure judge deployment saturates at ~18 judgements/min:
# 1 process at concurrency 3 gave 6.6/min, 3 processes 17.8/min, 10 processes
# only 18.4/min. Past saturation the extra pressure is harmful, not neutral --
# at 10 processes 3.75% of judgements exhausted all 6 retries, because under
# rate limiting eval.py's web-search call silently degrades to a plain chat
# call that 404s against this endpoint. So: 3 concurrent files, not 10.
set -u
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
EXT=benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl
OUT=results_extension_run2/raw
JUD=results_extension_run2/judgements
LOG=results_extension_run2/raw/leakage_logs
mkdir -p "$JUD" "$LOG"
CONC=${CONC:-3}

judge() {
  $PY scripts/judge_frq.py --predictions "$OUT/$1.jsonl" --benchmark "$EXT" \
      --output "$JUD/leakage_$1.jsonl" --stage leakage --endpoint azure \
      --concurrency "$CONC" --resume > "$LOG/$1.log" 2>&1
  echo "=== $(date +%H:%M:%S) done $1: $(wc -l < "$JUD/leakage_$1.jsonl" 2>/dev/null || echo 0)"
}

PAR=${PAR:-3}
for t in sonnet5_base_run1 gptoss20b_base llama33_base sonnet45_base \
         deepseekv4pro_base gpt4o_base gpt54_base sol_base \
         sonnet5_ws sonnet5_ws_cutoff; do
  [ -f "$OUT/$t.jsonl" ] || { echo "skip $t (no raw)"; continue; }
  while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n; done
  judge "$t" &
done
wait
echo "=== $(date +%H:%M:%S) EXTENSION LEAKAGE COMPLETE ==="
