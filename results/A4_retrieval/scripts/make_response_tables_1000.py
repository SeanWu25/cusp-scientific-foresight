"""Response-letter Tables (tab:gaps_pre, tab:gaps_post, tab:fixed_packet_agreement) on the 1,000 A4.3 events, in the
layout of sean_response.tex, from tables/A4_3_gaps_pre_post_1000.json and tables/A4_3_correlation_1000.json
(A43_EVENTS=1000 a43_pre_post_correlation.py). Writes tables/resp_{gaps_pre,gaps_post,agreement}_1000.tex. No inference."""
import json, sys
from pathlib import Path
OUT = Path("/home/seanwu/FutureScience/results/A4_retrieval"); T = OUT / "tables"
cells = json.load(open(T / "A4_3_gaps_pre_post_1000.json")); corr = json.load(open(T / "A4_3_correlation_1000.json"))["cell_level"]
ORDER = ["GPT-4o", "GPT-5.4", "LLaMA 3.3 70B", "Claude S4.5", "Claude Sonnet 5", "GPT-5.6 Sol"]
TASKS = [("Binary", "Binary"), ("Binary (pert.)", "Binary (pert.)"), ("MCQ", "MCQ"), ("FRQ (0-10)", "FRQ (0--10)"), ("Date (0-1)", "Date")]
def v(x):
    s = "+" if x >= 0 else "-"; a = abs(x); t = f"{a:.3f}"
    return s + (t[1:] if a < 1 else t)
def ci(c): return f"{{\\tiny[${v(c[0])},{v(c[1])}$]}}"
def cell(c, k):
    return f"${v(c[k])}$ {ci(c[k + '_ci'])}" if k in c else "--"
J = {(c["scope"], c["model"], c["task"]): c for c in cells}
HEAD = r"""\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.12}

\begin{tabular}{l l r c c c c}
\toprule
& & & \multicolumn{2}{c}{\textbf{Knowledge gap}} & \multicolumn{2}{c}{\textbf{Forecasting gap}} \\
\cmidrule(lr){4-5}
\cmidrule(lr){6-7}
\textbf{Model} & \textbf{Task} & $N$ & \textbf{Original} & \textbf{Fixed} & \textbf{Original} & \textbf{Fixed} \\
\midrule
"""
def gaps(scope):
    title = "Pre" if scope == "pre" else "Post"
    L = [r"\begin{table}[p]", r"\centering", r"\footnotesize", "", r"\caption{",
         rf"\textbf{{{title}-cutoff gap estimates under the original and fixed-evidence retrieval designs (1,000 events).}}",
         r"Values are paired performance differences on matched events with 95\%", r"confidence intervals.",
         r"Knowledge gap $=\mathrm{WS+Cutoff}-\mathrm{Base}$;", r"forecasting gap $=\mathrm{WS}-\mathrm{WS+Cutoff}$.",
         r"Binary, MCQ, and Date are reported on the $[0,1]$ scale; FRQ is reported", r"in rubric points on the 0--10 scale.", "}",
         rf"\label{{tab:gaps_{scope}}}", "", HEAD]
    blocks = []
    for m in ORDER:
        rows = [(lab, J.get((scope, m, t))) for t, lab in TASKS]
        if all(c is None or c["n"] == 0 for _, c in rows): continue
        B = []
        for i, (lab, c) in enumerate(rows):
            first = (m.replace("LLaMA 3.3 70B", "LLaMA 3.3 70B") if i == 0 else "")
            if c is None or c["n"] == 0: B.append(f"{first}\n& {lab}\n& 0\n& \\multicolumn{{4}}{{c}}{{\\textit{{no events}}}} \\\\"); continue
            if c.get("suppressed"): B.append(f"{first}\n& {lab}\n& {c['n']}\n& \\multicolumn{{4}}{{c}}{{\\textit{{$n<20$}}}} \\\\"); continue
            B.append(f"{first}\n& {lab}\n& {c['n']}\n& {cell(c, 'know_orig')}\n& {cell(c, 'know_fixed')}\n& {cell(c, 'fore_orig')}\n& {cell(c, 'fore_fixed')} \\\\")
        blocks.append("\n\n".join(B))
    L.append("\n\n\\addlinespace\n\n".join(blocks))
    notes = [r"\bottomrule", r"\end{tabular}", "", r"\vspace{3pt}", r"\begin{minipage}{0.98\textwidth}", r"\scriptsize", r"\textit{Notes.}",
             "The 1,000 events are the pinned 500-event subset and 500 events published from March to August 2026, which are post-cutoff events for every model.",
             ("Pre-cutoff events have a publication month at or before the model's knowledge cutoff. GPT-4o and LLaMA~3.3 are not shown because no event is a pre-cutoff event for these models."
              if scope == "pre" else "Post-cutoff events have a publication month after the model's knowledge cutoff."),
             "$N$ is the number of matched events; gap estimates are reported only for partitions with at least 20 matched events.",
             "Original denotes the original retrieval design, in which each evaluated model generated its own search query; for the 500 added events, each model was run again with the harness and settings of its original run.",
             "Fixed denotes the replication using evidence packets generated independently of the evaluated model.",
             "The original WS runs of GPT-4o and GPT-5.4 used the OpenAI web-search tool; all other runs used the single-query You.com pipeline.",
             "The fixed-packet FRQ answers of GPT-4o, GPT-5.4 and Claude S4.5 had a limit of 250 output tokens (original: 2,048 for GPT-4o and GPT-5.4).",
             "The Fixed columns are the values shown in revised Figure~3a.", "Brackets report 95\\% confidence intervals.", r"\end{minipage}", "", r"\end{table}"]
    return "\n".join(L + notes) + "\n"
def agreement():
    f = lambda k, sc: corr.get(f"{k}:{sc}")
    def rc(x, bold):
        b = (lambda s: f"\\textbf{{{s}}}") if bold else (lambda s: s)
        r_, m_ = "%.2f" % x["pearson"], "%.3f" % x["mad"]
        return (b(r_) + " {\\tiny[%.2f, %.2f]}" % tuple(x["pearson_ci"]) + "\n& " + b(m_) + " {\\tiny[%.3f, %.3f]}" % tuple(x["mad_ci"]))
    L = [r"\begin{table}[t]", r"\centering", r"\caption{", r"\textbf{Agreement between the original retrieval experiment and the", r"fixed-evidence experiment (1,000 events).}",
         r"Pearson $r$ measures agreement between the two experimental setups, and MAD", r"denotes their mean absolute difference. Values in brackets are 95\% confidence", r"intervals.", "}",
         r"\label{tab:fixed_packet_agreement}", "", r"\small", r"\setlength{\tabcolsep}{4pt}", r"\renewcommand{\arraystretch}{1.12}", "",
         r"\begin{tabular}{lcccc}", r"\toprule", "&", r"\multicolumn{2}{c}{\textbf{Pre- and post-cutoff}}", "&", r"\multicolumn{2}{c}{\textbf{Post-cutoff only}}", r"\\",
         r"\cmidrule(lr){2-3}", r"\cmidrule(lr){4-5}", "", r"\textbf{Quantity}", r"& \boldmath$r$", r"& \textbf{MAD}", r"& \boldmath$r$", r"& \textbf{MAD}", r"\\", r"\midrule", ""]
    for k, lab, bold in (("wscut", "WS+Cutoff performance", False), ("ws", "Unrestricted WS performance", False), ("know", "Knowledge gap", True), ("fore", "Forecasting gap", True)):
        L += [lab, "& " + rc(f(k, "all"), bold), "& " + rc(f(k, "post"), bold), r"\\", ""]
    na, npo = f("know", "all")["n_cells"], f("know", "post")["n_cells"]
    L += [r"\bottomrule", r"\end{tabular}", "", r"\vspace{3pt}", r"\begin{minipage}{0.96\textwidth}", r"\footnotesize", r"\textit{Notes.}",
          r"The knowledge gap is defined as $\Delta_{\mathrm{know}}=\mathrm{WS+Cutoff}-\mathrm{Base}$ and the forecasting gap as $\Delta_{\mathrm{fore}}=\mathrm{WS}-\mathrm{WS+Cutoff}$.",
          r"FRQ scores are divided by 10 so that all task scores are within $[0,1]$ scale.",
          f"Each point is one model $\\times$ task $\\times$ partition cell with at least 20 matched events among the 1,000 events ({na} cells; {npo} post-cutoff). Confidence intervals are 10,000 cell-level bootstrap resamples.",
          r"\end{minipage}", "", r"\end{table}"]
    return "\n".join(L) + "\n"
(T / "resp_gaps_pre_1000.tex").write_text(gaps("pre")); (T / "resp_gaps_post_1000.tex").write_text(gaps("post")); (T / "resp_agreement_1000.tex").write_text(agreement())
for k in ("wscut", "ws", "know", "fore"):
    for sc in ("all", "post"):
        x = corr[f"{k}:{sc}"]; print(f"{k:6s} {sc:4s} cells={x['n_cells']:2d} r={x['pearson']:.2f} [{x['pearson_ci'][0]:.2f},{x['pearson_ci'][1]:.2f}] MAD={x['mad']:.3f}")
