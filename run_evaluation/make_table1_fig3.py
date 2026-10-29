#!/usr/bin/env python3
"""
make_table1_fig3.py — revision versions of main-text Table 1 and Figure 3 (2026-10-16).

Table 1   nine-model panel (full_corpus_tables.PANEL minus Claude Opus 4.8, whose panel status is an open decision),
          original + Apr-Aug 2026 extension pooled; DeepSeek R1 original corpus only (Azure deployment retired before the
          extension). Post-cutoff value with Δ = post - pre beneath. Partition rule `main`: pre if pub month < cutoff month.
          Binary = balanced accuracy (mean of accuracy on the original question and on its perturbed twin; corrects for
          directional response bias, chance 0.50); MCQ = accuracy (chance 0.25); FRQ = rubric mean 0-10, Pass = share >= 5;
          temporal: mean predicted month, signed error (predicted - actual, months), share within 6 months, score exp(-0.1|Δt|).
          New material (models added since the submitted version, new caption text) is typeset in blue.
Figure 3a knowledge gap (WS+Cutoff - base) and forecasting gap (WS - WS+Cutoff) from the FIXED-EVIDENCE PACKET experiment
          (A4.3), per model, Binary (merged original + perturbed items), MCQ, FRQ, Temporal; pre-cutoff (top) and post-cutoff
          (bottom); ids shared by every condition (as in the A4.3 tables); error bars s.e.m. of the paired difference; n<20 hidden.
Figure 3b per-domain post-cutoff performance of the nine models, eight fields, four tasks; diamonds cross-model mean; dashed
          chance; error bars s.e.m.
Outputs   manuscript_updates/{table1_9models.tex, table1_9models.md, fig3a_gaps_fixed_evidence.{pdf,png},
          fig3b_domain_9models.{pdf,png}, fig3_caption.tex}
"""
from __future__ import annotations
import json, math, os, sys, statistics as st
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "manuscript_updates"; OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "run_evaluation")); from full_corpus_tables import PANEL
BENCH = [ROOT / "archive/data/canonical/merged_validated_cusp_fixed.jsonl", ROOT / "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"]
NINE = [p for p in PANEL if p[0] != "Claude Opus 4.8"]
NEW_MODELS = {"Claude Sonnet 5", "GPT-5.6 Sol", "DeepSeek-V4-Pro"}          # not in the submitted Table 1
AREAS = ["Artificial Intelligence", "Biology", "Chemistry", "Environmental Science", "Materials Science", "Medicine", "Neuroscience", "Physics"]
AREA_SHORT = {"Artificial Intelligence": "AI", "Biology": "Biology", "Chemistry": "Chemistry", "Environmental Science": "Env. Sci.",
              "Materials Science": "Materials", "Medicine": "Medicine", "Neuroscience": "Neuro.", "Physics": "Physics"}
WITHIN = 6


def mo(s):
    try: y, m = str(s)[:7].split("-"); return int(y) * 12 + int(m)
    except Exception: return None


def ym(m): m = int(round(m)); return f"{(m - 1) // 12:04d}-{(m - 1) % 12 + 1:02d}"


meta = {}
for p in BENCH:
    for l in open(p, encoding="utf-8"):
        if l.strip(): r = json.loads(l); meta[r["id"]] = dict(pub=str(r.get("publication_date", ""))[:7], area=r.get("main_area"))


def collect(name, cutoff, op, ep):
    """part -> metric -> list; plus per-area post accumulators."""
    A = defaultdict(lambda: defaultdict(list)); AR = defaultdict(lambda: defaultdict(list)); seen = set(); cm = mo(cutoff)
    for p in (op, ep):
        if not p or not os.path.exists(ROOT / p): continue
        for r in json.load(open(ROOT / p))["results"]:
            if r["id"] in seen: continue
            seen.add(r["id"]); m = meta.get(r["id"]); pm = mo(m["pub"]) if m else None
            if pm is None: continue
            part = "pre" if pm < cm else "post"; t = r.get("tasks", {}); area = m["area"]
            for task in ("binary", "binary_perturbed", "mcq"):
                v = t.get(task)
                if v and not v.get("skipped") and not v.get("refused") and "correct" in v:
                    x = 1.0 if v["correct"] else 0.0; A[part][task].append(x)
                    if part == "post": AR[area][task].append(x)
            v = t.get("frq")
            if v and not v.get("skipped") and v.get("score") is not None:
                A[part]["frq"].append(float(v["score"]))
                if part == "post": AR[area]["frq"].append(float(v["score"]))
            v = t.get("date")
            if v and not v.get("skipped") and v.get("score") is not None:
                # score over every scored item (unparseable answers score 0, the published convention);
                # predicted month, signed error and within-N over parsed predictions only
                A[part]["date_score"].append(float(v["score"]))
                if part == "post": AR[area]["date_score"].append(float(v["score"]))
                pd, gt = mo(v.get("parsed_date")), mo(v.get("ground_truth"))
                if pd is not None and gt is not None:
                    A[part]["date_pred"].append(pd); A[part]["date_gt"].append(gt)
                    A[part]["date_signed"].append(pd - gt); A[part]["date_within"].append(1.0 if abs(pd - gt) <= WITHIN else 0.0)
    return A, AR


def metrics(a):
    o = {}
    b, p = a.get("binary", []), a.get("binary_perturbed", [])
    o["binary"] = (st.fmean(b) + st.fmean(p)) / 2 if len(b) >= 20 and len(p) >= 20 else None
    o["n_binary"] = len(b) + len(p)
    o["mcq"] = st.fmean(a["mcq"]) if len(a.get("mcq", [])) >= 20 else None
    f = a.get("frq", [])
    o["frq"] = st.fmean(f) if len(f) >= 20 else None; o["pass"] = (sum(x >= 5 for x in f) / len(f)) if len(f) >= 20 else None
    d = a.get("date_score", [])
    ok = len(d) >= 20
    okp = len(a.get("date_pred", [])) >= 20
    o["date_pred"] = st.fmean(a["date_pred"]) if okp else None; o["date_signed"] = st.fmean(a["date_signed"]) if okp else None
    o["date_within"] = st.fmean(a["date_within"]) if okp else None; o["date_score"] = st.fmean(d) if ok else None
    o["date_gt"] = st.fmean(a["date_gt"]) if okp else None
    return o


rows = []; area_data = {}
for name, cutoff, op, ep in NINE:
    A, AR = collect(name, cutoff, op, ep); post, pre = metrics(A["post"]), metrics(A["pre"])
    rows.append(dict(name=name, cutoff=cutoff, post=post, pre=pre, n_pre=pre["n_binary"], n_post=post["n_binary"], ext=bool(ep)))
    area_data[name] = AR
rows.sort(key=lambda r: -(r["post"]["mcq"] or 0))
gt_mean = st.fmean([x for name, cutoff, op, ep in NINE for x in collect(name, cutoff, op, ep)[0]["post"]["date_gt"]])

# ----------------------------------------------------------------------------- Table 1
COLS = [("binary", "Binary", 3, "max", 1.0), ("mcq", "MCQ", 3, "max", 1.0), ("frq", "FRQ", 2, "max", 10.0), ("pass", r"Pass\,\%", 1, "max", 1.0),
        ("date_pred", "Mean pred.", None, None, None), ("date_signed", "Signed err.", 1, None, None),
        ("date_within", rf"$\le${WITHIN}\,mo", 1, "max", 1.0), ("date_score", "Date", 3, "max", 1.0)]


def fmtv(k, v, dp):
    if v is None: return "---"
    if k == "date_pred": return ym(v)
    if k in ("pass", "date_within"): return f"{100 * v:.{dp}f}"
    if k == "date_signed": return f"{v:+.{dp}f}"
    return f"{v:.{dp}f}"


def fmtd(k, d, dp, scale):
    if d is None: return r"$\Delta$\,=\,---"
    if k == "date_signed": s = f"{d:+.1f}"
    elif k in ("pass", "date_within"): s = f"{100 * d:+.1f}"
    else: s = f"{d:+.{dp}f}"
    s = s.replace("-", "$-$").replace("+", "$+$")
    shade = ""
    if scale is not None:
        z = d / scale if k == "frq" else d
        if k == "frq": z = d / 10
        shade = "green!25" if z > 0.05 else ("red!35" if z < -0.10 else ("orange!30" if z < -0.03 else ""))
    t = rf"{{\tiny\color{{gray}}{s}}}"
    return rf"\colorbox{{{shade}}}{{{t}}}" if shade else t


best = {}
for k, _, dp, mode, _ in COLS:
    vals = [r["post"][k] for r in rows if r["post"][k] is not None]
    if mode == "max" and vals: best[k] = max(vals)
L = [r"% Table 1 — revision version, generated by run_evaluation/make_table1_fig3.py. Requires \usepackage[table]{xcolor}, booktabs, makecell.",
     r"\begin{table}[t]", r"\centering", r"\scriptsize", r"\setlength{\tabcolsep}{3.2pt}",
     r"\caption{\textbf{Model performance on \CUSP{} with change across the training cutoff.} Overall performance on \CUSP{} post-cutoff instances. "
     r"Each metric shows the post-cutoff value; the small grey number beneath ($\Delta$) is the change from the pre-cutoff partition (post $-$ pre) for models that have one. "
     r"\emph{Binary} reports balanced accuracy over original and negation-flipped variants (mean of the two accuracies), which corrects for directional response bias (chance $=0.50$); \emph{MCQ} reports accuracy (chance $=0.25$). "
     r"\emph{FRQ} is an LLM rubric score (0--10); \emph{Pass\,\%} the fraction scoring $\ge 5$. "
     rf"\emph{{Temporal prediction}} reports mean predicted publication date (ground-truth mean {ym(gt_mean)}), signed error in months (predicted $-$ actual; positive $=$ later than truth), "
     rf"the fraction of predictions within {WITHIN} calendar months of truth, and an exponential-decay score $e^{{-0.1|\Delta t|}}$ (Date; $1.0=$ exact month). "
     r"Models are sorted by MCQ accuracy; bold marks the best value per column. $\Delta$ shading: \colorbox{green!25}{green} $>+0.05$ improvement, \colorbox{orange!30}{orange} $<-0.03$ degradation, \colorbox{red!35}{red} $<-0.10$ strong degradation (FRQ thresholds scaled to the 0--10 range). "
     r"Models with cutoff $\le$ Dec 2023 (GPT-4o, LLaMA 3.3) have no pre-cutoff instances ($\Delta=$\,---); $n_{\mathrm{pre}}$ is the number of binary-task pre-cutoff instances. "
     r"\textcolor{blue}{Benchmark papers span Jan 2024--Aug 2026 (original corpus, Jan 2024--Mar 2026, plus the Apr--Aug 2026 extension). "
     r"Nine models; rows in blue were added in revision. "
     r"$^\dagger$DeepSeek R1 is evaluated on the corpus before March 2026 only, because its deployment was retired before the extension could be run.}}",
     r"\label{tab:main}",
     r"\begin{tabular}{@{}l c r cccc cccc@{}}", r"\toprule",
     r" & & & & & & & \multicolumn{4}{c}{Temporal prediction} \\ \cmidrule(l){8-11}",
     r"Model & Cutoff & $n_{\mathrm{pre}}$ & Binary$\uparrow$ & MCQ$\uparrow$ & FRQ$\uparrow$ & Pass\,\%$\uparrow$ & Mean pred. & Signed err. & $\le$" + str(WITHIN) + r"\,mo\,\%$\uparrow$ & Date$\uparrow$ \\", r"\midrule"]
MD = ["| Model | Cutoff | n_pre | Binary | MCQ | FRQ | Pass % | Mean pred. | Signed err. | ≤6 mo % | Date |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    nm = r["name"] + (r"$^\dagger$" if not r["ext"] else ""); blue = r["name"] in NEW_MODELS
    cells = []
    for k, _, dp, mode, scale in COLS:
        v = r["post"][k]; s = fmtv(k, v, dp if dp is not None else 0)
        if mode == "max" and v is not None and abs(v - best[k]) < 1e-12: s = rf"\textbf{{{s}}}"
        if k == "date_pred": d = None if (v is None or r["pre"][k] is None) else None
        else: d = None if (v is None or r["pre"][k] is None) else v - r["pre"][k]
        cells.append(r"\makecell{" + s + r" \\ " + (fmtd(k, d, dp, scale) if k != "date_pred" else r"{\tiny\color{gray}\phantom{0}}") + "}")
    first = [nm, r["cutoff"], f"{r['n_pre']:,}"]
    if blue:   # \color inside a tabular only reaches the end of its cell, so colour every cell explicitly
        first = [rf"\textcolor{{blue}}{{{c}}}" for c in first]
        cells = [rf"\textcolor{{blue}}{{{c.replace(chr(92) + 'color{gray}', chr(92) + 'color{blue!60}')}}}" for c in cells]
    L.append(" & ".join(first) + " & " + " & ".join(cells) + r" \\")
    MD.append(f"| {r['name']}{'†' if not r['ext'] else ''}{' (new)' if blue else ''} | {r['cutoff']} | {r['n_pre']:,} | " + " | ".join(
        f"{fmtv(k, r['post'][k], dp if dp is not None else 0)}" + ("" if k == "date_pred" or r['post'][k] is None or r['pre'][k] is None else f" (Δ {fmtv(k if k in ('pass','date_within','date_signed') else 'x', r['post'][k] - r['pre'][k], dp if dp is not None else 1) if k not in ('pass','date_within') else format(100*(r['post'][k]-r['pre'][k]), '+.1f')})") for k, _, dp, _, _ in COLS) + " |")
L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(OUT / "table1_9models.tex").write_text("\n".join(L) + "\n"); (OUT / "table1_9models.md").write_text("\n".join(MD) + "\n")
print("\n".join(MD))

# ----------------------------------------------------------------------------- figures
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "sans-serif", "font.size": 6.5, "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
                     "xtick.major.width": 0.5, "ytick.major.width": 0.5, "legend.frameon": False, "pdf.fonttype": 42})
PAL = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD"]
COLOR = {name: PAL[i] for i, (name, *_) in enumerate(NINE)}

# 3a — fixed-evidence gaps
sys.path.insert(0, str(ROOT / "results/A4_retrieval/scripts")); import a43_gaps as G
GD = G.GD; pub = {i: r["publication_date"] for i, r in G.load_events().items()}
TASKS3 = [("Binary", ("binary", "binary_perturbed")), ("MCQ", ("mcq",)), ("FRQ (0–10)", ("frq",)), ("Temporal", ("date",))]
gap = {}
for mk, (name, cut, base, ws, wscut) in G.ORIG.items():
    fws, fwc = G.RP / f"{mk}_fixed_ws.json", G.RP / f"{mk}_fixed_ws_cutoff.json"
    if not (fws.exists() and fwc.exists() and Path(base).exists() and Path(wscut).exists()): continue
    B = GD.load(str(base), drop_retrieval_failures=False); C = GD.load(str(wscut)); FC = GD.load(str(fwc)); FW = GD.load(str(fws))
    W = GD.load(str(ws)) if ws and Path(ws).exists() else None
    shared = set(B) & set(C) & set(FC) & set(FW) & (set(W) if W else set(FW))
    for scope in ("pre", "post"):
        ids = [i for i in shared if (pub.get(i, "") > cut) == (scope == "post")]
        for lab, tasks in TASKS3:
            k, f = [], []
            for i in ids:
                for t in tasks:
                    b, fc, fw = GD.field(B[i], t, "score"), GD.field(FC[i], t, "score"), GD.field(FW[i], t, "score")
                    if None in (b, fc, fw): continue
                    k.append(fc - b); f.append(fw - fc)
            if len(k) >= 20:
                sem = lambda v: st.stdev(v) / math.sqrt(len(v))
                gap[(name, scope, lab)] = dict(k=st.fmean(k), ks=sem(k), f=st.fmean(f), fs=sem(f), n=len(k))
models3 = [n for n, *_ in G.ORIG.values() if any((n, s, t) in gap for s in ("pre", "post") for t, _ in TASKS3)]
fig, axes = plt.subplots(2, 4, figsize=(7.2, 3.9), sharex=False)
for row, scope in enumerate(("pre", "post")):
    for col, (lab, _) in enumerate(TASKS3):
        ax = axes[row, col]; ms = [m for m in models3 if (m, scope, lab) in gap]; x = np.arange(len(ms))
        if not ms: ax.text(0.5, 0.5, "no events (n < 20)", ha="center", va="center", transform=ax.transAxes, color="#888"); ax.set_xticks([])
        else:
            kv = [gap[(m, scope, lab)]["k"] for m in ms]; ke = [gap[(m, scope, lab)]["ks"] for m in ms]
            fv = [gap[(m, scope, lab)]["f"] for m in ms]; fe = [gap[(m, scope, lab)]["fs"] for m in ms]
            ax.bar(x - 0.19, kv, 0.36, yerr=ke, color="#3B6FB6", error_kw=dict(lw=0.6, capsize=1.5), label="Knowledge gap")
            ax.bar(x + 0.19, fv, 0.36, yerr=fe, color="#C8433A", error_kw=dict(lw=0.6, capsize=1.5), label="Forecasting gap")
            ax.set_xticks(x); ax.set_xticklabels([m.replace("Claude ", "").replace("GPT-5.6 ", "").replace(" 70B", "") for m in ms], rotation=40, ha="right", fontsize=5.5)
        ax.axhline(0, color="#555", lw=0.5)
        if row == 0: ax.set_title(lab, fontsize=7, fontweight="bold")
        if col == 0: ax.set_ylabel(("Pre-cutoff" if scope == "pre" else "Post-cutoff") + "\nΔ performance", fontsize=6.5)
axes[0, 0].legend(fontsize=5.5, loc="upper left")
fig.text(0.005, 0.985, "a", fontsize=9, fontweight="bold", va="top")
fig.tight_layout(); fig.savefig(OUT / "fig3a_gaps_fixed_evidence.pdf"); fig.savefig(OUT / "fig3a_gaps_fixed_evidence.png", dpi=300); plt.close(fig)

# 3b — per-domain, nine models, post-cutoff
TASKS_B = [("Binary (balanced acc.)", "binary", 0.5), ("MCQ accuracy", "mcq", 0.25), ("FRQ score (0–10)", "frq", None), ("Date score", "date_score", None)]
order = [r["name"] for r in sorted(rows, key=lambda r: r["cutoff"])]
fig, axes = plt.subplots(4, 1, figsize=(7.2, 8.2))
for ax, (title, key, chance) in zip(axes, TASKS_B):
    nm = len(order); w = 0.82 / nm; means = defaultdict(list)
    for j, m in enumerate(order):
        vals, errs = [], []
        for a in AREAS:
            d = area_data[m].get(a, {})
            if key == "binary":
                b, p = d.get("binary", []), d.get("binary_perturbed", [])
                if len(b) >= 10 and len(p) >= 10:
                    pb, pp = st.fmean(b), st.fmean(p); v = (pb + pp) / 2; e = 0.5 * math.sqrt(pb * (1 - pb) / len(b) + pp * (1 - pp) / len(p))
                else: v, e = np.nan, 0
            else:
                xs = d.get(key, [])
                v, e = (st.fmean(xs), st.stdev(xs) / math.sqrt(len(xs))) if len(xs) >= 10 else (np.nan, 0)
            vals.append(v); errs.append(e)
            if not np.isnan(v): means[a].append(v)
        ax.bar(np.arange(len(AREAS)) + (j - nm / 2 + 0.5) * w, vals, w * 0.9, yerr=errs, color=COLOR[m], error_kw=dict(lw=0.4, capsize=0.8),
               label=m + ("†" if m == "DeepSeek-R1" else ""))
    ax.plot(np.arange(len(AREAS)), [st.fmean(means[a]) if means[a] else np.nan for a in AREAS], "D", color="#222", ms=3.5, zorder=5, label="Cross-model mean")
    if chance is not None: ax.axhline(chance, color="#888", ls="--", lw=0.7, label="Chance")
    ax.set_xticks(np.arange(len(AREAS))); ax.set_xticklabels([AREA_SHORT[a] for a in AREAS], fontsize=6.5); ax.set_ylabel(title, fontsize=6.5)
    if key in ("binary", "mcq", "date_score"): ax.set_ylim(0, 1 if key != "binary" else 0.75)
axes[0].legend(ncol=6, fontsize=5.3, loc="upper center", bbox_to_anchor=(0.5, 1.32))
fig.text(0.005, 0.995, "b", fontsize=9, fontweight="bold", va="top")
fig.tight_layout(); fig.savefig(OUT / "fig3b_domain_9models.pdf"); fig.savefig(OUT / "fig3b_domain_9models.png", dpi=300); plt.close(fig)

cap = (r"% Figure 3 caption — revision version (new text in blue)" "\n"
       r"\caption{\textbf{Knowledge and forecasting gaps diverge across the knowledge cutoff.} \textbf{a}. Knowledge gaps (blue; WS+Cutoff $-$ Base) and forecasting gaps (red; WS $-$ WS+Cutoff) "
       r"across four task types on pre-cutoff (top) and post-cutoff (bottom) events"
       r"\textcolor{blue}{, measured with fixed evidence packets: one search query per event written by a model outside the evaluated panel, issued once per date ceiling, so every model receives identical retrieved evidence. "
       r"Binary pools original and perturbed items; FRQ in rubric points; error bars, s.e.m. of the paired difference; cells with fewer than 20 events are omitted, and GPT-4o and LLaMA 3.3 have no pre-cutoff events}. "
       r"Knowledge gaps dominate before the cutoff; after it the pattern inverts, with forecasting gaps largest for Temporal Prediction. "
       r"\textbf{b}. Per-domain \textcolor{blue}{post-cutoff} performance of \textcolor{blue}{nine} models across eight scientific fields for each task\textcolor{blue}{, on the full corpus to August 2026 (DeepSeek R1: corpus before March 2026 only)}; "
       r"diamonds, cross-model mean; dashed lines, chance. Error bars, s.e.m.}")
(OUT / "fig3_caption.tex").write_text(cap + "\n")
print("\nwrote", sorted(p.name for p in OUT.iterdir()))
print("3a cells:", {k: round(v['k'], 3) for k, v in gap.items() if k[2] == 'Temporal'})
