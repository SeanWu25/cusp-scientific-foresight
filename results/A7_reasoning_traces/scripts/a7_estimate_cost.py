"""a7_estimate_cost.py — token/cost estimate for Step 2 (coding) and analysis D (faithfulness).
Uses the real assembled prompts and the providers' own tokenizers where available. No coding calls."""
import json, os, sys, statistics as st
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_prompts as P

CODERS = {
    "haiku45": dict(name="Claude Haiku 4.5", model="claude-haiku-4-5", provider="anthropic",
                    price=(1.00, 5.00), cache=(1.25, 0.10),
                    src="Anthropic list price for Claude Haiku 4.5, assumed; cache write 1.25x / read 0.1x"),
    "gpt54mini": dict(name="GPT-5.4-mini", model="gpt-5.4-mini", provider="openai",
                      price=(0.25, 2.00), cache=(1.0, 0.10), out=430,
                      src="scripts/run_cusp.py PRICING (gpt-5.4-mini), assumed; cached input 0.1x; reasoning_effort=minimal, "
                          "but reasoning tokens bill as output so its output budget is raised to 430"),
}
OUT_CODE = 170   # compact format: spans for the 2-3 codes that fire, plus HEDGING
OUT_FAITH = 60

samp = json.load(open(C.STUDY / "coding_sample.json"))
ids = {r["trace_id"] for r in samp["traces"]}
tr = {r["trace_id"]: r for r in C.iter_traces(lambda r: r["trace_id"] in ids)}
import random
rng = random.Random(1)
sub = [tr[i] for i in rng.sample(sorted(ids), 400)]

def approx_tokens(s):
    return len(s) / 3.8   # conservative chars-per-token for technical English

sys_tok = approx_tokens(P.SYSTEM)
user_tok = st.mean(approx_tokens(P.code_prompt(r)[1]) for r in sub)
fa = [r for r in sub if r["task"] in ("binary", "binary_perturbed", "mcq")]
fsys_tok = approx_tokens(P.FAITH_SYSTEM)
fuser_tok = st.mean(approx_tokens(P.faith_prompt(r)[1]) for r in fa)

n_code = len(ids)
n_faith = sum(1 for r in tr.values() if r["task"] in ("binary", "binary_perturbed", "mcq"))
rows = []; tot = 0.0; tot_nc = 0.0
for k, m in CODERS.items():
    pi, po = m["price"]; cw, cr = m["cache"]
    # coding: system prompt cached across calls, user prompt fresh
    oc = m.get("out", OUT_CODE)
    c_cached = n_code * (sys_tok * pi * cr + user_tok * pi + oc * po) / 1e6 + sys_tok * pi * cw / 1e6
    c_plain = n_code * ((sys_tok + user_tok) * pi + oc * po) / 1e6
    f_cached = n_faith * (fsys_tok * pi * cr + fuser_tok * pi + OUT_FAITH * po) / 1e6
    rows.append((m["name"], f"{m['model']} / {m['provider']}", f"${pi}/${po}", n_code, f"${c_plain:,.2f}", f"${c_cached:,.2f}", m["src"]))
    tot += c_cached; tot_nc += c_plain
faith = next(iter(CODERS.values()))
pi, po = faith["price"]
f_cost = n_faith * ((fsys_tok + fuser_tok) * pi + OUT_FAITH * po) / 1e6

md = ["# A7 Step 2 cost estimate (before any coding call)\n",
      f"Coding sample: **{n_code:,} traces** (`coding_sample.json`, seed {samp['seed']}), each coded by **two independent coder models**, "
      f"{len(P.ALL_CODES)} codes in one structured call per trace. Faithfulness judge (analysis D): **{n_faith:,} binary / perturbed / MCQ traces**, one call each.\n",
      f"Measured prompt sizes: system {sys_tok:,.0f} tokens (identical every call, so it caches), user {user_tok:,.0f} tokens on average, "
      f"output budgeted at {OUT_CODE} tokens. Faithfulness: system {fsys_tok:,.0f} + user {fuser_tok:,.0f}, output {OUT_FAITH}.\n",
      "| coder | endpoint | price in/out per MTok | calls | cost without caching | cost with prompt caching | price source |",
      "|---|---|---|---|---|---|---|"]
for r in rows: md.append("| " + " | ".join(str(x) for x in r) + " |")
md.append(f"| Faithfulness judge (Claude Haiku 4.5) | claude-haiku-4-5 / anthropic | $1.0/$5.0 | {n_faith:,} | ${f_cost:,.2f} | ${f_cost:,.2f} | same |")
md.append(f"\n**Total with prompt caching: ${tot + f_cost:,.2f}** (without caching ${tot_nc + f_cost:,.2f}). "
          "Prices are assumed list prices, not verified against invoices. A 200-trace double-coded pilot (~$2) runs first to check the output format and the blinding asserts.\n")
md.append("## Sample composition\n")
md.append("| stratum | traces | purpose |\n|---|---|---|")
import collections
c = collections.Counter(s for r in samp["traces"] for s in r["strata"])
md.append(f"| MAIN — base condition, capped {samp['cap_main']} per model x task x partition | {c['MAIN']:,} | analyses A, B, E, G |")
md.append(f"| DATE — extra base date traces, to {samp['cap_date']} per model | {c['DATE']:,} | analysis C (priority) |")
md.append(f"| PAIRED — {samp['paired_events']} pinned-500 events per model x task, kept as base/WS+Cutoff/WS triples | {c['PAIRED']:,} | analysis F |")
md.append(f"\nBy task: " + ", ".join(f"{t} {sum(1 for r in samp['traces'] if r['task'] == t):,}" for t in C.TASKS))
md.append(f"\nBy condition: " + ", ".join(f"{x} {sum(1 for r in samp['traces'] if r['condition'] == x):,}" for x in ("base", "ws_cutoff", "ws")))
(C.STUDY / "tables").mkdir(exist_ok=True)
(C.STUDY / "tables" / "cost_estimate.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
