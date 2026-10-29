"""A4.3 extension — write ext500/benchmark_ext500.jsonl (the 500 events' benchmark rows from both corpus files)
and build per (model, condition) prediction files + scored reports for the ext500 set with the frozen
scripts/build_report.py (FRQ rubric scores included once judgements_merged/<m>_<c>.jsonl exists).
  python a43_ext_reports.py [--bench-only]"""
import json, sys, collections, subprocess, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from a42_common import ROOT, A43_SETS, BENCH_FILES
IDS, D = A43_SETS["ext500"]; BENCH = D / "benchmark_ext500.jsonl"; RP = D / "reports"; PY = sys.executable
def write_bench():
    keep = {l.strip() for l in open(IDS) if l.strip()}; n = 0
    with open(BENCH, "w", encoding="utf-8") as f:
        for bf in BENCH_FILES:
            for l in open(bf, encoding="utf-8"):
                if l.strip() and json.loads(l)["id"] in keep: f.write(l if l.endswith("\n") else l + "\n"); n += 1
    assert n == len(keep), (n, len(keep))
def build():
    RP.mkdir(exist_ok=True); by = collections.defaultdict(list)
    for l in open(D / "model_outputs.jsonl"):
        r = json.loads(l)
        if not r.get("fatal_error"): by[(r["model_key"], r["condition"])].append(r)
    for (m, c), rows in sorted(by.items()):
        pred = RP / f"pred_{m}_{c}.jsonl"
        with open(pred, "w") as f:
            for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
        judged = D / "judgements_merged" / f"{m}_{c}.jsonl"
        extra = ["--judged", str(judged), "--frq-scores", "include"] if judged.exists() else []
        subprocess.run([PY, str(ROOT / "scripts/build_report.py"), "--predictions", str(pred), "--benchmark", str(BENCH), "--out", str(RP / f"{m}_{c}.json")] + extra, check=True, capture_output=True)
        print(f"  report {m} {c}: {len(rows)} rows{' (FRQ judged)' if extra else ''}", file=sys.stderr)
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--bench-only", action="store_true"); a = ap.parse_args()
    write_bench()
    if not a.bench_only: build()
