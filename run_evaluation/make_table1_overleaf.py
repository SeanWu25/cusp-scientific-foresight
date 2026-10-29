#!/usr/bin/env python3
"""
make_table1_overleaf.py — main-text Table 1 in the exact layout of the submitted manuscript (main.tex, tab:main_results).

  --corpus orig      reproduces the submitted table (original corpus, six models) — used as a check
  --corpus full      revision table: original + Apr–Aug 2026 extension, nine models (submitted six + Claude Opus 4.8,
                     Claude Sonnet 5, GPT-5.6 Sol); DeepSeek R1 original corpus only (deployment retired)
Definitions: Binary = BALANCED accuracy (mean of the accuracies on original and perturbed questions; revision, replaces the
submitted merged accuracy); n_pre = number of pre-cutoff EVENTS (revision; the submitted table counted binary items); MCQ accuracy; FRQ rubric mean, Pass = share >= 5;
mean predicted month, signed error mean / median (predicted - actual), share within 3/6/12/24 months, Date = mean exp(-0.1|Δ|)
over all scored items. Post-cutoff value; Δ = post − pre beneath for Binary, MCQ, FRQ, Date. Partition: pre if pub month < cutoff month.
Δ shading: cellgood > +0.05, cellworse < −0.03, cellbad < −0.10 (raw units, as submitted). Models sorted by post MCQ.
Rows of models added in revision are wrapped cell by cell in \revise{} (blue).
"""
import argparse, json, os, statistics as st, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FR = "run_evaluation/frq_results/"; EXT = "results_extension_run2/reports/"
MODELS = [  # name, cutoff, icon, orig report, ext report, new-in-revision
    ("GPT-5.4", "2025-08", "openai_logo.png", FR + "gpt_5_4_eval.json", EXT + "gpt54_base.json", False),
    ("Claude S4.5", "2025-01", "claude.png", FR + "claude_sonnet.json", EXT + "sonnet45_base.json", False),
    ("DeepSeek R1", "2024-07", "deepseek_logo.png", FR + "deepseek_r1.json", None, False),
    ("GPT-4o", "2023-10", "openai_logo.png", FR + "gpt_4o_reeval.json", EXT + "gpt4o_base.json", False),
    ("GPT-OSS", "2024-06", "openai_logo.png", FR + "gpt_oss_20B_reeval.json", EXT + "gptoss20b_base.json", False),
    ("LLaMA 3.3", "2023-12", "llama.png", FR + "llama_3_3_full.json", EXT + "llama33_base.json", False),
    ("Claude Opus 4.8", "2026-01", "claude.png", "results_opus48_run1/reports/base_medium_run1.json", EXT + "opus48_base_run1.json", True),
    ("Claude Sonnet 5", "2026-01", "claude.png", "results_sonnet5_run1/reports/base_medium_run1.json", EXT + "sonnet5_base_run1.json", True),
    ("GPT-5.6 Sol", "2026-02", "openai_logo.png", "results_sol_run1/reports/base_medium_run1.json", EXT + "sol_base.json", True),
]
BENCH = ["archive/data/canonical/merged_validated_cusp_fixed.jsonl", "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"]
# 2026-10-25: events in the cutoff month count as PRE-cutoff (same rule as the information-access gaps, gap_decomposition.py).
# Set False to reproduce the earlier tables, which counted them as post-cutoff.
CUTOFF_MONTH_PRE = True
MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def mo(s):
    try: y, m = str(s)[:7].split("-"); return int(y) * 12 + int(m)
    except Exception: return None


def ym(m):  # post-cutoff mean, rounded to the nearest month
    m = int(round(m)); return f"{(m - 1) // 12:04d}-{(m - 1) % 12 + 1:02d}"


def load(corpus, six_only):
    pub = {}
    for b in BENCH[: 1 if corpus == "orig" else 2]:
        for l in open(ROOT / b):
            if l.strip(): r = json.loads(l); pub[r["id"]] = str(r["publication_date"])[:7]
    rows = []
    for name, cut, icon, op, ep, new in MODELS:
        if six_only and new: continue
        A = defaultdict(lambda: defaultdict(list)); seen = set(); cm = mo(cut)
        for p in [op] + ([ep] if corpus == "full" and ep else []):
            for r in json.load(open(ROOT / p))["results"]:
                if r["id"] in seen or r["id"] not in pub: continue
                seen.add(r["id"]); part = "pre" if (mo(pub[r["id"]]) <= cm if CUTOFF_MONTH_PRE else mo(pub[r["id"]]) < cm) else "post"; t = r.get("tasks", {})
                A[part]["events"].append(1.0)
                for task in ("binary", "binary_perturbed"):
                    v = t.get(task)
                    if v and not v.get("skipped") and "correct" in v: A[part][task].append(1.0 if v["correct"] else 0.0)
                v = t.get("mcq")
                if v and not v.get("skipped") and "correct" in v: A[part]["mcq"].append(1.0 if v["correct"] else 0.0)
                v = t.get("frq")
                if v and not v.get("skipped") and v.get("score") is not None: A[part]["frq"].append(float(v["score"]))
                v = t.get("date")
                if v and not v.get("skipped") and v.get("score") is not None:
                    A[part]["date"].append(float(v["score"]))
                    pd, gt = mo(v.get("parsed_date")), mo(v.get("ground_truth"))
                    if pd is not None and gt is not None: A[part]["pred"].append(pd); A[part]["gt"].append(gt); A[part]["err"].append(pd - gt)
        rows.append(dict(name=name, cut=cut, icon=icon, new=new, ext=bool(ep), A=A, n_pre=len(A["pre"]["events"])))
    return rows


def summ(a):
    m = lambda k: st.fmean(a[k]) if a.get(k) else None
    e = a.get("err", [])
    bal = (st.fmean(a["binary"]) + st.fmean(a["binary_perturbed"])) / 2 if a.get("binary") and a.get("binary_perturbed") else None
    return dict(binary=bal, mcq=m("mcq"), frq=m("frq"), pas=(100 * sum(x >= 5 for x in a["frq"]) / len(a["frq"]) if a.get("frq") else None),
                pred=m("pred"), err=m("err"), med=(st.median(e) if e else None), date=m("date"),
                **{f"w{k}": (100 * sum(abs(x) <= k for x in e) / len(e) if e else None) for k in (3, 6, 12, 24)})


def build(rows):
    for r in rows: r["post"], r["pre"] = summ(r["A"]["post"]), summ(r["A"]["pre"])
    rows.sort(key=lambda r: -r["post"]["mcq"])
    best = dict(binary=max, mcq=max, frq=max, pas=max, err=lambda v: min(v, key=abs), med=lambda v: min(v, key=abs),
                w3=max, w6=max, w12=max, w24=max, date=max)
    bv = {k: f([r["post"][k] for r in rows if r["post"][k] is not None]) for k, f in best.items()}
    out = []
    for r in rows:
        p = r["post"]
        def c(k, s): return rf"\textbf{{{s}}}" if p[k] is not None and abs(p[k] - bv[k]) < 1e-9 else s
        sg = lambda x: f"+{x:.1f}" if x >= 0 else f"$-${abs(x):.1f}"
        cells = [rf"\llmicon{{icons/{r['icon']}}} {r['name']}" + (r"$^\dagger$" if not r["ext"] and len(rows) > 6 else ""),
                 f"{MON[int(r['cut'][5:]) - 1]} {r['cut'][:4]}", (str(r["n_pre"]) if r["n_pre"] else r"{\textemdash}"),
                 c("binary", f"{p['binary']:.3f}"), c("mcq", f"{p['mcq']:.3f}"), c("frq", f"{p['frq']:.2f}"), c("pas", f"{p['pas']:.1f}"),
                 ym(p["pred"]), c("err", sg(p["err"])), c("med", sg(p["med"])),
                 c("w3", f"{p['w3']:.1f}"), c("w6", f"{p['w6']:.1f}"), c("w12", f"{p['w12']:.1f}"), c("w24", f"{p['w24']:.1f}"), c("date", f"{p['date']:.3f}")]
        def d(k, dp):
            if r["pre"][k] is None: return r"{\scriptsize\textcolor{gray}{---}}"
            x = round(round(p[k], dp) - round(r["pre"][k], dp), dp); s = ("$+$" if x >= 0 else "$-$") + f"{abs(x):.{dp}f}"
            if dp == 2 and abs(x) < 0.005: s = f"{0:.2f}"
            sh = "cellbad" if x < -0.10 else "cellworse" if x < -0.03 else "cellgood" if x > 0.05 else ""
            body = rf"{{\scriptsize\textcolor{{gray}}{{{s}}}}}"
            return (rf"\cellcolor{{{sh}}}" if sh else "") + body
        dl = ["", "", "", d("binary", 3), d("mcq", 3), d("frq", 2), "", "", "", "", "", "", "", "", d("date", 3)]
        if r["new"]:
            cells = [rf"\revise{{{x}}}" for x in cells]
            dl = [x.replace(r"\textcolor{gray}", r"\textcolor{revisionblue!60}") for x in dl]
        out.append(" & ".join(cells[:3]) + "\n  & " + " & ".join(cells[3:7]) + "\n  & " + " & ".join(cells[7:]) + r" \\" + "\n  " + " & ".join(dl) + r" \\" + "\n")
    gt = st.fmean([x for r in rows for x in r["A"]["post"]["gt"]])
    return out, rows, gt


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--corpus", choices=["orig", "full"], default="full"); a = ap.parse_args()
    body, rows, gt = build(load(a.corpus, six_only=(a.corpus == "orig")))
    print(f"% ground-truth mean (post rows pooled) = {ym(gt)}")
    print("\n".join(body))
    neg = [r["name"] for r in rows if r["post"]["err"] < 0]
    print("% models with negative mean signed error:", neg)
