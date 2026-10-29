"""
A4.3 extension — original-design runs on the 500 added events (ext500/original/raw): purge transport errors, adapt,
and build scored reports.

  python a43_ext_original_reports.py purge     # drop rows with transport errors (HTTP 429/5xx/connection) so the run resumes them
  python a43_ext_original_reports.py build     # adapt + build_report (FRQ included once judgements_merged/<k>.jsonl exists)

test_LLM.py (2026-05-08 harness; GPT-4o, GPT-5.4, Claude S4.5) stores parsed answers but no raw text, while
scripts/build_report.py scores a task only when "<task>_raw" is present. The adapter copies "<task>_reasoning" (or the
answer) into "<task>_raw" for every task the harness answered; grading uses the parsed "<task>_answer" fields with the
frozen graders (scoring_v1), as for every other report. Content-filter refusals (HTTP 400) are kept as answers, as in
the original runs. The original reports of these three models carry no retrieval-failure flag, so none is set here.
"""
import json, sys, glob, subprocess, collections, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from a42_common import ROOT, A43_SETS
D = A43_SETS["ext500"][1]; O = D / "original"; RAW, REP, JM = O / "raw", O / "reports", O / "judgements_merged"
BENCH = D / "benchmark_ext500.jsonl"; TASKS = ("binary", "binary_perturbed", "mcq", "frq", "date")
TRANSIENT = re.compile(r"Error code: (429|5\d\d)|RateLimit|rate limit|timed out|Timeout|Connection|overloaded|InternalServerError", re.I)
# The You.com prepaid credit ran out at about 2026-10-19 13:26 PDT (HTTP 402 payment_required): every search after that failed.
# run_cusp.py records this in web_search_error; test_LLM.py only logs it and stores no URLs, so for the old harness a row
# with no retrieved URL written during the outage is a failed search. The outage ended when a new key was installed
# (2026-10-19 23:10). Rows whose QUERY failed (the model returned no content: "ERROR: web_search._chat failed") are model
# behaviour, as in the original runs, and are kept.
YOU_DOWN, YOU_UP = "2026-10-19T13:20", "2026-10-19T23:10"

def runs():
    for p in sorted(RAW.iterdir()):
        if p.is_dir():
            f = sorted(p.glob("predictions_*.jsonl"))
            if f: yield p.name, f[0], "old"
        elif p.suffix == ".jsonl" and not p.name.endswith(".adapted.jsonl"):
            yield p.stem, p, "new"

def bad(r, kind):
    if r.get("fatal_error"): return True
    if kind == "new" and re.search(r"Status (402|429|5\d\d)", str(r.get("web_search_error") or "")): return True
    if kind == "old" and "web_search_urls" in r and str(r.get("web_search_urls")) in ("[]", "", "None") and YOU_DOWN <= str(r.get("timestamp", "")) < YOU_UP and not str(r.get("web_search_query", "")).startswith("ERROR"): return True
    for t in TASKS:
        txt = " ".join(str(r.get(f"{t}_{x}") or "") for x in (("reasoning", "answer") if kind == "old" else ("raw", "error")))
        if "Error:" in txt[:400] and TRANSIENT.search(txt[:600]): return True
    return False

def purge():
    for k, f, kind in runs():
        rows = [l for l in open(f, encoding="utf-8") if l.strip()]
        drop = [l for l in rows if bad(json.loads(l), kind)]
        if drop:
            gone = {json.loads(l)["id"] for l in drop}
            with open(O / "purged_transport_errors.jsonl", "a", encoding="utf-8") as g: g.writelines(drop)
            f.write_text("".join(l for l in rows if l not in drop), encoding="utf-8")
            # FRQ judgements of the dropped answers are stale: remove them so the re-run answers are judged again
            for jf in list((O / "judgements_rubric").glob(f"rubric_{k}*.jsonl")) + list(JM.glob(f"{k}.jsonl")):
                jl = [l for l in open(jf, encoding="utf-8") if l.strip()]
                jf.write_text("".join(l for l in jl if json.loads(l).get("id") not in gone), encoding="utf-8")
        print(f"purged {len(drop)} {k}")

def build():
    REP.mkdir(exist_ok=True)
    for k, f, kind in runs():
        src = f
        if kind == "old":
            src = RAW / f"{k}.adapted.jsonl"
            with open(src, "w", encoding="utf-8") as g:
                for l in open(f, encoding="utf-8"):
                    if not l.strip(): continue
                    r = json.loads(l)
                    for t in TASKS:
                        if f"{t}_answer" in r: r[f"{t}_raw"] = r.get(f"{t}_reasoning") or r.get(f"{t}_answer") or ""
                    g.write(json.dumps(r, ensure_ascii=False) + "\n")
        j = JM / f"{k}.jsonl"; extra = ["--judged", str(j), "--frq-scores", "include"] if j.exists() else []
        subprocess.run([sys.executable, str(ROOT / "scripts/build_report.py"), "--predictions", str(src), "--benchmark", str(BENCH), "--out", str(REP / f"{k}.json")] + extra,
                       check=True, capture_output=True)
        print(f"report {k}: {sum(1 for _ in open(src))} rows{' (FRQ judged)' if extra else ''} <- {src.name}")

if __name__ == "__main__":
    {"purge": purge, "build": build}[sys.argv[1]]()
