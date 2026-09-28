#!/bin/bash
# Regenerate study A8 end to end from stored outputs. No inference.
set -euo pipefail
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
S=results/A8_base_rate/scripts
$PY $S/a8_sample.py            # asserts sample.json is unchanged
$PY $S/a8_estimate_cost.py > /dev/null
$PY $S/a8_analyze.py --B 2000  # outputs.jsonl, tables/, figures/
$PY $S/a8_make_response.py     # results.md, response_A8.md
$PY $S/a8_manifest.py          # MANIFEST.json
echo "=== A8 complete ==="
