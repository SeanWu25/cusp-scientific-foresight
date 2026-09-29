#!/bin/bash
# Regenerate study A7 end to end from stored JSONL. No benchmark inference; no coding calls
# (raw/*.jsonl holds the stored coder output and is never regenerated here).
set -euo pipefail
cd /home/seanwu/FutureScience
PY=/home/seanwu/miniconda3/bin/python3
S=results/A7_reasoning_traces/scripts
$PY $S/a7_inventory.py > /dev/null          # Step 0
$PY $S/a7_build_traces.py                   # traces.jsonl
$PY $S/a7_sample.py                         # coding_sample.json (asserts the frozen seed)
$PY $S/a7_inductive_sample.py               # inductive_sample.jsonl
$PY $S/a7_test_blinding.py                  # blinding must pass before anything downstream
$PY $S/a7_expand.py                         # coded_traces.jsonl
$PY $S/a7_agreement.py > /dev/null          # agreement.md/.json (gates the analyses)
$PY $S/a7_analyze_ab.py                     # analyses A, B
$PY $S/a7_analyze_cg.py                     # analyses C, E, F, G
$PY $S/a7_analyze_d.py                      # analysis D
$PY $S/a7_examples.py                       # examples/boxes.md|.tex
$PY $S/a7_human_validation.py               # human_validation.csv
$PY $S/a7_estimate_cost.py > /dev/null
$PY $S/a7_make_response.py                  # response_A7.md
$PY $S/a7_manifest.py                       # MANIFEST.json
echo "=== A7 complete ==="
