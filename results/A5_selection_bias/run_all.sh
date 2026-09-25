#!/bin/bash
# Regenerate study A5 end to end from stored outputs. No inference.
# The metadata snapshot (metadata/*.jsonl) is cached; the two fetch scripts
# resume and never re-fetch a DOI already on disk, so they are no-ops here.
set -euo pipefail
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
S=results/A5_selection_bias/scripts
$PY $S/a5_fetch_metadata.py all      # OpenAlex + Crossref (cached)
$PY $S/a5_fetch_s2.py                # Semantic Scholar (cached)
for d in source visibility vis_rate latency lat_review legacy_visibility legacy_latency; do
  $PY $S/a5_analysis.py --only $d > results/A5_selection_bias/logs/analysis_$d.log 2>&1 &
done
wait
$PY $S/a5_analysis.py --manifest-only
$PY $S/a5_within_discipline.py
$PY $S/a5_citation_gap.py
$PY $S/a5_figures.py
$PY $S/a5_tables.py
$PY $S/a5_summarize.py
$PY $S/a5_make_response.py
$PY $S/a5_verify.py
echo "=== A5 complete ==="
