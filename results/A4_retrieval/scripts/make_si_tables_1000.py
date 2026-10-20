"""SI table bodies (rows between \\midrule and \\bottomrule) for si_retrieval.tex on the 1,000 A4.3 events:
tab:si_ret_gaps_post, tab:si_ret_gaps_pre, tab:si_ret_agreement, tab:si_ret_agreement_frq.
From tables/A4_3_gaps_pre_post_1000.json and tables/A4_3_correlation_1000.json. Writes tables/si_rows_<label>_1000.tex. No inference."""
import json
from pathlib import Path
T = Path("/home/seanwu/FutureScience/results/A4_retrieval/tables")
cells = json.load(open(T / "A4_3_gaps_pre_post_1000.json")); corr = json.load(open(T / "A4_3_correlation_1000.json"))["cell_level"]
ORDER = ["GPT-4o", "GPT-5.4", "LLaMA 3.3 70B", "Claude S4.5", "Claude Sonnet 5", "GPT-5.6 Sol"]
TASKS = [("Binary", "Binary"), ("Binary (pert.)", "Binary (perturbed)"), ("MCQ", "MCQ"), ("FRQ (0-10)", "FRQ (0--10)"), ("Date (0-1)", "Date")]
s = lambda v: ("$+$" if v >= 0 else "$-$") + f"{abs(v):.3f}"
cell = lambda c, k: f"{s(c[k])} {{\\scriptsize[{s(c[k + '_ci'][0])}, {s(c[k + '_ci'][1])}]}}" if k in c else "--"
J = {(c["scope"], c["model"], c["task"]): c for c in cells}
def gaps(scope):
    out = []
    for m in ORDER:
        rows = [(lab, J.get((scope, m, t))) for t, lab in TASKS]
        if all(c is None or c["n"] == 0 for _, c in rows): continue
        for i, (lab, c) in enumerate(rows):
            first = m if i == 0 else ""
            if c is None or c["n"] == 0: out.append(f"{first} & {lab} & 0 & \\multicolumn{{4}}{{l}}{{\\textit{{no events}}}} \\\\"); continue
            if c.get("suppressed"): out.append(f"{first} & {lab} & {c['n']} & \\multicolumn{{4}}{{l}}{{\\textit{{suppressed}} ($n<20$)}} \\\\"); continue
            out.append(f"{first} & {lab} & {c['n']} & {cell(c, 'know_orig')} & {cell(c, 'know_fixed')} & {cell(c, 'fore_orig')} & {cell(c, 'fore_fixed')} \\\\")
        out.append(r"\addlinespace")
    return "\n".join(out[:-1]) + "\n"
def agree():
    out = []
    for k, lab in (("wscut", "WS+Cutoff score "), ("ws", "WS score        "), ("know", "Knowledge gap   "), ("fore", "Forecasting gap "), ("fore_x4o", "Forecasting gap, without GPT-4o")):
        parts = []
        for sc in ("all", "post"):
            x = corr[f"{k}:{sc}"]
            parts.append(f"{x['pearson']:.2f} [{x['pearson_ci'][0]:.2f}, {x['pearson_ci'][1]:.2f}] & {x['spearman']:.2f} & {x['mad']:.3f} [{x['mad_ci'][0]:.3f}, {x['mad_ci'][1]:.3f}] & {x['n_cells']}")
        out.append(f"{lab} & " + " & ".join(parts) + r" \\")
    return "\n".join(out) + "\n"
def agree_frq():
    out = []
    for k, lab in (("wscut_frq", "WS+Cutoff score"), ("ws_frq", "WS score       "), ("know_frq", "Knowledge gap  "), ("fore_frq", "Forecasting gap")):
        parts = []
        for sc in ("all", "post"):
            x = corr.get(f"{k}:{sc}")
            parts.append("-- & -- & --" if x is None else f"{x['pearson']:.2f} [{x['pearson_ci'][0]:.2f}, {x['pearson_ci'][1]:.2f}] & {x['mad']:.3f} [{x['mad_ci'][0]:.3f}, {x['mad_ci'][1]:.3f}] & {x['n_cells']}")
        out.append(f"{lab} & " + " & ".join(parts) + r" \\")
    return "\n".join(out) + "\n"
for lab, body in (("si_ret_gaps_post", gaps("post")), ("si_ret_gaps_pre", gaps("pre")), ("si_ret_agreement", agree()), ("si_ret_agreement_frq", agree_frq())):
    (T / f"si_rows_{lab}_1000.tex").write_text(body)
print("written")
