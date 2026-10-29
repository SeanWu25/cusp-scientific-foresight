"""a7_agreement.py — inter-coder agreement per code (Cohen's kappa), and the reliability
decision that gates the inferential analyses. Writes agreement.md + agreement.json."""
import json, sys, collections, math
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_prompts as P

KAPPA_MIN = 0.60      # pre-registered: "substantial" on the Landis-Koch scale
MIN_POS = 30          # kappa is not estimable at very low prevalence; below this it is reported but not used
B = 2000

recs = collections.defaultdict(dict)
for l in open(C.STUDY / "coded_traces.jsonl", encoding="utf-8"):
    d = json.loads(l)
    recs[(d["trace_id"], d["code"])][d["coder"]] = d
coders = sorted({d["coder"] for v in recs.values() for d in v.values()})
assert len(coders) == 2, coders
A, Bc = coders


def kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    n = len(a)
    if n == 0: return float("nan"), float("nan")
    po = float((a == b).mean())
    ca, cb = collections.Counter(a.tolist()), collections.Counter(b.tolist())
    pe = sum(ca[k] / n * cb[k] / n for k in set(ca) | set(cb))
    return ((po - pe) / (1 - pe) if pe < 1 else float("nan")), po


rows = []
rng = np.random.default_rng(0)
for code in P.ALL_CODES:
    pairs = [(v[A], v[Bc]) for (t, c), v in recs.items() if c == code and A in v and Bc in v]
    if not pairs: continue
    if code == "HEDGING":
        a = np.array([x["verdict"] if x["verdict"] is not None else -1 for x, _ in pairs])
        b = np.array([y["verdict"] if y["verdict"] is not None else -1 for _, y in pairs])
        k, po = kappa(a, b)
        w1 = float(np.mean(np.abs(a - b) <= 1))
        pos = int((a >= 0).sum())
    else:
        a = np.array([x["verdict"] == "yes" for x, _ in pairs])
        b = np.array([y["verdict"] == "yes" for _, y in pairs])
        k, po = kappa(a, b); w1 = float("nan")
        pos = int((a | b).sum())
    idx = rng.integers(0, len(a), (B, len(a)))
    ks = np.array([kappa(a[i], b[i])[0] for i in idx])
    lo, hi = np.nanpercentile(ks, [2.5, 97.5])
    verb = [d["span_verbatim"] for (t, c), v in recs.items() if c == code for d in v.values()
            if d["verdict"] not in ("no",) and d["span"]]
    rows.append(dict(code=code, n=len(pairs), n_positive_either=pos, kappa=k, lo=float(lo), hi=float(hi),
                     agreement=po, within_1=w1,
                     rate_A=float(a.mean()) if code != "HEDGING" else float("nan"),
                     rate_B=float(b.mean()) if code != "HEDGING" else float("nan"),
                     span_verbatim_rate=(float(np.mean([bool(x) for x in verb])) if verb else float("nan")),
                     reliable=bool(k >= KAPPA_MIN and pos >= MIN_POS)))
rows.sort(key=lambda r: -r["kappa"])
keep = [r["code"] for r in rows if r["reliable"]]
json.dump(dict(kappa_min=KAPPA_MIN, min_positive=MIN_POS, bootstrap=B, coders=coders,
               reliable_codes=keep, rows=rows), open(C.STUDY / "agreement.json", "w"), indent=1)
md = ["# A7 inter-coder agreement\n",
      f"Two independent coders, blind to ground truth, correctness, model identity and condition: "
      f"**{A}** and **{Bc}**. Cohen's kappa on the binary verdicts (ordinal for HEDGING), with a "
      f"{B:,}-draw bootstrap 95% CI over traces.\n",
      f"**Pre-registered reliability rule:** a code enters the inferential analyses (B, C, E, F) only if "
      f"kappa >= {KAPPA_MIN} AND at least {MIN_POS} traces were marked positive by either coder. Kappa is "
      f"unstable at very low prevalence, so the second condition prevents a near-empty code from passing on "
      f"a handful of agreements. Codes that fail are reported as prevalence only and are excluded from every "
      f"model of outcome.\n",
      "| code | kappa [95% CI] | raw agreement | positives (either coder) | rate, coder A | rate, coder B | verbatim spans | enters inference |",
      "|---|---|---|---|---|---|---|---|"]
for r in rows:
    w = f" (within 1: {r['within_1']:.2f})" if r["code"] == "HEDGING" else ""
    ra = "--" if math.isnan(r["rate_A"]) else f"{100*r['rate_A']:.0f}%"
    rb = "--" if math.isnan(r["rate_B"]) else f"{100*r['rate_B']:.0f}%"
    sv = "--" if math.isnan(r["span_verbatim_rate"]) else f"{100*r['span_verbatim_rate']:.0f}%"
    md.append(f"| {r['code']} | {r['kappa']:.2f} [{r['lo']:.2f}, {r['hi']:.2f}] | {r['agreement']:.2f}{w} | "
              f"{r['n_positive_either']:,} | {ra} | {rb} | {sv} | {'yes' if r['reliable'] else 'no'} |")
md.append(f"\n**{len(keep)} of {len(rows)} codes enter the inferential analyses:** {', '.join(keep)}.\n")
md.append("Excluded: " + (", ".join(r["code"] for r in rows if not r["reliable"]) or "none") + ".\n")
md.append("\"Verbatim spans\" is the share of positive verdicts whose quoted justification is a contiguous quote "
          "of the passage; a span joined by an ellipsis counts if its longest fragment is verbatim.\n")
(C.STUDY / "agreement.md").write_text("\n".join(md) + "\n")
print("\n".join(md[:6])); print(f"\nreliable: {keep}")
