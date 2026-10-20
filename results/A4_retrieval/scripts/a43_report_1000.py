"""Write results/A4_retrieval/A4_3_FIXED_PACKETS_1000.md: the fixed-evidence-packet experiment on 1,000 events
(response Tables 20-22, FRQ agreement, Figure 3a values, event counts, method, caveats). Reads stored tables only:
tables/A4_3_gaps_pre_post_1000.json, tables/A4_3_correlation_1000.json (A43_EVENTS=1000 a43_pre_post_correlation.py)."""
import json, collections, sys
from pathlib import Path
import numpy as np
OUT = Path("/home/seanwu/FutureScience/results/A4_retrieval"); T = OUT / "tables"
cells = json.load(open(T / "A4_3_gaps_pre_post_1000.json")); corr = json.load(open(T / "A4_3_correlation_1000.json"))
cl = corr["cell_level"]; J = {(c["scope"], c["model"], c["task"]): c for c in cells}
samp = json.load(open(OUT / "A4_3_fixed_queries/ext500/sample.json"))
ORDER = [("GPT-4o", "2023-10"), ("LLaMA 3.3 70B", "2023-12"), ("Claude S4.5", "2025-01"), ("GPT-5.4", "2025-08"), ("Claude Sonnet 5", "2026-01"), ("GPT-5.6 Sol", "2026-02")]
TASKS = [("Binary", "Binary"), ("Binary (pert.)", "Binary (perturbed)"), ("MCQ", "MCQ"), ("FRQ (0-10)", "FRQ (0–10)"), ("Date (0-1)", "Date")]
FAM = [("Feasibility Assessment", ("Binary", "Binary (pert.)"), 1), ("Mechanistic Forecasting", ("MCQ",), 1), ("Temporal Prediction", ("Date (0-1)",), 1), ("Solution Design", ("FRQ (0-10)",), 10)]
f = lambda v: f"{v:+.3f}"
g = lambda c, k: f"{f(c[k])} [{f(c[k + '_ci'][0])}, {f(c[k + '_ci'][1])}]" if k in c else "—"
def nev(scope, m):
    return max((J[(scope, m, t)]["n"] for t, _ in TASKS if (scope, m, t) in J), default=0)
L = ["# Fixed evidence packets on 1,000 events: results", "",
     "CUSP revision, Reviewer 2 comment C4.3 (knowledge-access experiment, Figure 3a, response Tables 20–22). Computed 2026-10-20.", "",
     "## Summary", "",
     "- **Both designs give the same picture.** Across 50 model × task × partition cells, the knowledge gap correlates at r = 0.99 between the original design and the fixed-evidence design, and the forecasting gap at r = 0.91.",
     "- **After the cutoff, forecasting gaps dominate.** With fixed evidence, the forecasting gap is larger than the knowledge gap in all 24 post-cutoff model × task-family comparisons.",
     "- **Before the cutoff, knowledge gaps dominate.** The knowledge gap is larger than the forecasting gap in all 16 pre-cutoff comparisons.",
     "- **The two late-cutoff models are now covered.** Claude Sonnet 5 and GPT-5.6 Sol had too few post-cutoff events in the first 500 (31 and 4). With 1,000 events they have 143–399 and 131–403 matched post-cutoff events per task, and they show the same pattern as the other models.", "",
     "## Design", "",
     "- **Original design.** Each evaluated model writes its own search query. WS+Cutoff retrieves only documents dated before the model's knowledge cutoff; WS has no date limit. GPT-4o and GPT-5.4 used the OpenAI web-search tool in WS; all other runs used one You.com query per event.",
     "- **Fixed-evidence design.** Claude Opus 4.8 wrote one query per event (GPT-5.4-mini for events Opus declined). Each query was sent once per date limit, so every model received the same evidence packet for a given limit.",
     "- **Gaps.** Knowledge gap = WS+Cutoff − Base. Forecasting gap = WS − WS+Cutoff. Post-cutoff events have a publication month after the model's cutoff month.",
     "- **Statistics.** Paired differences on events present in all conditions of both designs (\"matched events\"), with normal 95% confidence intervals. Cells with fewer than 20 events are not reported. Binary, MCQ and Date use a 0–1 scale; FRQ uses rubric points on 0–10.", "",
     "## Events", "",
     f"The 1,000 events are the pinned 500-event subset (published Jan 2024 – Mar 2026) and 500 added events published Mar–Aug 2026 (seed {samp['seed']}, stratified by month). Every added event is a post-cutoff event for all six models.", "",
     "| Model | Knowledge cutoff | Matched pre-cutoff events (max over tasks) | Matched post-cutoff events (max over tasks) |", "|---|---|---|---|"]
for m, cut in ORDER: L.append(f"| {m} | {cut} | {nev('pre', m)} | {nev('post', m)} |")
for scope, num, title in (("pre", "20", "Pre-cutoff gaps"), ("post", "21", "Post-cutoff gaps")):
    L += ["", f"## Table {num}. {title}, original vs fixed evidence", "", "| Model | Task | N | Knowledge gap, original | Knowledge gap, fixed | Forecasting gap, original | Forecasting gap, fixed |", "|---|---|---|---|---|---|---|"]
    for m, _ in ORDER:
        rows = [(lab, J.get((scope, m, t))) for t, lab in TASKS]
        if all(c is None or c["n"] == 0 for _, c in rows): continue
        for i, (lab, c) in enumerate(rows):
            name = m if i == 0 else ""
            if c.get("suppressed"): L.append(f"| {name} | {lab} | {c['n']} | n < 20 | | | |"); continue
            L.append(f"| {name} | {lab} | {c['n']} | {g(c, 'know_orig')} | {g(c, 'know_fixed')} | {g(c, 'fore_orig')} | {g(c, 'fore_fixed')} |")
    if scope == "pre": L += ["", "GPT-4o and LLaMA 3.3 70B have no pre-cutoff events."]
L += ["", "## Table 22. Agreement between the original and fixed-evidence designs", "",
      "One point per model × task × partition cell with at least 20 matched events. FRQ is divided by 10 so all tasks share a 0–1 scale. r = Pearson correlation; MAD = mean absolute difference. Brackets: 95% CIs from 10,000 cell-level bootstrap resamples.", "",
      "| Quantity | r (pre + post) | MAD (pre + post) | r (post only) | MAD (post only) |", "|---|---|---|---|---|"]
def rm(k, sc):
    x = cl[f"{k}:{sc}"]; return f"{x['pearson']:.2f} [{x['pearson_ci'][0]:.2f}, {x['pearson_ci'][1]:.2f}]", f"{x['mad']:.3f} [{x['mad_ci'][0]:.3f}, {x['mad_ci'][1]:.3f}]"
for k, lab in (("wscut", "WS+Cutoff performance"), ("ws", "Unrestricted WS performance"), ("know", "**Knowledge gap**"), ("fore", "**Forecasting gap**"), ("fore_x4o", "Forecasting gap, without GPT-4o")):
    a, b = rm(k, "all"); c, d = rm(k, "post"); L.append(f"| {lab} | {a} | {b} | {c} | {d} |")
L += ["", f"Cells: {cl['know:all']['n_cells']} (pre + post), {cl['know:post']['n_cells']} (post only); without GPT-4o: {cl['fore_x4o:all']['n_cells']} and {cl['fore_x4o:post']['n_cells']}.", "",
      "## FRQ only (rubric points, 0–10)", "", "| Quantity | r (pre + post) | MAD (pre + post) | Cells | r (post only) | MAD (post only) | Cells |", "|---|---|---|---|---|---|---|"]
for k, lab in (("wscut_frq", "WS+Cutoff score"), ("ws_frq", "WS score"), ("know_frq", "Knowledge gap"), ("fore_frq", "Forecasting gap")):
    a, b = rm(k, "all"); c, d = rm(k, "post"); L.append(f"| {lab} | {a} | {b} | {cl[k + ':all']['n_cells']} | {c} | {d} | {cl[k + ':post']['n_cells']} |")
L += ["", "The post-only FRQ rows have six cells, so their intervals are wide.", "",
      "## Figure 3a values (fixed evidence)", "",
      "Knowledge gap / forecasting gap per task family. Feasibility Assessment is the mean of the original and perturbed binary gaps; Solution Design is FRQ ÷ 10. These are the Fixed columns of Tables 20 and 21.", ""]
for scope, title in (("post", "Post-cutoff events"), ("pre", "Pre-cutoff events")):
    L += [f"**{title}**", "", "| Model | " + " | ".join(x[0] for x in FAM) + " |", "|---|" + "---|" * len(FAM)]
    for m, _ in ORDER:
        row = []
        for fam, ts, d in FAM:
            cs = [J.get((scope, m, t)) for t in ts]
            row.append("—" if any(c is None or c.get("suppressed") for c in cs) else f"{np.mean([c['know_fixed'] for c in cs]) / d:+.3f} / {np.mean([c['fore_fixed'] for c in cs]) / d:+.3f}")
        if any(r != "—" for r in row): L.append(f"| {m} | " + " | ".join(row) + " |")
    L.append("")
cont = corr["containment"]
L += ["## Where the two designs differ", "",
      f"- **Knowledge gap.** The fixed-evidence value lies inside the original value's 95% CI in {cont['know']['n_inside']} of {cont['know']['n_cells']} cells. The exceptions are " + "; ".join(f"{o['model']} {o['task']} ({o['orig']:+.3f} → {o['fixed']:+.3f})" for o in cont["know"]["outside"]) + ". In each, fixed evidence gives the larger knowledge gap.",
      f"- **Forecasting gap.** Inside the CI in {cont['fore']['n_inside']} of {cont['fore']['n_cells']} cells. GPT-4o changes most, because its original unrestricted run used the OpenAI web-search tool rather than a single You.com query; without GPT-4o the forecasting-gap correlation rises to {cl['fore_x4o:all']['pearson']:.2f}.",
      "- **Single answers.** The same WS+Cutoff answer is given under both designs for "
      f"{float(corr['item_level']['pooled (all models)|pre + post|Binary']['wscut_agree']) * 100:.1f}% of Binary items and {float(corr['item_level']['pooled (all models)|pre + post|MCQ']['wscut_agree']) * 100:.1f}% of MCQ items (Cohen's κ {corr['item_level']['pooled (all models)|pre + post|Binary']['wscut_stat'].split('=')[1]} and {corr['item_level']['pooled (all models)|pre + post|MCQ']['wscut_stat'].split('=')[1]}).", "",
      "## Notes and caveats", "",
      "- **Added events, original design.** Each model was re-run on the 500 added events with the harness, prompts and decoding settings of its original retrieval run. The retired Azure OpenAI deployments of GPT-4o, GPT-5.4 and LLaMA 3.3 were replaced by the Azure AI Foundry deployments of the same models.",
      "- **Retrieval dates.** Fixed packets were retrieved on 2026-09-21 (first 500) and 2026-10-18 (added 500); the added original-design runs were made on 2026-10-19/20.",
      "- **FRQ token limits.** The fixed-packet FRQ answers of GPT-4o, GPT-5.4 and Claude Sonnet 4.5 were capped at 250 tokens (their original runs: 2,048 for GPT-4o and GPT-5.4).",
      "- **Claude Sonnet 4.5 query failures.** It returned no search query for 84–85 of the added events (37 in the first 500). As in its original runs, those events keep the answer given without retrieved evidence.",
      "- **Query writer.** Claude Opus 4.8 wrote the fixed queries; it is evaluated elsewhere in the paper but not in this experiment.",
      "- **DeepSeek R1** is not included: its deployment was retired before the fixed-evidence runs.", "",
      "Source: `results/A4_retrieval/` (scripts `a43_pre_post_correlation.py` with `A43_EVENTS=1000`, `a43_report_1000.py`)."]
(OUT / "A4_3_FIXED_PACKETS_1000.md").write_text("\n".join(L) + "\n"); print("written")
