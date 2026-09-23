#!/bin/bash
# Regenerate study A5 end to end. ~15 min on 96 cores; no inference, no network.
set -euo pipefail
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
S=results/A5_selection_bias/scripts
$PY $S/a5_analysis.py
$PY $S/a5_within_discipline.py
$PY $S/a5_citation_gap.py
$PY $S/a5_figures.py
$PY $S/a5_tables.py
$PY $S/a5_summarize.py
$PY $S/a5_verify.py
echo "=== A5 complete ==="
