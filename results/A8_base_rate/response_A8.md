# Reviewer 2, concern C5 — controlled experiments on why failures occur: base-rate information

> Reviewer 2 asks for controlled experiments that explain *why* the failures occur, including comparing "models with and without
> base-rate information." (Quoted fragment as relayed by the PI; the rest of the concern is paraphrased.)

**Status: analysis complete; ready for PI review.** Everything regenerates from stored JSONL with `bash results/A8_base_rate/run_all.sh`.
Supporting files: `results/A8_base_rate/results.md` (full tables), `sample.json`, `prompts.md`, `outputs.jsonl`, `tables/`, `figures/`,
`MANIFEST.json` (models, API-reported snapshots, dates, seed, prompt hashes, costs, git SHA).

## 1. Why we inject a base rate instead of supplying one

A true base rate for "this kind of progress" does not exist: every CUSP event is a realised advance drawn from a publication, so the
empirical Yes-rate of the corpus is 100% for original questions and 0% for their perturbed twins by construction, and no reference class
(field × claim type × horizon) has a documented historical success rate. Rather than supply a number we cannot defend, we treat the base
rate as an experimental variable: one sentence — *"Historically, in this field, the probability of this kind of progress happening is X%."* —
is inserted into the binary system prompt and X is swept over 10, 30, 50, 70 and 90%. Everything else is byte-identical to the base prompt,
including the confidence request; the sentence sits in the same position for every item and every X (`prompts.md`, sha256 per X in
`MANIFEST.json`). The comparison condition is each model's stored base run on the same items (not regenerated).

Items: a frozen random sample of 500 events (seed 8; `sample.json`) from the 2,289 corpus events that carry
both the original and the perturbed binary question, so each event contributes one ground-truth-Yes and one ground-truth-No item
(1,000 items per condition; 36 events are from the April–August 2026 extension). Models: the 9 panel models that can
still be run (GPT-4o, LLaMA 3.3 70B, GPT-OSS 20B, Claude S4.5, GPT-5.4, Claude Sonnet 5, GPT-5.6 Sol, DeepSeek-V4-Pro, Claude Opus 4.8); DeepSeek-R1's deployment is retired and appears only with its stored baseline. Decoding is each model's
base-run configuration (temperature 0 or effort = medium as in the published runs; GPT-5.4's original-corpus effort is not on record, so we
used medium, the setting of its extension-half run). 45,000 calls (33 rate-limited calls retried; the analysis keeps the last record per item), $123 at assumed list prices.

Metrics per model and X, on the *common set* (events whose both variants have a parsed answer and a confidence at baseline and at every X,
so every point of a curve is the same items; n = 341–500 events): accuracy on original items, on perturbed items, merged pooled
accuracy and balanced accuracy; fraction of Yes answers; mean self-reported confidence; mean implied P(Yes) (c if Yes, 1−c if No); ECE
(10 equal-width bins) and Brier of P(Yes) against the outcome. 2,000-draw event-cluster bootstrap CIs, shared resamples so changes versus
baseline are paired; OLS slope of each metric on X/100 across the five injected values as the sensitivity to the stated prior.

## 2. What we found

1. **Every model adopts the stated prior on its answer.** The fraction of Yes answers rises with X for all 9 models (monotonically for all of them); the slope of fraction-Yes on X runs from 0.59 (LLaMA 3.3 70B) to 1.20 (GPT-OSS 20B), with every 95% CI excluding zero. A slope of 1 means one extra Yes answer per item for every one-point rise in the stated rate: GPT-4o, GPT-OSS 20B, Claude Sonnet 5 are at or above 0.8, i.e. they take the number almost at face value.

2. **The prior shifts the decision threshold, not the discrimination.** Accuracy on original (ground-truth Yes) items rises from 0.00–0.53 at X=10% to 0.54–1.00 at X=90%, while accuracy on perturbed (ground-truth No) items falls from 0.54–1.00 to 0.01–0.44. The two moves largely cancel: balanced accuracy is significantly above the no-injection baseline in 3 of 45 model×X cells and significantly below it in 7; the significant gains are GPT-5.4 at X=10% (+0.072), GPT-5.6 Sol at X=10% (+0.059), GPT-5.6 Sol at X=30% (+0.051). The highest balanced accuracy anywhere in the sweep is 0.637 (GPT-5.6 Sol, X=10%), against a range of 0.486–0.578 at baseline. The gains belong to the Yes-biased reasoning models (baseline fraction-Yes 0.63 for GPT-5.4, 0.78 for GPT-5.6 Sol), for which a low stated rate moves the decision threshold toward the middle of their score distribution. Threshold-free discrimination does not move: AUROC of P(Yes) is 0.48–0.67 at baseline and is significantly higher than baseline in 6 of 45 cells and lower in 6. The one exception is GPT-5.4, whose AUROC rises from 0.52 at baseline to 0.55–0.60 across the sweep (significant at 5 of 5 values of X); the injected sentence appears to make its reported confidence more informative about the outcome, not merely shifted, although the level stays modest. The stated rate is used as a label prior, not as evidence about the item.

3. **The stated number contaminates the confidence field.** Under the paper's reading (confidence in the stated answer, so P(Yes) = c if Yes, 1−c if No) the slope of mean P(Yes) on X is 0.11–0.90; under the alternative reading (the field is P(event)) the slope of mean confidence on X is -0.06–0.73. For GPT-4o, LLaMA 3.3 70B, Claude S4.5 the reported confidence lies within ±0.05 of X/100 in ≥25% of responses at X=10% (share 0.81, 0.28, 0.33), i.e. the model writes the injected number into the confidence slot while answering No — for GPT-4o the 1−c convention then reads as a mean P(Yes) of 0.78 at X=10% although it answers No on 1.00 of items. We report both readings and the echo share so the reader can see where the elicitation is ambiguous.

4. **Calibration improves only where the stated rate matches the sample's built-in 50/50 outcome mix.** At X=50% ECE is significantly below baseline for 8 of 9 models and Brier for 9 of 9; the best ECE within the sweep sits at X=50% for 6 models and at X=30% or 70% for the rest. At the extreme rates (10% or 90%) ECE is significantly *worse* than baseline for 8 of 9 models. This is arithmetic, not skill: every event contributes one Yes and one No item, so a model that echoes 50% is trivially calibrated on this sample and one that echoes 10% or 90% is not. Over all 45 model×X cells ECE is significantly lower in 20 and higher in 16; Brier lower in 24 and higher in 15.

5. **Pre- and post-cutoff events both respond; the slopes are not identical.** 7 models have ≥20 events in both partitions of the common set. For 3 of them (Claude S4.5, Claude Sonnet 5, DeepSeek-V4-Pro) the fraction-Yes slope in one partition lies inside the other partition's CI; for GPT-OSS 20B, GPT-5.4, GPT-5.6 Sol, Claude Opus 4.8 it does not (pre 1.04, 0.52, 0.73, 0.65 vs post 1.23, 0.75, 1.16, 0.53). The response to a stated prior is not confined to events the model may have seen.

## 3. Sensitivity to the stated prior (per model)

| model | n events | slope frac-Yes [CI] | Δ frac-Yes (90−10) | slope mean P(Yes), answer reading [CI] | slope mean confidence, probability reading [CI] | echo share X=10% / X=90% |
|---|---|---|---|---|---|---|
| GPT-4o | 500 | 1.19 [1.15, 1.22] | +0.87 | 0.11 [0.08, 0.13] | 0.73 [0.71, 0.76] | 0.81 / 0.82 |
| LLaMA 3.3 70B | 455 | 0.59 [0.55, 0.63] | +0.52 | 0.90 [0.88, 0.91] | 0.49 [0.46, 0.52] | 0.28 / 0.98 |
| GPT-OSS 20B | 474 | 1.20 [1.16, 1.23] | +0.86 | 0.65 [0.63, 0.68] | 0.19 [0.17, 0.21] | 0.13 / 0.60 |
| Claude S4.5 | 341 | 0.64 [0.58, 0.70] | +0.48 | 0.24 [0.21, 0.26] | 0.19 [0.16, 0.23] | 0.33 / 0.14 |
| GPT-5.4 | 449 | 0.60 [0.56, 0.64] | +0.49 | 0.43 [0.41, 0.45] | 0.09 [0.08, 0.10] | 0.00 / 0.33 |
| Claude Sonnet 5 | 461 | 0.99 [0.95, 1.04] | +0.75 | 0.51 [0.50, 0.53] | -0.05 [-0.06, -0.03] | 0.00 / 0.05 |
| GPT-5.6 Sol | 493 | 0.79 [0.75, 0.84] | +0.60 | 0.60 [0.57, 0.63] | 0.04 [0.04, 0.05] | 0.00 / 0.77 |
| DeepSeek-V4-Pro | 500 | 0.79 [0.74, 0.84] | +0.55 | 0.58 [0.55, 0.61] | -0.05 [-0.06, -0.05] | 0.00 / 0.61 |
| Claude Opus 4.8 | 478 | 0.63 [0.59, 0.68] | +0.49 | 0.42 [0.40, 0.43] | -0.06 [-0.07, -0.04] | 0.00 / 0.09 |

## 4. Curves

Fraction of Yes answers (point [95% CI]; `base` = stored no-injection run on the same items):

| model | base (none) | X=10% | X=30% | X=50% | X=70% | X=90% | n items |
|---|---|---|---|---|---|---|
| GPT-4o | 0.203 [0.174, 0.233] | 0.003 [0.000, 0.007] | 0.099 [0.079, 0.120] | 0.321 [0.286, 0.355] | 0.729 [0.698, 0.760] | 0.875 [0.850, 0.899] | 1000 |
| LLaMA 3.3 70B | 0.923 [0.904, 0.942] | 0.474 [0.436, 0.510] | 0.846 [0.820, 0.872] | 0.959 [0.945, 0.973] | 0.986 [0.976, 0.993] | 0.996 [0.990, 0.999] | 910 |
| GPT-OSS 20B | 0.182 [0.155, 0.210] | 0.024 [0.014, 0.036] | 0.132 [0.110, 0.155] | 0.312 [0.278, 0.348] | 0.811 [0.781, 0.838] | 0.884 [0.862, 0.906] | 948 |
| Claude S4.5 | 0.280 [0.239, 0.319] | 0.091 [0.067, 0.117] | 0.139 [0.110, 0.170] | 0.227 [0.192, 0.262] | 0.452 [0.407, 0.497] | 0.573 [0.532, 0.617] | 682 |
| GPT-5.4 | 0.629 [0.594, 0.664] | 0.443 [0.406, 0.479] | 0.585 [0.548, 0.621] | 0.702 [0.669, 0.733] | 0.812 [0.783, 0.838] | 0.929 [0.910, 0.946] | 898 |
| Claude Sonnet 5 | 0.379 [0.344, 0.414] | 0.084 [0.062, 0.106] | 0.197 [0.168, 0.227] | 0.427 [0.391, 0.465] | 0.687 [0.652, 0.720] | 0.831 [0.801, 0.858] | 922 |
| GPT-5.6 Sol | 0.782 [0.754, 0.811] | 0.362 [0.331, 0.397] | 0.524 [0.490, 0.559] | 0.747 [0.718, 0.777] | 0.903 [0.882, 0.922] | 0.967 [0.954, 0.979] | 986 |
| DeepSeek-V4-Pro | 0.102 [0.080, 0.124] | 0.004 [0.001, 0.008] | 0.013 [0.006, 0.021] | 0.133 [0.110, 0.157] | 0.502 [0.465, 0.537] | 0.550 [0.514, 0.584] | 1000 |
| Claude Opus 4.8 | 0.393 [0.358, 0.431] | 0.172 [0.145, 0.199] | 0.262 [0.229, 0.295] | 0.423 [0.386, 0.460] | 0.536 [0.499, 0.571] | 0.666 [0.632, 0.699] | 956 |

Balanced accuracy:

| model | base (none) | X=10% | X=30% | X=50% | X=70% | X=90% | n items |
|---|---|---|---|---|---|---|
| GPT-4o | 0.493 [0.473, 0.513] | 0.499 [0.496, 0.502] | 0.491 [0.475, 0.508] | 0.477 [0.455, 0.500] | 0.501 [0.479, 0.523] | 0.499 [0.483, 0.515] | 1000 |
| LLaMA 3.3 70B | 0.515 [0.501, 0.531] | 0.514 [0.489, 0.541] | 0.524 [0.503, 0.544] | 0.514 [0.503, 0.526] | 0.499 [0.492, 0.505] | 0.502 [0.498, 0.507] | 910 |
| GPT-OSS 20B | 0.486 [0.464, 0.508] | 0.499 [0.490, 0.507] | 0.505 [0.485, 0.525] | 0.483 [0.460, 0.506] | 0.514 [0.494, 0.534] | 0.494 [0.476, 0.513] | 948 |
| Claude S4.5 | 0.487 [0.460, 0.514] | 0.497 [0.479, 0.515] | 0.499 [0.477, 0.519] | 0.507 [0.478, 0.536] | 0.482 [0.452, 0.512] | 0.472 [0.442, 0.503] | 682 |
| GPT-5.4 | 0.517 [0.490, 0.545] | 0.589 [0.560, 0.618] | 0.546 [0.520, 0.572] | 0.538 [0.509, 0.565] | 0.537 [0.513, 0.560] | 0.504 [0.489, 0.519] | 898 |
| Claude Sonnet 5 | 0.560 [0.534, 0.584] | 0.510 [0.497, 0.524] | 0.520 [0.499, 0.541] | 0.567 [0.543, 0.592] | 0.538 [0.513, 0.562] | 0.517 [0.498, 0.536] | 922 |
| GPT-5.6 Sol | 0.578 [0.555, 0.600] | 0.637 [0.612, 0.660] | 0.629 [0.603, 0.653] | 0.590 [0.567, 0.612] | 0.528 [0.512, 0.546] | 0.513 [0.503, 0.524] | 986 |
| DeepSeek-V4-Pro | 0.488 [0.473, 0.503] | 0.500 [0.496, 0.504] | 0.497 [0.490, 0.503] | 0.495 [0.476, 0.513] | 0.482 [0.455, 0.508] | 0.488 [0.462, 0.513] | 1000 |
| Claude Opus 4.8 | 0.556 [0.532, 0.580] | 0.525 [0.506, 0.545] | 0.542 [0.521, 0.563] | 0.559 [0.535, 0.582] | 0.548 [0.524, 0.574] | 0.558 [0.532, 0.582] | 956 |

Paired change in balanced accuracy versus baseline (Δ [CI], two-sided bootstrap p, not multiplicity-adjusted):

| model | base | Δ at X=10% | Δ at X=30% | Δ at X=50% | Δ at X=70% | Δ at X=90% |
|---|---|---|---|---|---|---|
| GPT-4o | 0.493 [0.473, 0.513] | +0.006 [-0.014, +0.026], p 0.597 | -0.002 [-0.026, +0.023], p 0.895 | -0.016 [-0.040, +0.008], p 0.214 | +0.008 [-0.021, +0.036], p 0.633 | +0.006 [-0.018, +0.030], p 0.703 |
| LLaMA 3.3 70B | 0.515 [0.501, 0.531] | -0.001 [-0.031, +0.029], p 0.981 | +0.009 [-0.014, +0.032], p 0.500 | -0.001 [-0.017, +0.013], p 0.884 | -0.016 [-0.033, -0.001], p 0.038 | -0.013 [-0.029, +0.001], p 0.101 |
| GPT-OSS 20B | 0.486 [0.464, 0.508] | +0.013 [-0.008, +0.034], p 0.290 | +0.019 [-0.006, +0.044], p 0.166 | -0.003 [-0.031, +0.025], p 0.822 | +0.027 [-0.001, +0.056], p 0.066 | +0.007 [-0.020, +0.036], p 0.612 |
| Claude S4.5 | 0.487 [0.460, 0.514] | +0.010 [-0.018, +0.039], p 0.543 | +0.012 [-0.017, +0.039], p 0.464 | +0.021 [-0.007, +0.049], p 0.179 | -0.004 [-0.033, +0.026], p 0.779 | -0.015 [-0.047, +0.020], p 0.399 |
| GPT-5.4 | 0.517 [0.490, 0.545] | +0.072 [+0.039, +0.108], p < 0.001 | +0.029 [-0.001, +0.060], p 0.078 | +0.021 [-0.011, +0.053], p 0.219 | +0.020 [-0.010, +0.050], p 0.224 | -0.012 [-0.041, +0.017], p 0.420 |
| Claude Sonnet 5 | 0.560 [0.534, 0.584] | -0.050 [-0.075, -0.023], p < 0.001 | -0.040 [-0.064, -0.014], p 0.003 | +0.008 [-0.015, +0.032], p 0.549 | -0.022 [-0.052, +0.008], p 0.158 | -0.042 [-0.069, -0.014], p 0.008 |
| GPT-5.6 Sol | 0.578 [0.555, 0.600] | +0.059 [+0.031, +0.087], p < 0.001 | +0.051 [+0.023, +0.079], p < 0.001 | +0.012 [-0.010, +0.033], p 0.302 | -0.050 [-0.071, -0.027], p < 0.001 | -0.065 [-0.087, -0.042], p < 0.001 |
| DeepSeek-V4-Pro | 0.488 [0.473, 0.503] | +0.012 [-0.004, +0.028], p 0.128 | +0.009 [-0.007, +0.026], p 0.293 | +0.007 [-0.013, +0.027], p 0.559 | -0.006 [-0.036, +0.023], p 0.714 | +0.000 [-0.028, +0.028], p 1.000 |
| Claude Opus 4.8 | 0.556 [0.532, 0.580] | -0.031 [-0.056, -0.006], p 0.017 | -0.015 [-0.039, +0.009], p 0.238 | +0.002 [-0.016, +0.021], p 0.812 | -0.008 [-0.033, +0.016], p 0.525 | +0.001 [-0.027, +0.028], p 0.965 |

AUROC of P(Yes) against the outcome (threshold-free discrimination):

| model | base (none) | X=10% | X=30% | X=50% | X=70% | X=90% | n items |
|---|---|---|---|---|---|---|
| GPT-4o | 0.496 [0.474, 0.520] | 0.501 [0.479, 0.522] | 0.496 [0.467, 0.526] | 0.471 [0.446, 0.496] | 0.497 [0.474, 0.522] | 0.498 [0.478, 0.517] | 1000 |
| LLaMA 3.3 70B | 0.534 [0.508, 0.560] | 0.527 [0.499, 0.555] | 0.485 [0.458, 0.512] | 0.493 [0.466, 0.520] | 0.500 [0.493, 0.507] | 0.506 [0.497, 0.515] | 910 |
| GPT-OSS 20B | 0.496 [0.468, 0.527] | 0.537 [0.505, 0.571] | 0.517 [0.486, 0.550] | 0.552 [0.520, 0.583] | 0.506 [0.480, 0.533] | 0.474 [0.443, 0.505] | 948 |
| Claude S4.5 | 0.479 [0.448, 0.509] | 0.492 [0.451, 0.530] | 0.471 [0.434, 0.505] | 0.477 [0.444, 0.507] | 0.482 [0.447, 0.519] | 0.461 [0.427, 0.495] | 682 |
| GPT-5.4 | 0.515 [0.484, 0.547] | 0.604 [0.574, 0.632] | 0.555 [0.524, 0.585] | 0.558 [0.527, 0.589] | 0.589 [0.558, 0.620] | 0.568 [0.537, 0.599] | 898 |
| Claude Sonnet 5 | 0.561 [0.533, 0.588] | 0.517 [0.491, 0.544] | 0.540 [0.514, 0.565] | 0.566 [0.538, 0.592] | 0.552 [0.524, 0.578] | 0.546 [0.518, 0.573] | 922 |
| GPT-5.6 Sol | 0.665 [0.635, 0.692] | 0.665 [0.636, 0.691] | 0.658 [0.631, 0.685] | 0.675 [0.649, 0.701] | 0.672 [0.644, 0.699] | 0.650 [0.624, 0.676] | 986 |
| DeepSeek-V4-Pro | 0.490 [0.463, 0.517] | 0.502 [0.490, 0.514] | 0.479 [0.450, 0.504] | 0.480 [0.449, 0.509] | 0.475 [0.447, 0.502] | 0.493 [0.466, 0.519] | 1000 |
| Claude Opus 4.8 | 0.557 [0.530, 0.583] | 0.543 [0.520, 0.568] | 0.535 [0.511, 0.562] | 0.553 [0.527, 0.579] | 0.549 [0.522, 0.575] | 0.540 [0.512, 0.568] | 956 |

ECE of P(Yes) against the outcome:

| model | base (none) | X=10% | X=30% | X=50% | X=70% | X=90% | n items |
|---|---|---|---|---|---|---|
| GPT-4o | 0.235 [0.215, 0.256] | 0.391 [0.372, 0.412] | 0.196 [0.170, 0.227] | 0.193 [0.170, 0.215] | 0.202 [0.180, 0.225] | 0.375 [0.359, 0.391] | 1000 |
| LLaMA 3.3 70B | 0.249 [0.237, 0.264] | 0.347 [0.335, 0.364] | 0.181 [0.162, 0.199] | 0.069 [0.052, 0.095] | 0.203 [0.198, 0.209] | 0.396 [0.392, 0.400] | 910 |
| GPT-OSS 20B | 0.244 [0.219, 0.274] | 0.331 [0.305, 0.359] | 0.201 [0.180, 0.224] | 0.080 [0.060, 0.111] | 0.189 [0.170, 0.210] | 0.372 [0.355, 0.391] | 948 |
| Claude S4.5 | 0.243 [0.217, 0.275] | 0.324 [0.291, 0.359] | 0.238 [0.208, 0.274] | 0.213 [0.184, 0.242] | 0.196 [0.173, 0.222] | 0.312 [0.288, 0.337] | 682 |
| GPT-5.4 | 0.183 [0.154, 0.213] | 0.184 [0.157, 0.212] | 0.151 [0.128, 0.181] | 0.155 [0.130, 0.183] | 0.205 [0.192, 0.230] | 0.326 [0.312, 0.344] | 898 |
| Claude Sonnet 5 | 0.102 [0.086, 0.129] | 0.259 [0.246, 0.274] | 0.158 [0.141, 0.180] | 0.059 [0.048, 0.091] | 0.138 [0.121, 0.162] | 0.208 [0.191, 0.228] | 922 |
| GPT-5.6 Sol | 0.260 [0.239, 0.284] | 0.247 [0.225, 0.273] | 0.155 [0.131, 0.182] | 0.202 [0.184, 0.221] | 0.272 [0.260, 0.288] | 0.406 [0.396, 0.416] | 986 |
| DeepSeek-V4-Pro | 0.415 [0.399, 0.432] | 0.402 [0.398, 0.406] | 0.241 [0.236, 0.248] | 0.208 [0.181, 0.237] | 0.239 [0.212, 0.266] | 0.373 [0.348, 0.399] | 1000 |
| Claude Opus 4.8 | 0.156 [0.138, 0.186] | 0.268 [0.252, 0.289] | 0.161 [0.145, 0.186] | 0.105 [0.085, 0.131] | 0.134 [0.108, 0.160] | 0.191 [0.171, 0.220] | 956 |

Mean implied P(Yes) (answer reading) and mean confidence (probability reading):

| model | base (none) | X=10% | X=30% | X=50% | X=70% | X=90% | n items |
|---|---|---|---|---|---|---|
| GPT-4o | 0.368 [0.353, 0.383] | 0.779 [0.760, 0.797] | 0.471 [0.458, 0.484] | 0.450 [0.437, 0.462] | 0.610 [0.597, 0.623] | 0.817 [0.802, 0.833] | 1000 |
| LLaMA 3.3 70B | 0.722 [0.711, 0.733] | 0.170 [0.159, 0.182] | 0.351 [0.342, 0.360] | 0.551 [0.546, 0.556] | 0.696 [0.693, 0.699] | 0.895 [0.892, 0.898] | 910 |
| GPT-OSS 20B | 0.364 [0.347, 0.380] | 0.301 [0.284, 0.318] | 0.350 [0.339, 0.361] | 0.483 [0.472, 0.493] | 0.632 [0.620, 0.643] | 0.815 [0.800, 0.829] | 948 |
| Claude S4.5 | 0.427 [0.406, 0.448] | 0.527 [0.501, 0.554] | 0.450 [0.432, 0.468] | 0.464 [0.446, 0.482] | 0.583 [0.567, 0.599] | 0.698 [0.678, 0.717] | 682 |
| GPT-5.4 | 0.551 [0.535, 0.567] | 0.448 [0.427, 0.467] | 0.538 [0.522, 0.554] | 0.590 [0.577, 0.605] | 0.683 [0.669, 0.696] | 0.803 [0.791, 0.814] | 898 |
| Claude Sonnet 5 | 0.466 [0.453, 0.480] | 0.258 [0.247, 0.270] | 0.380 [0.368, 0.392] | 0.486 [0.474, 0.497] | 0.576 [0.563, 0.588] | 0.671 [0.657, 0.684] | 922 |
| GPT-5.6 Sol | 0.698 [0.679, 0.718] | 0.386 [0.362, 0.412] | 0.551 [0.531, 0.572] | 0.655 [0.638, 0.672] | 0.740 [0.726, 0.753] | 0.893 [0.883, 0.903] | 986 |
| DeepSeek-V4-Pro | 0.165 [0.148, 0.182] | 0.101 [0.099, 0.104] | 0.262 [0.256, 0.267] | 0.328 [0.317, 0.339] | 0.483 [0.466, 0.500] | 0.569 [0.542, 0.594] | 1000 |
| Claude Opus 4.8 | 0.451 [0.434, 0.469] | 0.274 [0.258, 0.290] | 0.391 [0.376, 0.406] | 0.479 [0.466, 0.494] | 0.525 [0.510, 0.540] | 0.624 [0.607, 0.642] | 956 |

| model | base (none) | X=10% | X=30% | X=50% | X=70% | X=90% | n items |
|---|---|---|---|---|---|---|
| GPT-4o | 0.728 [0.724, 0.732] | 0.221 [0.203, 0.239] | 0.537 [0.524, 0.550] | 0.665 [0.661, 0.669] | 0.701 [0.698, 0.705] | 0.873 [0.868, 0.877] | 1000 |
| LLaMA 3.3 70B | 0.759 [0.754, 0.764] | 0.554 [0.528, 0.580] | 0.411 [0.400, 0.423] | 0.560 [0.556, 0.564] | 0.699 [0.698, 0.701] | 0.898 [0.897, 0.899] | 910 |
| GPT-OSS 20B | 0.704 [0.692, 0.716] | 0.703 [0.686, 0.720] | 0.632 [0.620, 0.643] | 0.567 [0.558, 0.576] | 0.690 [0.685, 0.696] | 0.863 [0.856, 0.869] | 948 |
| Claude S4.5 | 0.705 [0.695, 0.715] | 0.494 [0.467, 0.521] | 0.566 [0.548, 0.585] | 0.606 [0.592, 0.621] | 0.591 [0.576, 0.606] | 0.676 [0.657, 0.695] | 682 |
| GPT-5.4 | 0.698 [0.691, 0.706] | 0.765 [0.758, 0.772] | 0.694 [0.687, 0.701] | 0.687 [0.679, 0.694] | 0.742 [0.734, 0.749] | 0.829 [0.823, 0.835] | 898 |
| Claude Sonnet 5 | 0.659 [0.652, 0.666] | 0.768 [0.762, 0.775] | 0.676 [0.670, 0.682] | 0.627 [0.620, 0.633] | 0.671 [0.665, 0.676] | 0.725 [0.719, 0.732] | 922 |
| GPT-5.6 Sol | 0.826 [0.819, 0.833] | 0.884 [0.879, 0.889] | 0.781 [0.773, 0.789] | 0.762 [0.753, 0.771] | 0.798 [0.791, 0.805] | 0.919 [0.916, 0.922] | 986 |
| DeepSeek-V4-Pro | 0.902 [0.896, 0.907] | 0.901 [0.900, 0.902] | 0.739 [0.734, 0.744] | 0.678 [0.668, 0.688] | 0.716 [0.710, 0.721] | 0.859 [0.854, 0.865] | 1000 |
| Claude Opus 4.8 | 0.712 [0.704, 0.720] | 0.791 [0.783, 0.798] | 0.700 [0.693, 0.707] | 0.659 [0.652, 0.666] | 0.683 [0.676, 0.690] | 0.744 [0.737, 0.752] | 956 |

Accuracy on original and on perturbed items, Brier, merged pooled accuracy, the all-valid sensitivity tables and the paired deltas for
every metric are in `results/A8_base_rate/results.md` and `tables/`.

## 5. Pre- versus post-cutoff events

| model | cutoff | partition | n events | base frac-Yes | slope frac-Yes [CI] | slope mean P(Yes) [CI] |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | pre | 0 | — | — | — |
| GPT-4o | 2023-10 | post | 500 | 0.203 | 1.19 [1.15, 1.22] | 0.11 [0.08, 0.13] |
| LLaMA 3.3 70B | 2023-12 | pre | 0 | — | — | — |
| LLaMA 3.3 70B | 2023-12 | post | 455 | 0.923 | 0.59 [0.55, 0.63] | 0.90 [0.88, 0.91] |
| GPT-OSS 20B | 2024-06 | pre | 76 | 0.164 | 1.04 [0.95, 1.14] | 0.60 [0.53, 0.66] |
| GPT-OSS 20B | 2024-06 | post | 398 | 0.186 | 1.23 [1.19, 1.26] | 0.67 [0.64, 0.69] |
| Claude S4.5 | 2025-01 | pre | 145 | 0.341 | 0.63 [0.55, 0.71] | 0.30 [0.26, 0.34] |
| Claude S4.5 | 2025-01 | post | 196 | 0.235 | 0.64 [0.57, 0.72] | 0.19 [0.16, 0.23] |
| GPT-5.4 | 2025-08 | pre | 293 | 0.647 | 0.52 [0.47, 0.57] | 0.40 [0.37, 0.42] |
| GPT-5.4 | 2025-08 | post | 156 | 0.596 | 0.75 [0.67, 0.82] | 0.48 [0.45, 0.52] |
| Claude Sonnet 5 | 2026-01 | pre | 389 | 0.405 | 1.00 [0.95, 1.04] | 0.51 [0.50, 0.53] |
| Claude Sonnet 5 | 2026-01 | post | 72 | 0.236 | 0.97 [0.84, 1.09] | 0.51 [0.47, 0.54] |
| GPT-5.6 Sol | 2026-02 | pre | 425 | 0.799 | 0.73 [0.69, 0.78] | 0.56 [0.53, 0.59] |
| GPT-5.6 Sol | 2026-02 | post | 68 | 0.676 | 1.16 [1.06, 1.26] | 0.84 [0.79, 0.90] |
| DeepSeek-V4-Pro | 2026-04 | pre | 464 | 0.100 | 0.79 [0.74, 0.84] | 0.58 [0.55, 0.61] |
| DeepSeek-V4-Pro | 2026-04 | post | 36 | 0.125 | 0.80 [0.66, 0.94] | 0.56 [0.47, 0.66] |
| Claude Opus 4.8 | 2026-01 | pre | 400 | 0.435 | 0.65 [0.60, 0.70] | 0.42 [0.41, 0.44] |
| Claude Opus 4.8 | 2026-01 | post | 78 | 0.179 | 0.53 [0.42, 0.65] | 0.39 [0.35, 0.44] |

## 6. Proposed manuscript text (marked as proposed)

> **[Proposed addition to Results, after the calibration paragraph]** To test whether the near-chance binary forecasting reflects a
> missing prior rather than missing discrimination, we injected a stated base rate into the binary prompt ("Historically, in this field,
> the probability of this kind of progress happening is X%") and swept X over 10–90% on a fixed random sample of 500 events (each with
> its original and perturbed question) for the 9 panel models that remain available (Supplementary Section S-A8). Models adopt the
> stated rate almost at face value: the fraction of Yes answers rises with X with slopes of 0.59–1.20 per unit of X, every CI excluding
> zero. The adoption is a threshold shift, not new information: accuracy on true events and on their perturbed counterparts move in
> opposite directions and cancel, so balanced accuracy is not significantly above the no-injection baseline in 42 of 45 model×X
> cells, threshold-free discrimination (AUROC) is unchanged for 8 of 9 models (GPT-5.4 gains modestly),
> and calibration is not improved except at the rate that happens to match the sample's 50/50 outcome mix. A supplied prior
> therefore changes what the models say, not what they know.

> **[Proposed Supplementary Section S-A8 — Base-rate injection sweep]** Design, exact prompts, per-model curves with CIs for all eight
> metrics, sensitivity slopes, the confidence-echo diagnostic and the pre/post-cutoff split, as in `results/A8_base_rate/results.md`;
> Supplementary Figure: `figures/frac_yes_panels.png`, `figures/bal_acc_panels.png`, `figures/ece_panels.png`, `figures/slopes.png`;
> Supplementary Table: `tables/slopes.csv`, `tables/curves.csv`.

## 7. Limitations we state

* The injected rate is a fiction: it is the same number for every item at a given X. The experiment measures conditioning on a *stated*
  prior, not the value of a *correct* one; a correct reference-class rate does not exist for these events (Section 1).
* The confidence field is ambiguous once a number is in the prompt: some models write the injected rate into it while answering No
  (the echo share). We report both readings. The ECE and Brier improvements at X=50% are the sample's construction (one Yes and one No item
  per event), not forecasting skill; at 10% and 90% the same mechanism makes calibration worse.
* The sweep cannot create discrimination the base run lacks, and for 8 of 9 models it does not; the exception is
  GPT-5.4, whose AUROC rises modestly at every X, which we report as is.
* Decoding matches each model's stored base run; GPT-5.4's original-corpus reasoning effort is not on record (we used medium, its
  extension-half setting). DeepSeek-R1 could not be re-run (deployment retired). Costs are at assumed list prices.
* One sample of 500 events (seed 8); CIs are event-cluster bootstrap and the deltas are not multiplicity-adjusted.

## 8. Reproducibility

| model | snapshot reported by the API | records | refusals | cost (assumed list prices) |
|---|---|---|---|---|
| GPT-4o | gpt-4o-2024-11-20 | 5000 | 0 | $5.17 |
| LLaMA 3.3 70B | Llama-3.3-70B-Instruct | 5033 | 0 | $0.84 |
| GPT-OSS 20B | gpt-oss-20b | 5000 | 0 | $0.00 |
| Claude S4.5 | claude-sonnet-4-5-20250929 | 5000 | 673 | $10.15 |
| GPT-5.4 | gpt-5.4-2026-03-05 | 5000 | 0 | $35.07 |
| Claude Sonnet 5 | claude-sonnet-5 | 5000 | 146 | $8.14 |
| GPT-5.6 Sol | gpt-5.6-sol | 5000 | 1 | $43.68 |
| DeepSeek-V4-Pro | DeepSeek-V4-Pro | 5000 | 0 | $2.36 |
| Claude Opus 4.8 | claude-opus-4-8 | 5000 | 155 | $17.26 |

Total: $122.67 at assumed list prices; git `23ff399e72`; frozen grader `scripts/eval.py` and parser/prompt `scripts/test_LLM.py`
(sha256 in `MANIFEST.json`); no base output, prompt, scoring code or benchmark file was modified.
