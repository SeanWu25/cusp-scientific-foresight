"""a7_analyze_cg.py — analyses C (delayed dates), E (response bias), F (cross-condition), G (trace length)."""
from __future__ import annotations
import json, re, sys, collections
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_stats as S, a7_prompts as P

FOCAL_C = ["ABSENCE_AS_EVIDENCE", "ROUND_ANCHOR", "CUTOFF_REFERENCED", "DIFFICULTY_APPEAL"]
CONTRAST_C = ["PROVENANCE_INFERRED", "RATE_OF_PROGRESS", "FIELD_MOMENTUM", "EVIDENCE_CITED"]
# Table S13 response-bias index (calibration_study/common.py bias_s13): most yes-biased and most no-biased
YES_BIASED, NO_BIASED = "LLaMA 3.3 70B", "GPT-OSS 20B"
RETRIEVAL_REF = re.compile(r"\b(source\s*\d|sources?\b|search results?|retrieved|the (provided|given) (context|results)|"
                           r"according to the (context|sources|results)|per the (context|sources)|snippet)\b", re.I)


def main():
    rows, coders = S.load_labels()
    rel = set(S.reliable_codes())
    by = collections.defaultdict(list)
    for r in rows: by[r["code"]].append(r)
    traces = {r["trace_id"]: r for r in C.iter_traces(lambda r: True)}

    # ================= C: delayed dates
    D = C.STUDY / "analyses" / "C_delayed_dates"
    md = ["# Analysis C — the delayed-date mechanism (priority)\n",
          "CUSP's temporal task asks for the month a development was or will first be achieved. The paper reports "
          "systematic lateness. The hypothesis under test is that traces which reason from the absence of known "
          "work, anchor on a round future year, invoke the knowledge cutoff, or appeal to difficulty are the ones "
          "that run late.\n",
          "Outcome: **signed error in months**, predicted minus ground truth. Positive is late. Model: Gaussian "
          "random-intercept fit with an intercept for event and for model, so item difficulty and model-level "
          "lateness are absorbed; the coefficient is the extra lateness in months attributable to the code. "
          "p-values Holm-adjusted across the codes tested. Base condition only.\n"]
    sel_all = [r for r in by["ABSENCE_AS_EVIDENCE"] if r["task"] == "date" and r["condition"] == "base"
               and r["signed_error_months"] is not None]
    md.append(f"Date traces with a signed error and a consensus label: **{len(sel_all):,}**. "
              f"Mean signed error {np.mean([r['signed_error_months'] for r in sel_all]):+.1f} months, "
              f"median {np.median([r['signed_error_months'] for r in sel_all]):+.0f}.\n")
    res, ps, untested = [], [], []
    for code in FOCAL_C + CONTRAST_C:
        if code not in rel:
            if code in FOCAL_C: untested.append((code, "failed the inter-coder reliability rule"))
            continue
        sel = [r for r in by[code] if r["task"] == "date" and r["condition"] == "base"
               and r["signed_error_months"] is not None and r["label"] is not None]
        if len(sel) < 100:
            if code in FOCAL_C: untested.append((code, f"only {len(sel)} date traces"))
            continue
        y = np.array([float(r["signed_error_months"]) for r in sel]); x = np.array([r["label"] for r in sel], float)
        if x.sum() < 20:
            if code in FOCAL_C: untested.append((code, f"present in only {int(x.sum())} date traces ({100*x.mean():.1f}%)"))
            continue
        g = S.glmm_effect(y, x, [r["id"] for r in sel], models=[r["model"] for r in sel], family="gaussian")
        d = S.diff_ci(y, x, [r["id"] for r in sel], B=1000)
        res.append(dict(code=code, focal=code in FOCAL_C, **g, raw=d)); ps.append(g["p"])
    for r, a in zip(res, S.holm(ps)): r["p_holm"] = a
    md.append("| code | tested as | n with code | mean signed error, with | without | difference [95% CI] | beta months [95% CI] | p (Holm) |")
    md.append("|---|---|---|---|---|---|---|---|")
    for r in res:
        d = r["raw"]
        md.append(f"| {r['code']} | {'hypothesised' if r['focal'] else 'contrast'} | {d['n1']:,} | {d['m1']:+.1f} | {d['m0']:+.1f} | "
                  f"{d['diff']:+.1f} [{d['lo']:+.1f}, {d['hi']:+.1f}] | {r['beta']:+.1f} [{r['lo']:+.1f}, {r['hi']:+.1f}] | {S.fmtp(r['p_holm'])} |")
    up = [r for r in res if r["focal"] and np.isfinite(r["p_holm"]) and r["p_holm"] < 0.05 and r["beta"] > 0]
    dn = [r for r in res if r["focal"] and np.isfinite(r["p_holm"]) and r["p_holm"] < 0.05 and r["beta"] < 0]
    ns = [r for r in res if r["focal"] and not (np.isfinite(r["p_holm"]) and r["p_holm"] < 0.05)]
    if untested:
        md.append("\n**Codes the hypothesis named that could not be tested here:** "
                  + "; ".join(f"{c} ({why})" for c, why in untested)
                  + ". These are reported as prevalence only. The hypothesis is therefore tested on the subset of its "
                    "named mechanisms that the data can support, and that restriction is part of the result.\n")
    md.append(f"\n**Verdict on the hypothesis.** Of the {len([r for r in res if r['focal']])} hypothesised codes that could be tested, "
              f"{len(up)} are associated with significantly LATER predictions"
              + (" (" + ", ".join(f"{r['code']} {r['beta']:+.1f} months" for r in up) + ")" if up else "")
              + f", {len(dn)} with significantly EARLIER"
              + (" (" + ", ".join(f"{r['code']} {r['beta']:+.1f} months" for r in dn) + ")" if dn else "")
              + f", and {len(ns)} show no significant association"
              + (" (" + ", ".join(r["code"] for r in ns) + ")" if ns else "") + ".\n")
    # distribution of predicted dates conditional on each code
    md.append("\n## Distribution of the signed error conditional on each code\n")
    md.append("| code | n | p10 | p25 | median | p75 | p90 | share late (> 0) | share more than a year late |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for code in FOCAL_C + CONTRAST_C:
        if code not in by: continue
        sel = [r for r in by[code] if r["task"] == "date" and r["condition"] == "base"
               and r["signed_error_months"] is not None and r["label"] == 1]
        if len(sel) < 20: continue
        v = np.array([float(r["signed_error_months"]) for r in sel])
        q = np.percentile(v, [10, 25, 50, 75, 90])
        md.append(f"| {code} (present) | {len(v):,} | {q[0]:+.0f} | {q[1]:+.0f} | {q[2]:+.0f} | {q[3]:+.0f} | {q[4]:+.0f} | "
                  f"{100*np.mean(v > 0):.0f}% | {100*np.mean(v > 12):.0f}% |")
    base = np.array([float(r["signed_error_months"]) for r in sel_all])
    q = np.percentile(base, [10, 25, 50, 75, 90])
    md.append(f"| *all date traces* | {len(base):,} | {q[0]:+.0f} | {q[1]:+.0f} | {q[2]:+.0f} | {q[3]:+.0f} | {q[4]:+.0f} | "
              f"{100*np.mean(base > 0):.0f}% | {100*np.mean(base > 12):.0f}% |")
    json.dump([{k: (v if k != "raw" else v) for k, v in r.items()} for r in res], open(D / "results.json", "w"), indent=1, default=float)
    (D / "results.md").write_text("\n".join(md) + "\n")
    print("C written")

    # ================= E: response bias
    E = C.STUDY / "analyses" / "E_response_bias"
    md = ["# Analysis E — what differs in the traces of a yes-biased and a no-biased model\n",
          f"Table S13 puts **{YES_BIASED}** at the yes-biased extreme and **{NO_BIASED}** at the no-biased extreme. "
          "Comparison is on binary and perturbed-binary traces, base condition.\n",
          "| code | " + YES_BIASED + " | " + NO_BIASED + " | difference [95% CI] | p (Holm) |", "|---|---|---|---|---|"]
    sel_pool = [r for r in by["EVIDENCE_CITED"] if r["task"] in ("binary", "binary_perturbed")
                and r["condition"] == "base" and r["model"] in (YES_BIASED, NO_BIASED)]
    res, ps = [], []
    for code in [c for c in P.CODES if c in rel]:
        sel = [r for r in by[code] if r["task"] in ("binary", "binary_perturbed") and r["condition"] == "base"
               and r["model"] in (YES_BIASED, NO_BIASED)]
        if len(sel) < 100: continue
        y = np.array([r["label"] for r in sel], float); g = np.array([r["model"] == YES_BIASED for r in sel])
        d = S.diff_ci(y, g, [r["id"] for r in sel], B=1000)
        res.append((code, d)); ps.append(d["p"])
    for (code, d), a in zip(res, S.holm(ps)):
        md.append(f"| {code} | {100*d['m1']:.1f}% | {100*d['m0']:.1f}% | {100*d['diff']:+.1f} pts "
                  f"[{100*d['lo']:+.1f}, {100*d['hi']:+.1f}] | {S.fmtp(a)} |")
    # generic vs item-engaged: lexical overlap with the item, and near-duplicate traces
    md.append("\n## Does the biased model engage with the item, or repeat a generic pattern?\n")
    md.append("| measure | " + YES_BIASED + " | " + NO_BIASED + " |"); md.append("|---|---|---|")
    stats = {}
    for m in (YES_BIASED, NO_BIASED):
        ts = [traces[r["trace_id"]] for r in {x["trace_id"]: x for x in sel_pool if x["model"] == m}.values()]
        if not ts: continue
        def toks(s): return set(re.findall(r"[a-z]{4,}", s.lower()))
        ov = [len(toks(t["trace"]) & toks(t["question"])) / max(1, len(toks(t["trace"]))) for t in ts]
        opens = collections.Counter(" ".join(t["trace"].split()[:5]).lower() for t in ts)
        vocab = collections.Counter(w for t in ts for w in re.findall(r"[a-z]{4,}", t["trace"].lower()))
        tot = sum(vocab.values())
        stats[m] = dict(n=len(ts), overlap=float(np.mean(ov)), words=float(np.mean([t["trace_words"] for t in ts])),
                        top_open=opens.most_common(1)[0], open_share=opens.most_common(1)[0][1] / len(ts),
                        ttr=len(vocab) / max(1, tot))
    for lab, key, f in (("traces compared", "n", lambda v: f"{v:,}"),
                        ("mean trace length (words)", "words", lambda v: f"{v:.0f}"),
                        ("share of trace vocabulary drawn from the item", "overlap", lambda v: f"{100*v:.1f}%"),
                        ("type-token ratio of the trace corpus", "ttr", lambda v: f"{v:.3f}"),
                        ("share of traces sharing the single commonest 5-word opening", "open_share", lambda v: f"{100*v:.1f}%")):
        md.append(f"| {lab} | " + " | ".join(f(stats[m][key]) for m in (YES_BIASED, NO_BIASED) if m in stats) + " |")
    for m in (YES_BIASED, NO_BIASED):
        if m in stats:
            md.append(f"\nCommonest opening for {m}: \"{stats[m]['top_open'][0]}...\" ({stats[m]['top_open'][1]} traces).")
    (E / "results.md").write_text("\n".join(md) + "\n")
    print("E written")

    # ================= F: cross-condition paired traces
    F = C.STUDY / "analyses" / "F_cross_condition"
    trip = collections.defaultdict(dict)
    for r in rows:
        if r["code"] != "EVIDENCE_CITED": continue
        trip[(r["model"], r["task"], r["id"])][r["condition"]] = r
    full = {k: v for k, v in trip.items() if {"base", "ws_cutoff", "ws"} <= set(v)}
    md = ["# Analysis F — the same item under base, WS+Cutoff and unrestricted WS\n",
          f"Matched triples: the same model, task and event coded under all three conditions. "
          f"**{len(full):,} complete triples** ({len({k[2] for k in full}):,} distinct events, "
          f"{len({k[0] for k in full})} models).\n",
          "## Is the retrieved evidence actually referred to in the trace?\n",
          "Detected by an explicit reference to the supplied material (\"Source 2\", \"the search results\", "
          "\"according to the context\"). This is a lower bound: a trace can use retrieved content without naming it.\n",
          "| condition | traces | explicitly reference retrieved material | carry EVIDENCE_CITED |", "|---|---|---|---|"]
    for cond in ("base", "ws_cutoff", "ws"):
        ts = [traces[v[cond]["trace_id"]] for v in full.values()]
        ref = np.mean([bool(RETRIEVAL_REF.search(t["trace"])) for t in ts])
        ev = np.mean([v[cond]["label"] for v in full.values()])
        md.append(f"| {cond} | {len(ts):,} | {100*ref:.1f}% | {100*ev:.1f}% |")
    md.append("\n## Does the conclusion change, and does it change more when the evidence is referenced?\n")
    chg = collections.defaultdict(lambda: [0, 0])
    for k, v in full.items():
        tb = traces[v["base"]["trace_id"]]
        for cond in ("ws_cutoff", "ws"):
            tc = traces[v[cond]["trace_id"]]
            if tb.get("parsed_answer") is None or tc.get("parsed_answer") is None: continue
            referenced = bool(RETRIEVAL_REF.search(tc["trace"]))
            chg[(cond, referenced)][0] += int(str(tb["parsed_answer"]) != str(tc["parsed_answer"]))
            chg[(cond, referenced)][1] += 1
    md.append("| condition vs base | retrieved material referenced | answer changed | n |"); md.append("|---|---|---|---|")
    for cond in ("ws_cutoff", "ws"):
        for referenced in (True, False):
            c, n = chg[(cond, referenced)]
            if n: md.append(f"| {cond} | {'yes' if referenced else 'no'} | {100*c/n:.1f}% | {n:,} |")
    md.append("\n## Code prevalence shift across conditions, on the matched triples\n")
    md.append("| code | base | WS+Cutoff | WS | WS+Cutoff minus base [95% CI] | p (Holm) |"); md.append("|---|---|---|---|---|---|")
    res, ps = [], []
    for code in [c for c in P.CODES if c in rel]:
        t2 = collections.defaultdict(dict)
        for r in by[code]: t2[(r["model"], r["task"], r["id"])][r["condition"]] = r
        f2 = {k: v for k, v in t2.items() if {"base", "ws_cutoff", "ws"} <= set(v)}
        if len(f2) < 100: continue
        b = np.array([v["base"]["label"] for v in f2.values()], float)
        wc = np.array([v["ws_cutoff"]["label"] for v in f2.values()], float)
        w = np.array([v["ws"]["label"] for v in f2.values()], float)
        ids = [k[2] for k in f2]
        W = S.boot_events(ids, 1000)
        d = S.wmean(wc - b, W)
        lo, hi = np.percentile(d, [2.5, 97.5])
        p = float(min(1.0, 2 * min(((d <= 0).sum() + 1) / (len(d) + 1), ((d >= 0).sum() + 1) / (len(d) + 1))))
        res.append((code, b.mean(), wc.mean(), w.mean(), float(wc.mean() - b.mean()), float(lo), float(hi))); ps.append(p)
    for (code, mb, mwc, mw, dd, lo, hi), a in zip(res, S.holm(ps)):
        md.append(f"| {code} | {100*mb:.1f}% | {100*mwc:.1f}% | {100*mw:.1f}% | {100*dd:+.1f} pts [{100*lo:+.1f}, {100*hi:+.1f}] | {S.fmtp(a)} |")
    (F / "results.md").write_text("\n".join(md) + "\n")
    print("F written")

    # ================= G: trace length
    G = C.STUDY / "analyses" / "G_trace_length"
    md = ["# Analysis G — trace length and correctness\n",
          "Does a longer stated justification accompany a better answer once item difficulty is held fixed? "
          "Predictor is log word count, standardised within task. Random intercepts for event and model.\n",
          "| task | model | n | beta per SD of log length [95% CI] | p (Holm) | mean words, correct | mean words, wrong |",
          "|---|---|---|---|---|---|---|"]
    from a7_analyze_ab import OUTCOME
    res, ps = [], []
    for task in ["binary_merged"] + C.TASKS:
        ycol, fam, _ = OUTCOME[task]
        tsel = (("binary", "binary_perturbed") if task == "binary_merged" else (task,))
        pool = [r for r in by["EVIDENCE_CITED"] if r["task"] in tsel and r["condition"] == "base" and r[ycol] is not None]
        for scope, msel in [("all", None)] + [("model", m) for m in sorted({r["model"] for r in rows})]:
            sel = [r for r in pool if msel is None or r["model"] == msel]
            if len(sel) < 150: continue
            lw = np.log1p(np.array([r["trace_words"] for r in sel], float))
            x = (lw - lw.mean()) / (lw.std() or 1)
            y = np.array([float(r[ycol]) for r in sel])
            g = S.glmm_effect(y, x, [r["id"] for r in sel], models=([r["model"] for r in sel] if msel is None else None), family=fam)
            corr = np.array([bool(r["correct"]) if r["correct"] is not None else (float(r[ycol]) >= 5.0) for r in sel])
            res.append((task, msel or "all (pooled)", g, float(np.mean([s["trace_words"] for s, c in zip(sel, corr) if c]) if corr.any() else np.nan),
                        float(np.mean([s["trace_words"] for s, c in zip(sel, corr) if not c]) if (~corr).any() else np.nan)))
            ps.append(g["p"])
    for (task, m, g, wc, ww), a in zip(res, S.holm(ps)):
        md.append(f"| {task} | {m} | {g['n']:,} | {S.fmt(g['beta'])} [{S.fmt(g['lo'])}, {S.fmt(g['hi'])}] | {S.fmtp(a)} | {S.fmt(wc,0)} | {S.fmt(ww,0)} |")
    md.append("\n`binary_merged` pools the original and perturbed variants of each event and is the row to read for "
              "the binary task: the single-variant rows confound length with the direction of the answer, because "
              "ground truth is Yes for every original item and No for every perturbed one.\n")
    md.append("\nA positive beta means longer justifications accompany better outcomes at equal item difficulty. "
              "Length is a property of the model's style as much as of the item, so the pooled fits carry a model "
              "random intercept and the per-model fits hold style fixed by construction.\n")
    (G / "results.md").write_text("\n".join(md) + "\n")
    print("G written")


if __name__ == "__main__":
    main()
