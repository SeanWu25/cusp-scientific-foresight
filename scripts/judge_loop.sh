#!/bin/bash
# Judge an in-progress predictions file: re-invoke with --resume until every
# FRQ response present in the file has a judgement. Safe to run while the
# inference job is still appending.
PRED="$1"; OUT="$2"; CONC="${3:-3}"; MAXIDLE="${4:-3}"
idle=0
while true; do
  have=$(wc -l < "$OUT" 2>/dev/null || echo 0)
  want=$(grep -c '"frq_answer"' "$PRED" 2>/dev/null || echo 0)
  echo "[judge_loop] $(date +%H:%M:%S) judged=$have  frq_available=$want"
  if [ "$have" -ge "$want" ] && [ "$want" -gt 0 ]; then
    idle=$((idle+1))
    [ "$idle" -ge "$MAXIDLE" ] && { echo "[judge_loop] complete"; break; }
    sleep 120; continue
  fi
  idle=0
  /home/seanwu/miniconda3/bin/python3 scripts/judge_frq.py \
      --predictions "$PRED" --output "$OUT" \
      --endpoint azure --concurrency "$CONC" --resume 2>&1 \
    | grep -E "^  [0-9]+/|DONE|judging"
done
