"""A4.3 inclusion summary: ground-truth inclusion in the FIXED-QUERY evidence per bound, pre vs post the bound, with the ResearchGate share; appended to A4_3 results.md."""
import json, math, collections, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); from a42_common import *
from urllib.parse import urlparse
def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return (max(0, c - h), min(1, c + h))
def months(ym): y, m = ym.split("-")[:2]; return int(y) * 12 + int(m)
ev = load_events(); rs = [json.loads(l) for l in open(OUT / "A4_3_fixed_queries/inclusion_verdicts.jsonl") if l.strip()]
ok = [r for r in rs if (r.get("judge") or {}).get("verdict") in ("INCLUDED", "NOT_INCLUDED")]
BOUNDS = {"2023-10-01": "GPT-4o", "2023-12-01": "LLaMA 3.3 70B", "2025-01-01": "Claude S4.5", "2025-08-01": "GPT-5.4", "2026-01-01": "Claude Sonnet 5", "2026-02-01": "GPT-5.6 Sol", "unrestricted": "WS (all models)"}
def cell(sub):
    n = len(sub); k = sum(r["judge"]["verdict"] == "INCLUDED" for r in sub); lo, hi = wilson(k, n); return f"{k/n:.1%} [{lo:.1%}, {hi:.1%}] (n={n})" if n else "—"
L = ["\n## Ground-truth inclusion in the fixed-query evidence (same judge as A4.2)\n", f"Judged {len(ok)} of {len(rs)} (bound × event) evidence packets. Post-bound inclusion is leakage through the date filter.", "",
     "| bound (= cutoff of) | all events | pre-bound events | post-bound events | post-bound: URL match | post-bound leak source (top domains) |", "|---|---|---|---|---|---|"]
summary = {}
for b, who in BOUNDS.items():
    sub = [r for r in ok if r["bound"] == b]
    if not sub: continue
    if b == "unrestricted": pre, post = [], sub
    else: cm = months(b[:7]); pre = [r for r in sub if months(ev[r["id"]]["publication_date"]) < cm]; post = [r for r in sub if months(ev[r["id"]]["publication_date"]) >= cm]
    dom = collections.Counter(urlparse((r["judge"].get("matched_url") or "")).netloc.replace("www.", "") for r in post if r["judge"]["verdict"] == "INCLUDED")
    um = sum(bool(r.get("url_match")) for r in post)
    summary[b] = dict(n=len(sub), n_pre=len(pre), n_post=len(post), inc_all=sum(r["judge"]["verdict"] == "INCLUDED" for r in sub), inc_pre=sum(r["judge"]["verdict"] == "INCLUDED" for r in pre), inc_post=sum(r["judge"]["verdict"] == "INCLUDED" for r in post), url_match_post=um, post_domains=dict(dom.most_common(5)))
    L.append(f"| {b} ({who}) | {cell(sub)} | {cell(pre)} | {cell(post)} | {(f'{um/len(post):.1%}' if post else '—')} | {', '.join(f'{d} {n}' for d, n in dom.most_common(3))} |")
json.dump(summary, open(OUT / "tables/A4_3_inclusion_summary.json", "w"), indent=1)
p = OUT / "A4_3_fixed_queries/results.md"; s = open(p).read() if p.exists() else "# A4.3 — Fixed queries\n"
s = s.split("\n## Ground-truth inclusion in the fixed-query evidence")[0] + "\n".join(L) + "\n"; open(p, "w").write(s); print("\n".join(L))
