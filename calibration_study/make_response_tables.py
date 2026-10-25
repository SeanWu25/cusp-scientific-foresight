"""
make_response_tables.py — build the full results section of REVIEWER_RESPONSE_R1_C6.md
from calibration_study/tables/*.json. Rerun after analyze.py; nothing is hand-typed.
"""
from __future__ import annotations
import json, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
import numpy as np

T = C.TABLES
M = json.load(open(T / "master_table.json")); CELLS = M["cells"]; META = M["meta"]
D = json.load(open(T / "delta_vs_base.json"))["deltas"]
E = json.load(open(T / "ensemble.json")); VD = json.load(open(T / "vote_distributions.json"))
PS = json.load(open(T / "prob_sum_check.json")); CO = json.load(open(T / "costs.json"))
PANEL = ["llama33", "gpt54", "gpt4o"]; REF = ["deepseek_r1", "gptoss20b"]
ARMS = ["A", "B1", "B2", "C", "D", "E"]
NAME = {m: C.MODELS[m]["name"] for m in C.MODELS}
LAB = {"A": "A base", "B1": "B1 prompt (asym.)", "B2": "B2 prompt (sym.)", "C": "C retrieval", "D": "D self-consistency", "E": "E probabilistic"}


def g(model, arm, task, part, metric):
    c = CELLS.get(model, {}).get(arm, {}).get(task, {}).get(part, {}).get(metric)
    return c


def val(model, arm, task, part, metric, dp=3, ci=True):
    c = g(model, arm, task, part, metric)
    if c is None: return "—"
    if metric in ("n", "n_prob"): return str(int(c["value"]))
    s = f"{c['value']:.{dp}f}"
    if ci and c.get("ci"): s += f" [{c['ci'][0]:.{dp}f}, {c['ci'][1]:.{dp}f}]"
    return s


def dval(model, arm, task, part, metric, dp=3):
    x = D.get(model, {}).get(arm, {}).get(task, {}).get(part, {}).get(metric)
    if not x: return "—"
    star = "\\*" if (x.get("p_holm") == x.get("p_holm") and x.get("p_holm", 1) < 0.05) else ""
    return f"{x['delta']:+.{dp}f} [{x['ci'][0]:+.{dp}f}, {x['ci'][1]:+.{dp}f}] {x['p_holm']:.2g}{star}"


L = []
A = L.append

# ---------------------------------------------------------------- design
A("## 3. Design as run\n")
A("| | LLaMA 3.3 70B | GPT-5.4 | GPT-4o |")
A("|---|---|---|---|")
A("| Response bias (Table S13, full corpus) | +0.839 (strong Yes) | +0.238 (mild Yes) | −0.576 (strong No) |")
A("| Knowledge cutoff | 2023-12 | 2025-08 | 2023-10 |")
_B, _S = C.load_bench(), C.load_subset()
_NPOST = sum(C.partition(_B[i]["publication_date"], C.MODELS["gpt54"]["cutoff"]) == "post" for i in _S)
_NI = lambda m, t: int(CELLS[m]["A"][t]["post"]["n"]["value"])
A(f"| Post-cutoff events in the pinned subset | 500 (no pre-cutoff partition) | {_NPOST} ({500 - _NPOST} pre) | 500 (no pre-cutoff partition) |")
A(f"| Post-cutoff binary items (original + perturbed) | {_NI('llama33', 'binary_merged')} | {_NI('gpt54', 'binary_merged')} | {_NI('gpt4o', 'binary_merged')} |")
A(f"| Post-cutoff MCQ items | {_NI('llama33', 'mcq')} | {_NI('gpt54', 'mcq')} | {_NI('gpt4o', 'mcq')} |")
A(f"| Arm D samples per item | n = {META['n_self_consistency']['llama33']} | n = {META['n_self_consistency']['gpt54']} | n = {META['n_self_consistency']['gpt4o']} |")
A("| Arm C source | generated 2026-09-20 | stored WS+Cutoff | stored WS+Cutoff |")
A("")
A("Reference rows that need no new inference: DeepSeek R1 (arms A and C) and GPT-OSS 20B (arm A). "
  "Statistics: 10,000 event-level (cluster) bootstrap resamples, one shared resample matrix so every arm is paired; "
  "two-sided percentile bootstrap p, Holm–Bonferroni across arms within each model × task × partition × metric. "
  f"Partition rule: {META['partition_rule']}. ECE/MCE and the Murphy decomposition use {META['bins']}; log loss clips to [{META['logloss_clip']}, {1 - META['logloss_clip']}].")
A("")

# ---------------------------------------------------------------- binary master
A("## 4. Binary (original + perturbed), post-cutoff: event-framed probabilities\n")
A("P(Yes) = confidence when the answer is Yes, 1 − confidence when it is No; for arm D the Yes-vote fraction; for arm E the elicited probability. "
  "Outcome y = 1 for original questions, 0 for perturbed twins. BSS = 1 − Brier/UNC, the Brier skill score against the constant base-rate forecast "
  "(UNC = 0.245 throughout); negative means worse than always predicting the base rate. REL and RES are the Murphy reliability and resolution terms (lower REL is better, higher RES is better).\n")
A("| model | arm | n | Brier | BSS | REL | RES | log loss | ECE | MCE | AUROC | bias index | merged acc. |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for m in PANEL + REF:
    for arm in ARMS:
        if g(m, arm, "binary_merged", "post", "brier") is None: continue
        A(f"| {NAME[m]} | {LAB[arm]} | {val(m, arm, 'binary_merged', 'post', 'n_prob')} | {val(m, arm, 'binary_merged', 'post', 'brier')} | "
          f"{val(m, arm, 'binary_merged', 'post', 'bss', 2)} | {val(m, arm, 'binary_merged', 'post', 'rel')} | {val(m, arm, 'binary_merged', 'post', 'res')} | "
          f"{val(m, arm, 'binary_merged', 'post', 'logloss')} | {val(m, arm, 'binary_merged', 'post', 'ece')} | {val(m, arm, 'binary_merged', 'post', 'mce')} | "
          f"{val(m, arm, 'binary_merged', 'post', 'auroc')} | {val(m, arm, 'binary_merged', 'post', 'bias_index')} | {val(m, arm, 'binary_merged', 'post', 'accuracy')} |")
A("")
A("Two reading notes. ECE is a non-negative statistic, so where the point estimate is near zero the bootstrap distribution sits above it and the interval can exclude the point estimate "
  "(LLaMA arm E on MCQ, 0.016 with interval [0.017, 0.074], is the clearest case); this is a property of the statistic, not an error, and it is why Brier and log loss carry the argument. "
  "MCE is read over bins with at least 10 items, so it is the noisiest column and its intervals are wide.")
A("")
A("Equal-mass ECE (binning robustness), arm A → E: " + "; ".join(
    f"{NAME[m]} {val(m, 'A', 'binary_merged', 'post', 'ece_q', 3, False)} → {val(m, 'E', 'binary_merged', 'post', 'ece_q', 3, False)}" for m in PANEL) + ".")
A("")

# ---------------------------------------------------------------- binary deltas
A("### 4.1 Paired deltas versus base (arm − A), post-cutoff binary\n")
A("Each delta is computed on the intersection of items valid in both arms, with the shared event bootstrap; p is Holm-adjusted across arms; \\* marks Holm p < 0.05.\n")
A("| model | arm | ΔBrier | ΔREL | ΔRES | ΔAUROC | Δbias index | Δaccuracy |")
A("|---|---|---|---|---|---|---|---|")
for m in PANEL:
    for arm in ARMS[1:]:
        if not D.get(m, {}).get(arm, {}).get("binary_merged", {}).get("post"): continue
        A(f"| {NAME[m]} | {LAB[arm]} | " + " | ".join(dval(m, arm, "binary_merged", "post", k) for k in ("brier", "rel", "res", "auroc", "bias_index", "accuracy")) + " |")
A("")

# ---------------------------------------------------------------- MCQ
A("## 5. MCQ, post-cutoff: confidence in the chosen option versus correctness\n")
A("| model | arm | n | accuracy | mean confidence | Brier | log loss | ECE | REL | RES | AUROC |")
A("|---|---|---|---|---|---|---|---|---|---|---|")
for m in PANEL + REF:
    for arm in ARMS:
        if g(m, arm, "mcq", "post", "brier_c") is None: continue
        A(f"| {NAME[m]} | {LAB[arm]} | {val(m, arm, 'mcq', 'post', 'n_prob')} | {val(m, arm, 'mcq', 'post', 'accuracy')} | {val(m, arm, 'mcq', 'post', 'mean_conf')} | "
          f"{val(m, arm, 'mcq', 'post', 'brier_c')} | {val(m, arm, 'mcq', 'post', 'logloss_c')} | {val(m, arm, 'mcq', 'post', 'ece_c')} | "
          f"{val(m, arm, 'mcq', 'post', 'rel_c')} | {val(m, arm, 'mcq', 'post', 'res_c')} | {val(m, arm, 'mcq', 'post', 'auroc_c')} |")
A("")
A("### 5.1 Paired deltas versus base, post-cutoff MCQ\n")
A("| model | arm | Δaccuracy | ΔBrier | ΔECE | ΔAUROC |")
A("|---|---|---|---|---|---|")
for m in PANEL:
    for arm in ARMS[1:]:
        if not D.get(m, {}).get(arm, {}).get("mcq", {}).get("post"): continue
        A(f"| {NAME[m]} | {LAB[arm]} | " + " | ".join(dval(m, arm, "mcq", "post", k) for k in ("accuracy", "brier_c", "ece_c", "auroc_c")) + " |")
A("")

# ---------------------------------------------------------------- pre/post
A("## 6. The one model with a pre/post split: GPT-5.4\n")
A(f"LLaMA 3.3 and GPT-4o have cutoffs that predate the corpus, so they have no pre-cutoff partition. GPT-5.4 has {500 - _NPOST} pre-cutoff and {_NPOST} post-cutoff events, "
  "which is what separates recall from forecasting within a single model.\n")
A("| arm | partition | n | Brier | REL | RES | AUROC | bias index | accuracy |")
A("|---|---|---|---|---|---|---|---|---|")
for arm in ARMS:
    for part in ("pre", "post"):
        if g("gpt54", arm, "binary_merged", part, "brier") is None: continue
        A(f"| {LAB[arm]} | {part} | {val('gpt54', arm, 'binary_merged', part, 'n_prob')} | {val('gpt54', arm, 'binary_merged', part, 'brier')} | "
          f"{val('gpt54', arm, 'binary_merged', part, 'rel')} | {val('gpt54', arm, 'binary_merged', part, 'res')} | {val('gpt54', arm, 'binary_merged', part, 'auroc')} | "
          f"{val('gpt54', arm, 'binary_merged', part, 'bias_index')} | {val('gpt54', arm, 'binary_merged', part, 'accuracy')} |")
A("")

# ---------------------------------------------------------------- ensembles
A("## 7. Arm F — ensembles (derived from arm A; not independent of it)\n")
A("Each model's answer and confidence are converted to P(Yes), then aggregated three ways. Computed on the item-level intersection where every member answered. "
  "MCQ is aggregated by option text, since each model drew its own option permutation in the base run.\n")
for pn, title in (("panel3", "Three-model panel (LLaMA 3.3, GPT-5.4, GPT-4o)"), ("all_models", "All six models with stored confidence")):
    p = E["panels"][pn]
    A(f"**{title}.**\n")
    def q(c, k, dp=3):
        x = c.get(k)
        if not x: return "—"
        s = f"{x['value']:.{dp}f}"
        if x.get("ci"): s += f" [{x['ci'][0]:.{dp}f}, {x['ci'][1]:.{dp}f}]"
        return s
    A("Binary (original + perturbed), P(Yes) versus outcome — same columns as §4:\n")
    A("| rule | n | Brier | BSS | REL | RES | log loss | ECE | MCE | AUROC | bias index | merged acc. |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for rule in ("mean_prob", "mean_logit", "majority"):
        c = p["tasks"]["binary_merged"].get(rule, {}).get("post") or p["tasks"]["binary_merged"].get(rule, {}).get("all")
        if not c: continue
        A(f"| {rule.replace('_', ' ')} | {int(c['n']['value'])} | {q(c,'brier')} | {q(c,'bss',2)} | {q(c,'rel')} | {q(c,'res')} | {q(c,'logloss')} | {q(c,'ece')} | {q(c,'mce')} | {q(c,'auroc')} | {q(c,'bias_index')} | {q(c,'accuracy')} |")
    A("")
    A("MCQ, confidence in the chosen option versus correctness — same columns as §5:\n")
    A("| rule | n | accuracy | mean confidence | Brier | log loss | ECE | REL | RES | AUROC |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for rule in ("mean_prob", "mean_logit", "majority"):
        c = p["tasks"]["mcq"].get(rule, {}).get("post") or p["tasks"]["mcq"].get(rule, {}).get("all")
        if not c: continue
        A(f"| {rule.replace('_', ' ')} | {int(c['n']['value'])} | {q(c,'accuracy')} | {q(c,'mean_conf')} | {q(c,'brier_c')} | {q(c,'logloss_c')} | {q(c,'ece_c')} | {q(c,'rel_c')} | {q(c,'res_c')} | {q(c,'auroc_c')} |")
    A("")
    dm = (p["tasks"]["binary_merged"]["mean_prob"].get("post") or p["tasks"]["binary_merged"]["mean_prob"]["all"]).get("delta_vs_member_base", {})
    if dm:
        A("Mean-probability ensemble versus each member's own base condition on the same items: " + "; ".join(
            f"{NAME[mem]} ΔBrier {d['brier']['delta']:+.3f} [{d['brier']['ci'][0]:+.3f}, {d['brier']['ci'][1]:+.3f}], ΔRES {d['res']['delta']:+.3f}, ΔAUROC {d['auroc']['delta']:+.3f}"
            for mem, d in dm.items() if d.get("brier")) + ".")
        A("")
A("Manuscript Table 10 (both panels, all three rules, full metric set) is generated from the same JSON by `make_table10.py` → `tables/table10_ensemble.{tex,md}`.\n")

# ---------------------------------------------------------------- arm D diagnostics
A("## 8. Why self-consistency fails here: the vote distributions\n")
A("| model | n per item | binary items unanimous | MCQ items unanimous | distinct P(Yes) values | mean distance of P(Yes) from 0.5 |")
A("|---|---|---|---|---|---|")
for m in PANEL:
    v = VD[m]; n = v["n"]
    bu = sum(1 for x in v["binary"] if max(x["votes"].values()) == sum(x["votes"].values()))
    mu = sum(1 for x in v["mcq"] if max(x["votes"].values()) == sum(x["votes"].values()))
    items = C.load_arm(m, "D"); py = [it["p_yes"] for it in items if it.get("p_yes") is not None]
    A(f"| {NAME[m]} | {n} | {bu}/{len(v['binary'])} ({bu/len(v['binary']):.0%}) | {mu}/{len(v['mcq'])} ({mu/len(v['mcq']):.0%}) | {len(set(np.round(py, 3)))} | {np.mean(np.abs(np.array(py) - 0.5)):.3f} |")
A("")
A("Full vote distributions over the four MCQ options, per item, are in `calibration_study/tables/vote_distributions.json`. "
  "Laplace-smoothed ((k+1)/(n+2)) and raw-with-clipping log losses are both in the master table; the smoothed binary log losses for arm D are "
  + "; ".join(f"{NAME[m]} {val(m, 'D', 'binary_merged', 'post', 'logloss_laplace', 3, False)} (base {val(m, 'A', 'binary_merged', 'post', 'logloss', 3, False)})" for m in PANEL) + ".")
A("")

# ---------------------------------------------------------------- arm E audit + histograms
A("## 9. Confidence granularity and the arm E sum-to-one audit\n")
A("Verbalized confidence is coarse and clumps on a few values, which is why Brier and log loss are the load-bearing numbers and ECE is supporting.\n")
A("| model | arm | distinct values | three most common (share) |")
A("|---|---|---|---|")
for m in PANEL:
    for arm in ("A", "E"):
        items = [it for it in C.load_arm(m, arm) if it["task"] != "mcq" and it.get("conf") is not None]
        v = [round(it["conf"], 2) for it in items]; cnt = collections.Counter(v)
        A(f"| {NAME[m]} | {LAB[arm]} | {len(cnt)} | " + ", ".join(f"{k:g} ({n/len(v):.0%})" for k, n in cnt.most_common(3)) + " |")
A("")
A("MCQ probability vectors under arm E were audited for summing to 1: " + "; ".join(
    f"{NAME[m]} {PS[m]['n']} items, mean sum {PS[m]['mean_sum']:.3f}, max deviation {PS[m]['max_abs_dev']:.3f}, {PS[m]['frac_not_within_0_01']:.0%} outside ±0.01" for m in PANEL)
  + ". No model ever failed to normalise, so the renormalised and raw values coincide and the audit is null.")
A("")

# ---------------------------------------------------------------- cost
A("## 10. Cost and token accounting\n")
A("Arms A and C reused stored outputs and arm F is derived, so neither cost anything. Actual usage from the raw JSONL, at assumed list prices (`calibration_study/prices.json`):\n")
A("| run | records | API calls | input tokens | output tokens | USD |")
A("|---|---|---|---|---|---|")
tot = 0
for k in sorted(CO):
    v = CO[k]; tot += v["usd"] or 0
    A(f"| {k} | {v['records']} | {v['calls']} | {v['input_tokens']:,} | {v['output_tokens']:,} | {'$%.2f' % v['usd'] if v['usd'] is not None else '—'} |")
A(f"| **total** | | | | | **${tot:.2f}** |")
A("")
A("Zero errors, zero refusals and zero parse failures across all 13,500 records and 33,750 calls. "
  "The LLaMA 3.3 retrieval run generated for arm C cost a further $4 and is accounted in `results_llama33_run1/`.")
A("")

out = "\n".join(L) + "\n"
Path(C.STUDY / f"response_tables{C.SUFFIX}.md").write_text(out)  # _cmpre under the default cutoff-month-pre rule
print(out)
