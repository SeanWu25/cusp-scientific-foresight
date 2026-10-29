"""
A4.3 supplement — (1) knowledge and forecasting gaps on PRE- and POST-cutoff events separately
under the original (self-generated query) and fixed-evidence-packet setups; (2) how well the
fixed-packet results reproduce the original manuscript's retrieval results, at the cell level
(model x task x partition means and gaps) and at the item level (same event, same model, same
condition). Reads the stored reports only; no inference. Definitions and loaders are the ones
used by a43_gaps.py / run_evaluation/gap_decomposition.py (post = publication month > cutoff
month; ids shared by every condition; retrieval-failed rows dropped; paired normal 95% CIs).

Writes  A4_3_fixed_queries/gaps_pre_post.md, tables/A4_3_gaps_pre_post.json,
        A4_3_fixed_queries/correlation.md, tables/A4_3_correlation.json
"""
import json, sys, collections, math
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from a43_gaps import ORIG, TASKS, RP, D3, GD, OUT, load_events
import os

B_BOOT = 10000
# A43_EVENTS=1000: use the first 500 + the 500 events added 2026-10-18 (ext500/). Base = Table 1 base runs (original +
# extension corpus); original design = the stored runs + ext500/original/reports; fixed = reports/ + ext500/reports/.
# Outputs get the suffix _1000. Default (unset or 500): the first 500 only, unchanged.
N1000 = os.environ.get("A43_EVENTS") == "1000"; SUF = "_1000" if N1000 else ""
EXT = D3 / "ext500"


def loaders(mk, base, ws, wscut):
    """(B, C, W, FC, FW) report dicts for one model; W is None if the model has no original WS run."""
    if not N1000:
        fws, fwscut = RP / f"{mk}_fixed_ws.json", RP / f"{mk}_fixed_ws_cutoff.json"
        return (GD.load(str(base), drop_retrieval_failures=False), GD.load(str(wscut)), GD.load(str(ws)) if ws and ws.exists() else None,
                GD.load(str(fwscut)), GD.load(str(fws)))
    from a43_ext_sample import BASES
    ext_ids = {l.strip() for l in open(EXT / "subset_ext500_ids.txt") if l.strip()}
    def both(p_main, p_ext, **kw):
        d = GD.load(str(p_main), **kw) if p_main and Path(p_main).exists() else {}
        e = {i: v for i, v in GD.load(str(p_ext), **kw).items() if i in ext_ids} if Path(p_ext).exists() else {}
        d = {i: v for i, v in d.items() if i not in ext_ids}; d.update(e); return d
    B = {}
    for p in BASES[mk]: B.update(GD.load(str(OUT.parent.parent / p), drop_retrieval_failures=False))
    C = both(wscut, EXT / f"original/reports/{mk}_ws_cutoff.json")
    W = both(ws, EXT / f"original/reports/{mk}_ws.json") if ws and ws.exists() else None
    FC = both(RP / f"{mk}_fixed_ws_cutoff.json", EXT / f"reports/{mk}_fixed_ws_cutoff.json")
    FW = both(RP / f"{mk}_fixed_ws.json", EXT / f"reports/{mk}_fixed_ws.json")
    return B, C, W, FC, FW


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.std() == 0 or y.std() == 0: return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x, y):
    from scipy.stats import rankdata
    return pearson(rankdata(x), rankdata(y))


def boot_r(x, y, fn=pearson, B=B_BOOT, seed=0):
    x, y = np.asarray(x, float), np.asarray(y, float); rng = np.random.default_rng(seed); n = len(x); rs = []
    for _ in range(B):
        i = rng.integers(0, n, n); rs.append(fn(x[i], y[i]))
    rs = np.array([r for r in rs if not np.isnan(r)])
    return [float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))]


def boot_mad(x, y, B=B_BOOT, seed=0):
    d = np.abs(np.asarray(x, float) - np.asarray(y, float)); rng = np.random.default_rng(seed); n = len(d)
    m = d[rng.integers(0, n, (B, n))].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def kappa(a, b):
    a, b = np.asarray(a), np.asarray(b); po = float((a == b).mean()); cats = set(a) | set(b)
    pe = sum(float((a == c).mean()) * float((b == c).mean()) for c in cats)
    return float("nan") if pe == 1 else float((po - pe) / (1 - pe))


def main():
    pub = {i: r["publication_date"] for i, r in load_events().items()}
    cells = []; items = []  # item-level records for correlation
    for mk, (name, cut, base, ws, wscut) in ORIG.items():
        if not (RP / f"{mk}_fixed_ws_cutoff.json").exists():   # e.g. DeepSeek R1: no fixed-packet run (deployment retired)
            print(f"  skip {name}: no fixed-packet reports", file=sys.stderr); continue
        B, C, W, FC, FW = loaders(mk, base, ws, wscut)
        shared = set(B) & set(C) & set(FC) & set(FW) & (set(W) if W else set(FW))
        for scope in ("pre", "post"):
            ids = sorted(i for i in shared if (pub.get(i, "") > cut) == (scope == "post"))
            for label, task in TASKS:
                vals = collections.defaultdict(list)
                for i in ids:
                    v = dict(b=GD.field(B[i], task, "score"), c=GD.field(C[i], task, "score"), fc=GD.field(FC[i], task, "score"), fw=GD.field(FW[i], task, "score"), w=(GD.field(W[i], task, "score") if W else None))
                    if any(v[k] is None for k in ("b", "c", "fc", "fw")) or (W and v["w"] is None): continue
                    for k, x in v.items():
                        if x is not None: vals[k].append(x)
                    items.append(dict(model=name, scope=scope, task=label, id=i, **{k: x for k, x in v.items() if x is not None}))
                n = len(vals["b"]); cell = dict(model=name, model_key=mk, cutoff=cut, scope=scope, task=label, n=n)
                if n >= 20:
                    b, c, fc, fw = (np.array(vals[k]) for k in ("b", "c", "fc", "fw"))
                    ko, kf, ff = c - b, fc - b, fw - fc
                    cell.update(mean_base=float(b.mean()), mean_wscut_orig=float(c.mean()), mean_wscut_fixed=float(fc.mean()), mean_ws_fixed=float(fw.mean()),
                                know_orig=float(ko.mean()), know_orig_ci=list(GD.paired_ci(list(ko))), know_fixed=float(kf.mean()), know_fixed_ci=list(GD.paired_ci(list(kf))),
                                fore_fixed=float(ff.mean()), fore_fixed_ci=list(GD.paired_ci(list(ff))))
                    if W is not None:
                        w = np.array(vals["w"]); fo = w - c
                        cell.update(mean_ws_orig=float(w.mean()), fore_orig=float(fo.mean()), fore_orig_ci=list(GD.paired_ci(list(fo))))
                else:
                    cell["suppressed"] = True
                cells.append(cell)
    json.dump(cells, open(OUT / f"tables/A4_3_gaps_pre_post{SUF}.json", "w"), indent=1)
    # containment: is the fixed-setup gap inside the original gap's paired CI?
    cont = {}
    for g in ("know", "fore"):
        pts = [c for c in cells if not c.get("suppressed") and f"{g}_orig" in c]
        inside = [c for c in pts if c[f"{g}_orig_ci"][0] <= c[f"{g}_fixed"] <= c[f"{g}_orig_ci"][1]]
        cont[g] = dict(n_cells=len(pts), n_inside=len(inside), outside=[dict(model=c["model"], scope=c["scope"], task=c["task"], orig=c[f"{g}_orig"], orig_ci=c[f"{g}_orig_ci"], fixed=c[f"{g}_fixed"]) for c in pts if c not in inside])

    # ---------------- table: pre vs post, both setups
    def f(v, ci=None):
        if v is None or (isinstance(v, float) and math.isnan(v)): return "—"
        return f"{v:+.3f} [{ci[0]:+.3f}, {ci[1]:+.3f}]" if ci else f"{v:+.3f}"
    L = ["# A4.3 — knowledge and forecasting gaps on pre- and post-cutoff events, original vs fixed evidence packets", "",
         "Knowledge gap = WS+Cutoff − base; forecasting gap = WS − WS+Cutoff. `original` = the manuscript's runs (each model wrote its own query; GPT-4o's "
         "unrestricted run used the provider's native search tool). `fixed` = identical evidence packets from Opus 4.8 queries. Pre = publication month ≤ "
         "cutoff month, post = publication month > cutoff month. Same events in all four conditions; retrieval-failed rows dropped; paired normal 95% CIs. "
         "GPT-4o and LLaMA 3.3 have no pre-cutoff events in the subset (LLaMA 3.3's unrestricted run was generated 2026-10-05). Cells with n < 20 suppressed.", ""]
    for scope, title in (("pre", "Pre-cutoff events (recall regime)"), ("post", "Post-cutoff events (forecasting regime)")):
        L += [f"\n## {title}\n", "| model | task | n | base | WS+Cutoff orig | WS+Cutoff fixed | WS orig | WS fixed | knowledge gap orig | knowledge gap fixed | forecasting gap orig | forecasting gap fixed |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in cells:
            if r["scope"] != scope or r["n"] == 0: continue
            if r.get("suppressed"): L.append(f"| {r['model']} | {r['task']} | {r['n']} | suppressed (n<20) | | | | | | | | |"); continue
            L.append(f"| {r['model']} | {r['task']} | {r['n']} | {r['mean_base']:.3f} | {r['mean_wscut_orig']:.3f} | {r['mean_wscut_fixed']:.3f} | "
                     f"{('%.3f' % r['mean_ws_orig']) if 'mean_ws_orig' in r else '—'} | {r['mean_ws_fixed']:.3f} | {f(r['know_orig'], r['know_orig_ci'])} | {f(r['know_fixed'], r['know_fixed_ci'])} | "
                     f"{f(r.get('fore_orig'), r.get('fore_orig_ci'))} | {f(r['fore_fixed'], r['fore_fixed_ci'])} |")
    (D3 / f"gaps_pre_post{SUF}.md").write_text("\n".join(L) + "\n")

    # ---------------- correlation, cell level
    # FRQ is scored 0-10; it is divided by 10 here so every task is on a unit scale before pooling cells,
    # otherwise the FRQ cells dominate the Pearson correlation and the MAD by scale alone.
    corr = {"cell_level": {}, "item_level": {}}
    ok = [c for c in cells if not c.get("suppressed")]
    def u(c, k):
        return c[k] / 10 if c["task"] == "FRQ (0-10)" else c[k]
    CL = ["# A4.3 — agreement between the fixed-evidence-packet runs and the original manuscript's retrieval runs", "",
          f"Cell level: one point per model × task × partition (pre/post) with n ≥ 20. FRQ cells are rescaled from 0–10 to 0–1 before pooling so all tasks share a unit scale. "
          f"Pearson r and Spearman ρ with {B_BOOT:,} cell-bootstrap 95% CIs; MAD = mean absolute difference between setups, with the same cell-bootstrap 95% CI.", "",
          "| quantity | cells | Pearson r [CI] | Spearman ρ [CI] | MAD [CI] | mean orig | mean fixed |", "|---|---|---|---|---|---|---|"]
    def frq_filter(key, c):
        if key.endswith("_x4o"): return c["model"] != "GPT-4o"
        if key.endswith("_nofrq"): return c["task"] != "FRQ (0-10)"
        if key.endswith("_frq"): return c["task"] == "FRQ (0-10)"
        return True
    for key, lab, ko, kf in (("wscut", "WS+Cutoff accuracy/score (condition mean)", "mean_wscut_orig", "mean_wscut_fixed"),
                             ("ws", "WS accuracy/score (condition mean)", "mean_ws_orig", "mean_ws_fixed"),
                             ("wscut_frq", "WS+Cutoff score, FRQ cells only (0–10 units)", "mean_wscut_orig", "mean_wscut_fixed"),
                             ("ws_frq", "WS score, FRQ cells only (0–10 units)", "mean_ws_orig", "mean_ws_fixed"),
                             ("know", "knowledge gap (WS+Cutoff − base)", "know_orig", "know_fixed"),
                             ("know_nofrq", "knowledge gap, four 0–1 tasks only (no FRQ)", "know_orig", "know_fixed"),
                             ("know_frq", "knowledge gap, FRQ cells only (0–10 units)", "know_orig", "know_fixed"),
                             ("fore", "forecasting gap (WS − WS+Cutoff)", "fore_orig", "fore_fixed"),
                             ("fore_nofrq", "forecasting gap, four 0–1 tasks only (no FRQ)", "fore_orig", "fore_fixed"),
                             ("fore_frq", "forecasting gap, FRQ cells only (0–10 units)", "fore_orig", "fore_fixed"),
                             ("fore_x4o", "forecasting gap, excluding GPT-4o (native-tool WS run)", "fore_orig", "fore_fixed")):
        for sc, scl in (("all", "pre + post"), ("post", "post only")):
            pts = [c for c in ok if ko in c and kf in c and (sc == "all" or c["scope"] == "post") and frq_filter(key, c)]
            raw = key.endswith("_frq")
            x = [c[ko] if raw else u(c, ko) for c in pts]; y = [c[kf] if raw else u(c, kf) for c in pts]
            if len(pts) < 3: continue
            r, rho = pearson(x, y), spearman(x, y); rci, rhoci = boot_r(x, y), boot_r(x, y, spearman)
            mad = float(np.mean(np.abs(np.array(x) - np.array(y)))); madci = boot_mad(x, y)
            corr["cell_level"][f"{key}:{sc}"] = dict(label=lab, scope=scl, n_cells=len(pts), pearson=r, pearson_ci=rci, spearman=rho, spearman_ci=rhoci, mad=mad, mad_ci=madci, mean_orig=float(np.mean(x)), mean_fixed=float(np.mean(y)))
            CL.append(f"| {lab}, {scl} | {len(pts)} | {r:.3f} [{rci[0]:.3f}, {rci[1]:.3f}] | {rho:.3f} [{rhoci[0]:.3f}, {rhoci[1]:.3f}] | {mad:.3f} [{madci[0]:.3f}, {madci[1]:.3f}] | {np.mean(x):+.3f} | {np.mean(y):+.3f} |")

    # ---------------- correlation, item level
    CL += ["", "Item level: same event, same model, same condition, original run vs fixed-packet run. Binary/MCQ scores are 0/1, so agreement and Cohen's κ are reported; "
           "date (0–1) and FRQ (0–10) scores are continuous, so Pearson r (agreement = exact equality). Pooled rows combine every model with that condition.", "",
           "| model | partition | task | n (WS+Cutoff / WS if different) | WS+Cutoff: agreement | WS+Cutoff: κ / r | WS: agreement | WS: κ / r |", "|---|---|---|---|---|---|---|---|"]
    def stat(a, b, task):
        a, b = np.asarray(a, float), np.asarray(b, float)
        if task in ("Date (0-1)", "FRQ (0-10)"): return f"{float((np.abs(a - b) < 1e-9).mean()):.3f}", f"r={pearson(a, b):.3f}"
        return f"{float((a == b).mean()):.3f}", f"κ={kappa(a, b):.3f}"
    groups = collections.defaultdict(list)
    for it in items:
        groups[(it["model"], it["scope"], it["task"])].append(it); groups[("pooled (all models)", it["scope"], it["task"])].append(it); groups[("pooled (all models)", "pre + post", it["task"])].append(it)
    order = [c["model"] for c in cells] + ["pooled (all models)"]
    for (m, sc, t), its in sorted(groups.items(), key=lambda kv: (order.index(kv[0][0]), kv[0][1], [l for l, _ in TASKS].index(kv[0][2]))):
        if len(its) < 20: continue
        a1, a2 = stat([i["c"] for i in its], [i["fc"] for i in its], t)
        iw = [i for i in its if "w" in i]  # models with an original unrestricted run (all but LLaMA 3.3)
        b1, b2 = stat([i["w"] for i in iw], [i["fw"] for i in iw], t) if len(iw) >= 20 else ("—", "—")
        corr["item_level"][f"{m}|{sc}|{t}"] = dict(n=len(its), n_ws=len(iw), wscut_agree=a1, wscut_stat=a2, ws_agree=b1, ws_stat=b2)
        CL.append(f"| {m} | {sc} | {t} | {len(its)}{'' if len(iw) in (0, len(its)) else ' / ' + str(len(iw))} | {a1} | {a2} | {b1} | {b2} |")
    CL += ["", "Containment: fixed-setup gap inside the original gap's paired 95% CI.", ""]
    for g, lab in (("know", "knowledge gap"), ("fore", "forecasting gap")):
        CL.append(f"- {lab}: {cont[g]['n_inside']} of {cont[g]['n_cells']} cells inside; outside: " + "; ".join(f"{o['model']} {o['scope']} {o['task']} ({o['orig']:+.3f} → {o['fixed']:+.3f})" for o in cont[g]["outside"]))
    corr["containment"] = cont
    (D3 / f"correlation{SUF}.md").write_text("\n".join(CL) + "\n")
    json.dump(corr, open(OUT / f"tables/A4_3_correlation{SUF}.json", "w"), indent=1)
    print("\n".join(L)); print(); print("\n".join(CL))


if __name__ == "__main__":
    main()
