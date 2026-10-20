#!/bin/bash
# Wait until the You.com API accepts requests again (prepaid credit ran out 2026-10-19 ~13:26 PDT), then purge the failed-search
# rows and re-run them (a43_ext_original_finish.sh: purge -> resume runs -> judge -> merge -> reports -> 1,000-event tables).
set -u; cd /home/seanwu/FutureScience; PY=/home/seanwu/miniconda3/bin/python3
until $PY -c "
import os,sys
from dotenv import load_dotenv; load_dotenv('.env', override=True)
from youdotcom import You
try: You(os.environ['YOU_API_KEY']).search.unified(query='protein folding', freshness='1900-01-01to2100-01-01')
except Exception as e: print('$(date +%T)', str(e)[:80]); sys.exit(1)
"; do sleep 600; done
echo "=== $(date +%F' '%T) You.com OK, resuming"
bash results/A4_retrieval/scripts/a43_ext_original_finish.sh "anthropic_old sonnet5 sol"
