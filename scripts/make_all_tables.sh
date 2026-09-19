#!/bin/bash
# Regenerate every table in the results directory from the raw JSONL.
# Nothing here calls an API: it reads run_cusp.py predictions plus judge_frq.py
# judgements and recomputes. Safe to re-run at any time.
set -eu
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
BENCH=archive/data/canonical/merged_validated_cusp_fixed.jsonl
PUB=run_evaluation/frq_results

build () {  # build <dir> <tag>
  local d="$1" t="$2"
  [ -f "$d/raw/$t.jsonl" ] || { echo "  skip $t (no raw)"; return; }
  $PY scripts/build_report.py --predictions "$d/raw/$t.jsonl" \
      --judged "$d/raw/judged_$t.jsonl" --benchmark "$BENCH" \
      --out "$d/reports/$t.json" >/dev/null
  echo "  built $d/reports/$t.json"
}

for d in results_sonnet5_run1 results_fable5_run1 results_sol_run1; do
  [ -d "$d" ] || continue
  echo "== $d =="
  mkdir -p "$d/reports" "$d/tables"
  for t in base_medium_run1 base_medium_run2 base_medium_run3 base_low_run1 \
           ws_cutoff_500 ws_500; do
    build "$d" "$t"
  done
done

S5=results_sonnet5_run1/reports
F5=results_fable5_run1/reports
SOL=results_sol_run1/reports
OUT=results_sonnet5_run1/tables
EXTRA=()
[ -f "$S5/base_medium_run1.json" ] && EXTRA+=(--extra "Claude Sonnet 5=2026-01=$S5/base_medium_run1.json")
# Claude Fable 5 is deliberately NOT in the panel: the run was aborted at 824
# events after it declined 82% of matched biomedical items, so its partial row
# would cover a different slice of CUSP than every other row.
# [ -f "$F5/base_medium_run1.json" ] && EXTRA+=(--extra "Claude Fable 5=2026-01=$F5/base_medium_run1.json")
[ -f "$SOL/base_medium_run1.json" ] && EXTRA+=(--extra "GPT-5.6 Sol=2026-02=$SOL/base_medium_run1.json")

echo "== panel tables =="
REPEATS=()
for r in base_medium_run1 base_medium_run2 base_medium_run3; do
  [ -f "$S5/$r.json" ] && REPEATS+=(--repeats "Claude Sonnet 5=$S5/$r.json")
done
$PY run_evaluation/main_tables.py --results "$PUB" --benchmark "$BENCH" --rule main \
    "${EXTRA[@]}" "${REPEATS[@]}" --out "$OUT/main_tables.json" > "$OUT/main_tables.txt"
echo "  $OUT/main_tables.{json,txt}"

$PY run_evaluation/binary_extended.py --results "$PUB" --benchmark "$BENCH" --rule main \
    "${EXTRA[@]}" --out "$OUT/binary_extended.json" > "$OUT/binary_extended.txt"
echo "  $OUT/binary_extended.{json,txt}"

$PY run_evaluation/horizon_stratified.py --results "$PUB" --benchmark "$BENCH" \
    "${EXTRA[@]}" --out "$OUT/horizon_stratified.json" > "$OUT/horizon_stratified.txt"
echo "  $OUT/horizon_stratified.{json,txt}"

GAP=()
[ -f "$S5/ws_500.json" ] && GAP+=(--extra "Claude Sonnet 5=2026-01=$S5/base_medium_run1.json=$S5/ws_500.json=$S5/ws_cutoff_500.json")
[ -f "$SOL/ws_500.json" ] && GAP+=(--extra "GPT-5.6 Sol=2026-02=$SOL/base_medium_run1.json=$SOL/ws_500.json=$SOL/ws_cutoff_500.json")
$PY run_evaluation/gap_decomposition.py --benchmark "$BENCH" \
    "${GAP[@]}" --out "$OUT/gap_decomposition.json" > "$OUT/gap_decomposition.txt"
echo "  $OUT/gap_decomposition.{json,txt}"

for pair in "results_sonnet5_run1:Claude Sonnet 5" "results_sol_run1:GPT-5.6 Sol"; do
  d="${pair%%:*}"; lab="${pair##*:}"
  [ -f "$d/reports/ws_500.json" ] || continue
  $PY run_evaluation/web_search_block.py --benchmark "$BENCH" --label "$lab" \
      --base "$d/reports/base_medium_run1.json" \
      --wscut "$d/reports/ws_cutoff_500.json" --ws "$d/reports/ws_500.json" \
      --out "$d/tables/web_search_block.json" > "$d/tables/web_search_block.txt"
  echo "  $d/tables/web_search_block.{json,txt}"
done
echo "done."
