#!/usr/bin/env python3
"""make_si_subdomain_overleaf.py - SI sub-domain predictability tables (tab:subdomain_binary/date/mcq) for the nine
Table-1 models on the FULL corpus (all events; DeepSeek R1 original corpus only). Same layout as the submitted tables:
top 3 and bottom 3 sub-domains per area, ranked by the cross-model mean; values in %; n = mean items per model.
An event counts in every sub-category it lists. A sub-domain needs a mean n >= 10 (Binary: >= 10 items of each variant).
Binary = balanced accuracy (mean of original and perturbed accuracy), not pooled accuracy as in the submitted table.
Areas with <= 6 qualifying sub-domains list each once (the submitted tables repeated rows in that case)."""
import json, statistics as st, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "run_evaluation")); import make_table1_overleaf as T
OUT = ROOT / "manuscript_updates/si_tables"; OUT.mkdir(parents=True, exist_ok=True)
AREAS = ["Biology", "Artificial Intelligence", "Medicine", "Neuroscience", "Materials Science", "Physics", "Environmental Science", "Chemistry", "Other"]
KEEP = set(AREAS[:-1])
meta = {}
for b in T.BENCH:
    for l in open(ROOT / b):
        if l.strip():
            r = json.loads(l); a = r["main_area"] if r["main_area"] in KEEP else "Other"
            meta[r["id"]] = (a, [s for s in (r.get("sub_categories") or []) if s] or ["Unknown"])
M = [m[0] for m in T.MODELS]; NEW = {m[0] for m in T.MODELS if m[5]}
# acc[model][(area,sub)][task] -> list
acc = {m: defaultdict(lambda: defaultdict(list)) for m in M}
for name, cut, icon, op, ep, new in T.MODELS:
    seen = set()
    for p in [op] + ([ep] if ep else []):
        for r in json.load(open(ROOT / p))["results"]:
            if r["id"] in seen or r["id"] not in meta: continue
            seen.add(r["id"]); a, subs = meta[r["id"]]; t = r["tasks"]
            for s in set(subs):
                for k in ("binary", "binary_perturbed", "mcq"):
                    if t.get(k) and "correct" in t[k]: acc[name][(a, s)][k].append(1.0 if t[k]["correct"] else 0.0)
                if t.get("date") and t["date"].get("score") is not None: acc[name][(a, s)]["date"].append(t["date"]["score"])
def cell(m, key, task):
    d = acc[m][key]
    if task == "binary":
        o, q = d["binary"], d["binary_perturbed"]
        return (100 * (st.fmean(o) + st.fmean(q)) / 2, len(o) + len(q)) if len(o) >= 10 and len(q) >= 10 else (None, 0)
    v = d[task]; return (100 * st.fmean(v), len(v)) if len(v) >= 10 else (None, 0)
def table(task, label, title, centre_fn, chance_txt):
    rows_by_area = {}
    allmeans = []
    for a in AREAS:
        keys = {k for m in M for k in acc[m] if k[0] == a and k[1] != "Unknown"}
        rows = []
        for k in keys:
            vals = [cell(m, k, task) for m in M]; ok = [v for v, n in vals if v is not None]
            if len(ok) < 5: continue   # need most models
            rows.append((st.fmean(ok), k[1], vals, st.fmean([n for v, n in vals if v is not None])))
        rows.sort(key=lambda x: -x[0]); rows_by_area[a] = rows; allmeans += [r[0] for r in rows]
    centre = centre_fn(allmeans)
    def shade(v):
        if v is None: return "---"
        d = v - centre; k = min(30, max(5, round(abs(d) * 0.85)))
        return rf"\cellcolor{{{'green' if d >= 0 else 'red'}!{k}}} {v:.0f}"
    hdr = r"\textbf{Sub-domain} & $\boldsymbol{n}$ & \textbf{Mean} & " + " & ".join(
        (rf"\rotatebox{{55}}{{\revise{{\textbf{{{m}}}}}}}" if m in NEW else rf"\rotatebox{{55}}{{\textbf{{{m}}}}}") for m in M) + r" \\"
    nc = 3 + len(M)
    L = [r"\setlength{\tabcolsep}{2.5pt}", r"\renewcommand{\arraystretch}{0.95}", r"\begin{revblock}", r"{\scriptsize",
         r"\begin{longtable}{@{}l r r " + "r " * len(M) + "@{}}",
         rf"\caption{{{title} Chance level = {chance_txt}. Cells shaded \colorbox{{green!25}}{{\,}} above / \colorbox{{red!25}}{{\,}} below {'chance' if task != 'date' else f'the cross-model mean ({centre:.0f})'}. Cross-model \textit{{mean}} shown; best individual model per row in \textbf{{bold}}. Top 3 (most predictable) and bottom 3 (least predictable) sub-domains per area, ranked by cross-model mean; an area with six or fewer sub-domains lists each once. $n$: mean sample size across models. All events of the full corpus (January 2024--August 2026); DeepSeek R1: original corpus only. A sub-domain needs at least 10 items for at least five models; ``---'': fewer than 10 items for that model. Blue: models added in the revision.}} \label{{{label}}} \\",
         r"\toprule", hdr, r"\midrule", r"\endfirsthead", rf"\multicolumn{{{nc}}}{{l}}{{\small\tablename~\thetable{{}} \textit{{(continued)}}}} \\",
         r"\toprule", hdr, r"\midrule", r"\endhead", r"\midrule", rf"\multicolumn{{{nc}}}{{r}}{{\small\textit{{Continued on next page}}}} \\", r"\endfoot",
         r"\bottomrule", r"\endlastfoot"]
    for a in AREAS:
        rows = rows_by_area[a]
        if not rows: continue
        L.append(rf"\multicolumn{{{nc}}}{{@{{}}l@{{}}}}{{\cellcolor{{gray!18}}\quad\textbf{{{a}}}}} \\*")
        blocks = [rows] if len(rows) <= 6 else [rows[:3], rows[-3:]]
        for bi, blk in enumerate(blocks):
            for ri, (mu, s, vals, n) in enumerate(blk):
                best = max(v for v, _ in vals if v is not None)
                cs = [("---" if v is None else (shade(v).replace(f" {v:.0f}", rf" \textbf{{{v:.0f}}}") if round(v) == round(best) else shade(v))) for v, _ in vals]
                end = r" \\*" if not (bi == len(blocks) - 1 and ri == len(blk) - 1) else r" \\"
                s_esc = s.replace('&', r'\&')
                L.append(f"{s_esc} & {n:.0f} & {shade(mu)} & " + " & ".join(cs) + end)
            if bi == 0 and len(blocks) == 2: L.append(rf"\cmidrule{{1-{nc}}}")
        L.append(r"\noalign{\medskip}")
    L += [r"\end{longtable}", r"}", r"\end{revblock}"]
    return "\n".join(L) + "\n"
(OUT / "subdomain_binary.tex").write_text(table("binary", "tab:subdomain_binary", r"Sub-domain predictability --- Binary prediction (balanced accuracy: mean of original GT=yes and perturbed GT=no accuracy) (values in \%).", lambda m: 50, r"50\%"))
(OUT / "subdomain_date.tex").write_text(table("date", "tab:subdomain_date", r"Sub-domain predictability --- Date prediction score (values: score $\times$100).", lambda m: st.fmean(m), "n/a"))
(OUT / "subdomain_mcq.tex").write_text(table("mcq", "tab:subdomain_mcq", r"Sub-domain predictability --- MCQ, 4-choice (values in \%).", lambda m: 25, r"25\%"))
for f in ("subdomain_binary", "subdomain_date", "subdomain_mcq"): print(f, sum(1 for l in open(OUT / f"{f}.tex") if "cellcolor" in l and "gray" not in l))
