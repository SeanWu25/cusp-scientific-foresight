# A6 — Calibration interventions: results

*Reviewer 1, comment 6. Numbers below are copied from `tables/master_table.md`,
`tables/delta_vs_base.md` and `tables/ensemble.md` (10,000 event-level bootstrap
resamples, Holm-corrected two-sided p-values). Every delta is arm − base on the
paired intersection of items. Post-cutoff partition unless stated.*

## Setup as run

| | LLaMA 3.3 70B | GPT-5.4 | GPT-4o |
|---|---|---|---|
| S13 bias index (full corpus) | +0.839 (strong Yes) | +0.238 (mild Yes) | −0.576 (strong No) |
| cutoff | 2023-12 | 2025-08 | 2023-10 |
| post-cutoff events in the 500 subset | 500 (no pre partition) | 144 (356 pre) | 500 (no pre partition) |
| post-cutoff binary items (orig + perturbed) | 690 | 188 | 690 |
| arm C (WS+Cutoff) | generated 2026-09-20 (`results_llama33_run1/`) | stored | stored |
| arm D samples n | 10 | 5 | 5 |

DeepSeek R1 was the intended balanced model (S13 bias index −0.025). Its Azure
Foundry deployment was retired before this study ran (HTTP 410 `model_deprecated`
on 2026-09-19; the R1-0528 and MAI-DS-R1 checkpoints are catalogued but not
deployed, and no other endpoint serves the original weights). New inference for
R1 is therefore impossible, and any substitute checkpoint would not be paired
with R1's stored base outputs. GPT-5.4 (bias +0.238, the next-closest to neutral
with a live deployment and a stored WS+Cutoff run) takes the middle position.
R1 is kept as a reference row for the two arms that need no inference (A and C),
and its own retrieval arm gives the same picture as the panel: post-cutoff,
retrieval leaves its Brier unchanged (+0.013 [−0.004, +0.031]), reliability and
resolution unchanged, AUROC +0.038 [−0.018, +0.095], while on its pre-cutoff
items the same arm lifts AUROC by +0.164 [+0.050, +0.281] and accuracy by
+0.156 — the recall signature, not forecasting. All new arms ran on the Foundry endpoint
(`Llama-3.3-70B-Instruct`, `gpt-5.4` → `gpt-5.4-2026-03-05`, `gpt-4o` →
`gpt-4o-2024-11-20`), JSON mode, max 2048 tokens, retries 2, no reasoning_effort;
B1/B2/E at temperature 0 (matching the stored base runs), D at temperature 1.0.
12 runs, 13,500 (id, task) records, 33,750 calls, zero errors, zero refusals, zero
parse failures. Actual spend ≈ $29 at assumed list prices (`tables/costs.md`).

## Headline

1. **No intervention gives any model forecasting skill.** The Brier skill score
   against the constant base-rate forecast (BSS = 1 − Brier/UNC) is negative in
   every model × arm cell post-cutoff; the best cell is GPT-5.4 arm E at
   −0.11 [−0.23, −0.01]. Resolution never leaves the 0.00–0.02 band (UNC = 0.245)
   and no arm moves it by more than 0.011 with a CI that excludes zero.
2. **Probabilistic elicitation (E) is the only intervention that improves calibration
   for all three models, and the gain is entirely reliability.** Brier −0.028
   [−0.039, −0.016] (LLaMA), −0.010 [−0.032, +0.011] (GPT-5.4), −0.019 [−0.028,
   −0.008] (GPT-4o); the reliability deltas are the same numbers to three decimals;
   resolution deltas are 0.000, +0.001, −0.002; AUROC deltas all have CIs spanning zero.
3. **The two interventions that change the answer distribution (prompting, retrieval)
   act as bias shifts, and their sign does not depend on the model's baseline bias.**
   Both debiasing prompts push every model toward No; retrieval pushes every model
   toward Yes. So the same intervention helps the model whose bias it opposes and
   hurts the one whose bias it reinforces, while calibration is essentially untouched.
4. **Self-consistency is the worst arm for calibration in every model**, because
   sampling is near-degenerate: 77% of LLaMA items are 10/10 unanimous at T = 1.0,
   70% of GPT-4o and 73% of GPT-5.4 items are 5/5. The vote fraction is a
   confident restatement of the model's bias, not a probability.
5. **Retrieval is the only arm that improves discrimination** (binary AUROC
   +0.093 [+0.052, +0.132] for GPT-4o, +0.100 [+0.016, +0.190] for GPT-5.4,
   +0.038 [−0.002, +0.079] for LLaMA; MCQ AUROC +0.114 [+0.056, +0.171] for
   LLaMA), and it does so while leaving calibration worse or unchanged. LLaMA is
   the one cell in the study where resolution moves with a CI excluding zero
   (+0.012 [+0.003, +0.021]), still inside the 0.00–0.02 band. On GPT-5.4's
   pre-cutoff partition the same arm reaches AUROC 0.81 and resolution 0.050, which
   is recall through the search context, and is why the pre/post split matters.

## Post-cutoff binary (original + perturbed), event-framed: P(event) vs outcome

| model | arm | Brier | BSS | REL | RES | AUROC | bias index | merged acc |
|---|---|---|---|---|---|---|---|---|
| LLaMA 3.3 | A | 0.336 | −0.37 | 0.097 | 0.005 | 0.569 | +0.830 | 0.457 |
| | B1 | 0.333 | −0.36 | 0.095 | 0.007 | 0.569 | +0.790 | 0.451 |
| | B2 | 0.341 | −0.39 | 0.101 | 0.005 | 0.553 | +0.794 | 0.442 |
| | D (n=10) | 0.528 | −1.16 | 0.287 | 0.003 | 0.530 | +0.889 | 0.435 |
| | C | 0.342 | −0.40 | 0.115 | 0.018 | **0.611** | +0.687 | 0.472 |
| | E | **0.306** | −0.25 | **0.069** | 0.006 | 0.562 | +0.565 | **0.491** |
| GPT-5.4 | A | 0.272 | −0.16 | 0.048 | 0.011 | 0.565 | +0.200 | 0.537 |
| | B1 | 0.280 | −0.19 | 0.055 | 0.009 | 0.558 | +0.071 | 0.505 |
| | B2 | 0.273 | −0.16 | 0.046 | 0.005 | 0.532 | +0.051 | 0.489 |
| | C | 0.321 | −0.37 | 0.108 | 0.022 | **0.665** | +0.515 | 0.511 |
| | D (n=5) | 0.381 | −0.62 | 0.153 | 0.006 | 0.574 | +0.175 | 0.553 |
| | E | **0.262** | −0.11 | **0.038** | 0.012 | 0.531 | −0.264 | 0.559 |
| GPT-4o | A | 0.291 | −0.19 | 0.050 | 0.004 | 0.477 | −0.605 | 0.535 |
| | B1 | 0.286 | −0.17 | 0.045 | 0.004 | 0.471 | −0.640 | 0.548 |
| | B2 | 0.284 | −0.16 | 0.040 | 0.001 | 0.499 | −0.603 | 0.543 |
| | C | 0.293 | −0.20 | 0.056 | 0.007 | **0.569** | −0.153 | 0.564 |
| | D (n=5) | 0.403 | −0.64 | 0.159 | 0.001 | 0.497 | −0.638 | 0.533 |
| | E | **0.273** | −0.11 | **0.029** | 0.002 | 0.490 | −0.505 | 0.532 |

CIs, log loss (clipped and Laplace), ECE (equal-width and equal-mass), MCE and the
answer-framed (`_c`) columns are in `tables/master_table.md`. Reliability diagrams:
`figures/reliability_binary_event_post.png`; confidence histograms:
`figures/hist_binary_confidence.png`, `figures/hist_binary_pyes_post.png`.

## Per model

**LLaMA 3.3 70B (strong Yes bias).** Best calibration: arm E (Brier −0.028
[−0.039, −0.016], Holm p < 0.001; reliability −0.027; resolution 0.000
[−0.007, +0.006]). E also raises merged accuracy by +0.033 [+0.006, +0.061], but
only because it drags the bias index from +0.83 to +0.57: mean P(Yes) falls from
0.72 to 0.63 against an item base rate of 0.43. Discrimination does not move
(AUROC −0.012 [−0.044, +0.021]). Neither prompt changes Brier (−0.002, +0.006) and
both shift bias by only −0.04. Self-consistency is catastrophic (Brier +0.195
[+0.181, +0.209]; Laplace log loss 1.34 vs base 0.90) and lowers AUROC
(−0.045 [−0.075, −0.013]). Retrieval (arm C, generated for this study on the
same subset with documents restricted to Dec 2023) behaves as in the other two
models: Brier unchanged (+0.005 [−0.009, +0.020]), reliability slightly worse
(+0.017), bias pulled toward No (−0.142 [−0.203, −0.081]), and discrimination up
(binary AUROC +0.038 [−0.002, +0.079]; MCQ accuracy +0.042, MCQ AUROC +0.114
[+0.056, +0.171], Holm p = 0.002). Its resolution gain of +0.012 [+0.003, +0.021]
is the largest in the study and still leaves resolution at 0.018 against an
uncertainty of 0.245.

**GPT-5.4 (mild Yes bias; the only model with a pre/post split).** Post-cutoff
N is small (188 items), so CIs are wide. Best calibration: arm E (Brier −0.010
[−0.032, +0.011], not significant; reliability −0.010; resolution +0.001). E
overshoots the bias: +0.20 → −0.26 [−0.41, −0.11], i.e. the mildly Yes-biased model
becomes No-biased when asked for a probability. The prompts move bias to ≈ 0
(B1 +0.07, B2 +0.05) without changing Brier (+0.008, 0.000) or AUROC. Retrieval is
the one arm with a discrimination gain (AUROC +0.100 [+0.016, +0.190]; resolution
+0.011 [−0.012, +0.031]) but it worsens calibration (Brier +0.049 [+0.015, +0.082],
reliability +0.061 [+0.031, +0.087]) by pushing bias to +0.52. Pre-cutoff, the same
arm gives AUROC 0.81 (+0.283 [+0.226, +0.338]) and resolution 0.050 — the recall
signature, absent post-cutoff.

**GPT-4o (strong No bias).** Best calibration: arm E (Brier −0.019 [−0.028,
−0.008], Holm p = 0.001; reliability −0.021; resolution −0.002). Here E moves bias
the *other* way (−0.61 → −0.51, +0.100 [+0.045, +0.155]) and accuracy is unchanged
(−0.003). Prompts: Brier −0.006 / −0.007, CIs span zero, bias essentially unchanged
(−0.035, +0.003), i.e. "consider what would refute this" cannot make a No-biased
model more No. Retrieval flips bias almost to neutral (+0.452 [+0.366, +0.536]),
raises AUROC (+0.093 [+0.052, +0.132], p = 0.001) and accuracy (+0.029
[−0.007, +0.064]) but leaves Brier unchanged (+0.001). Self-consistency: Brier
+0.112 [+0.093, +0.130]; 59% of items get P(Yes) = 0 exactly.

**Does the effect direction depend on baseline bias?** For calibration, no: E
lowers reliability for all three, and prompting changes nothing for all three.
For bias and accuracy, the *direction of the shift* is fixed by the intervention
(prompts → No, E → toward the middle, retrieval → Yes) and the *sign of the
accuracy change* is then fixed by whether that shift opposes or reinforces the
model's bias: E helps LLaMA (+3.3 pts) and not GPT-4o (−0.3); retrieval helps GPT-4o
(+2.9) and not GPT-5.4 (−2.7). Bias index deltas under E: −0.267 (LLaMA), −0.464
(GPT-5.4), +0.100 (GPT-4o) — three models, three different magnitudes and two signs,
with a near-identical reliability gain. That is a bias correction that happens to
help, not a calibration improvement that generalises.

## MCQ (answer-framed: confidence in the chosen option vs correctness)

| model | arm | accuracy | mean conf | ECE | AUROC_c |
|---|---|---|---|---|---|
| LLaMA 3.3 | A / B1 / B2 / D / E | 0.490 / 0.441 / 0.471 / 0.476 / 0.430 | 0.82 / 0.81 / 0.81 / 0.92 / 0.42 | 0.336 / 0.369 / 0.339 / 0.441 / **0.016** | 0.54 / 0.54 / 0.57 / 0.58 / 0.62 |
| GPT-5.4 (post, n=125) | A / B1 / B2 / C / D / E | 0.816 / 0.824 / 0.808 / 0.784 / 0.824 / 0.824 | 0.82 / 0.80 / 0.81 / 0.83 / 0.98 / 0.60 | **0.026** / 0.067 / 0.061 / 0.076 / 0.154 / 0.222 | 0.73 / 0.70 / 0.70 / 0.70 / 0.57 / 0.70 |
| GPT-4o | A / B1 / B2 / C / D / E | 0.543 / 0.510 / 0.522 / 0.589 / 0.533 / 0.425 | 0.87 / 0.86 / 0.86 / 0.90 / 0.92 / 0.40 | 0.330 / 0.352 / 0.333 / 0.310 / 0.385 / **0.056** | 0.59 / 0.61 / 0.54 / 0.64 / 0.57 / 0.66 |

* The asymmetric prompt (B1) *hurts* MCQ accuracy for the two weaker models
  (LLaMA −0.048 [−0.077, −0.021], GPT-4o −0.032 [−0.060, −0.007]); the symmetric
  prompt is neutral. GPT-5.4 is unaffected by either.
* Arm E collapses over-confidence on MCQ (ECE 0.34 → 0.02 for LLaMA, 0.33 → 0.06 for
  GPT-4o, both Holm p ≤ 0.001) but the argmax of the elicited distribution is a
  worse answer than the single pick (accuracy −0.060 and −0.117). GPT-5.4, already
  calibrated on MCQ, becomes *under*-confident under E (mean prob 0.60 vs accuracy
  0.82, ECE +0.197). Every model returned four probabilities summing to exactly 1.00
  on all 435 items (`tables/prob_sum_check.json`), so the audit is null.
* Self-consistency inflates MCQ confidence (0.92–0.98) with no accuracy change;
  full vote distributions are in `tables/vote_distributions.json`.

## Ensembles (arm F, derived from arm A; not independent of it)

Three-model panel, binary, intersection N = 656 items:

| rule | Brier | BSS | REL | RES | AUROC | bias | acc |
|---|---|---|---|---|---|---|---|
| mean probability | 0.271 [0.262, 0.280] | −0.11 | 0.029 | 0.003 | 0.530 | +0.27 | 0.494 |
| mean logit | 0.274 | −0.12 | 0.031 | 0.002 | 0.534 | +0.30 | 0.486 |
| majority vote | 0.335 | −0.37 | 0.090 | 0.000 | 0.512 | +0.28 | 0.491 |

Mean-probability ensembling beats every member on Brier (−0.065 vs LLaMA, −0.009 vs
GPT-5.4, −0.020 vs GPT-4o) purely through reliability (the opposite biases cancel,
bias index +0.83/+0.20/−0.61 → +0.27); resolution deltas are −0.002 / +0.004 /
−0.002 and AUROC stays at 0.53. The six-model all-panel ensemble (N = 569) is the
best-calibrated forecaster in the study — Brier 0.267 [0.258, 0.276], bias +0.05 —
and has AUROC 0.503 [0.464, 0.543], i.e. exactly chance. MCQ ensembles (aggregated by option text, since each model drew its own permutation) reach
accuracy 0.644 [0.598, 0.688] (three-model) and 0.673 [0.625, 0.720] (all six), above LLaMA
and GPT-4o but below GPT-5.4 alone (0.82).

## What this means for the paper

The reviewer's alternative reading — that near-chance binary performance reflects a
poor single-shot yes/no elicitation — is not supported. Across prompting, retrieval,
self-consistency, direct probability elicitation and three ensembling rules, no
configuration of any of three models raises resolution or AUROC above the noise
band on post-cutoff events, and none reaches the Brier score of a constant
base-rate forecast. What the interventions *can* do is move reliability: asking for
a probability instead of a label (E) or averaging models with opposite biases (F)
removes a substantial part of the miscalibration, and does so in the same direction
for every model regardless of its baseline bias. Resolution is untouched in every
case. The suggested phrasing: *elicitation determines how badly miscalibrated the
forecasts are; it does not determine whether they contain information about which
events occur.*

## Caveats to state

* LLaMA 3.3 and GPT-4o have cutoffs before the corpus starts, so they have no
  pre-cutoff partition; only GPT-5.4 supports the pre/post contrast, with 144 post
  events. DeepSeek R1 (the designed balanced model) could not be re-run.
* LLaMA 3.3 had no stored WS+Cutoff run; one was generated on 2026-09-20 on the
  same pinned subset (`results_llama33_run1/`, Foundry deployment, T = 0,
  You.com retrieval restricted to ≤ 2023-12, one transient search error out of
  500 rows). It is the only arm-C run not produced by the original pipeline.
* The stored LLaMA base run has no surviving inference log; the model field is
  `Llama-3.3-70B`, the new arms used the Foundry `Llama-3.3-70B-Instruct` deployment.
  Same weights, possibly a different serving stack. GPT-5.4's stored base run
  likewise has no log, so its reasoning_effort is unknown; new arms sent none.
* Verbalized confidence is coarse (7–13 distinct values for LLaMA/GPT-4o, 42–76 for
  GPT-5.4; see the histograms), so ECE/MCE are binning-sensitive; Brier and log loss
  are the load-bearing numbers and the equal-mass ECE is reported alongside.
* Prices in `prices.json` are assumed list prices, not invoice figures.
