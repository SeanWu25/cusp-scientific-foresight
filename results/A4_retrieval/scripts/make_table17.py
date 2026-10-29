"""
Manuscript Table 17, full version: knowledge and forecasting gaps under the original and
fixed-evidence retrieval designs for every model, task and partition (pre/post-cutoff), with
paired 95% CIs. Reads tables/A4_3_gaps_pre_post.json (from a43_pre_post_correlation.py).
Writes tables/table17_gaps_full.tex and .md.
"""
import json, math
from pathlib import Path
OUT = Path("results/A4_retrieval")
cells = json.load(open(OUT / "tables/A4_3_gaps_pre_post.json"))
MODELS = ["GPT-4o", "GPT-5.4", "LLaMA 3.3 70B", "DeepSeek R1", "Claude S4.5", "Claude Sonnet 5", "GPT-5.6 Sol"]
TASKS = ["Binary", "Binary (pert.)", "MCQ", "FRQ (0-10)", "Date (0-1)"]
TLAB = {"Binary": "Binary", "Binary (pert.)": "Binary (perturbed)", "MCQ": "MCQ", "FRQ (0-10)": "FRQ (0--10)", "Date (0-1)": "Date"}
PART = {"pre": "Pre", "post": "Post"}


def val(c, k, tex):
    v = c.get(k)
    if v is None or (isinstance(v, float) and math.isnan(v)): return "—" if not tex else "---"
    lo, hi = c[f"{k}_ci"]
    if tex:
        s = lambda x: f"{x:+.3f}".replace("-", "$-$").replace("+", "$+$")
        return f"{s(v)} {{\\scriptsize[{s(lo)}, {s(hi)}]}}"
    return f"{v:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def rows(tex):
    out = []
    for m in MODELS:
        first = True
        for t in TASKS:
            for p in ("pre", "post"):
                c = next((x for x in cells if x["model"] == m and x["task"] == t and x["scope"] == p), None)
                if c is None or c["n"] == 0: continue
                mlab = m if first else ""; first = False
                if c.get("suppressed"):
                    vals = [("---" if tex else "—")] * 4
                    note = f"n = {c['n']}, suppressed"
                else:
                    vals = [val(c, k, tex) for k in ("know_orig", "know_fixed", "fore_orig", "fore_fixed")]
                    note = str(c["n"])
                out.append((mlab, TLAB[t], PART[p], note, vals))
    return out


tex = [r"\begin{table}[p]", r"\centering", r"\footnotesize",
       r"\caption{\textbf{Post- and pre-cutoff gap estimates under the original and fixed-evidence retrieval designs, all models and tasks.} "
       r"Values are paired performance differences on the same events with 95\% confidence intervals (normal approximation on the paired differences). "
       r"Knowledge gap $=$ WS+Cutoff $-$ Base; forecasting gap $=$ WS $-$ WS+Cutoff. Binary, MCQ and Date gaps are in accuracy or score units on $[0,1]$; FRQ gaps are in rubric points on the 0--10 scale. Original: each model wrote its own search query (GPT-4o's unrestricted run used the provider's native search tool). "
       r"Fixed: identical evidence packets for every model, from queries written by a model outside the panel. Pre $=$ publication month $\le$ cutoff month (recall regime); Post $=$ publication month $>$ cutoff month (forecasting regime). "
       r"GPT-4o and LLaMA 3.3 have no pre-cutoff events in the 500-event subset. LLaMA 3.3's unrestricted (WS) run was generated on 2026-10-05 with the same harness and endpoint as its WS+Cutoff run. Cells with $n<20$ are suppressed.}",
       r"\label{tab:gaps_full}",
       r"\begin{tabular}{l l l r l l l l}", r"\toprule",
       r"Model & Task & Partition & $N$ & \makecell[l]{Knowledge gap\\Original} & \makecell[l]{Knowledge gap\\Fixed} & \makecell[l]{Forecasting gap\\Original} & \makecell[l]{Forecasting gap\\Fixed} \\",
       r"\midrule"]
prev = None
for mlab, t, p, n, vals in rows(True):
    if mlab and prev is not None: tex.append(r"\addlinespace")
    if mlab: prev = mlab
    tex.append(f"{mlab} & {t} & {p} & {n} & " + " & ".join(vals) + r" \\")
tex += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(OUT / "tables/table17_gaps_full.tex").write_text("\n".join(tex) + "\n")

md = ["| Model | Task | Partition | N | Knowledge gap, original | Knowledge gap, fixed | Forecasting gap, original | Forecasting gap, fixed |", "|---|---|---|---|---|---|---|---|"]
for mlab, t, p, n, vals in rows(False):
    md.append(f"| {mlab} | {t} | {p} | {n} | " + " | ".join(vals) + " |")
(OUT / "tables/table17_gaps_full.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
