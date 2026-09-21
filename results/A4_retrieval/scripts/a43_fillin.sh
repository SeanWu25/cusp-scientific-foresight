#!/bin/bash
# Second fill-in: the 42 events Opus refused -> gpt-5.4-mini queries -> evidence -> reruns -> inclusion -> gaps.
set -u; cd /home/seanwu/FutureScience; PY=/home/seanwu/miniconda3/bin/python3; S=results/A4_retrieval/scripts; D=results/A4_retrieval/A4_3_fixed_queries; L=$D/logs
until grep -q "A43 FOLLOWUP DONE" $D/followup.log; do sleep 120; done
$PY - <<'PY'
import json; p="results/A4_retrieval/A4_3_fixed_queries/queries.jsonl"; rs=[json.loads(l) for l in open(p)]
keep=[r for r in rs if r.get("query")]; open(p,"w").write("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in keep)); print("queries kept", len(keep), "errored dropped", len(rs)-len(keep))
PY
echo "=== $(date +%H:%M:%S) fallback queries ==="; $PY $S/a43_queries.py --query-model gpt-5.4-mini --concurrency 3 2>&1 | tail -1
echo "=== $(date +%H:%M:%S) evidence ==="; $PY $S/a43_evidence.py --concurrency 4 2>&1 | tail -7
for m in gpt4o gpt54 llama33 claude45 sonnet5 sol; do for c in fixed_ws_cutoff fixed_ws; do $PY $S/a43_run.py --model $m --condition $c --concurrency 4 2>&1 | tail -1; done; done
echo "=== $(date +%H:%M:%S) inclusion ==="; $PY $S/a43_inclusion.py --concurrency 3 2>&1 | tail -1
echo "=== $(date +%H:%M:%S) gaps ==="; $PY $S/a43_gaps.py 2>&1 | grep -v "^  report" | head -2; $PY $S/a43_inclusion_summary.py > /dev/null 2>&1
echo "=== $(date +%H:%M:%S) A43 FILLIN DONE ==="
