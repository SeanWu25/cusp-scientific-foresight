#!/usr/bin/env python3
"""
A1.2 — relationships among the four CUSP tasks (Reviewer 2, C1).

Reads ONLY finalized report JSONs. Writes ONLY under results/A1_2_task_correlation/.

Two levels, because they answer different questions:

  MODEL level (what the reviewer literally asked for): each model's aggregate
  performance on the four tasks, correlated across models. n = number of
  models (9), so CIs are wide, and a high value mostly reflects a shared
  "general capability" factor -- newer models are better at everything.

  ITEM level (the version with power): within each model, across thousands of
  events, does success on one task predict success on another task about the
  SAME paper? Model identity is held fixed, so the capability factor drops out.

Binary is reported bias-corrected: balanced accuracy = mean(recall on the real
question, specificity on the perturbed twin). Raw merged accuracy is dominated
by class balance x response bias (see RUN2_RESULTS.md section 3). MCC is a
sensitivity check.

FRQ scores are the finalized published-rubric scores (judge_frq_combined,
sha256 fc24e69d...), graded 2026-09-20/21 for every model -- NOT the archived
legacy-rubric scores.
"""
from __future__ import annotations
import argparse, csv, json, os, subprocess, sys
from datetime import datetime, timezone
import numpy as np
from scipy import stats

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.dirname(os.path.abspath(__file__))

# name, cutoff, original-corpus report, extension report
PANEL = [
    ("GPT-4o",          "2023-10", "run_evaluation/frq_results/gpt_4o_reeval.json",     "results_extension_run2/reports/gpt4o_base.json"),
    ("LLaMA 3.3 70B",   "2023-12", "run_evaluation/frq_results/llama_3_3_full.json",    "results_extension_run2/reports/llama33_base.json"),
    ("GPT-OSS 20B",     "2024-06", "run_evaluation/frq_results/gpt_oss_20B_reeval.json","results_extension_run2/reports/gptoss20b_base.json"),
    ("DeepSeek-R1",     "2024-07", "run_evaluation/frq_results/deepseek_r1.json",       None),
    ("Claude S4.5",     "2025-01", "run_evaluation/frq_results/claude_sonnet.json",     "results_extension_run2/reports/sonnet45_base.json"),
    ("GPT-5.4",         "2025-08", "run_evaluation/frq_results/gpt_5_4_eval.json",      "results_extension_run2/reports/gpt54_base.json"),
    ("Claude Sonnet 5", "2026-01", "results_sonnet5_run1/reports/base_medium_run1.json","results_extension_run2/reports/sonnet5_base_run1.json"),
    ("GPT-5.6 Sol",     "2026-02", "results_sol_run1/reports/base_medium_run1.json",    "results_extension_run2/reports/sol_base.json"),
    ("DeepSeek-V4-Pro", "2026-04", "results_dsv4pro_run1/reports/base_run1.json",       "results_extension_run2/reports/deepseekv4pro_base.json"),
    ("Claude Opus 4.8", "2026-01", "results_opus48_run1/reports/base_medium_run1.json", "results_extension_run2/reports/opus48_base_run1.json"),
]
TASKS = ["Binary (feasibility)", "MCQ (mechanism)", "FRQ (solution)", "Date"]
SHORT = ["binary", "mcq", "frq", "date"]


def load_events(paths):
    """Per event: binary_correct, perturbed_correct, mcq_correct, date_score, frq_score (None if absent)."""
    ev = []
    for p in paths:
        if not p:
            continue
        rep = json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
        for x in rep.get("results", []):
            t = x.get("tasks") or {}
            def ok(k):
                d = t.get(k)
                return d if d and not d.get("skipped") and not d.get("refused") else None
            b, bp, m, d, f = ok("binary"), ok("binary_perturbed"), ok("mcq"), ok("date"), ok("frq")
            ev.append({
                "id": x.get("id"),
                "binary":    (1.0 if b["correct"] else 0.0) if b and "correct" in b else None,
                "perturbed": (1.0 if bp["correct"] else 0.0) if bp and "correct" in bp else None,
                "mcq":       (1.0 if m["correct"] else 0.0) if m and "correct" in m else None,
                "date":      float(d["score"]) if d and d.get("score") is not None else None,
                "frq":       float(f["score"]) if f and f.get("score") is not None else None,
            })
    return ev


def model_metrics(ev, idx=None):
    """Aggregate metrics over events (optionally a resampled index)."""
    rows = ev if idx is None else [ev[i] for i in idx]
    b = [r["binary"] for r in rows if r["binary"] is not None]
    bp = [r["perturbed"] for r in rows if r["perturbed"] is not None]
    tp, fn = sum(b), len(b) - sum(b)
    tn, fp = sum(bp), len(bp) - sum(bp)
    recall = tp / len(b) if b else np.nan
    spec = tn / len(bp) if bp else np.nan
    den = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = (tp * tn - fp * fn) / den if den else np.nan
    mcq = [r["mcq"] for r in rows if r["mcq"] is not None]
    dt = [r["date"] for r in rows if r["date"] is not None]
    fr = [r["frq"] for r in rows if r["frq"] is not None]
    return {
        "balanced_acc": 0.5 * (recall + spec), "mcc": mcc,
        "merged_acc_raw": (tp + tn) / (len(b) + len(bp)) if (b or bp) else np.nan,
        "mcq_acc": np.mean(mcq) if mcq else np.nan,
        "date_score": np.mean(dt) if dt else np.nan,
        "frq_score": np.mean(fr) if fr else np.nan,
        "n_binary": len(b) + len(bp), "n_mcq": len(mcq), "n_date": len(dt), "n_frq": len(fr),
        "n_events": len(rows),
    }


def fisher_ci(r, n, z=1.96):
    if n < 4 or not np.isfinite(r) or abs(r) >= 1:
        return (np.nan, np.nan)
    zr = np.arctanh(r); se = 1 / np.sqrt(n - 3)
    return (np.tanh(zr - z * se), np.tanh(zr + z * se))


def corr_matrix(M, method):
    """M: models x 4. Returns r matrix and p matrix."""
    k = M.shape[1]; R = np.eye(k); P = np.zeros((k, k))
    for i in range(k):
        for j in range(i + 1, k):
            if method == "pearson":
                r, p = stats.pearsonr(M[:, i], M[:, j])
            else:
                r, p = stats.spearmanr(M[:, i], M[:, j])
            R[i, j] = R[j, i] = r; P[i, j] = P[j, i] = p
    return R, P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude", action="append", default=[], help="model name to drop (sensitivity)")
    ap.add_argument("--tag", default="", help="suffix for output files")
    ap.add_argument("--boots", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    panel = [m for m in PANEL if m[0] not in a.exclude]
    tag = a.tag

    # ---- load ----
    data = {name: load_events([o, e]) for name, _, o, e in panel}
    names = [m[0] for m in panel]
    metrics = {n: model_metrics(data[n]) for n in names}

    # ---- model-level table ----
    with open(os.path.join(OUT, f"model_task_performance{tag}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "cutoff", "n_events", "binary_balanced_acc", "binary_mcc", "binary_merged_acc_raw",
                    "mcq_acc", "frq_score_0to10", "date_score", "n_binary_items", "n_mcq", "n_frq", "n_date"])
        for name, cut, _, _ in panel:
            m = metrics[name]
            w.writerow([name, cut, m["n_events"], f"{m['balanced_acc']:.4f}", f"{m['mcc']:.4f}", f"{m['merged_acc_raw']:.4f}",
                        f"{m['mcq_acc']:.4f}", f"{m['frq_score']:.4f}", f"{m['date_score']:.4f}",
                        m["n_binary"], m["n_mcq"], m["n_frq"], m["n_date"]])

    def matrix_for(key_binary):
        return np.array([[metrics[n][key_binary], metrics[n]["mcq_acc"], metrics[n]["frq_score"], metrics[n]["date_score"]]
                         for n in names])

    M = matrix_for("balanced_acc")
    nm = len(names)
    results = {}
    for method in ("pearson", "spearman"):
        R, P = corr_matrix(M, method)
        # event-bootstrap: resample events WITHIN each model, recompute metrics, recompute r
        rng = np.random.default_rng(a.seed)
        boots = []
        for _ in range(a.boots):
            Mb = []
            for n in names:
                ev = data[n]; idx = rng.integers(0, len(ev), len(ev))
                mm = model_metrics(ev, idx)
                Mb.append([mm["balanced_acc"], mm["mcq_acc"], mm["frq_score"], mm["date_score"]])
            Rb, _ = corr_matrix(np.array(Mb), method)
            boots.append(Rb)
        boots = np.array(boots)
        lo_b, hi_b = np.percentile(boots, 2.5, axis=0), np.percentile(boots, 97.5, axis=0)
        results[method] = (R, P, lo_b, hi_b)

    # sensitivity: MCC instead of balanced accuracy
    R_mcc, _ = corr_matrix(matrix_for("mcc"), "pearson")
    R_raw, _ = corr_matrix(matrix_for("merged_acc_raw"), "pearson")

    # ---- item level: within-model Spearman across events, per pair ----
    item = {}   # (i,j) -> list of (model, rho, n)
    pooled_resid = {}
    for i in range(4):
        for j in range(i + 1, 4):
            item[(i, j)] = []
            xs_all, ys_all = [], []
            for n in names:
                pts = []
                for r in data[n]:
                    bf = [v for v in (r["binary"], r["perturbed"]) if v is not None]
                    vals = [np.mean(bf) if bf else None, r["mcq"], r["frq"], r["date"]]
                    if vals[i] is not None and vals[j] is not None:
                        pts.append((vals[i], vals[j]))
                if len(pts) >= 30:
                    x, y = zip(*pts)
                    rho, p = stats.spearmanr(x, y)
                    item[(i, j)].append((n, rho, p, len(pts)))
                    xm, ym = np.mean(x), np.mean(y)
                    xs_all += [v - xm for v in x]; ys_all += [v - ym for v in y]
            pooled_resid[(i, j)] = (stats.pearsonr(xs_all, ys_all)[0], len(xs_all)) if len(xs_all) > 30 else (np.nan, 0)

    # ---- write CSV / MD ----
    def write_corr_csv(name, R, lo, hi, P=None):
        with open(os.path.join(OUT, name), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["task_i", "task_j", "r", "ci_low_fisher", "ci_high_fisher",
                                          "ci_low_eventboot", "ci_high_eventboot", "p", "n_models"])
            for i in range(4):
                for j in range(4):
                    fl, fh = fisher_ci(R[i, j], nm) if i != j else (1, 1)
                    w.writerow([TASKS[i], TASKS[j], f"{R[i,j]:.3f}", f"{fl:.3f}", f"{fh:.3f}",
                                f"{lo[i,j]:.3f}", f"{hi[i,j]:.3f}", f"{P[i,j]:.3f}" if P is not None and i != j else "", nm])
    for method in ("pearson", "spearman"):
        R, P, lo, hi = results[method]
        write_corr_csv(f"task_correlation_{method}{tag}.csv", R, lo, hi, P)
    with open(os.path.join(OUT, f"item_level_correlation{tag}.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["task_i", "task_j", "model", "spearman_rho", "p", "n_events"])
        for (i, j), rows in item.items():
            for n, rho, p, k in rows:
                w.writerow([TASKS[i], TASKS[j], n, f"{rho:.3f}", f"{p:.2e}", k])

    md = []
    md.append(f"# A1.2 — relationships among the four CUSP tasks{(' ('+tag.strip('_')+')') if tag else ''}\n")
    md.append(f"Panel: {nm} models — {', '.join(names)}. Entire dataset (original + extension; DeepSeek-R1 original only).\n")
    md.append("Binary = **balanced accuracy** (bias-corrected merged binary). FRQ = finalized **published-rubric** scores "
              "(judge_frq_combined, sha256 fc24e69d…), not the legacy archive. Refusals excluded from denominators.\n")
    md.append("## Model-level performance (inputs to the correlation)\n")
    md.append("| model | cutoff | binary bal. acc | MCC | MCQ acc | FRQ (0–10) | date score | n events |\n|---|---|---|---|---|---|---|---|")
    for name, cut, _, _ in panel:
        m = metrics[name]
        md.append(f"| {name} | {cut} | {m['balanced_acc']:.3f} | {m['mcc']:+.3f} | {m['mcq_acc']:.3f} | {m['frq_score']:.2f} | {m['date_score']:.3f} | {m['n_events']:,} |")
    for method in ("pearson", "spearman"):
        R, P, lo, hi = results[method]
        md.append(f"\n## Model-level {method.capitalize()} correlation (n = {nm} models)\n")
        md.append("Cell: r [Fisher-z 95% CI over models] {event-bootstrap 95% CI}. With n = 9 the Fisher CIs are wide by construction.\n")
        md.append("| | " + " | ".join(TASKS) + " |\n|---|" + "---|" * 4)
        for i in range(4):
            cells = []
            for j in range(4):
                if i == j: cells.append("1"); continue
                fl, fh = fisher_ci(R[i, j], nm)
                cells.append(f"{R[i,j]:.2f} [{fl:+.2f}, {fh:+.2f}] {{{lo[i,j]:+.2f}, {hi[i,j]:+.2f}}}")
            md.append(f"| **{TASKS[i]}** | " + " | ".join(cells) + " |")
    md.append("\n## Sensitivity: binary metric choice (model-level Pearson with the other three tasks)\n")
    md.append("| binary metric | vs MCQ | vs FRQ | vs Date |\n|---|---|---|---|")
    for lab, Rx in (("balanced accuracy (primary)", results["pearson"][0]), ("MCC", R_mcc), ("raw merged accuracy (NOT recommended)", R_raw)):
        md.append(f"| {lab} | {Rx[0,1]:+.2f} | {Rx[0,2]:+.2f} | {Rx[0,3]:+.2f} |")
    md.append("\n## Item-level: within each model, across events (does success on one task predict success on another for the same paper?)\n")
    md.append("Spearman ρ per model; table shows median across models, range, and the pooled within-model (demeaned) Pearson r with its n.\n")
    md.append("| pair | median ρ | min | max | models | pooled within-model r | pooled n |\n|---|---|---|---|---|---|---|")
    for (i, j), rows in item.items():
        rh = [r for _, r, _, _ in rows]
        pr, pn = pooled_resid[(i, j)]
        md.append(f"| {TASKS[i]} × {TASKS[j]} | {np.median(rh):+.3f} | {min(rh):+.3f} | {max(rh):+.3f} | {len(rh)} | {pr:+.3f} | {pn:,} |")
    open(os.path.join(OUT, f"task_correlation{tag}.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")

    # ---- heatmap ----
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
    I = np.eye(4)
    for ax, (title, R) in zip(axes, [
        (f"Model-level Pearson r (n={nm} models)", results["pearson"][0]),
        (f"Model-level Spearman ρ (n={nm} models)", results["spearman"][0]),
        ("Item-level: median within-model Spearman ρ", I.copy())]):
        if title.startswith("Item"):
            for (i, j), rows in item.items():
                R[i, j] = R[j, i] = np.median([r for _, r, _, _ in rows])
        im = ax.imshow(R, vmin=-1, vmax=1, cmap="RdBu_r")
        ax.set_xticks(range(4)); ax.set_yticks(range(4))
        ax.set_xticklabels([t.split(" (")[0] for t in TASKS], rotation=30, ha="right"); ax.set_yticklabels([t.split(" (")[0] for t in TASKS])
        for i in range(4):
            for j in range(4):
                ax.text(j, i, f"{R[i,j]:.2f}", ha="center", va="center", fontsize=10, color="black" if abs(R[i, j]) < 0.6 else "white")
        ax.set_title(title, fontsize=10)
    fig.colorbar(im, ax=axes, fraction=0.02, pad=0.02)
    fig.suptitle("A1.2 — relationships among the four CUSP tasks (entire dataset)", y=1.02)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"task_correlation_heatmap{tag}.{ext}"), dpi=200, bbox_inches="tight")

    # ---- manifest ----
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    json.dump({
        "generated_utc": datetime.now(timezone.utc).isoformat(), "git_sha": sha, "tag": tag,
        "models": [{"name": n, "cutoff": c, "reports": [p for p in (o, e) if p], "n_events": metrics[n]["n_events"]} for n, c, o, e in panel],
        "binary_metric": "balanced accuracy (bias-corrected merged binary); MCC and raw merged accuracy as sensitivity",
        "frq_scores": "finalized published-rubric scores, judge_frq_combined sha256 fc24e69dfec1b214..., graded 2026-09-20/21; NOT the legacy archive",
        "refusals": "excluded from denominators (matches published tables)",
        "bootstrap": {"events_resampled_within_model": a.boots, "seed": a.seed},
        "outputs": sorted(f for f in os.listdir(OUT) if tag in f or not tag),
    }, open(os.path.join(OUT, f"MANIFEST{tag}.json"), "w"), indent=2)
    print("\n".join(md))


if __name__ == "__main__":
    main()
