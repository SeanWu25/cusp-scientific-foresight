"""A4.3 — drop model_outputs records in which any task holds a provider API error after the harness's retries
(raw text starting with "Error:", e.g. HTTP 429 rate limits), so a43_run.py re-runs those events (it is resumable by
(model, condition, id)). Refusals and empty-but-valid answers are kept: they are model behaviour, not transport errors.
The removed records are appended to <set>/purged_api_errors.jsonl for the record.  python a43_purge_errors.py --set ext500"""
import json, sys, argparse, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); from a42_common import A43_SETS
TASKS = ("binary", "binary_perturbed", "mcq", "frq", "date")
ap = argparse.ArgumentParser(); ap.add_argument("--set", default="ext500", choices=list(A43_SETS)); a = ap.parse_args()
d = A43_SETS[a.set][1]; p = d / "model_outputs.jsonl"
keep, drop = [], []
for l in open(p, encoding="utf-8"):
    if not l.strip(): continue
    r = json.loads(l)
    bad = r.get("fatal_error") or any(str(r.get(f"{t}_raw") or "").startswith("Error:") for t in TASKS)
    (drop if bad else keep).append(l if l.endswith("\n") else l + "\n")
if drop:
    with open(d / "purged_api_errors.jsonl", "a", encoding="utf-8") as f: f.writelines(drop)
    tmp = p.with_suffix(".tmp"); tmp.write_text("".join(keep), encoding="utf-8"); tmp.replace(p)
c = collections.Counter((json.loads(l)["model_key"], json.loads(l)["condition"]) for l in drop)
print(f"purged {len(drop)} records: {dict(c)}")
