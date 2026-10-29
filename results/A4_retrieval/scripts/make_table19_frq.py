"""FRQ-only version of the agreement table (0-10 rubric units), from tables/A4_3_correlation.json."""
import json
from pathlib import Path
OUT = Path("results/A4_retrieval")
c = json.load(open(OUT / "tables/A4_3_correlation.json"))["cell_level"]
ROWS = [("wscut_frq", "WS+Cutoff performance"), ("ws_frq", "Unrestricted WS performance"), ("know_frq", "Knowledge gap"), ("fore_frq", "Forecasting gap")]
def m(x): return "$-$" if x < 0 else ""
def cell(k, sc, tex):
    x = c[f"{k}:{sc}"]; r, (lo, hi) = x["pearson"], x["pearson_ci"]; d, (dlo, dhi) = x["mad"], x["mad_ci"]
    if tex:
        f = lambda v: f"{m(v)}{abs(v):.2f}"
        return f"{f(r)} [{f(lo)}, {f(hi)}] & {d:.3f} [{dlo:.3f}, {dhi:.3f}] & {x['n_cells']}"
    return f"{r:.2f} [{lo:.2f}, {hi:.2f}] | {d:.3f} [{dlo:.3f}, {dhi:.3f}] | {x['n_cells']}"
tex = [r"\begin{table}[t]", r"\centering", r"\small",
       r"\caption{\textbf{Agreement between the original retrieval experiment and the fixed-evidence replication on the FRQ task.} "
       r"FRQ is scored on the 0--10 rubric scale, so it is reported separately from the unit-scale tasks. Pearson $r$ measures agreement in effect magnitude "
       r"between the two experimental setups across model $\times$ partition cells, MAD is their mean absolute difference in rubric points, and $N$ is the number of cells. "
       r"Confidence intervals are 10,000 cell-level bootstrap resamples; with four cells the post-only forecasting-gap interval is uninformative.}",
       r"\label{tab:agreement_frq}", r"\begin{tabular}{l l l r l l r}", r"\toprule",
       r"& \multicolumn{3}{c}{Pre- and post-cutoff} & \multicolumn{3}{c}{Post-cutoff only} \\", r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
       r"Quantity & $r$ [95\% CI] & MAD [95\% CI] & $N$ & $r$ [95\% CI] & MAD [95\% CI] & $N$ \\", r"\midrule"]
md = ["| Quantity | Pre + post: r [95% CI] | MAD [95% CI] | N | Post only: r [95% CI] | MAD [95% CI] | N |", "|---|---|---|---|---|---|---|"]
for k, lab in ROWS:
    tex.append(f"{lab} & {cell(k, 'all', True)} & {cell(k, 'post', True)} \\\\")
    md.append(f"| {lab} | {cell(k, 'all', False)} | {cell(k, 'post', False)} |")
tex += [r"\bottomrule", r"\end{tabular}",
        r"\begin{flushleft}\footnotesize\textit{Notes.} Knowledge gap $=$ WS+Cutoff $-$ Base; forecasting gap $=$ WS $-$ WS+Cutoff. "
        r"GPT-5.6 Sol has three post-cutoff events, so its post-cutoff cell is suppressed. "
        r"The WS+Cutoff performance and knowledge-gap rows share a MAD because the Base condition is identical in both setups.\end{flushleft}", r"\end{table}"]
(OUT / "tables/table19_agreement_frq.tex").write_text("\n".join(tex) + "\n")
(OUT / "tables/table19_agreement_frq.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
