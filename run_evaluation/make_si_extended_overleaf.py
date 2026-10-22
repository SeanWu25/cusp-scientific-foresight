#!/usr/bin/env python3
"""
make_si_extended_overleaf.py — nine-model versions of the SI "Extended Results" tables and figures (sean_si.tex).
SI_ORIG_ONLY=1 reproduces the submitted six-model SI values on the original corpus (checked 2026-10-17).
Population as in the submitted SI tables: ALL events (pre + post cutoff), full corpus (DeepSeek R1: original corpus only).
Binary uses balanced accuracy where the submitted SI said "merged" (mean of original and perturbed accuracy).
ECE: 10 equal-width bins on [0,1] (as in the submitted calibration table). Writes manuscript_updates/si_tables/*.tex and
manuscript_updates/{frq_dimensions_rev,frq_area_rev,date_prediction_rev,calibration_rev}.png
"""
import json, math, statistics as st, sys
from collections import defaultdict
from pathlib import Path
import numpy as np, os
ORIG = os.environ.get("SI_ORIG_ONLY") == "1"
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "run_evaluation")); import make_table1_overleaf as T
OUT = ROOT / "manuscript_updates"; TB = OUT / ("si_tables_origcheck" if ORIG else "si_tables"); TB.mkdir(exist_ok=True)
COL = {"GPT-4o": "#D55E00", "GPT-OSS": "#E69F00", "DeepSeek R1": "#CC79A7", "LLaMA 3.3": "#56B4E9", "Claude S4.5": "#0072B2",
       "GPT-5.4": "#009E73", "Claude Opus 4.8": "#7B4FA0", "Claude Sonnet 5": "#B2182B", "GPT-5.6 Sol": "#6E6E6E"}
ICON = {m[0]: m[2] for m in T.MODELS}; CUT = {m[0]: m[1] for m in T.MODELS}; NEW = {m[0] for m in T.MODELS if m[5]}
MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
AREAS = [("Biology", "Biology"), ("Artificial Intelligence", "AI"), ("Medicine", "Medicine"), ("Neuroscience", "Neurosci."),
         ("Materials Science", "Mat.\\ Sci."), ("Physics", "Physics"), ("Environmental Science", "Env.\\ Sci."), ("Chemistry", "Chemistry"), ("Other", "Other")]
DIMS = ["alignment", "specificity", "novelty", "feasibility"]
def ece(pairs, n=10):
    if not pairs: return None
    b = defaultdict(list)
    for c, y in pairs: b[min(int(c * n), n - 1)].append((c, y))
    return sum(len(v) / len(pairs) * abs(np.mean([c for c, _ in v]) - np.mean([y for _, y in v])) for v in b.values())
meta = {}
for bf in T.BENCH:
    for l in open(ROOT / bf):
        if l.strip(): r = json.loads(l); meta[r["id"]] = (r["main_area"], r["publication_date"][:7])
D = {}
for name, cut, icon, op, ep, new in T.MODELS:
    seen = set(); d = defaultdict(list); da = defaultdict(lambda: defaultdict(list))
    if ORIG and new: continue
    for p in [op] + ([ep] if ep and not ORIG else []):
        for r in json.load(open(ROOT / p))["results"]:
            if r["id"] in seen or r["id"] not in meta: continue
            seen.add(r["id"]); ar = meta[r["id"]][0]; t = r["tasks"]
            for k in ("binary", "binary_perturbed"):
                v = t.get(k)
                if v and "correct" in v:
                    c = 1.0 if v["correct"] else 0.0; d[k].append(c); da[ar][k].append(c)
                    ans = str(v.get("parsed_answer", "")).lower(); d[k + "_yes"].append(ans == "yes")
                    if v.get("confidence") is not None: d["bconf"].append(float(v["confidence"])); d["bcal"].append((float(v["confidence"]), c))
            v = t.get("mcq")
            if v and "correct" in v:
                c = 1.0 if v["correct"] else 0.0; d["mcq"].append(c); da[ar]["mcq"].append(c)
                if v.get("confidence") is not None: d["mconf"].append(float(v["confidence"])); d["mcal"].append((float(v["confidence"]), c))
            v = t.get("frq")
            if v and v.get("score") is not None:
                d["frq"].append(float(v["score"])); da[ar]["frq"].append(float(v["score"]))
                for k in DIMS:
                    if v.get(k) is not None: d[k].append(float(v[k])); da[ar][k].append(float(v[k]))
            v = t.get("date")
            if v and v.get("score") is not None:
                d["date"].append(float(v["score"])); da[ar]["date"].append(float(v["score"]))
                if v.get("confidence") is not None: d["dconf"].append(float(v["confidence"])); d["dcal"].append((float(v["confidence"]), float(v["score"])))
                if v.get("parsed_date") and v.get("ground_truth"):
                    a, g = T.mo(v["parsed_date"]), T.mo(v["ground_truth"])
                    if a is not None and g is not None: d["hex"].append((g, a))
    D[name] = dict(d=d, da=da)
M = list(D)
def nm(m, bold=False):
    s = rf"\llmicon{{icons/{ICON[m]}}} {m}" + (r"$^\dagger$" if m == "DeepSeek R1" else "")
    return rf"\revise{{{s}}}" if m in NEW else s
def cut(m): c = CUT[m]; return f"{MON[int(c[5:]) - 1]} {c[:4]}"
def legend(scale, fmt):
    names = ["cellbad", "cellworse", "cellneutral", "cellgood", "cellbetter", "cellbest"]; out = [rf"\colorbox{{cellbad}}{{\strut\,$<${fmt(scale[0])}\,}}"]
    for i in range(len(scale) - 1): out.append(rf"\colorbox{{{names[i+1]}}}{{\strut\,{fmt(scale[i])}--{fmt(scale[i+1])}\,}}")
    out.append(rf"\colorbox{{cellbest}}{{\strut\,$\geq${fmt(scale[-1])}\,}}"); return "Colour scale: " + " ".join(out) + "."
def shade_acc(v, scale):
    for th, c in zip(scale, ["cellbad", "cellworse", "cellneutral", "cellgood", "cellbetter"]):
        if v < th: return c
    return "cellbest"
NOTE = r"\revise{All events (pre- and post-cutoff) of the full corpus (January 2024--August 2026). $^\dagger$DeepSeek R1: original corpus only. Blue: models added in revision.}"
def table(label, caption, colspec, header, rows):
    return "\n".join([r"\begin{table}[htbp]", r"\centering", r"\begin{revblock}", r"\begin{adjustbox}{max width=\textwidth}", r"\small\renewcommand{\arraystretch}{1.18}",
                      rf"\begin{{tabular}}{{{colspec}}}", r"\toprule", header, r"\midrule"] + rows + [r"\bottomrule", r"\end{tabular}", r"\end{adjustbox}",
                      rf"\caption{{{caption}}}", rf"\label{{{label}}}", r"\end{revblock}", r"\end{table}"]) + "\n"
# ---- FRQ sub-dimensions
rows = []
for m in sorted(M, key=lambda m: np.mean(D[m]["d"]["frq"])):
    d = D[m]["d"]; a, s_, n_, f_ = (np.mean(d[k]) for k in DIMS)
    sh = lambda v: shade_acc(v, [3, 4, 5, 6, 6.5])
    rows.append(f"{nm(m)} & {cut(m)} & \\cellcolor{{{sh(a)}}}{a:.2f} & \\cellcolor{{{sh(s_)}}}{s_:.2f} & \\cellcolor{{{sh(n_)}}}{n_:.2f} & \\cellcolor{{{sh(f_)}}}{f_:.2f} & {s_ - a:+.1f} & {np.mean(d['frq']):.2f} \\\\")
(TB / "frq_subdims.tex").write_text(table("tab:frq_subdims", r"\textbf{FRQ sub-dimension profile.} \textbf{Alignment}: match with the realized approach. \textbf{Specificity}: technical concreteness. \textbf{Novelty}: non-obvious ideas. \textbf{Feasibility}: technical plausibility. \textbf{Spec.\,$-$\,Align.}: a positive value shows detailed answers that miss the realized approach. Scores use the 0--10 rubric. " + legend([3, 4, 5, 6, 6.5], lambda x: f"{x:g}") + " " + NOTE,
    "@{}ll rrrr rr@{}", r"\textbf{Model} & \textbf{Cutoff} & \textbf{Align.\,$\uparrow$} & \textbf{Spec.\,$\uparrow$} & \textbf{Nov.\,$\uparrow$} & \textbf{Feas.\,$\uparrow$} & \textbf{Spec.\,$-$\,Align.} & \textbf{Overall} \\", rows))
# ---- area tables
order_m = sorted(M, key=lambda m: -np.mean(D[m]["d"]["mcq"]))
def area_table(key, label, title, fmt, scale, extra):
    hdr = r"\textbf{Research area} & $n$ & " + " & ".join(rf"\textbf{{{m}}}" for m in order_m) + r" & \textit{Mean} \\"
    rows = []; colmeans = defaultdict(list)
    for a, lab in AREAS:
        vals = []
        for m in order_m:
            da = D[m]["da"][a]
            if key == "bal": v = (np.mean(da["binary"]) + np.mean(da["binary_perturbed"])) / 2 if len(da["binary"]) >= 10 and len(da["binary_perturbed"]) >= 10 else None
            else: v = np.mean(da[key]) if len(da[key]) >= 10 else None
            vals.append(v)
            if v is not None: colmeans[m].append(v)
        n = max((len(D[m]["da"][a]["binary"]) + len(D[m]["da"][a]["binary_perturbed"])) if key == "bal" else len(D[m]["da"][a][key]) for m in order_m)
        ok = [v for v in vals if v is not None]; best = max(ok) if ok else None
        cells = [("---" if v is None else (rf"\cellcolor{{{shade_acc(v, scale)}}}" + (rf"\textbf{{{fmt(v)}}}" if v == best else fmt(v)))) for v in vals]
        rows.append(f"{lab} & {n} & " + " & ".join(cells) + f" & {fmt(np.mean(ok)) if ok else '---'} \\\\")
    rows.append(r"\midrule"); rows.append(r"\textit{Mean} & & " + " & ".join(fmt(np.mean(colmeans[m])) for m in order_m) + r" & \\")
    return table(label, title + " " + extra + " " + legend(scale, lambda x: f"{x:g}") + " " + NOTE, "@{}lr " + "r" * len(order_m) + " r@{}", hdr, rows)
f3 = lambda v: f"{v:.3f}"; f2 = lambda v: f"{v:.2f}"
(TB / "area_mcq.tex").write_text(area_table("mcq", "tab:area_mcq", r"\textbf{MCQ accuracy by research area.}", f3, [0.40, 0.50, 0.60, 0.70, 0.80], r"Chance is 0.25. $n$: MCQ questions per area. Bold: best model per row. Cells with fewer than 10 questions show ---."))
(TB / "area_date.tex").write_text(area_table("date", "tab:area_date", r"\textbf{Date prediction score by research area.}", f3, [0.15, 0.22, 0.29, 0.36, 0.43], r"The score uses exponential decay (1.0\,=\,exact month). $n$: date questions per area. Bold: best model per row."))
(TB / "area_binary.tex").write_text(area_table("bal", "tab:area_binary", r"\textbf{Binary balanced accuracy by research area.}", f3, [0.44, 0.48, 0.52, 0.56, 0.60], r"Balanced accuracy is the mean of the accuracies on original and perturbed questions (chance 0.50). $n$: binary items per area (original and perturbed). Bold: best model per row."))
(TB / "area_frq.tex").write_text(area_table("frq", "tab:frq_by_area", r"\textbf{Mean FRQ score (0--10) by research area.}", f2, [3, 4, 5, 6, 7], r"$n$: FRQ instances per area (maximum across models). Bold: best model per row."))
# ---- bias table
rows = []
for m in sorted(M, key=lambda m: np.mean(D[m]["d"]["binary"]) - np.mean(D[m]["d"]["binary_perturbed"])):
    d = D[m]["d"]; a1, a2 = np.mean(d["binary"]), np.mean(d["binary_perturbed"]); bi = a1 - a2; bal = (a1 + a2) / 2
    tend = "Strong ``No'' bias" if bi < -0.5 else "``No'' bias" if bi < -0.1 else "Balanced" if bi <= 0.1 else "``Yes'' bias" if bi <= 0.5 else "Strong ``Yes'' bias"
    rows.append(f"{nm(m)} & {cut(m)} & {a1:.3f} & {a2:.3f} & {bi:+.2f} & {bal:.3f} & {tend} \\\\")
rows += [r"\addlinespace[0.5em]", r"\textit{Chance (random)} & & 0.500 & 0.500 & 0.00 & 0.500 & --- \\"]
(TB / "bias.tex").write_text(table("tab:binary_bias", r"\textbf{Binary response-bias analysis.} \textbf{Bias index}\,=\,accuracy on original questions\,$-$\,accuracy on perturbed questions; $+1$\,=\,always ``Yes'', $-1$\,=\,always ``No'', $0$\,=\,unbiased. \textbf{Balanced}: the mean of the two accuracies (chance\,=\,0.50). Models are sorted from most No-biased to most Yes-biased. " + NOTE,
    "@{}ll rrrrl@{}", r"\textbf{Model} & \textbf{Cutoff} & \textbf{Original acc.} & \textbf{Perturbed acc.} & \textbf{Bias index} & \textbf{Balanced\,$\uparrow$} & \textbf{Response tendency} \\", rows))
# ---- calibration table
def ecell(v): return rf"\cellcolor{{{'cellbest' if v < .05 else 'cellgood' if v < .10 else 'cellneutral' if v < .15 else 'cellworse' if v < .25 else 'cellbad'}}}{v:.3f}"
def ocell(v): a = abs(v); return rf"\cellcolor{{{'cellbest' if a < .05 else 'cellgood' if a < .10 else 'cellneutral' if a < .15 else 'cellworse' if a < .25 else 'cellbad'}}}{v:+.2f}"
rows = []
for m in sorted(M, key=lambda m: -np.mean(D[m]["d"]["mcq"])):
    d = D[m]["d"]; bc, ba = np.mean(d["bconf"]), np.mean([y for _, y in d["bcal"]]); mc, ma = np.mean(d["mconf"]), np.mean([y for _, y in d["mcal"]])
    dc, ds = np.mean(d["dconf"]), np.mean([y for _, y in d["dcal"]])
    rows.append(f"{nm(m)} & {bc:.3f} & {ba:.3f} & {ocell(bc - ba)} & {ecell(ece(d['bcal']))} & {mc:.3f} & {ma:.3f} & {ocell(mc - ma)} & {ecell(ece(d['mcal']))} & {dc:.3f} & {ds:.3f} & {ocell(dc - ds)} & {ecell(ece(d['dcal']))} \\\\")
(TB / "calibration.tex").write_text(table("tab:calibration", r"\textbf{Confidence calibration across tasks.} \textbf{Conf.}: mean self-reported confidence (0--1). \textbf{Acc.}/\textbf{Score}: mean accuracy or date score. \textbf{Over-conf.}: confidence\,$-$\,accuracy; a positive value shows overconfidence. \textbf{ECE}: expected calibration error with 10 equal-width bins; lower is better. Most older models are overconfident on MCQ. Claude Opus 4.8 and Claude Sonnet 5 are underconfident on MCQ. All models are overconfident on date prediction. Colours for ECE and overconfidence magnitude: \colorbox{cellbest}{\strut\,$<$0.05\,} \colorbox{cellgood}{\strut\,0.05--0.10\,} \colorbox{cellneutral}{\strut\,0.10--0.15\,} \colorbox{cellworse}{\strut\,0.15--0.25\,} \colorbox{cellbad}{\strut\,$>$0.25\,}. " + NOTE,
    "@{}l rrrr rrrr rrrr@{}", r"\textbf{Model} & \multicolumn{4}{c}{\textbf{Binary}} & \multicolumn{4}{c}{\textbf{MCQ}} & \multicolumn{4}{c}{\textbf{Date}} \\ \cmidrule(lr){2-5} \cmidrule(lr){6-9} \cmidrule(lr){10-13}" + "\n" + r" & \textbf{Conf.} & \textbf{Acc.} & \textbf{Over-conf.} & \textbf{ECE} & \textbf{Conf.} & \textbf{Acc.} & \textbf{Over-conf.} & \textbf{ECE} & \textbf{Conf.} & \textbf{Score} & \textbf{Over-conf.} & \textbf{ECE} \\", rows))
# ---- binary extended
BS = [0.44, 0.48, 0.52, 0.56, 0.60]
rows = []
for m in sorted(M, key=lambda m: -((np.mean(D[m]["d"]["binary"]) + np.mean(D[m]["d"]["binary_perturbed"])) / 2)):
    d = D[m]["d"]; tp = sum(d["binary"]); fn = len(d["binary"]) - tp; tn = sum(d["binary_perturbed"]); fp = len(d["binary_perturbed"]) - tn
    prec = tp / (tp + fp) if tp + fp else 0; rec = tp / (tp + fn); spec = tn / (tn + fp); f1y = 2 * prec * rec / (prec + rec) if prec + rec else 0
    npv = tn / (tn + fn) if tn + fn else 0; f1n = 2 * npv * spec / (npv + spec) if npv + spec else 0
    mcc = (tp * tn - fp * fn) / math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)) if (tp + fp) * (tn + fn) else 0
    rows.append(f"{nm(m)} & {cut(m)} & {int(tp + fn + tn + fp)} & \\cellcolor{{{shade_acc((rec + spec) / 2, BS)}}}{(rec + spec) / 2:.3f} & {prec:.3f} & {rec:.3f} & {spec:.3f} & {f1y:.3f} & {f1n:.3f} & \\cellcolor{{{shade_acc((f1y + f1n) / 2, BS)}}}{(f1y + f1n) / 2:.3f} & \\cellcolor{{{shade_acc(mcc, [-0.05, -0.02, 0.02, 0.06, 0.10])}}}{mcc:+.3f} \\\\")
rows += [r"\addlinespace[0.5em]", r"\textit{Chance (random)} & & & 0.500 & 0.500 & 0.500 & 0.500 & 0.500 & 0.500 & 0.500 & 0.000 \\"]
(TB / "binary_extended.tex").write_text(table("tab:binary_extended", r"\textbf{Binary task: extended classification metrics.} We use a 2$\times$2 confusion matrix. Original questions have the ground truth \textit{Yes} (TP/FN). Negation-flipped questions have the ground truth \textit{No} (TN/FP). \textbf{Bal.\ Acc.}: balanced accuracy. \textbf{Prec.}: precision for \textit{Yes}. \textbf{Spec.}: specificity. \textbf{MCC}: Matthews correlation coefficient (0\,=\,random). Models are sorted by balanced accuracy. Shading for Bal.\ Acc.\ and Macro F1 uses the scale of Table~\ref{tab:area_binary}. " + NOTE,
    "@{}ll r r rrr rrr r@{}", r"\textbf{Model} & \textbf{Cutoff} & $n$ & \textbf{Bal.\ Acc.}$\uparrow$ & \textbf{Prec.} & \textbf{Recall} & \textbf{Spec.} & \textbf{F1-Yes} & \textbf{F1-No} & \textbf{Macro F1}$\uparrow$ & \textbf{MCC}$\uparrow$ \\", rows))
if ORIG:
    for m in M:
        d=D[m]["d"]; print(m, "bin", round(np.mean(d["bconf"]),3), round(np.mean([y for _,y in d["bcal"]]),3), round(ece(d["bcal"]),3), "| mcq", round(np.mean(d["mconf"]),3), round(np.mean([y for _,y in d["mcal"]]),3), round(ece(d["mcal"]),3), "| date", round(np.mean(d["dconf"]),3), round(np.mean([y for _,y in d["dcal"]]),3), round(ece(d["dcal"]),3), "| frq", [round(np.mean(d[k]),2) for k in DIMS], round(np.mean(d["frq"]),2), "| mcqBio n", len(D[m]["da"]["Biology"]["mcq"]), round(np.mean(D[m]["da"]["Biology"]["mcq"]),3))
    sys.exit()
# ---- figures
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import sys as _s; _s.path.insert(0, "/home/seanwu/FutureScience/run_evaluation"); import display_names; display_names.install()
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
DC = {"alignment": "#D6604D", "specificity": "#F4A582", "novelty": "#92C5DE", "feasibility": "#4DAC26"}
ordf = sorted(M, key=lambda m: np.mean(D[m]["d"]["frq"]))
fig, axes = plt.subplots(1, 2, figsize=(15, 5.2))
x = np.arange(len(ordf)); w = 0.2
for j, k in enumerate(DIMS):
    axes[0].bar(x + (j - 1.5) * w, [np.mean(D[m]["d"][k]) for m in ordf], w, color=DC[k], label=k.capitalize())
axes[0].set_xticks(x); axes[0].set_xticklabels(ordf, rotation=35, ha="right", fontsize=9); axes[0].set_ylabel("Mean score (0–10)"); axes[0].legend(frameon=False, ncol=4, fontsize=9, loc="upper left"); axes[0].set_ylim(0, 8)
axes[0].set_title("a   Four FRQ criteria per model", loc="left", fontweight="bold")
parts = axes[1].violinplot([D[m]["d"]["frq"] for m in ordf], showmeans=True, widths=0.8)
for pc, m in zip(parts["bodies"], ordf): pc.set_facecolor(COL[m]); pc.set_alpha(0.6)
axes[1].axhline(5, color="#aaa", ls=":"); axes[1].set_xticks(x + 1); axes[1].set_xticklabels(ordf, rotation=35, ha="right", fontsize=9); axes[1].set_ylabel("FRQ score (0–10)")
axes[1].set_title("b   FRQ score distribution per model", loc="left", fontweight="bold")
fig.tight_layout(); fig.savefig(OUT / "frq_dimensions_rev.png", dpi=200); plt.close(fig)
fig, axes = plt.subplots(1, 2, figsize=(15, 5.2))
arl = [a for a, _ in AREAS[:-1]]; mat = np.array([[np.mean(np.array(D[m]["da"][a]["frq"]) >= 5) if len(D[m]["da"][a]["frq"]) >= 10 else np.nan for a in arl] for m in ordf])
im = axes[0].imshow(mat, cmap="Greens", vmin=0, vmax=0.7, aspect="auto")
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        if not np.isnan(mat[i, j]): axes[0].text(j, i, f"{100*mat[i,j]:.0f}", ha="center", va="center", fontsize=7)
axes[0].set_yticks(range(len(ordf))); axes[0].set_yticklabels(ordf, fontsize=9); axes[0].set_xticks(range(len(arl))); axes[0].set_xticklabels([s for _, s in AREAS[:-1]], rotation=35, ha="right", fontsize=9)
axes[0].set_title("a   Pass rate (score ≥ 5, %) by model and domain", loc="left", fontweight="bold"); fig.colorbar(im, ax=axes[0], shrink=0.8)
for j, k in enumerate(DIMS):
    axes[1].bar(np.arange(len(arl)) + (j - 1.5) * w, [np.mean([np.mean(D[m]["da"][a][k]) for m in M if len(D[m]["da"][a][k]) >= 10]) for a in arl], w, color=DC[k], label=k.capitalize())
axes[1].set_xticks(range(len(arl))); axes[1].set_xticklabels([s.replace("\\ ", " ") for _, s in AREAS[:-1]], rotation=35, ha="right", fontsize=9); axes[1].set_ylim(0, 8); axes[1].legend(frameon=False, ncol=4, fontsize=9, loc="upper left")
axes[1].set_ylabel("Cross-model mean score (0–10)"); axes[1].set_title("b   Four FRQ criteria by domain (cross-model mean)", loc="left", fontweight="bold")
axes[0].set_xticklabels([s.replace("\\ ", " ") for _, s in AREAS[:-1]], rotation=35, ha="right", fontsize=9)
fig.tight_layout(); fig.savefig(OUT / "frq_area_rev.png", dpi=200); plt.close(fig)
from matplotlib.colors import LinearSegmentedColormap
fig, axes = plt.subplots(3, 3, figsize=(15, 13))
for ax, m in zip(axes.flat, sorted(M, key=lambda m: CUT[m])):
    g = np.array([h[0] for h in D[m]["d"]["hex"]]); p_ = np.array([h[1] for h in D[m]["d"]["hex"]]); lo, hi = g.min() - 1, g.max() + 1
    keep = (p_ >= lo - 12) & (p_ <= lo + 72)
    ax.hexbin(g[keep], p_[keep], gridsize=20, mincnt=1, cmap=LinearSegmentedColormap.from_list("c", ["#f2f2f2", COL[m]]))
    ax.plot([lo, hi], [lo, hi], "--", color="#444", lw=1.2); cm = T.mo(CUT[m]); ax.axhline(cm, color=COL[m], ls=":", lw=1.2)
    ticks = list(range(T.mo("2023-01"), T.mo("2032-01"), 12))
    ax.set_xticks([t for t in ticks if lo <= t <= hi]); ax.set_xticklabels([T.ym(t) for t in ax.get_xticks()], fontsize=7, rotation=30)
    ax.set_yticks([t for t in ticks if lo - 12 <= t <= lo + 72]); ax.set_yticklabels([T.ym(t) for t in ax.get_yticks()], fontsize=7)
    ax.set_title(f"{m} [cutoff {CUT[m]}]", fontsize=10, fontweight="bold", color=COL[m])
for ax in axes[-1]: ax.set_xlabel("Ground-truth date")
for ax in axes[:, 0]: ax.set_ylabel("Predicted date")
fig.tight_layout(); fig.savefig(OUT / "date_prediction_rev.png", dpi=170); plt.close(fig)
fig, axes = plt.subplots(3, 3, figsize=(13, 12))
for ax, m in zip(axes.flat, sorted(M, key=lambda m: CUT[m])):
    ax.plot([0, 1], [0, 1], "--", color="#bbb")
    for key, c, mk, lab in (("bcal", "#2166AC", "o", "Binary"), ("mcal", "#C0392B", "s", "MCQ")):
        pts = D[m]["d"][key]; bins = defaultdict(list)
        for cc, y in pts: bins[min(int(cc * 10), 9)].append((cc, y))
        xs = [np.mean([a for a, _ in v]) for k, v in sorted(bins.items()) if len(v) >= 20]; ys = [np.mean([b for _, b in v]) for k, v in sorted(bins.items()) if len(v) >= 20]
        ax.plot(xs, ys, marker=mk, color=c, label=f"{lab} (ECE {ece(pts):.3f})")
    ax.set_xlim(0, 1.02); ax.set_ylim(0, 1.02); ax.set_title(m, fontsize=10, fontweight="bold"); ax.legend(fontsize=7, frameon=False, loc="upper left")
for ax in axes[-1]: ax.set_xlabel("Stated confidence")
for ax in axes[:, 0]: ax.set_ylabel("Fraction correct")
fig.tight_layout(); fig.savefig(OUT / "calibration_rev.png", dpi=170); plt.close(fig)
print("written:", sorted(p.name for p in TB.iterdir()))
for m in M:
    d = D[m]["d"]; print(f"{m:16s} MCQ ECE {ece(d['mcal']):.3f} bin ECE {ece(d['bcal']):.3f} bal {(np.mean(d['binary'])+np.mean(d['binary_perturbed']))/2:.3f}")
