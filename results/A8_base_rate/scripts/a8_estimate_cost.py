"""a8_estimate_cost.py — pre-run token/cost estimate from each model's STORED base run
(no API calls). Input tokens per call = stored mean + the injected sentence; output tokens
= stored mean (reasoning tokens included where the provider bills them as output)."""
import json, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a8_common as C

N_CALLS = 500 * 2 * len(C.XS)
INJ_TOK = 22  # ~ tokens of "Historically, in this field, ... is 90%." + blank line
rows = []; total = 0.0
for k in C.ORDER:
    m = C.MODELS[k]
    if not m["provider"]:
        rows.append((m["name"], "not runnable", "", "", "", "", "", m["price_src"])); continue
    ti, to, lat = [], [], []
    for l in open(C.ROOT / m["tokens_from"], encoding="utf-8"):
        if not l.strip(): continue
        r = json.loads(l)
        for t in ("binary", "binary_perturbed"):
            if r.get(f"{t}_input_tokens") is not None:
                ti.append(r[f"{t}_input_tokens"]); to.append(r[f"{t}_output_tokens"] or 0); lat.append(r.get(f"{t}_latency_s") or 0)
    mi, mo, ml = st.mean(ti) + INJ_TOK, st.mean(to), st.mean(lat)
    pi, po = m["price"]
    cost = N_CALLS * (mi * pi + mo * po) / 1e6; total += cost
    hours = N_CALLS * ml / m["conc"] / 3600
    rows.append((m["name"], f"{m['model']} via {m['provider']}", f"{mi:.0f}", f"{mo:.0f}", f"${pi}/${po}", f"${cost:,.2f}", f"{hours:.1f} h @ conc {m['conc']}", m["price_src"]))
hdr = "| model | endpoint | in tok/call | out tok/call | price in/out per MTok | est. cost (5,000 calls) | est. wall time | price source |"
md = [f"# A8 cost estimate (before running)\n", f"Calls per model: 500 events x 2 variants x {len(C.XS)} values of X = {N_CALLS:,}. Token counts are the per-call means of each model's stored base run (binary tasks) plus ~{INJ_TOK} tokens for the injected sentence. Prices are assumed list prices, not verified against invoices.\n", hdr, "|" + "---|" * 8]
for r in rows: md.append("| " + " | ".join(r) + " |")
md.append(f"\n**Total (runnable models): ${total:,.2f}** plus ~$0.02 already spent on ten one-line endpoint probes.\n")
(C.TABLES / "cost_estimate.md").write_text("\n".join(md))
print("\n".join(md))
