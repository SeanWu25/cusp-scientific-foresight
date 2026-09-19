# A6 — calibration intervention study (Reviewer 1, comment 6)

Does the near-chance binary forecasting performance reflect a limit on forecasting
ability, or a poor elicitation set-up? Five arms on the pinned 500-event retrieval
subset, three models chosen to span response bias, closed-form scoring only.

Everything in `tables/`, `figures/` and `RESULTS.md` is regenerated from stored
JSONL / reports by one command and never hand-edited:

    python calibration_study/analyze.py            # 10k bootstrap, ~20 min
    python calibration_study/analyze.py --B 2000   # quick look

## Layout

    common.py         model registry, cutoffs, partition rule, arm loaders (A/C from
                      stored eval.py reports; B1/B2/D/E from raw/; F derived)
    metrics.py        ECE/MCE/Brier/log loss/Murphy/AUROC, vectorised for bootstrap
    analyze.py        master table, paired deltas, ensembles, figures, costs
    run_arm.py        inference runner for arms B1/B2/D/E (resumable per item)
    estimate_cost.py  pre-run token/cost estimate (no API calls)
    prices.json       assumed list prices — edit before quoting money
    raw/              <model>_<arm>.jsonl + .manifest.json (prompts, sha256, T, n)
    tables/           master_table, delta_vs_base, ensemble, vote_distributions,
                      prob_sum_check, costs  (.json + .md)
    figures/          reliability_*.{png,pdf}, hist_*.{png,pdf}, faceted model x arm

## Items

`results_sonnet5_run1/subset500_ids.txt` — the same 500 ids as every stored
`*_500*` retrieval report (verified: 500/500 overlap with each). In the subset:
296 original binary questions, 394 perturbed, 435 MCQ. Events span 2024-01 to 2026-03.

## Arms

| arm | what changes | source |
|---|---|---|
| A | nothing | stored base reports (`run_evaluation/frq_results/`) |
| B1 | + "Before answering, consider what evidence would refute this realization." | `run_arm.py --arm B1 --temperature 0` |
| B2 | + "Before answering, consider the evidence for and the evidence against this realization." | `run_arm.py --arm B2 --temperature 0` |
| C | web search restricted to pre-cutoff | stored WS+Cutoff reports |
| D | confidence request removed, n samples at explicit T, p = k/n | `run_arm.py --arm D --temperature T` |
| E | P(Yes) elicited directly / per-option probabilities | `run_arm.py --arm E --temperature 0` |
| F | mean prob / mean logit / majority vote over models' arm-A P(Yes) | derived in `analyze.py` |

The debiasing sentence is inserted into the system prompt after the role
sentence; the JSON-format / confidence instruction that follows is asserted
byte-identical to the base prompt at start-up. Arm D and E prompts are
derived from the base prompt by string replacement and asserted; the full text
and sha256 of every system prompt is in `raw/<model>_<arm>.manifest.json`.
User prompts are byte-identical to the base run, including the per-item MCQ
option permutation (read from the stored base predictions).

## Conventions

* Partition: main-table rule, `pre` if pub_month < cutoff month (cutoff month is post).
* P(Yes) for arms A/B/C = confidence if answer is Yes, 1 − confidence if No.
  Outcome y = 1 for original questions, 0 for perturbed.
* Event-framed metrics score P(Yes) vs y over binary + perturbed ("binary_merged").
  `_c` metrics score confidence-in-answer vs correctness (the paper's S14 convention).
* ECE / MCE / Murphy: 10 equal-width bins; MCE over bins with ≥10 items; `ece_q` uses
  10 equal-mass bins. Log loss clips to [0.01, 0.99]; arm D also reports (k+1)/(n+2).
* Murphy: Brier = REL − RES + UNC + within-bin residual (reported, so it sums exactly).
* Bootstrap: 10,000 event-level (cluster) resamples, percentile CIs, one shared
  resample matrix so every arm/task/partition is paired. Deltas on the intersection
  of items valid in both arms. Two-sided percentile p; Holm–Bonferroni across arms
  within each model × task × partition × metric family.
