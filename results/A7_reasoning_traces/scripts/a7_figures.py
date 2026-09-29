"""a7_figures.py — figures for the analyses. Regenerated from the stored analysis outputs."""
from __future__ import annotations
import json, re, sys, collections
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_stats as S

FIG = C.STUDY / "figures"; FIG.mkdir(exist_ok=True)
AG = json.load(open(C.STUDY / "agreement.json"))
BJ = json.load(open(C.STUDY / "analyses" / "B_code_outcome" / "results.json"))
CJ = json.load(open(C.STUDY / "analyses" / "C_delayed_dates" / "results.json"))
rel = set(AG["reliable_codes"])
BLUE, RED, GREY = "#1f77b4", "#d62728", "#7f7f7f"

rows, _ = S.load_labels()
by = collections.defaultdict(list)
for r in rows: by[r["code"]].append(r)
codes = [r["code"] for r in AG["rows"] if r["code"] != "HEDGING"]

# ---- 1. prevalence heatmap by task
M = np.full((len(codes), len(C.TASKS)), np.nan)
for i, c in enumerate(codes):
    for j, t in enumerate(C.TASKS):
        sel = [r["label"] for r in by[c] if r["task"] == t and r["condition"] == "base"]
        if sel: M[i, j] = 100 * np.mean(sel)
fig, ax = plt.subplots(figsize=(7.2, 6.4))
im = ax.imshow(M, cmap="Blues", vmin=0, vmax=np.nanmax(M), aspect="auto")
ax.set_xticks(range(len(C.TASKS))); ax.set_xticklabels(C.TASKS, rotation=30, ha="right", fontsize=9)
ax.set_yticks(range(len(codes)))
ax.set_yticklabels([c + ("" if c in rel else "  (not reliable)") for c in codes], fontsize=8)
for i in range(len(codes)):
    for j in range(len(C.TASKS)):
        if np.isfinite(M[i, j]):
            ax.text(j, i, f"{M[i,j]:.0f}", ha="center", va="center", fontsize=7,
                    color="white" if M[i, j] > 0.6 * np.nanmax(M) else "#333")
ax.set_title("Prevalence of each stated-reasoning code, base condition (%)", fontsize=10)
fig.colorbar(im, ax=ax, fraction=0.03, label="% of traces")
fig.tight_layout(); fig.savefig(FIG / "A_prevalence_heatmap.png", dpi=150); plt.close(fig)

# ---- 2. delayed dates: effect on signed error
cs = [r for r in CJ if np.isfinite(r.get("beta", np.nan))]
cs.sort(key=lambda r: r["beta"])
fig, ax = plt.subplots(figsize=(7.4, 3.6))
y = np.arange(len(cs))
col = [RED if r["focal"] else GREY for r in cs]
ax.barh(y, [r["beta"] for r in cs], xerr=[[r["beta"] - r["lo"] for r in cs], [r["hi"] - r["beta"] for r in cs]],
        color=col, alpha=0.85, capsize=3, height=0.6)
ax.axvline(0, color="#333", lw=1)
ax.set_yticks(y); ax.set_yticklabels([r["code"] + ("*" if r["focal"] else "") for r in cs], fontsize=9)
ax.set_xlabel("extra lateness in months, holding the event fixed")
ax.set_title("Temporal task: which stated moves accompany a late prediction\n(* = named in the delayed-date hypothesis)", fontsize=10)
ax.grid(axis="x", alpha=0.25)
fig.tight_layout(); fig.savefig(FIG / "C_date_error_by_code.png", dpi=150); plt.close(fig)

# ---- 3. bias versus discrimination on the binary task
dirn = {c: (d, g) for c, d, g in BJ["direction"]}
mg = {r["code"]: r for r in BJ["fits"] if r["scope"] == "pooled" and r["task"] == "binary_merged"}
ks = [c for c in dirn if c in mg]
fig, ax = plt.subplots(figsize=(7.2, 4.2))
xb = [dirn[c][1]["beta"] for c in ks]; yb = [mg[c]["beta"] for c in ks]
xe = [[dirn[c][1]["beta"] - dirn[c][1]["lo"] for c in ks], [dirn[c][1]["hi"] - dirn[c][1]["beta"] for c in ks]]
ye = [[mg[c]["beta"] - mg[c]["lo"] for c in ks], [mg[c]["hi"] - mg[c]["beta"] for c in ks]]
ax.errorbar(xb, yb, xerr=xe, yerr=ye, fmt="o", color=BLUE, ms=6, lw=1, capsize=2)
for c, x, yy in zip(ks, xb, yb):
    ax.annotate(c, (x, yy), xytext=(6, 5), textcoords="offset points", fontsize=8)
ax.axhline(0, color="#333", lw=1); ax.axvline(0, color="#333", lw=1)
ax.set_xlabel("effect on P(answer Yes), log-odds  ->  response bias")
ax.set_ylabel("effect on merged binary accuracy, log-odds\n->  discrimination")
ax.set_title("Most stated moves shift the answer, not the chance of being right", fontsize=10)
ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(FIG / "B_bias_vs_discrimination.png", dpi=150); plt.close(fig)

# ---- 4. response bias: two models' strategies
YES, NO = "LLaMA 3.3 70B", "GPT-OSS 20B"
ks2 = [c for c in codes if c in rel]
va = [100 * np.mean([r["label"] for r in by[c] if r["model"] == YES and r["task"] in ("binary", "binary_perturbed") and r["condition"] == "base"] or [np.nan]) for c in ks2]
vb = [100 * np.mean([r["label"] for r in by[c] if r["model"] == NO and r["task"] in ("binary", "binary_perturbed") and r["condition"] == "base"] or [np.nan]) for c in ks2]
fig, ax = plt.subplots(figsize=(7.2, 3.8))
y = np.arange(len(ks2))
ax.barh(y - 0.2, va, height=0.38, color=BLUE, label=f"{YES} (yes-biased)")
ax.barh(y + 0.2, vb, height=0.38, color=RED, label=f"{NO} (no-biased)")
ax.set_yticks(y); ax.set_yticklabels(ks2, fontsize=8); ax.invert_yaxis()
ax.set_xlabel("% of binary justifications"); ax.legend(fontsize=8, frameon=False)
ax.set_title("The two extremes of response bias reason in almost disjoint ways", fontsize=10)
ax.grid(axis="x", alpha=0.25)
fig.tight_layout(); fig.savefig(FIG / "E_response_bias.png", dpi=150); plt.close(fig)

# ---- 5. cross-condition shift on matched triples
t2 = collections.defaultdict(lambda: collections.defaultdict(dict))
for c in ks2:
    for r in by[c]: t2[c][(r["model"], r["task"], r["id"])][r["condition"]] = r["label"]
fig, ax = plt.subplots(figsize=(7.2, 4.0))
conds = ["base", "ws_cutoff", "ws"]
for c in ks2:
    f2 = {k: v for k, v in t2[c].items() if set(conds) <= set(v)}
    if len(f2) < 100: continue
    v = [100 * np.mean([x[cd] for x in f2.values()]) for cd in conds]
    ax.plot(range(3), v, "-o", ms=5, lw=1.6, label=c)
    ax.annotate(c, (2, v[2]), xytext=(5, 0), textcoords="offset points", fontsize=7, va="center")
ax.set_xticks(range(3)); ax.set_xticklabels(["base", "WS+Cutoff", "WS (unrestricted)"])
ax.set_ylabel("% of traces"); ax.set_xlim(-0.2, 2.9)
ax.set_title("Retrieval displaces generic momentum reasoning with evidence and recognition\n(matched triples: same model, task and event)", fontsize=10)
ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(FIG / "F_condition_shift.png", dpi=150); plt.close(fig)

# ---- 6. agreement
ar = [r for r in AG["rows"]]
ar.sort(key=lambda r: r["kappa"])
fig, ax = plt.subplots(figsize=(7.0, 4.4))
y = np.arange(len(ar))
ax.barh(y, [r["kappa"] for r in ar], xerr=[[r["kappa"] - r["lo"] for r in ar], [r["hi"] - r["kappa"] for r in ar]],
        color=[BLUE if r["reliable"] else GREY for r in ar], capsize=2, height=0.62)
ax.axvline(AG["kappa_min"], color=RED, ls="--", lw=1.2, label=f"pre-registered threshold {AG['kappa_min']}")
ax.set_yticks(y); ax.set_yticklabels([r["code"] for r in ar], fontsize=8)
ax.set_xlabel("Cohen's kappa between the two blind coders"); ax.legend(fontsize=8, frameon=False, loc="lower right")
ax.set_title("Inter-coder agreement gates which codes enter the analyses", fontsize=10)
ax.grid(axis="x", alpha=0.25)
fig.tight_layout(); fig.savefig(FIG / "agreement_kappa.png", dpi=150); plt.close(fig)
print("6 figures written to", FIG)
