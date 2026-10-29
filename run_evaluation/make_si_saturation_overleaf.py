#!/usr/bin/env python3
"""make_si_saturation_overleaf.py - SI Figure fig:saturation on the full corpus.
External benchmark scores (MMLU-Pro, GPQA Diamond, MedQA) are those of the submitted figure (Figures/saturation.pdf):
read from its raster bars (19.1 px per point at render scale 4) and corrected by +0.3 points, the offset that maps the
read CUSP bars onto their exactly recomputed submitted values (38.8, 51.6, 46.9, 44.5, 43.4).
CUSP score = mean of Binary balanced accuracy, MCQ accuracy, FRQ/10 and date score over ALL events of the full corpus
(submitted: pooled binary accuracy, original corpus). Output: manuscript_updates/saturation_rev.png"""
import json, statistics as st, sys
from pathlib import Path
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "run_evaluation")); import make_table1_overleaf as T
ICONS = Path(sys.argv[1]) if len(sys.argv) > 1 else None
EXT = {  # model: (MMLU-Pro, GPQA Diamond, MedQA)  read from the submitted figure (+0.3)
    "GPT-4o": (80.6, 54.6, 88.3), "GPT-5.4": (87.8, 87.4, 96.3), "Claude S4.5": (86.2, 73.0, 95.0),
    "DeepSeek R1": (84.6, 71.1, 91.0), "LLaMA 3.3": (71.6, 50.0, 91.2)}
LABEL = {"GPT-4o": "GPT-4o", "GPT-5.4": "GPT-5.4", "Claude S4.5": "Claude Sonnet 4.5", "DeepSeek R1": "DeepSeek-R1", "LLaMA 3.3": "Llama 3.3 70B"}
ICON = {m[0]: m[2] for m in T.MODELS}
def cusp(name):
    _, cut, icon, op, ep, new = [m for m in T.MODELS if m[0] == name][0]
    seen, c = set(), {"binary": [], "binary_perturbed": [], "mcq": []}; frq, date = [], []
    for p in [op] + ([ep] if ep else []):
        for r in json.load(open(ROOT / p))["results"]:
            if r["id"] in seen: continue
            seen.add(r["id"]); t = r["tasks"]
            for k in c:
                if t.get(k) and "correct" in t[k]: c[k].append(1.0 if t[k]["correct"] else 0.0)
            if t.get("frq") and t["frq"].get("score") is not None: frq.append(t["frq"]["score"] / 10)
            if t.get("date") and t["date"].get("score") is not None: date.append(t["date"]["score"])
    bal = (st.fmean(c["binary"]) + st.fmean(c["binary_perturbed"])) / 2
    return 100 * st.fmean([bal, st.fmean(c["mcq"]), st.fmean(frq), st.fmean(date)])
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(12, 6.5), dpi=200)
cols = ["#6BA3C7", "#7FAF8E", "#D8B365", "#5B3F8C"]; names = ["MMLU-Pro", "GPQA Diamond", "MedQA", "CUSP (full corpus)"]
models = list(EXT); w = 0.19; x = np.arange(len(models))
vals = {m: list(EXT[m]) + [cusp(m)] for m in models}
for j in range(4):
    ax.bar(x + (j - 1.5) * w, [vals[m][j] for m in models], w, color=cols[j], edgecolor="black", linewidth=1.6 if j == 3 else 0.6, label=names[j])
for i, m in enumerate(models): ax.text(x[i] + 1.5 * w, vals[m][3] + 1, f"{vals[m][3]:.1f}", ha="center", fontsize=9, color="#3a2560")
ax.set_ylim(0, 100); ax.set_ylabel("Benchmark score", fontsize=13); ax.set_xticks(x); ax.set_xticklabels([LABEL[m] for m in models], fontsize=12, fontweight="bold", rotation=0)
ax.grid(axis="y", alpha=0.25); ax.legend(frameon=False, fontsize=11, loc="upper left", bbox_to_anchor=(1.0, 1.0))
if ICONS:
    for i, m in enumerate(models):
        try:
            im = plt.imread(str(ICONS / ICON[m])); ab = AnnotationBbox(OffsetImage(im, zoom=40 / max(im.shape[:2])), (x[i], -7), xycoords=("data", "data"), frameon=False, annotation_clip=False); ax.add_artist(ab)
        except Exception as e: print("icon", m, e)
    ax.tick_params(axis="x", pad=58)
fig.tight_layout(); fig.savefig(ROOT / "manuscript_updates/saturation_rev.png", bbox_inches="tight")
for m in models: print(m, [round(v, 1) for v in vals[m]])
