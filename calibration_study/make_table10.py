"""
make_table10.py — manuscript Table 10 (model ensembling, arm F) from tables/ensemble.json.
Writes tables/table10_ensemble.tex and tables/table10_ensemble.md. Nothing is hand-typed;
rerun after analyze.py. Both panels (three-model, all six models), all three aggregation
rules, and the full metric set used by the single-model tables (binary: Brier, BSS, REL,
RES, log loss, ECE, AUROC, bias index; MCQ: accuracy, mean confidence, Brier, log loss,
ECE, REL, RES, AUROC on confidence-in-chosen-option versus correctness).
"""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

T = C.TABLES
E = json.load(open(T / "ensemble.json"))
PANELS = (("panel3", "3-model"), ("all_models", "All-model"))
RULES = (("mean_prob", "mean probability"), ("mean_logit", "mean logit"), ("majority", "majority vote"))
BIN = [("brier", "Brier", 3, "low"), ("bss", "BSS", 2, "high"), ("rel", "REL", 3, "low"), ("res", "RES", 3, "high"),
       ("logloss", "Log loss", 3, "low"), ("ece", "ECE", 3, "low"), ("auroc", "AUROC", 3, "high"), ("bias_index", "Bias", 2, None)]
MCQ = [("accuracy", "Accuracy", 3, "high"), ("mean_conf", "Mean conf.", 3, None), ("brier_c", "Brier", 3, "low"),
       ("logloss_c", "Log loss", 3, "low"), ("ece_c", "ECE", 3, "low"), ("rel_c", "REL", 3, "low"), ("res_c", "RES", 3, "high"),
       ("auroc_c", "AUROC", 3, "high")]
ARROW = {"low": r"$\downarrow$", "high": r"$\uparrow$", None: ""}


def cell(pn, task, rule):
    r = E["panels"][pn]["tasks"][task][rule]
    return r.get("post") or r["all"]


def pt(c, k, dp, signed=False, tex=False):
    v = c[k]["value"]
    s = (f"{v:+.{dp}f}" if signed else f"{v:.{dp}f}")
    if tex:  # typeset the sign in math mode so LaTeX uses a real minus
        s = s.replace("-", "$-$", 1).replace("+", "$+$", 1)
    return s


def ci(c, k, dp):
    lo, hi = c[k]["ci"]; return f"[{lo:.{dp}f}, {hi:.{dp}f}]"


def rows(task, cols):
    out = []
    for pn, plab in PANELS:
        for rk, rlab in RULES:
            c = cell(pn, task, rk)
            out.append((f"{plab} {rlab}", int(c["n"]["value"]), c))
    return out


def best(rs, k, direction):
    if direction is None: return None
    vals = [r[2][k]["value"] for r in rs]
    return (min if direction == "low" else max)(vals)


def tex():
    L = [r"\begin{table}[t]", r"\centering", r"\small",
         r"\caption{\textbf{Effects of model ensembling on calibration and forecasting performance.} "
         r"Ensembles are constructed from Base-condition predictions and therefore require no additional model inference. "
         r"The three-model ensemble pools LLaMA 3.3 70B, GPT-5.4 and GPT-4o; the all-model ensemble pools the six panel models "
         r"with stored confidence (LLaMA 3.3 70B, DeepSeek R1, GPT-4o, GPT-OSS 20B, GPT-5.4, Claude Sonnet 4.5). "
         r"For Binary forecasting we compare mean-probability, mean-logit and majority-vote aggregation of each member's $P(\mathrm{Yes})$ "
         r"and report probabilistic calibration and discrimination metrics. For MCQ, predictions are aggregated by option text because "
         r"candidate order is independently permuted across models, and metrics score confidence in the chosen option against correctness.}",
         r"\label{tab:ensemble}"]
    # binary
    rs = rows("binary_merged", BIN)
    L += [r"\vspace{2pt}\textbf{Binary event-realization forecasting}\\[2pt]",
          r"\begin{tabular}{l r " + "r" * len(BIN) + "}", r"\toprule",
          "Ensemble & $N$ & " + " & ".join(f"{lab}{ARROW[d]}" for _, lab, _, d in BIN) + r" \\", r"\midrule"]
    bests = {k: best(rs, k, d) for k, _, _, d in BIN}
    for lab, n, c in rs:
        cells = []
        for k, _, dp, d in BIN:
            s = pt(c, k, dp, signed=(k in ("bias_index", "bss")), tex=True)
            if d and abs(c[k]["value"] - bests[k]) < 1e-12: s = r"\textbf{" + s + "}"
            cells.append(s)
        L.append(f"{lab} & {n} & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\\[8pt]"]
    # mcq
    rs = rows("mcq", MCQ)
    L += [r"\textbf{MCQ mechanism forecasting}\\[2pt]",
          r"\begin{tabular}{l r " + "r" * len(MCQ) + "}", r"\toprule",
          "Ensemble & $N$ & " + " & ".join(f"{lab}{ARROW[d]}" for _, lab, _, d in MCQ) + r" \\", r"\midrule"]
    bests = {k: best(rs, k, d) for k, _, _, d in MCQ}
    for lab, n, c in rs:
        cells = []
        for k, _, dp, d in MCQ:
            s = pt(c, k, dp, tex=True)
            if d and abs(c[k]["value"] - bests[k]) < 1e-12: s = r"\textbf{" + s + "}"
            cells.append(s)
        L.append(f"{lab} & {n} & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    # notes with CIs
    b3, b6 = cell("panel3", "binary_merged", "mean_prob"), cell("all_models", "binary_merged", "mean_prob")
    m3, m6 = cell("panel3", "mcq", "mean_prob"), cell("all_models", "mcq", "mean_prob")
    L += [r"\begin{flushleft}\footnotesize\textit{Notes.} "
          f"Each ensemble is evaluated on the intersection of items answered by every member: $N={int(b3['n']['value'])}$ binary and "
          f"$N={int(m3['n']['value'])}$ MCQ items for the three-model ensemble, $N={int(b6['n']['value'])}$ and $N={int(m6['n']['value'])}$ "
          r"for the all-model ensemble. Binary metrics score $P(\mathrm{Yes})$ against the event outcome (original question $=1$, perturbed twin $=0$). "
          r"BSS $=1-\mathrm{Brier}/\mathrm{UNC}$ is the Brier skill score against the constant base-rate forecast; REL and RES are the Murphy "
          r"reliability and resolution terms; Bias is the response-bias index (accuracy on original minus accuracy on perturbed items). "
          r"95\% confidence intervals from 10,000 event-level bootstrap resamples: three-model mean probability Brier "
          f"{pt(b3,'brier',3)} {ci(b3,'brier',3)}, BSS {pt(b3,'bss',2,True)} {ci(b3,'bss',2)}, AUROC {pt(b3,'auroc',3)} {ci(b3,'auroc',3)}; "
          f"all-model mean probability Brier {pt(b6,'brier',3)} {ci(b6,'brier',3)}, BSS {pt(b6,'bss',2,True)} {ci(b6,'bss',2)}, "
          f"REL {pt(b6,'rel',3)} {ci(b6,'rel',3)}, RES {pt(b6,'res',3)} {ci(b6,'res',3)}, AUROC {pt(b6,'auroc',3)} {ci(b6,'auroc',3)}, "
          f"bias {pt(b6,'bias_index',2,True)} {ci(b6,'bias_index',2)}. "
          f"MCQ mean-probability accuracy {pt(m3,'accuracy',3)} {ci(m3,'accuracy',3)} (three-model) and {pt(m6,'accuracy',3)} {ci(m6,'accuracy',3)} (all-model); "
          f"Brier {pt(m3,'brier_c',3)} {ci(m3,'brier_c',3)} and {pt(m6,'brier_c',3)} {ci(m6,'brier_c',3)}; "
          f"AUROC {pt(m3,'auroc_c',3)} {ci(m3,'auroc_c',3)} and {pt(m6,'auroc_c',3)} {ci(m6,'auroc_c',3)}. "
          r"Bold marks the best value in each column. Full intervals for every cell are in \texttt{calibration\_study/tables/ensemble.md}.",
          r"\end{flushleft}", r"\end{table}"]
    return "\n".join(L) + "\n"


def md():
    L = ["# Table 10 — model ensembling (arm F, derived from arm A)", "",
         "Point estimate [95% CI], 10,000 event-level bootstrap resamples. Post-cutoff partition (identical to `all` for every ensemble member's items).", "",
         "## Binary event-realization forecasting (P(Yes) vs outcome, original + perturbed)", "",
         "| Ensemble | N | " + " | ".join(lab for _, lab, _, _ in BIN) + " |", "|---|---|" + "---|" * len(BIN)]
    for lab, n, c in rows("binary_merged", BIN):
        L.append(f"| {lab} | {n} | " + " | ".join(f"{pt(c,k,dp,k in ('bias_index','bss'))} {ci(c,k,dp)}" for k, _, dp, _ in BIN) + " |")
    L += ["", "## MCQ mechanism forecasting (confidence in chosen option vs correctness; aggregated by option text)", "",
          "| Ensemble | N | " + " | ".join(lab for _, lab, _, _ in MCQ) + " |", "|---|---|" + "---|" * len(MCQ)]
    for lab, n, c in rows("mcq", MCQ):
        L.append(f"| {lab} | {n} | " + " | ".join(f"{pt(c,k,dp)} {ci(c,k,dp)}" for k, _, dp, _ in MCQ) + " |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    (T / "table10_ensemble.tex").write_text(tex())
    (T / "table10_ensemble.md").write_text(md())
    print(md())
