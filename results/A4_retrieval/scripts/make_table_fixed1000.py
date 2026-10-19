"""LaTeX SI table of the fixed-packet gaps on 1,000 events (tables/table_fixed1000.tex), from tables/A4_3_gaps_fixed1000.json,
plus the Figure 3a counts quoted in the main text (printed). No inference."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from a43_gaps_1000 import FAM, MODELS
from a42_common import OUT
C = json.load(open(OUT / "tables/A4_3_gaps_fixed1000.json")); J = {(c["scope"], c["task"], c["model"]): c for c in C}
TN = {"Binary": "Binary", "Binary (pert.)": "Binary (perturbed)", "MCQ": "MCQ", "FRQ (0-10)": "FRQ (0--10)", "Date (0-1)": "Date"}
s = lambda v: ("$+$" if v >= 0 else "$-$") + f"{abs(v):.3f}"
cell = lambda c, g: "--" if c is None or c.get("suppressed") else f"{s(c[g + '_fixed'])} {{\\scriptsize[{s(c[g + '_fixed_ci'][0])}, {s(c[g + '_fixed_ci'][1])}]}}"
nn = lambda c: "--" if c is None or c["n"] == 0 else str(c["n"])
L = [r"\begin{table}[htbp]", r"\centering", r"\footnotesize",
     r"\caption{\textbf{Fixed-evidence gaps on 1,000 events.}",
     r"The events are the pinned 500-event subset and 500 events published from March to August 2026.",
     r"Each row is one model and one task.",
     r"Values are paired score differences on the same events, with 95\% confidence intervals in brackets.",
     r"The knowledge gap is fixed-packet WS+Cutoff minus Base.",
     r"The forecasting gap is fixed-packet WS minus fixed-packet WS+Cutoff.",
     r"Binary, MCQ and Date gaps use a 0--1 scale.",
     r"FRQ gaps use rubric points on a 0--10 scale.",
     r"$N$ is the number of shared events.",
     r"Post-cutoff events have a publication month after the cutoff month.",
     r"A dash marks a cell with fewer than 20 events.",
     r"Main Fig.~\ref{fig:gaps}a shows these values.}",
     r"\label{tab:si_ret_gaps_1000}", r"\begin{adjustbox}{max width=\textwidth}", r"\begin{tabular}{l l r l l r l l}", r"\toprule",
     r"& & \multicolumn{3}{c}{Pre-cutoff events} & \multicolumn{3}{c}{Post-cutoff events} \\", r"\cmidrule(lr){3-5}\cmidrule(lr){6-8}",
     r"Model & Task & $N$ & Knowledge gap & Forecasting gap & $N$ & Knowledge gap & Forecasting gap \\", r"\midrule"]
for k, (mk, name, cut) in enumerate(MODELS):
    for i, t in enumerate(TN):
        pre, post = J.get(("pre", t, name)), J.get(("post", t, name))
        disp = {"Claude S4.5": "Claude Sonnet 4.5"}.get(name, name)
        L.append(f"{disp + f' (cutoff {cut})' if i == 0 else ''} & {TN[t]} & {nn(pre)} & {cell(pre, 'know')} & {cell(pre, 'fore')} & {nn(post)} & {cell(post, 'know')} & {cell(post, 'fore')} \\\\")
    if k < len(MODELS) - 1: L.append(r"\addlinespace")
L += [r"\bottomrule", r"\end{tabular}", r"\end{adjustbox}", r"\end{table}"]
(OUT / "tables/table_fixed1000.tex").write_text("\n".join(L) + "\n")
# main-text counts (Figure 3a task families)
def fam(scope, name, f):
    cs = [J.get((scope, t, name)) for t in f[1]]
    if any(c is None or c.get("suppressed") for c in cs): return None
    return np.mean([c["know_fixed"] for c in cs]) / f[2], np.mean([c["fore_fixed"] for c in cs]) / f[2]
for scope in ("pre", "post"):
    v = [(name, f[0], fam(scope, name, f)) for _, name, _ in MODELS for f in FAM]; v = [x for x in v if x[2]]
    print(scope, "comparisons", len(v), "know>fore", sum(k > f for _, _, (k, f) in v), "fore>know", sum(f > k for _, _, (k, f) in v),
          "exceptions", [(n, t, round(k, 3), round(f, 3)) for n, t, (k, f) in v if (f <= k if scope == "post" else k <= f)])
    print("  mean fore by family", {f[0]: round(np.mean([x[2][1] for x in v if x[1] == f[0]]), 3) for f in FAM})
for name in ("GPT-5.4", "Claude S4.5"):
    print(name, "post Temporal", [round(x, 4) for x in fam("post", name, FAM[2])])
