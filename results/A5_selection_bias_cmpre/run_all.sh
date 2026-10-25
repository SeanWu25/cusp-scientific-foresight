#!/bin/bash
# A5 selection-bias study WITHOUT DeepSeek-V4-Pro, cutoff month counted as PRE (A5_RULE, default cmpre) (copy of results/A5_selection_bias; panel filtered in scripts/a5_common.py).
# Uses the cached metadata snapshot (symlink to ../A5_selection_bias/metadata). No inference, no network.
set -euo pipefail
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
S=results/A5_selection_bias_cmpre/scripts
L=results/A5_selection_bias_cmpre/logs
for d in source visibility vis_rate latency lat_review legacy_visibility legacy_latency; do
  $PY $S/a5_analysis.py --only $d > $L/analysis_$d.log 2>&1 &
done
wait
$PY $S/a5_analysis.py --manifest-only
$PY $S/a5_within_discipline.py
$PY $S/a5_citation_gap.py
$PY $S/a5_figures.py
$PY $S/a5_tables.py
$PY $S/a5_summarize.py
$PY $S/a5_make_response.py
echo "=== A5 (no V4-Pro) complete ==="
