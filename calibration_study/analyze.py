"""
analyze.py — regenerate every table, figure and RESULTS.md of the A6 study from
stored JSONL / reports. No inference happens here.

  python calibration_study/analyze.py [--B 10000] [--seed 0] [--models llama33,deepseek_r1,gpt4o]

Outputs (calibration_study/):
  tables/master_table.json|md     model x arm x task x {all,pre,post} x metrics (+95% CI)
  tables/delta_vs_base.json|md    arm-vs-A paired deltas, bootstrap CI, raw + Holm p
  tables/ensemble.json|md         arm F, three aggregation rules, panel and all-model
  tables/vote_distributions.json  arm D MCQ full vote distributions
  tables/prob_sum_check.json      arm E MCQ raw-sum-to-one audit
  figures/reliability_*.png|pdf   faceted model x arm
  figures/hist_*.png|pdf          faceted model x arm
  tables/costs.json|md            token + cost accounting per arm (from raw JSONL usage)
  RESULTS.md
"""
from __future__ import annotations
import argparse, json, math, sys, collections
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
import metrics as M

PARTS = ["all", "pre", "post"]
METRIC_ORDER = ["n", "n_prob", "accuracy", "bias_index", "mean_p", "brier", "logloss", "logloss_laplace",
                "ece", "ece_q", "mce", "rel", "res", "unc", "resid", "auroc",
                "mean_conf", "brier_c", "logloss_c", "logloss_c_laplace", "ece_c", "mce_c", "rel_c", "res_c", "unc_c", "auroc_c",
                "logloss_true", "logloss_true_laplace"]
HIGHER_BETTER = {"accuracy", "res", "res_c", "auroc", "auroc_c"}
ARM_COLORS = {"A": "#000000", "B1": "#E69F00", "B2": "#56B4E9", "C": "#009E73", "D": "#CC79A7", "E": "#D55E00"}


# --------------------------------------------------------------------------- cells
def select(items, task, part):
    out = []
    for it in items:
        if task == "binary_merged" and it["task"] not in ("binary", "binary_perturbed"):
            continue
        if task != "binary_merged" and it["task"] != task:
            continue
        if part != "all" and it["partition"] != part:
            continue
        out.append(it)
    return out


def _arr(items, key):
    return np.array([it.get(key) for it in items], dtype=float)


def cell_metrics(items, task, counts, ev_idx, arm):
    """Point estimates + bootstrap arrays for one model x arm x task x partition cell."""
    res = {}
    n = len(items)
    res["n"] = (n, None)
    ans = [it for it in items if it.get("correct") is not None]
    if ans:
        w = counts[:, [ev_idx[it["id"]] for it in ans]]
        c = _arr(ans, "correct")
        res["accuracy"] = (float(c.mean()), M.accuracy(c, w))
        if task == "binary_merged":
            b = [it for it in ans if it["task"] == "binary"]; pz = [it for it in ans if it["task"] == "binary_perturbed"]
            if b and pz:
                cb, cp = _arr(b, "correct"), _arr(pz, "correct")
                wb, wp = counts[:, [ev_idx[i["id"]] for i in b]], counts[:, [ev_idx[i["id"]] for i in pz]]
                res["bias_index"] = (float(cb.mean() - cp.mean()), M.accuracy(cb, wb) - M.accuracy(cp, wp))
    # event-framed (binary tasks): P(Yes) vs outcome
    if task != "mcq":
        pr = [it for it in items if it.get("p_yes") is not None]
        res["n_prob"] = (len(pr), None)
        if len(pr) >= 20:
            p, y = _arr(pr, "p_yes"), _arr(pr, "y"); w = counts[:, [ev_idx[it["id"]] for it in pr]]
            res["mean_p"] = (float(p.mean()), M.wmean(p, w))
            res["brier"] = (float(M.brier(p, y)[0]), M.brier(p, y, w))
            res["logloss"] = (float(M.logloss(p, y)[0]), M.logloss(p, y, w))
            if arm == "D":
                pl = _arr(pr, "p_yes_laplace"); res["logloss_laplace"] = (float(M.logloss(pl, y, eps=0)[0]), M.logloss(pl, y, w, eps=0))
            res["ece"] = (float(M.ece(p, y)[0]), M.ece(p, y, w))
            qe = M.quantile_edges(p); res["ece_q"] = (float(M.ece(p, y, edges=qe)[0]), M.ece(p, y, w, edges=qe))
            res["mce"] = (float(M.mce(p, y)[0]), M.mce(p, y, w))
            mu0, mu = M.murphy(p, y), M.murphy(p, y, w)
            for k in ("rel", "res", "unc", "resid"):
                res[k] = (float(mu0[k][0]), mu[k])
            if 0 < y.sum() < len(y):
                res["auroc"] = (float(M.auroc(p, y)[0]), M.auroc(p, y, w))
    # answer-framed (all tasks): confidence in the given answer vs correctness
    cf = [it for it in ans if it.get("conf") is not None]
    if task == "mcq":
        res["n_prob"] = (len(cf), None)
    if len(cf) >= 20:
        p, y = _arr(cf, "conf"), _arr(cf, "correct"); w = counts[:, [ev_idx[it["id"]] for it in cf]]
        res["mean_conf"] = (float(p.mean()), M.wmean(p, w))
        res["brier_c"] = (float(M.brier(p, y)[0]), M.brier(p, y, w))
        res["logloss_c"] = (float(M.logloss(p, y)[0]), M.logloss(p, y, w))
        if arm == "D":
            pl = _arr(cf, "conf_laplace"); res["logloss_c_laplace"] = (float(M.logloss(pl, y, eps=0)[0]), M.logloss(pl, y, w, eps=0))
        res["ece_c"] = (float(M.ece(p, y)[0]), M.ece(p, y, w))
        res["mce_c"] = (float(M.mce(p, y)[0]), M.mce(p, y, w))
        mu0, mu = M.murphy(p, y), M.murphy(p, y, w)
        for k in ("rel", "res", "unc"):
            res[k + "_c"] = (float(mu0[k][0]), mu[k])
        if 0 < y.sum() < len(y):
            res["auroc_c"] = (float(M.auroc(p, y)[0]), M.auroc(p, y, w))
        if task == "mcq" and arm in ("D", "E"):
            pt = [it for it in cf if it.get("p_true") is not None]
            if len(pt) >= 20:
                p_t = _arr(pt, "p_true"); y1 = np.ones(len(pt)); w2 = counts[:, [ev_idx[it["id"]] for it in pt]]
                res["logloss_true"] = (float(M.logloss(p_t, y1)[0]), M.logloss(p_t, y1, w2))
                if arm == "D":
                    ptl = _arr(pt, "p_true_laplace"); res["logloss_true_laplace"] = (float(M.logloss(ptl, y1, eps=0)[0]), M.logloss(ptl, y1, w2, eps=0))
    return res


def paired_delta(itA, itX, task, metric, counts, ev_idx, armX):
    """Delta (X - A) of one metric on the intersection of valid items."""
    keyA = {(it["id"], it["task"]): it for it in itA}
    pairs = [(keyA[(it["id"], it["task"])], it) for it in itX if (it["id"], it["task"]) in keyA]
    if metric in ("accuracy", "bias_index"):
        pairs = [(a, x) for a, x in pairs if a.get("correct") is not None and x.get("correct") is not None]
    elif metric.endswith("_c") or metric in ("mean_conf",):
        pairs = [(a, x) for a, x in pairs if a.get("conf") is not None and x.get("conf") is not None and a.get("correct") is not None and x.get("correct") is not None]
    elif metric in ("logloss_true",):
        return None
    else:
        pairs = [(a, x) for a, x in pairs if a.get("p_yes") is not None and x.get("p_yes") is not None]
    if len(pairs) < 20:
        return None
    A = [a for a, _ in pairs]; X = [x for _, x in pairs]
    mA = cell_metrics(A, task, counts, ev_idx, "A"); mX = cell_metrics(X, task, counts, ev_idx, armX)
    if metric not in mA or metric not in mX or mA[metric][1] is None:
        return None
    d0 = mX[metric][0] - mA[metric][0]; d = mX[metric][1] - mA[metric][1]
    lo, hi = M.ci(d)
    return dict(delta=d0, ci=[lo, hi], p=M.boot_p(d), n_paired=len(pairs), base=mA[metric][0], arm=mX[metric][0])


# --------------------------------------------------------------------------- ensemble
def _logit(p):
    p = np.clip(p, M.EPS, 1 - M.EPS); return np.log(p / (1 - p))


def ensemble_items(data, members, task):
    """Build arm-F items from the members' arm-A items (binary: P(Yes); MCQ: conf-on-chosen)."""
    per = {m: {(it["id"], it["task"]): it for it in select(data[(m, "A")], task, "all")} for m in members}
    keys = set.intersection(*(set(d) for d in per.values()))
    rules = {"mean_prob": [], "mean_logit": [], "majority": []}
    for key in sorted(keys):
        its = [per[m][key] for m in members]
        base = {k: its[0][k] for k in ("id", "task", "partition")}
        if task != "mcq":
            if any(it.get("p_yes") is None for it in its):
                continue
            ps = np.array([it["p_yes"] for it in its]); y = its[0]["y"]
            for rule, p in (("mean_prob", ps.mean()), ("mean_logit", 1 / (1 + np.exp(-_logit(ps).mean()))),
                            ("majority", (ps >= 0.5).mean())):
                ans = "yes" if p >= 0.5 else "no"
                rules[rule].append(dict(base, arm="F", answer=ans, correct=(ans == ("yes" if y == 1 else "no")),
                                        p_yes=float(p), y=y, conf=float(p if ans == "yes" else 1 - p)))
        else:
            if any(it.get("answer") is None or it.get("conf") is None for it in its):
                continue
            gt = None
            dists = []
            for it in its:
                d = {L: (1 - it["conf"]) / 3 for L in "ABCD"}; d[it["answer"]] = it["conf"]; dists.append(d)
                if it["correct"]:
                    gt = it["answer"]
            if gt is None:  # nobody right: true letter unknown from A alone -> use majority-wrong flag
                pass
            D = {L: np.array([d[L] for d in dists]) for L in "ABCD"}
            for rule in rules:
                if rule == "mean_prob":
                    agg = {L: float(D[L].mean()) for L in "ABCD"}
                elif rule == "mean_logit":
                    agg = {L: float(np.exp(_logit(D[L]).mean())) for L in "ABCD"}; s = sum(agg.values()); agg = {L: v / s for L, v in agg.items()}
                else:
                    votes = collections.Counter(it["answer"] for it in its)
                    agg = {L: votes.get(L, 0) / len(its) for L in "ABCD"}
                ans = max(agg, key=lambda L: (agg[L], sum(it["conf"] for it in its if it["answer"] == L)))
                correct = (ans == gt) if gt is not None else False
                rules[rule].append(dict(base, arm="F", answer=ans, correct=correct, conf=float(agg[ans]), dist=agg))
    return rules


# --------------------------------------------------------------------------- figures
def fig_reliability(data, models, arms, task, framed, out):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    rows, cols = len(models), len(arms)
    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 2.1 * rows), squeeze=False, sharex=True, sharey=True)
    for r, m in enumerate(models):
        for c, arm in enumerate(arms):
            ax = axes[r][c]; ax.plot([0, 1], [0, 1], color="#BBBBBB", lw=1, ls="--", zorder=1)
            its = data.get((m, arm))
            if its is None:
                ax.text(0.5, 0.5, "not run", ha="center", va="center", fontsize=7, color="#888888")
            else:
                its = select(its, task, "all")
                if framed == "event":
                    its = [it for it in its if it.get("p_yes") is not None]; p, y = _arr(its, "p_yes"), _arr(its, "y")
                else:
                    its = [it for it in its if it.get("conf") is not None and it.get("correct") is not None]; p, y = _arr(its, "conf"), _arr(its, "correct")
                if len(p) >= 20:
                    b = M.bin_index(p); xs, ys, ns = [], [], []
                    for k in range(M.NBINS):
                        sel = b == k
                        if sel.sum() >= 5:
                            xs.append(p[sel].mean()); ys.append(y[sel].mean()); ns.append(sel.sum())
                    ax.plot(xs, ys, "-o", color=ARM_COLORS[arm], lw=1.5, ms=4, zorder=3)
                    for x_, y_, n_ in zip(xs, ys, ns):
                        ax.annotate(str(n_), (x_, y_), textcoords="offset points", xytext=(0, 5), ha="center", fontsize=5, color="#555555")
                    e = float(M.ece(p, y)[0]); bs = float(M.brier(p, y)[0])
                    ax.text(0.03, 0.93, f"ECE {e:.3f}\nBrier {bs:.3f}\nn={len(p)}", fontsize=6, va="top", transform=ax.transAxes)
            ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xticks([0, .5, 1]); ax.set_yticks([0, .5, 1]); ax.tick_params(labelsize=6)
            ax.grid(color="#EEEEEE", lw=0.5)
            if r == 0: ax.set_title(C.ARM_LABEL[arm], fontsize=7)
            if c == 0: ax.set_ylabel(C.MODELS[m]["name"] + ("\nobserved P(Yes)" if framed == "event" else "\nobserved accuracy"), fontsize=7)
            if r == rows - 1: ax.set_xlabel("forecast P(Yes)" if framed == "event" else "reported confidence", fontsize=7)
    ttl = {"event": "Binary (original + perturbed): P(event occurs) vs outcome", "answer": f"{task}: confidence in given answer vs correctness"}[framed]
    fig.suptitle(ttl + "  —  10 equal-width bins, bins with n<5 hidden, labels = bin counts", fontsize=8)
    fig.tight_layout(); fig.savefig(str(out) + ".png", dpi=200); fig.savefig(str(out) + ".pdf"); plt.close(fig)


def fig_hist(data, models, arms, task, framed, out):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    rows, cols = len(models), len(arms)
    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.8 * rows), squeeze=False, sharex=True)
    edges = np.linspace(0, 1, 21)
    for r, m in enumerate(models):
        for c, arm in enumerate(arms):
            ax = axes[r][c]; its = data.get((m, arm))
            if its is None:
                ax.text(0.5, 0.5, "not run", ha="center", va="center", fontsize=7, color="#888888", transform=ax.transAxes)
            else:
                its = select(its, task, "all"); key = "p_yes" if framed == "event" else "conf"
                v = _arr([it for it in its if it.get(key) is not None], key)
                if len(v):
                    ax.hist(v, bins=edges, color=ARM_COLORS[arm], alpha=0.85, edgecolor="white", lw=0.5)
                    top = collections.Counter(np.round(v, 2)).most_common(3)
                    ax.text(0.03, 0.93, f"n={len(v)}, {len(set(np.round(v, 2)))} distinct\ntop: " + ", ".join(f"{k:g} ({n / len(v):.0%})" for k, n in top),
                            fontsize=5.5, va="top", transform=ax.transAxes)
            ax.set_xlim(0, 1); ax.tick_params(labelsize=6); ax.set_yticks([])
            if r == 0: ax.set_title(C.ARM_LABEL[arm], fontsize=7)
            if c == 0: ax.set_ylabel(C.MODELS[m]["name"], fontsize=7)
            if r == rows - 1: ax.set_xlabel("P(Yes)" if framed == "event" else "reported confidence / derived prob.", fontsize=7)
    fig.suptitle(f"{task}: distribution of {'P(Yes)' if framed == 'event' else 'reported confidence'} per model x arm (0.05-wide bins)", fontsize=8)
    fig.tight_layout(); fig.savefig(str(out) + ".png", dpi=200); fig.savefig(str(out) + ".pdf"); plt.close(fig)


# --------------------------------------------------------------------------- rendering
def f3(v):
    return "—" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.3f}"


def render_master(master, models, arms):
    L = ["# Master table — model × arm × task × partition",
         "", f"Partition rule: {C.PARTITION_RULE}. 95% CIs from 10k event-level bootstrap resamples.",
         "Event-framed columns (mean_p, brier, logloss, ece, ece_q, mce, rel/res/unc/resid, auroc) score P(Yes) against the event outcome",
         "(original question = 1, perturbed = 0). `_c` columns score the reported confidence against answer correctness (the paper's S14 convention).",
         "ECE/MCE/Murphy use 10 equal-width bins; ece_q uses 10 equal-mass bins; MCE over bins with n≥10; log loss clips to [0.01, 0.99]; arm D `_laplace` = (k+1)/(n+2).",
         "Arm D n per model: " + ", ".join(f"{C.MODELS[m]['name']} n={C.MODELS[m]['n_sc']}" for m in models) + ".", ""]
    cols = ["n", "n_prob", "accuracy", "bias_index", "mean_p", "brier", "logloss", "logloss_laplace", "ece", "ece_q", "mce", "rel", "res", "unc", "auroc",
            "mean_conf", "brier_c", "logloss_c", "ece_c", "mce_c", "rel_c", "res_c", "auroc_c", "logloss_true"]
    for m in models:
        L.append(f"\n## {C.MODELS[m]['name']}  (cutoff {C.MODELS[m]['cutoff']}, S13 bias index {C.MODELS[m]['bias_s13']:+.3f})\n")
        L.append("| task | part | arm | " + " | ".join(cols) + " |")
        L.append("|" + "---|" * (len(cols) + 3))
        for task in C.TASKS:
            for part in PARTS:
                for arm in arms:
                    cellv = master.get(m, {}).get(arm, {}).get(task, {}).get(part)
                    if not cellv or cellv.get("n", {}).get("value", 0) == 0:
                        continue
                    row = []
                    for k in cols:
                        v = cellv.get(k)
                        if v is None:
                            row.append("—")
                        elif k in ("n", "n_prob"):
                            row.append(str(int(v["value"])))
                        else:
                            row.append(f"{v['value']:.3f} [{v['ci'][0]:.3f}, {v['ci'][1]:.3f}]" if v.get("ci") else f3(v["value"]))
                    L.append(f"| {task} | {part} | {arm} | " + " | ".join(row) + " |")
    return "\n".join(L) + "\n"


def render_delta(delta, models):
    L = ["# Arm-vs-base paired deltas (arm − A)", "",
         "Paired on the intersection of items valid in both arms; 10k event-level bootstrap resamples shared across arms;",
         "two-sided percentile-bootstrap p; Holm–Bonferroni across the intervention arms within each model × task × partition × metric family.",
         "Never read a delta without its CI. `*` marks Holm-adjusted p < 0.05.", ""]
    keymetrics = ["accuracy", "bias_index", "brier", "logloss", "ece", "rel", "res", "auroc", "brier_c", "ece_c", "auroc_c"]
    for m in models:
        L.append(f"\n## {C.MODELS[m]['name']}\n")
        L.append("| task | part | metric | " + " | ".join(f"{a}" for a in C.ARMS if a != "A") + " |")
        L.append("|" + "---|" * (3 + len(C.ARMS) - 1))
        for task in C.TASKS:
            for part in PARTS:
                for met in keymetrics:
                    cells = []
                    any_ = False
                    for arm in C.ARMS:
                        if arm == "A":
                            continue
                        d = delta.get(m, {}).get(arm, {}).get(task, {}).get(part, {}).get(met)
                        if not d:
                            cells.append("—"); continue
                        any_ = True
                        star = "*" if (d.get("p_holm") is not None and d["p_holm"] == d["p_holm"] and d["p_holm"] < 0.05) else ""
                        cells.append(f"{d['delta']:+.3f} [{d['ci'][0]:+.3f}, {d['ci'][1]:+.3f}] p={d['p']:.3g}/{d['p_holm']:.3g}{star} n={d['n_paired']}")
                    if any_:
                        L.append(f"| {task} | {part} | {met} | " + " | ".join(cells) + " |")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--models", default=",".join(C.PANEL))
    ap.add_argument("--extra-models", default="deepseek_r1,gptoss20b", help="reference rows in the master table only")
    a = ap.parse_args()
    models = a.models.split(",")
    extra = [m for m in a.extra_models.split(",") if m]
    subset = C.load_subset(); ev_idx = {i: k for k, i in enumerate(subset)}
    counts = M.boot_counts(len(subset), a.B, a.seed)
    data = C.load_all(models=list(dict.fromkeys(models + extra + list(C.MODELS))))

    # ---- master table
    master = {}
    for (m, arm), items in data.items():
        if m not in models + extra:
            continue
        for task in C.TASKS:
            for part in PARTS:
                its = select(items, task, part)
                if not its:
                    continue
                cm = cell_metrics(its, task, counts, ev_idx, arm)
                out = {}
                for k, (v, boot) in cm.items():
                    out[k] = {"value": v}
                    if boot is not None:
                        lo, hi = M.ci(boot); out[k]["ci"] = [lo, hi]
                master.setdefault(m, {}).setdefault(arm, {}).setdefault(task, {})[part] = out
        print(f"  master: {m} {arm}", file=sys.stderr)
    meta = dict(partition_rule=C.PARTITION_RULE, bootstrap=dict(B=a.B, seed=a.seed, unit="event (cluster)"),
                bins="10 equal-width; ece_q 10 equal-mass; MCE bins n>=10", logloss_clip=M.EPS,
                n_self_consistency={m: C.MODELS[m]["n_sc"] for m in models},
                arms_present={m: sorted(arm for (mm, arm) in data if mm == m) for m in models + extra})
    json.dump({"meta": meta, "cells": master}, open(C.TABLES / "master_table.json", "w"), indent=1)
    open(C.TABLES / "master_table.md", "w").write(render_master(master, models + extra, C.ARMS))

    # ---- deltas vs base
    delta = {}
    for m in models + extra:
        if (m, "A") not in data:
            continue
        for arm in C.ARMS:
            if arm == "A" or (m, arm) not in data:
                continue
            for task in C.TASKS:
                for part in PARTS:
                    itA, itX = select(data[(m, "A")], task, part), select(data[(m, arm)], task, part)
                    if not itA or not itX:
                        continue
                    for met in [k for k in METRIC_ORDER if k not in ("n", "n_prob", "logloss_laplace", "logloss_c_laplace", "logloss_true", "logloss_true_laplace")]:
                        if task == "mcq" and not (met in ("accuracy", "mean_conf") or met.endswith("_c")):
                            continue
                        if task in ("binary", "binary_perturbed") and met in ("bias_index", "auroc", "res", "rel", "unc", "resid"):
                            continue
                        d = paired_delta(itA, itX, task, met, counts, ev_idx, arm)
                        if d:
                            delta.setdefault(m, {}).setdefault(arm, {}).setdefault(task, {}).setdefault(part, {})[met] = d
            print(f"  delta: {m} {arm}", file=sys.stderr)
    # Holm within (model, task, part, metric) across arms
    for m in delta:
        fams = collections.defaultdict(list)
        for arm in delta[m]:
            for task in delta[m][arm]:
                for part in delta[m][arm][task]:
                    for met in delta[m][arm][task][part]:
                        fams[(task, part, met)].append(arm)
        for (task, part, met), arms_ in fams.items():
            ps = [delta[m][arm][task][part][met]["p"] for arm in arms_]
            for arm, ph in zip(arms_, M.holm(ps)):
                delta[m][arm][task][part][met]["p_holm"] = ph
    json.dump({"meta": dict(meta, correction="Holm-Bonferroni across arms within model x task x partition x metric"), "deltas": delta},
              open(C.TABLES / "delta_vs_base.json", "w"), indent=1)
    open(C.TABLES / "delta_vs_base.md", "w").write(render_delta(delta, models + extra))

    # ---- ensemble (arm F, derived from A)
    ens = {"note": "Arm F is derived from arm A outputs, not independent of it. Rules: mean of P(Yes); mean of logits "
                   "(P clipped to [0.01,0.99]); unweighted majority vote (probability = fraction of members voting Yes). "
                   "MCQ members contribute conf on their chosen option and (1-conf)/3 elsewhere.", "panels": {}}
    allm = [m for m in C.MODELS if (m, "A") in data]
    L = ["# Arm F — ensembles (derived from arm A; not independent of it)", "", ens["note"], ""]
    for pname, members in (("panel3", models), ("all_models", allm)):
        ens["panels"][pname] = {"members": members, "tasks": {}}
        for task in ("binary_merged", "mcq"):
            rules = ensemble_items(data, members, task)
            ens["panels"][pname]["tasks"][task] = {}
            for rule, items in rules.items():
                if not items:
                    continue
                per_part = {}
                for part in PARTS:
                    its = select(items, task, part)
                    if not its:
                        continue
                    cm = cell_metrics(its, task, counts, ev_idx, "F")
                    out = {k: {"value": v, **({"ci": list(M.ci(b))} if b is not None else {})} for k, (v, b) in cm.items()}
                    # deltas vs each member's base on the same items
                    out["delta_vs_member_base"] = {}
                    for mem in members:
                        itA = select(data[(mem, "A")], task, part)
                        dd = {}
                        for met in (["accuracy", "bias_index", "brier", "logloss", "ece", "rel", "res", "auroc"] if task != "mcq" else ["accuracy", "brier_c", "ece_c", "auroc_c"]):
                            d = paired_delta(itA, its, task, met, counts, ev_idx, "F")
                            if d: dd[met] = d
                        out["delta_vs_member_base"][mem] = dd
                    per_part[part] = out
                ens["panels"][pname]["tasks"][task][rule] = per_part
                L.append(f"\n## {pname} ({', '.join(C.MODELS[x]['name'] for x in members)}) — {task} — rule: {rule}\n")
                keys = ["n", "n_prob", "accuracy", "bias_index", "brier", "logloss", "ece", "rel", "res", "unc", "auroc"] if task != "mcq" else ["n", "n_prob", "accuracy", "brier_c", "ece_c", "auroc_c"]
                L.append("| part | " + " | ".join(keys) + " |"); L.append("|" + "---|" * (len(keys) + 1))
                for part, out in per_part.items():
                    L.append(f"| {part} | " + " | ".join((str(int(out[k]['value'])) if k in ('n', 'n_prob') else (f"{out[k]['value']:.3f} [{out[k]['ci'][0]:.3f}, {out[k]['ci'][1]:.3f}]" if 'ci' in out[k] else f3(out[k]['value']))) if k in out else "—" for k in keys) + " |")
                L.append("\nΔ vs each member's base (same items):\n")
                for part, out in per_part.items():
                    for mem, dd in out["delta_vs_member_base"].items():
                        L.append(f"- {part} vs {C.MODELS[mem]['name']}: " + "; ".join(f"{k} {v['delta']:+.3f} [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}] p={v['p']:.3g}" for k, v in dd.items()) + f" (n={next(iter(dd.values()))['n_paired'] if dd else 0})")
        print(f"  ensemble: {pname}", file=sys.stderr)
    json.dump(ens, open(C.TABLES / "ensemble.json", "w"), indent=1)
    open(C.TABLES / "ensemble.md", "w").write("\n".join(L) + "\n")

    # ---- arm D vote distributions and arm E sum-to-one audit
    vd = {}
    for m in models:
        if (m, "D") in data:
            vd[m] = {"n": C.MODELS[m]["n_sc"], "mcq": [{k: it[k] for k in ("id", "partition", "votes", "answer", "correct")} for it in data[(m, "D")] if it["task"] == "mcq" and it.get("votes")],
                     "binary": [{k: it[k] for k in ("id", "task", "partition", "votes", "answer", "correct")} for it in data[(m, "D")] if it["task"] != "mcq" and it.get("votes")]}
    json.dump(vd, open(C.TABLES / "vote_distributions.json", "w"), indent=1)
    audit = {}
    for m in models:
        if (m, "E") in data:
            sums = [it["raw_sum"] for it in data[(m, "E")] if it["task"] == "mcq" and it.get("raw_sum") is not None]
            if sums:
                s = np.array(sums, float); off = np.abs(s - 1)
                audit[m] = dict(n=len(s), frac_not_within_0_01=float((off > 0.01).mean()), frac_not_within_0_05=float((off > 0.05).mean()),
                                mean_abs_dev=float(off.mean()), max_abs_dev=float(off.max()), mean_sum=float(s.mean()),
                                hist={"<0.9": int((s < 0.9).sum()), "0.9-0.99": int(((s >= 0.9) & (s < 0.99)).sum()), "0.99-1.01": int(((s >= 0.99) & (s <= 1.01)).sum()), "1.01-1.1": int(((s > 1.01) & (s <= 1.1)).sum()), ">1.1": int((s > 1.1).sum())})
    json.dump(audit, open(C.TABLES / "prob_sum_check.json", "w"), indent=1)

    # ---- figures
    figm = models + extra
    fig_reliability(data, figm, C.ARMS, "binary_merged", "event", C.FIGS / "reliability_binary_event")
    fig_reliability(data, figm, C.ARMS, "binary_merged", "answer", C.FIGS / "reliability_binary_answer")
    fig_reliability(data, figm, C.ARMS, "mcq", "answer", C.FIGS / "reliability_mcq")
    fig_hist(data, figm, C.ARMS, "binary_merged", "answer", C.FIGS / "hist_binary_confidence")
    fig_hist(data, figm, C.ARMS, "binary_merged", "event", C.FIGS / "hist_binary_pyes")
    fig_hist(data, figm, C.ARMS, "mcq", "answer", C.FIGS / "hist_mcq_confidence")
    print("figures written", file=sys.stderr)

    # ---- costs (actual, from raw JSONL usage)
    costs = {}
    prices = json.load(open(C.STUDY / "prices.json")) if (C.STUDY / "prices.json").exists() else {}
    for p in sorted(C.RAW.glob("*.jsonl")):
        m, arm = p.stem.rsplit("_", 1)
        tin = tout = calls = 0; n_rec = 0
        for l in open(p):
            if not l.strip(): continue
            r = json.loads(l); n_rec += 1
            tin += r.get("input_tokens") or 0; tout += r.get("output_tokens") or 0; calls += r.get("n_calls") or 1
        pr = prices.get(C.MODELS[m]["deploy"] or m, {})
        usd = (tin * pr.get("input_per_m", 0) + tout * pr.get("output_per_m", 0)) / 1e6 if pr else None
        costs[f"{m}_{arm}"] = dict(records=n_rec, calls=calls, input_tokens=tin, output_tokens=tout, usd=usd, price=pr or "not set")
    json.dump(costs, open(C.TABLES / "costs.json", "w"), indent=1)
    with open(C.TABLES / "costs.md", "w") as f:
        f.write("# Token and cost accounting (actual, from raw JSONL usage fields)\n\nArms A and C reused stored outputs: zero new inference. Arm F is derived: zero inference.\n\n| run | records | calls | input tokens | output tokens | USD (list price) |\n|---|---|---|---|---|---|\n")
        for k, v in costs.items():
            f.write(f"| {k} | {v['records']} | {v['calls']} | {v['input_tokens']:,} | {v['output_tokens']:,} | {('$%.2f' % v['usd']) if v['usd'] is not None else 'price not set'} |\n")
    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
