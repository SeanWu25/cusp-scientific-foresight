#!/usr/bin/env python3
"""make_si_gapdecomp_overleaf.py - SI tab:gap_decomposition for all seven models of the original knowledge-access experiment:
post-cutoff events (publication month > cutoff month) of the pinned 500 subset, items valid in Base, WS+Cutoff and WS.
Reproduces the submitted three-model values (GPT-5.4 Binary +0.172/+0.172). Output: manuscript_updates/si_tables/gap_decomposition.tex"""
import json, statistics as st, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "results/A4_retrieval/scripts")); import a43_gaps as G
sys.path.insert(0, str(ROOT / "run_evaluation")); import web_search_block as W
pub = {}
for b in ("archive/data/canonical/merged_validated_cusp_fixed.jsonl",):
    for l in open(ROOT / b):
        if l.strip(): r = json.loads(l); pub[r["id"]] = r["publication_date"][:7]
ORDER = ["gpt4o", "llama33", "deepseek_r1", "claude45", "gpt54", "sonnet5"]  # GPT-5.6 Sol: 4 post-cutoff events -> omitted
SH = {"LLaMA 3.3 70B": "LLaMA 3.3"}; NEWM = {"llama33", "sonnet5", "sol"}
TASKS = [("Binary (original)", "binary"), ("Binary (perturbed)", "binary_perturbed"), ("MCQ", "mcq"), ("FRQ (0--10)", "frq"), ("Date (0--1)", "date")]
cols = []
for mk in ORDER:
    name, cut, base, ws, wc = G.ORIG[mk]
    B = W.load(str(base), drop_failed=False); C = W.load(str(wc)); Wd = W.load(str(ws))
    ids = [i for i in sorted(set(B) & set(C) & set(Wd)) if pub.get(i, "0") > cut]
    vals = {}
    for lab, t in TASKS:
        tr = [(W.val(B[i], t, "score"), W.val(C[i], t, "score"), W.val(Wd[i], t, "score")) for i in ids]
        tr = [x for x in tr if None not in x]
        vals[lab] = None if len(tr) < 20 else (st.fmean(c - b for b, c, w in tr), st.fmean(w - c for b, c, w in tr), len(tr))
    cols.append((mk, SH.get(name, name), cut, len(ids), vals))
    print(name, len(ids), {k: (None if v is None else tuple(round(x, 3) for x in v[:2])) for k, v in vals.items()})
f = lambda v: f"${v:+.3f}$"
hdr = " & ".join((r"\revise{" if mk in NEWM else "{") + rf"\makecell{{{n}\\({c}; $n={k}$)}}" + "}" for mk, n, c, k, _ in cols)
lines = [r"\begin{table}[h]", r"\centering", r"\begin{revblock}", r"\scriptsize", r"\setlength{\tabcolsep}{3pt}", r"\begin{adjustbox}{max width=\textwidth}",
         r"\begin{tabular}{@{}l " + "cc " * len(cols) + "@{}}", r"\toprule",
         "Metric & " + " & ".join(rf"\multicolumn{{2}}{{c}}{{{h}}}" for h in hdr.split(" & ")) + r" \\",
         "".join(rf"\cmidrule(lr){{{2+2*j}-{3+2*j}}}" for j in range(len(cols))),
         " & " + " & ".join([r"$\Delta_{\mathrm{know}}$ & $\Delta_{\mathrm{fore}}$"] * len(cols)) + r" \\", r"\midrule"]
for lab, _ in TASKS:
    cells = []
    for mk, n, c, k, v in cols:
        x = v[lab]; cells += (["---", "---"] if x is None else [f(x[0]), f(x[1])])
    lines.append(lab + " & " + " & ".join(cells) + r" \\")
lines += [r"\bottomrule", r"\end{tabular}", r"\end{adjustbox}",
          r"\caption{Knowledge gap ($\Delta_{\mathrm{know}} = \overline{\mathrm{WS+cut}} - \overline{\mathrm{base}}$) and forecasting gap ($\Delta_{\mathrm{fore}} = \overline{\mathrm{WS}} - \overline{\mathrm{WS+cut}}$) computed on post-cutoff instances for each model. Knowledge gap captures improvement from accessing pre-cutoff information; forecasting gap captures the additional gain from retrospective analysis via post-cutoff information. Their sum equals the total web-search improvement over the baseline. \revise{The table now includes six of the seven models with retrieval runs in the original design. GPT-5.6 Sol has only 4 post-cutoff events in the subset, so the table omits it. Post-cutoff events have a publication month after the cutoff month; $n$ is the number of post-cutoff events of the 500-event subset with all three conditions. ``---'': fewer than 20 items. The WS runs of GPT-4o and GPT-5.4 used the OpenAI web-search tool. Supplementary Tables~\ref{tab:si_ret_gaps_post} and~\ref{tab:si_ret_gaps_pre} give these gaps with confidence intervals and under fixed evidence packets.}}",
          r"\label{tab:gap_decomposition}", r"\end{revblock}", r"\end{table}"]
(ROOT / "manuscript_updates/si_tables/gap_decomposition.tex").write_text("\n".join(lines) + "\n")
