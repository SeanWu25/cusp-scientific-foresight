"""Write results/A4_retrieval/A4_3_FIXED_PACKETS_1000.md from the stored tables (no inference):
tables/A4_3_gaps_fixed1000*.json (a43_gaps_1000.py) and tables/A4_3_gaps_pre_post.json (the 500-event Figure 3a source)."""
import json, collections, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from a43_gaps_1000 import FAM, MODELS
from a42_common import OUT
T = OUT / "tables"
c1000 = json.load(open(T / "A4_3_gaps_fixed1000.json")); c500 = json.load(open(T / "A4_3_gaps_pre_post.json"))
cm, ce = json.load(open(T / "A4_3_gaps_fixed1000_main.json")), json.load(open(T / "A4_3_gaps_fixed1000_ext500.json"))
samp = json.load(open(OUT / "A4_3_fixed_queries/ext500/sample.json"))
q = collections.Counter(json.loads(l)["query_model"] for l in open(OUT / "A4_3_fixed_queries/ext500/queries.jsonl") if json.loads(l).get("query"))
purged = sum(1 for _ in open(OUT / "A4_3_fixed_queries/ext500/purged_api_errors.jsonl"))
def J(cells): return {(c["scope"], c["task"], c["model"]): c for c in cells}
def fam(cells, scope, name, f):
    j = J(cells); fam_, ts, sc = f; cs = [j.get((scope, t, name)) for t in ts]
    if any(c is None or c.get("suppressed") for c in cs): return None
    return (np.mean([c["know_fixed"] for c in cs]) / sc, np.mean([c["fore_fixed"] for c in cs]) / sc, min(c["n"] for c in cs))
fmt = lambda v: "—" if v is None else f"{v[0]:+.3f} / {v[1]:+.3f}"
ci = lambda v, c: f"{v:+.3f} [{c[0]:+.3f}, {c[1]:+.3f}]"
ev = {(c["model_key"], c["scope"]): c for c in c1000 if c["task"] == "MCQ"}
n500 = {}
for c in c500:
    if c["task"] == "MCQ": n500[(c["model"], c["scope"])] = None
L = ["# Fixed-evidence-packet experiment (Figure 3a): extension from 500 to 1,000 events", "",
     "Run on 2026-10-18. The original 500 events are unchanged. 500 events were added, every one of them published after",
     "February 2026, so every added event is post-cutoff for every evaluated model.", "",
     "## Summary", "",
     "- **The goal is met.** Claude Sonnet 5 now has 531 post-cutoff events (31 before) and GPT-5.6 Sol has 504 (4 before).",
     "- **No post-cutoff cell of Figure 3a is suppressed any more.** Before, Sol had no post-cutoff values at all, and Sonnet 5 lacked Feasibility Assessment and Temporal Prediction.",
     "- **The pattern of the paper holds for the two new models.** On post-cutoff events the forecasting gap is positive in every task family, and the knowledge gap is small (between −0.02 and +0.10).",
     "- **The added events reproduce the first 500.** For the four models with post-cutoff events in both halves, the forecasting gaps agree in sign in every task family. The knowledge gaps agree except GPT-4o Temporal Prediction (see Caveats) and Claude S4.5 Mechanistic Forecasting, whose two values are both near zero.", "",
     "## Events per model", "",
     "Post-cutoff means the publication month is after the cutoff month. An event counts when the base run and both fixed-packet runs have a record for it.", "",
     "| Model | Cutoff | Pre-cutoff events | Post-cutoff events (500-event set) | Post-cutoff events (1,000-event set) |", "|---|---|---|---|---|"]
for mk, name, cut in MODELS:
    pre, post = ev[(mk, "pre")], ev[(mk, "post")]
    L.append(f"| {name} | {cut} | {pre['n_events']} | {post['n_events_by_set'].get('main', 0)} | **{post['n_events']}** |")
L += ["", "Not every event has all five tasks. In the added 500, 130 events have a Binary and a Date question, 401 a perturbed Binary question, 379 an MCQ and 385 an FRQ. This is how the extension corpus was built.", "",
      "## Figure 3a values on post-cutoff events", "",
      "Each cell is knowledge gap / forecasting gap. Knowledge gap = WS+Cutoff − base. Forecasting gap = WS − WS+Cutoff. Feasibility Assessment is the mean of the original and perturbed binary gaps. Solution Design is the FRQ score divided by 10. A dash means a cell with fewer than 20 events. The 500-event rows are the values in the current Figure 3a, which also require the original-setup runs, so their event sets differ slightly from the first-500 rows of the consistency check.", "",
      "| Model | Events | " + " | ".join(f[0] for f in FAM) + " |", "|---|---|" + "---|" * len(FAM)]
SH = {"LLaMA 3.3 70B": "LLaMA 3.3 70B"}
for mk, name, cut in MODELS:
    for lab, cells in (("500", c500), ("1,000", c1000)):
        L.append(f"| {name} | {lab} | " + " | ".join(fmt(fam(cells, 'post', name, f)) for f in FAM) + " |")
L += ["", "## Per-task post-cutoff gaps with 95% CIs (1,000 events)", "", "FRQ is on the 0–10 scale here. CIs are paired normal intervals, as in the gap decomposition code.", "",
      "| Model | Task | n | Knowledge gap [95% CI] | Forecasting gap [95% CI] |", "|---|---|---|---|---|"]
for c in c1000:
    if c["scope"] != "post" or c["n"] == 0: continue
    L.append(f"| {c['model']} | {c['task']} | {c['n']} | " + ("suppressed (n<20) | |" if c.get("suppressed") else f"{ci(c['know_fixed'], c['know_fixed_ci'])} | {ci(c['fore_fixed'], c['fore_fixed_ci'])} |"))
L += ["", "## Consistency check: first 500 against added 500 (post-cutoff)", "",
      "| Model | Half | " + " | ".join(f[0] for f in FAM) + " |", "|---|---|" + "---|" * len(FAM)]
for mk, name, cut in MODELS[:4]:
    for lab, cells in (("first 500", cm), ("added 500", ce)):
        L.append(f"| {name} | {lab} | " + " | ".join(fmt(fam(cells, 'post', name, f)) for f in FAM) + " |")
jm, je = J(cm), J(ce)
g4m, g4e = jm[("post", "Date (0-1)", "GPT-4o")], je[("post", "Date (0-1)", "GPT-4o")]
L += ["", "## Caveats", "",
      f"- **GPT-4o Temporal Prediction knowledge gap.** It is {g4m['know_fixed']:+.3f} on the first 500 and {g4e['know_fixed']:+.3f} on the added 500. "
      f"The fixed-packet scores are similar ({g4m['mean_wscut_fixed']:.3f} and {g4e['mean_wscut_fixed']:.3f}), but the base score moves from {g4m['mean_base']:.3f} to {g4e['mean_base']:.3f}. "
      "Most added events take their base scores from the Apr–Aug 2026 extension base runs (the Table 1 runs), not from the original-corpus base runs. The base Date scores of the older models differ between those runs. "
      f"LLaMA 3.3 shows the same base shift ({jm[('post', 'Date (0-1)', 'LLaMA 3.3 70B')]['mean_base']:.3f} to {je[('post', 'Date (0-1)', 'LLaMA 3.3 70B')]['mean_base']:.3f}), in the other direction. "
      "The shift is in the base, not in the evidence. The paper should not read much into the GPT-4o and LLaMA 3.3 Temporal Prediction knowledge gaps.",
      "- **Retrieval date.** The added evidence was retrieved on 2026-10-18; the first 500 on 2026-09-21.",
      "- **Original-setup comparison stays on 500 events.** The self-query runs of the original manuscript exist only for the first 500. The fixed − original tables (response Tables 20/21) are unchanged. Only Figure 3a, which uses base and fixed-packet runs, moves to 1,000 events.",
      "- **Query writer.** The fixed queries are again from Claude Opus 4.8, which is now in the evaluated panel (open decision 1 in REVISION_STATUS.md applies to the added events too).", "",
      "## Method", "",
      f"- **Sample.** Pool: CUSP events not in the first 500, published after 2026-02, with a stored base record for all six models ({samp['pool']} events). 500 were drawn, stratified by month, seed {samp['seed']}. By month: " + ", ".join(f"{k} {v}" for k, v in samp["sample_by_month"].items()) + ".",
      f"- **Queries.** Claude Opus 4.8 wrote {q['claude-opus-4-8']} queries with the same prompt (same prompt hash). It returned empty content for {q.get('gpt-5.4-mini', 0)} events; those got gpt-5.4-mini queries, as in the first 500.",
      "- **Evidence.** One You.com call per event for each of seven freshness bounds (the six model cutoffs and unrestricted), filtered by the unmodified retrieval code. 3,500 calls, no errors, one empty packet. The DeepSeek R1 bound was skipped; R1 has no fixed-packet run.",
      f"- **Model runs.** Six models × two conditions × 500 events, each model with its original decoding parameters. {purged} records hit provider rate limits (GPT-4o, LLaMA 3.3, GPT-5.4); they were removed and re-run until no transport errors remained. Claude Sonnet 4.5 API refusals were kept as model behaviour, as in the first 500.",
      "- **FRQ.** Graded with the same stage-2 rubric and Azure judge as the first 500. Every judgeable answer in all 12 runs has a score.", "",
      "## Files", "",
      "- `results/A4_retrieval/A4_3_fixed_queries/ext500/`: sample, queries, evidence, model outputs, judgements, reports, logs, README.",
      "- `results/A4_retrieval/A4_3_fixed_queries/gaps_fixed1000.md` and `results/A4_retrieval/tables/A4_3_gaps_fixed1000*.json`: full tables, including pre-cutoff.",
      "- `manuscript_updates/forecasting_gap_rev_1000.png` (and `.pdf`): Figure 3 with panel a on 1,000 events. Panel b is unchanged. Not pushed to Overleaf.", "",
      "Regenerate (no inference):", "", "```", "python results/A4_retrieval/scripts/a43_gaps_1000.py", "python results/A4_retrieval/scripts/a43_report_1000.py", "python run_evaluation/make_fig3_overleaf.py --packets 1000", "```"]
(OUT / "A4_3_FIXED_PACKETS_1000.md").write_text("\n".join(L) + "\n"); print("written")
