#!/usr/bin/env python3
"""
make_si_websearch_overleaf.py - SI tables of the original knowledge-access experiment for all SEVEN models with
retrieval runs (GPT-4o, LLaMA 3.3, DeepSeek R1, Claude S4.5, GPT-5.4, Claude Sonnet 5, GPT-5.6 Sol), pinned 500 events.
  tab:combined_web_search_cutoff  Base / WS / WS+Cutoff means, deltas and tests (as run_evaluation/web_search_block.py)
  tab:cutoff_split                same, split pre/post cutoff (pre = publication month <= cutoff month, as submitted)
  tab:calib_cutoff_split          ECE (10 bins) / Brier / Gap, split pre/post
Definitions reproduce the submitted values (GPT-4o MCQ 0.543/0.873/0.589; GPT-5.4 pre Binary ECE 0.109, Brier 0.238).
The submitted tables pooled original and perturbed binary items (raw accuracy); here they are separate rows.
Runs: results/A4_retrieval/scripts/a43_gaps.py ORIG. Output: manuscript_updates/si_tables/websearch_*.tex
"""
import json, math, statistics as st, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "results/A4_retrieval/scripts")); import a43_gaps as G
sys.path.insert(0, str(ROOT / "run_evaluation")); import web_search_block as W
TB = ROOT / "manuscript_updates/si_tables"; TB.mkdir(parents=True, exist_ok=True)
ORDER = ["gpt4o", "llama33", "deepseek_r1", "claude45", "gpt54", "sonnet5", "sol"]
ICON = {"gpt4o": "openai_logo.png", "llama33": "llama.png", "deepseek_r1": "deepseek_logo.png", "claude45": "claude.png",
        "gpt54": "openai_logo.png", "sonnet5": "claude.png", "sol": "openai_logo.png"}
NEW = {"llama33": "WS run new in the revision", "sonnet5": "new model", "sol": "new model"}
SHORT = {"LLaMA 3.3 70B": "LLaMA 3.3"}
ROWS = [("Binary (original)", "binary", "score", "mcnemar"), ("Binary (perturbed)", "binary_perturbed", "score", "mcnemar"),
        ("MCQ", "mcq", "score", "mcnemar"), ("FRQ score (0--10)", "frq", "score", "ttest"), ("Date score (0--1)", "date", "score", "ttest"),
        ("Date exact match", "date", "exact_match", "mcnemar"), ("Date month error", "date", "month_distance", "ttest")]
pub = {}
for b in ("archive/data/canonical/merged_validated_cusp_fixed.jsonl",):
    for l in open(ROOT / b):
        if l.strip(): r = json.loads(l); pub[r["id"]] = r["publication_date"][:7]
def mname(mk):
    n = SHORT.get(G.ORIG[mk][0], G.ORIG[mk][0]); s = rf"\llmicon{{icons/{ICON[mk]}}} \textit{{{n}}}"
    return rf"\revise{{{s}}}" if mk in NEW else s
def stars(p): return "" if p != p else ("^{***}" if p < 0.001 else "^{**}" if p < 0.01 else "^{*}" if p < 0.05 else "")
def ptxt(p): return "n/a" if p != p else (r"$<0.001$~\textbf{***}" if p < 0.001 else (rf"${p:.3f}$~\textbf{{{stars(p).strip('^{}')}}}" if p < 0.05 else rf"${p:.3f}$"))
def test(kind, b, x):
    return W.mcnemar([int(round(v)) for v in b], [int(round(v)) for v in x])[1] if kind == "mcnemar" else W.ttest(b, x)[1]
def triples(B, C, Wd, ids, task, field):
    b, c, w = [], [], []
    for i in ids:
        vb, vc, vw = W.val(B[i], task, field), W.val(C[i], task, field), W.val(Wd[i], task, field)
        if None in (vb, vc, vw): continue
        b.append(vb); c.append(vc); w.append(vw)
    return b, c, w
DATA = {}
for mk in ORDER:
    name, cut, base, ws, wc = G.ORIG[mk]
    B = W.load(str(base), drop_failed=False); C = W.load(str(wc)); Wd = W.load(str(ws))
    ids = sorted(set(B) & set(C) & set(Wd)); DATA[mk] = (cut, B, C, Wd, ids)
# ---------------- combined
L = []
for mk in ORDER:
    cut, B, C, Wd, ids = DATA[mk]
    L.append(rf"\multicolumn{{9}}{{l}}{{{mname(mk)} (cutoff {cut}; {len(ids)} events)}} \\ \addlinespace[2pt]")
    for lab, task, field, kind in ROWS:
        b, c, w = triples(B, C, Wd, ids, task, field); n = len(b)
        if n < 20: L.append(rf"\quad {lab} & {n} & \multicolumn{{7}}{{l}}{{\textit{{suppressed ($n<20$)}}}} \\"); continue
        se = lambda v: st.stdev(v) / math.sqrt(len(v))
        f = (lambda v: f"{v:.1f}") if "month" in lab else (lambda v: f"{v:.3f}")
        cells = [f"${f(st.fmean(b))} \\pm {f(se(b))}$"]
        for x in (w, c):
            d = st.fmean(x) - st.fmean(b); cells += [f"${f(st.fmean(x))} \\pm {f(se(x))}$", f"${'+' if d >= 0 else '-'}{f(abs(d))}$", ptxt(test(kind, b, x))]
        L.append(rf"\quad {lab} & {n} & " + " & ".join(cells) + r" \\")
    L.append(r"\addlinespace[4pt]")
hdr = r"""\begin{table}[p]
\centering
\begin{revblock}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{lr c ccc ccc}
\toprule
 & & & \multicolumn{3}{c}{Web search (no cutoff)} & \multicolumn{3}{c}{Web search (with cutoff)} \\
\cmidrule(lr){4-6}\cmidrule(lr){7-9}
Metric & $n$ & Base & Value & $\Delta$ & $p$ & Value & $\Delta$ & $p$ \\
\midrule
"""
foot = r"""\bottomrule
\end{tabular}
\end{adjustbox}
\caption{\textbf{Web-search augmentation in the original knowledge-access experiment.} Each block is one model on the pinned subset of 500 events. Values are means $\pm$ standard error. $n$ is the number of items that have a valid answer in all three conditions. $\Delta$ is the difference from Base. Binary, MCQ and date exact match use the continuity-corrected McNemar test (exact binomial when fewer than 25 discordant pairs); FRQ, date score and month error use the paired $t$-test. *** $p<0.001$, ** $p<0.01$, * $p<0.05$. The submitted version pooled original and perturbed binary items; this version gives them separately, because the pooled accuracy depends on the share of each item type. The WS runs of GPT-4o and GPT-5.4 used the OpenAI web-search tool; the other runs used the single-query You.com pipeline (Supplementary Section~\ref{sec:si_retrieval}). Blue: models or runs added in the revision.}
\label{tab:combined_web_search_cutoff}
\end{revblock}
\end{table}
"""
(TB / "websearch_combined.tex").write_text(hdr + "\n".join(L) + "\n" + foot)
# ---------------- cutoff split (Base / WS / WS+Cut)
SPLIT_ROWS = ROWS[:5]
L = []
for mk in ORDER:
    cut, B, C, Wd, ids = DATA[mk]
    for scope in ("pre", "post"):
        sid = [i for i in ids if (pub.get(i, "9999") <= cut) == (scope == "pre")]
        if not sid: continue
        cells = []
        for lab, task, field, kind in SPLIT_ROWS:
            b, c, w = triples(B, C, Wd, sid, task, field)
            if len(b) < 20: cells.append("---"); continue
            f = (lambda v: f"{v:.2f}")
            cells.append(f"${f(st.fmean(b))}$ / ${f(st.fmean(w))}{stars(test(kind, b, w))}$ / ${f(st.fmean(c))}{stars(test(kind, b, c))}$")
        L.append(rf"{mname(mk) if scope == 'pre' or not any(pub.get(i,'9999') <= cut for i in ids) else ''} & {'Pre' if scope == 'pre' else 'Post'} ($n={len(sid)}$) & " + " & ".join(cells) + r" \\")
    L.append(r"\addlinespace[3pt]")
txt = r"""\begin{table}[p]
\centering
\begin{revblock}
\setlength{\tabcolsep}{4pt}
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{@{}ll ccccc@{}}
\toprule
Model & Partition & Binary (original) & Binary (perturbed) & MCQ & FRQ (0--10) & Date (0--1) \\
\midrule
""" + "\n".join(L) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{\textbf{Original knowledge-access experiment split by knowledge cutoff.} Each cell gives Base / WS / WS+Cutoff means on the items that have a valid answer in all three conditions. Pre-cutoff: publication month on or before the cutoff month; post-cutoff: publication month after the cutoff month. $n$ is the number of events in the partition. Significance of WS and WS+Cutoff against Base, with the tests of Supplementary Table~\ref{tab:combined_web_search_cutoff}: $^{***}p<0.001$, $^{**}p<0.01$, $^{*}p<0.05$. ``---'': fewer than 20 items. GPT-4o and LLaMA~3.3 have no pre-cutoff events in the subset. Blue: models added in the revision.}
\label{tab:cutoff_split}
\end{revblock}
\end{table}
"""
(TB / "websearch_cutoff_split.tex").write_text(txt)
# ---------------- calibration split
def ece(c, y, n=10):
    c, y = np.array(c), np.array(y); b = np.minimum((c * n).astype(int), n - 1)
    return float(sum((b == k).mean() * abs(c[b == k].mean() - y[b == k].mean()) for k in range(n) if (b == k).any()))
def calib(D, ids, task):
    c, y = [], []
    for i in ids:
        t = (D[i].get("tasks") or {}).get(task) or {}
        if t.get("skipped") or t.get("confidence") is None or t.get("score") is None: continue
        c.append(float(t["confidence"])); y.append(float(t["score"]))
    if len(c) < 20: return None
    c, y = np.array(c), np.array(y); return ece(c, y), float(np.mean((c - y) ** 2)), float(c.mean() - y.mean())
L = []
for mk in ORDER:
    cut, B, C, Wd, ids = DATA[mk]
    first = True
    for scope in ("pre", "post"):
        sid = [i for i in ids if (pub.get(i, "9999") <= cut) == (scope == "pre")]
        if not sid: continue
        for task, tl in (("binary", "Binary (original)"), ("binary_perturbed", "Binary (perturbed)"), ("mcq", "MCQ"), ("date", "Date")):
            r = [calib(D, sid, task) for D in (B, Wd, C)]
            if any(x is None for x in r): cells = ["---"] * 3
            else: cells = [" / ".join(f"{x[k]:.3f}" if k < 2 else f"{x[k]:+.3f}" for x in r) for k in range(3)]
            L.append(rf"{mname(mk) if first else ''} & {('Pre' if scope=='pre' else 'Post') + f' ($n={len(sid)}$)' if tl.startswith('Binary (o') else ''} & {tl} & " + " & ".join(cells) + r" \\")
            first = False
    L.append(r"\midrule")
L[-1] = r"\bottomrule"
txt = r"""\begin{table}[p]
\centering
\begin{revblock}
\scriptsize
\setlength{\tabcolsep}{4pt}
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{@{}lll ccc@{}}
\toprule
Model & Partition & Task & ECE$\downarrow$ & Brier$\downarrow$ & Gap \\
\midrule
""" + "\n".join(L) + r"""
\end{tabular}
\end{adjustbox}
\caption{\textbf{Confidence calibration in the original knowledge-access experiment, split by knowledge cutoff.} Each cell gives Base / WS / WS+Cutoff values. ECE: expected calibration error with 10 equal-width bins. Brier: mean squared difference between confidence and outcome (correctness, or the date score). Gap: mean confidence minus mean outcome; a positive value shows overconfidence. Partitions as in Supplementary Table~\ref{tab:cutoff_split}. ``---'': fewer than 20 items with a confidence in a condition. Blue: models added in the revision.}
\label{tab:calib_cutoff_split}
\end{revblock}
\end{table}
"""
(TB / "websearch_calib_split.tex").write_text(txt)
for mk in ORDER:
    cut, B, C, Wd, ids = DATA[mk]; print(mk, len(ids), "pre", sum(pub.get(i, "9999") <= cut for i in ids))
