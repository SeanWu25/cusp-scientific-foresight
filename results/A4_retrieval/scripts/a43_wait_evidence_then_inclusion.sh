#!/bin/bash
set -u; cd /home/seanwu/FutureScience
until [ "$(grep -c '^evidence .*: ' results/A4_retrieval/A4_3_fixed_queries/pipeline.log 2>/dev/null)" -ge 7 ]; do sleep 60; done
echo "=== $(date +%H:%M:%S) evidence complete; judging fixed-query evidence ==="
/home/seanwu/miniconda3/bin/python3 results/A4_retrieval/scripts/a43_inclusion.py --concurrency 3 2>&1 | tail -3
echo "=== $(date +%H:%M:%S) A43 INCLUSION DONE ==="
