# A4 horizon study — binary split into original / perturbed, FRQ split into its four rubric dimensions

Reviewer 1, comment 4 (horizon-dependent forecasting error). Supplement to the main horizon analysis,
generated 2026-10-09 by `horizon_study/run_split.py` from the same stored, already-scored reports: no new
inference, no new judging. Same definitions as the main analysis (horizon = months from the first-observable
date to the model's cutoff, post-cutoff = h ≥ 1; bins 1–3, 4–6, 7–12, 13–24, 25+; 10k event-level bootstrap;
crossed event × model GLMM; Holm within each family). FRQ dimensions are the judge's alignment, specificity,
novelty and feasibility scores (0–10 each; the published FRQ score is their mean). Figures:
`horizon_study/figures/split/horizon_split_{orig,ext,merged,ws}.png` and `binned_coef_*.png`.

## 1. Summary of findings

The analyses above treat binary as the merged original + perturbed task and FRQ
as the rubric mean. Here each is split and re-run with the same loaders,
estimators and bootstrap (`horizon_study/run_split.py`; tables in
`horizon_study/tables/split/`, figures in `figures/split/`): binned means with
10k event-bootstrap CIs, within-model slopes with Holm correction, the crossed
event × model GLMM, the spline / broken-stick fits, WS+Cutoff vs base on the
pinned subset, and the reviewer's bin-dummy mixed model. Holm is applied within
this file's own family. The date task, the MCC analysis (which already uses both
binary variants) and the sensitivity stage are unchanged by the split and are not
re-run.

### Binary: the merged slope hides two opposite, near-equal slopes

| outcome, merged corpus (10 models, 1–34 months) | pooled GLMM horizon coef (log-odds / yr) | Holm | event-FE curvature p |
|---|---|---|---|
| binary, original question (n = 13,538) | **+0.742 [+0.604, +0.881]** | < 10⁻⁴ | 0.97 |
| binary, perturbed twin (n = 21,993) | **−0.662 [−0.779, −0.546]** | < 10⁻⁴ | 0.36 |
| (for reference) merged binary, §3 | −0.057 | 0.086 | — |

Original corpus alone: +0.859 [+0.700, +1.019] and −0.711 [−0.860, −0.562].
Within model, every model with at least 12 months of horizon shows the same
mirror image, with the two slopes of nearly equal size:

| model | horizon | original acc. slope /12 mo | perturbed acc. slope /12 mo | P(Yes) slope /12 mo |
|---|---|---|---|---|
| GPT-4o | 3–34 | +0.111 [+0.092, +0.131] | −0.104 [−0.121, −0.087] | +0.110 |
| LLaMA 3.3 70B | 1–32 | +0.044 [+0.031, +0.058] | −0.033 [−0.045, −0.020] | +0.035 |
| GPT-OSS 20B | 1–26 | +0.046 [+0.017, +0.075] | −0.063 [−0.086, −0.040] | +0.062 |
| DeepSeek R1 | 1–20 | +0.130 [+0.085, +0.177] | −0.141 [−0.180, −0.102] | +0.137 |
| Claude S4.5 | 1–19 | +0.099 [+0.045, +0.153] | −0.101 [−0.141, −0.062] | +0.106 |
| GPT-5.4 | 1–12 | +0.107 [−0.018, +0.234] | −0.079 [−0.160, +0.002] | +0.084 |

The last column is the mechanism. Accuracy on the original question equals the
Yes-rate, and accuracy on the perturbed twin equals one minus the Yes-rate, so
the two accuracies can only move in opposite directions if the Yes-rate moves.
It does: pooled over all models the Yes-rate is 0.36 at 1–3 months, 0.41 at 4–6,
0.43 at 7–12, 0.49 at 13–24 and 0.56 at 25+, and the rise is present in every
model regardless of its baseline bias (GPT-4o from 0.03 to 0.31, LLaMA from 0.87
to 0.95, DeepSeek R1 from 0.39 to 0.56). Models say Yes more often the further
an event lies past their cutoff. This is response-bias drift, not foresight, and
it is exactly what §3 inferred from the merged slopes and the flat MCC; the split
makes it visible directly. The four models with ≤ 7 months of range (Sonnet 5,
Opus 4.8, Sol, DeepSeek-V4-Pro) show no consistent pattern, as expected from
their intervals.

Shape and retrieval behave accordingly. No curvature on the merged corpus
(quadratic −0.028 and +0.041; event-FE curvature p = 0.97 and 0.36); the original
corpus shows a mild mirror-image curvature (+0.255, p = 0.008 for originals;
−0.173, p = 0.03 for perturbed). The bin-dummy model gives a large GLMM omnibus
for both variants (p ≈ 10⁻³¹) but a weak stratified Wald (p = 0.039 originals,
0.28 perturbed, 3-month bins): a linear drift that the within-event estimator
cannot separate from calendar, as in §9. Retrieval restricted to pre-cutoff
documents pushes answers toward Yes, +0.84 log-odds on originals and −0.42 on
perturbed items (conditional logit within event × model strata), and its effect
does not change with horizon (ws × horizon p = 0.80 and 0.28). The one cell that
moves is GPT-4o's original-question slope, which retrieval flattens from +0.158
to +0.049 per 12 months (difference −0.110 [−0.206, −0.013], uncorrected).

### FRQ: three dimensions flat, novelty rises

| dimension, merged corpus (23,895 items, 4,765 events, 10 models) | pooled GLMM coef (points / yr) | Holm | original corpus only | event SD / model SD |
|---|---|---|---|---|
| total (mean of four) | +0.014 [−0.012, +0.039] | 1 | +0.026 [−0.006, +0.059] | 0.47 / 1.39 |
| alignment | −0.025 [−0.072, +0.021] | 1 | −0.023 [−0.081, +0.035] | 0.94 / 0.95 |
| specificity | −0.016 [−0.043, +0.011] | 1 | −0.033 [−0.068, +0.002] | 0.40 / 1.92 |
| novelty | **+0.067 [+0.039, +0.094]** | **5 × 10⁻⁵** | **+0.117 [+0.082, +0.152]** | 0.40 / 1.91 |
| feasibility | +0.026 [−0.014, +0.066] | 1 | +0.031 [−0.021, +0.083] | 0.67 / 0.78 |

1. **Novelty is the only dimension with a horizon gradient, and it is positive.**
   Within the original corpus every long-range model's novelty slope is positive:
   GPT-4o +0.167 [+0.119, +0.215], DeepSeek R1 +0.132, GPT-OSS +0.085, LLaMA
   +0.077 [+0.037, +0.116], Claude S4.5 +0.149 (p = 0.07) per 12 months. The bin
   profile is smooth, +0.04 points at 4–6 months rising to +0.17 at 22–24 months
   (GLMM), and the stratified estimator gives the same shape with intervals that
   include zero (Wald p = 0.18), i.e. a linear drift that is not separable from
   calendar within events. The judge scores novelty against the realized paper,
   so the natural reading is that the further an event lies beyond the cutoff,
   the more a model's proposal diverges from what the field actually did, and the
   judge reads that divergence as novelty. The size is 0.17 points on a 0–10
   scale over two years, and it is offset in the total by specificity and
   alignment edging down, which is why the total is flat.
2. **GPT-5.4's Holm-significant total decline (§4) decomposes into specificity
   (−0.62 [−0.79, −0.46] per year) and novelty (−0.60 [−0.78, −0.40]), with
   alignment and feasibility flat.** Both are the corpus step already diagnosed in
   §4: on the original corpus alone all four of its dimension slopes are
   non-significant and three are positive.
3. **Feasibility's apparently strong bin-dummy omnibus on the merged corpus
   (stratified Wald p = 2 × 10⁻¹⁵) is a corpus artefact.** All bins up to 27 months
   sit within ±0.13 points of the reference; the signal is the 28–36 month bins
   (+0.15, +0.34, +0.74), which for the two oldest-cutoff models exist only in
   the extension. On the original corpus the feasibility omnibus is p = 0.11
   (GLMM) and 0.14 (stratified) and the pooled slope is +0.031 [−0.021, +0.083].
4. **Retrieval raises alignment most and interacts with horizon on no
   dimension.** Mean WS − base differences on the pinned subset: alignment
   +0.47 points, feasibility +0.28, specificity +0.28, novelty +0.12, total
   +0.29; ws × horizon p between 0.07 and 0.55 for every dimension. Per model,
   the only cells with uncorrected p < 0.05 are GPT-4o's novelty and alignment
   gradients, which retrieval flattens (−0.23 and −0.31 per 12 months), and
   GPT-5.4's feasibility on 106 items.
5. **The variance decomposition is dimension-specific.** Specificity and novelty
   are model properties (model SD 1.9 vs event SD 0.4), which is where the §4
   statement "model identity explains three times what paper identity does"
   comes from. Alignment is the exception: event SD 0.94 and model SD 0.95, so
   which paper is asked matters as much as which model answers. Feasibility sits
   between (0.67 vs 0.78). The conclusion in §4 should be stated for specificity
   and novelty rather than for FRQ as a whole.

**Bottom line for the reviewer.** Splitting the tasks changes no conclusion and
sharpens two. The binary horizon slopes of opposite sign on the two question
forms, with matching magnitudes in every long-range model, show that the merged
binary trend is a drift in the Yes-rate rather than a change in discrimination.
FRQ's flat total hides one rising dimension, novelty, whose gradient is small,
positive, and most plausibly a scoring consequence of the forecast diverging from
the realized approach; no dimension declines with horizon within a corpus.



## 2. Pooled crossed-random-effects GLMM, all datasets

Same estimator as `tables/pooled.md`: crossed random intercepts for EVENT and MODEL, horizon in years (centred), Laplace GLMM (logistic for the two binary variants, Gaussian for the FRQ total and each rubric dimension). Holm across the family of pooled linear-horizon coefficients in this file; `*` = Holm p < 0.05. The identification note of the main table applies unchanged.


### 1. original corpus (Jan 2024–Mar 2026), base

#### binary — n=11844 items, 2755 events, 9 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | +0.859 [+0.700, +1.019] | 0 / 0* | — | — [—, —] | 1.693 | 2.030 | — |
| h+cal | +0.427 [-1.146, +1.999] | — | 0.436 | — [—, —] | 1.693 | 2.013 | — |
| h+h2 | +0.826 [+0.662, +0.990] | — | — | 0.160 [0.001, 0.318] | 1.698 | 2.027 | — |
| h+random_slope | +0.779 [+0.522, +1.036] | — | — | — [—, —] | 1.695 | 2.042 | 0.221 |
| event-FE conditional logit, curvature only | quadratic +0.255 [+0.065, +0.445] p=0.00838 (n informative strata = 2403) | | | | | | |
#### binary_perturbed — n=16454 items, 3656 events, 9 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.711 [-0.860, -0.562] | 0 / 0* | — | — [—, —] | 2.009 | 1.797 | — |
| h+cal | -0.653 [-2.024, +0.718] | — | -0.058 | — [—, —] | 2.009 | 1.797 | — |
| h+h2 | -0.697 [-0.849, -0.545] | — | — | -0.071 [-0.204, 0.062] | 2.011 | 1.798 | — |
| h+random_slope | -0.632 [-0.899, -0.365] | — | — | — [—, —] | 2.016 | 1.813 | 0.249 |
| event-FE conditional logit, curvature only | quadratic -0.173 [-0.329, -0.017] p=0.0302 (n informative strata = 3002) | | | | | | |
#### FRQ by rubric dimension — n=18461 items, 4135 events, 9 models, horizon 1–29 months

| dimension | model | horizon coef (points per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| FRQ total (mean of 4) | h | +0.026 [-0.006, +0.059] | 0.115 / 1 | — | — | 0.472 | 1.444 | 0.706 |
| FRQ total (mean of 4) | h+cal | -0.611 [-1.696, +0.475] | — | 0.638 | — | 0.472 | 1.444 | 0.706 |
| FRQ total (mean of 4) | h+h2 | +0.038 [+0.005, +0.072] | — | — | -0.050 | 0.472 | 1.870 | 0.705 |
| FRQ alignment | h | -0.023 [-0.081, +0.035] | 0.433 / 1 | — | — | 0.928 | 0.481 | 1.084 |
| FRQ alignment | h+cal | -0.512 [-0.712, -0.312] | — | 0.500 | — | 0.928 | 0.244 | 1.084 |
| FRQ alignment | h+h2 | +0.008 [-0.052, +0.067] | — | — | -0.098 | 0.928 | 0.962 | 1.084 |
| FRQ specificity | h | -0.033 [-0.068, +0.002] | 0.0634 / 1 | — | — | 0.390 | 1.900 | 0.952 |
| FRQ specificity | h+cal | -0.961 [-2.376, +0.455] | — | 0.928 | — | 0.390 | 1.883 | 0.952 |
| FRQ specificity | h+h2 | -0.024 [-0.061, +0.012] | — | — | -0.037 | 0.389 | 1.419 | 0.952 |
| FRQ novelty | h | +0.117 [+0.082, +0.152] | 4.25e-11 / 1.02e-09* | — | — | 0.386 | 1.948 | 0.955 |
| FRQ novelty | h+cal | -0.850 [-2.313, +0.614] | — | 0.967 | — | 0.387 | 1.947 | 0.955 |
| FRQ novelty | h+h2 | +0.117 [+0.080, +0.153] | — | — | 0.003 | 0.386 | 1.947 | 0.955 |
| FRQ feasibility | h | +0.031 [-0.021, +0.083] | 0.24 / 1 | — | — | 0.683 | 0.377 | 1.281 |
| FRQ feasibility | h+cal | -0.067 [-0.363, +0.230] | — | 0.100 | — | 0.683 | 0.369 | 1.281 |
| FRQ feasibility | h+h2 | +0.047 [-0.006, +0.101] | — | — | -0.068 | 0.684 | 0.385 | 1.281 |

### 2. extension (Apr–Aug 2026), base

#### binary — n=1694 items, 196 events, 9 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | +0.590 [-0.862, +2.041] | 0.426 / 1 | — | — [—, —] | 1.807 | 2.465 | — |
| h+cal | +0.796 [-0.953, +2.545] | — | -0.652 | — [—, —] | 1.804 | 2.456 | — |
| h+h2 | +0.521 [-0.945, +1.987] | — | — | 0.414 [-0.305, 1.132] | 1.812 | 2.486 | — |
| h+random_slope | +0.590 [-0.861, +2.041] | — | — | — [—, —] | 1.807 | 2.465 | 0.002 |
| event-FE conditional logit, curvature only | quadratic +0.560 [-0.257, +1.377] p=0.179 (n informative strata = 193) | | | | | | |
#### binary_perturbed — n=5539 items, 649 events, 9 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.899 [-1.963, +0.164] | 0.0975 / 1 | — | — [—, —] | 2.240 | 1.956 | — |
| h+cal | -0.929 [-2.313, +0.455] | — | 0.072 | — [—, —] | 2.240 | 1.956 | — |
| h+h2 | -0.958 [-2.025, +0.109] | — | — | 0.297 [-0.083, 0.676] | 2.242 | 1.957 | — |
| h+random_slope | -0.932 [-2.021, +0.158] | — | — | — [—, —] | 2.242 | 1.801 | 0.577 |
| event-FE conditional logit, curvature only | quadratic +0.378 [-0.042, +0.798] p=0.0779 (n informative strata = 595) | | | | | | |
#### FRQ by rubric dimension — n=5434 items, 630 events, 9 models, horizon 1–34 months

| dimension | model | horizon coef (points per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| FRQ total (mean of 4) | h | -0.150 [-0.503, +0.203] | 0.406 / 1 | — | — | 0.470 | 4.823 | 0.658 |
| FRQ total (mean of 4) | h+cal | -0.467 [-3.871, +2.937] | — | 0.321 | — | 0.470 | 4.822 | 0.658 |
| FRQ total (mean of 4) | h+h2 | -0.157 [-0.498, +0.184] | — | — | -0.080 | 0.464 | 1.985 | 0.658 |
| FRQ alignment | h | -0.252 [-0.737, +0.233] | 0.308 / 1 | — | — | 1.003 | 0.910 | 1.189 |
| FRQ alignment | h+cal | -0.357 [-1.001, +0.286] | — | 0.243 | — | 1.003 | 0.910 | 1.189 |
| FRQ alignment | h+h2 | -0.238 [-0.725, +0.248] | — | — | -0.055 | 1.003 | 0.910 | 1.189 |
| FRQ specificity | h | -0.359 [-0.647, -0.071] | 0.0144 / 0.274 | — | — | 0.407 | 0.714 | 0.910 |
| FRQ specificity | h+cal | -0.906 [-1.263, -0.550] | — | 0.809 | — | 0.406 | 0.504 | 0.910 |
| FRQ specificity | h+h2 | -0.378 [-0.653, -0.103] | — | — | -0.169 | 0.407 | 0.622 | 0.909 |
| FRQ novelty | h | -0.236 [-0.601, +0.129] | 0.205 / 1 | — | — | 0.458 | 1.567 | 0.972 |
| FRQ novelty | h+cal | -0.711 [-1.818, +0.395] | — | 0.533 | — | 0.458 | 1.567 | 0.972 |
| FRQ novelty | h+h2 | -0.222 [-0.586, +0.143] | — | — | -0.124 | 0.458 | 1.568 | 0.972 |
| FRQ feasibility | h | +0.006 [-0.281, +0.293] | 0.968 / 1 | — | — | 0.606 | 0.497 | 1.147 |
| FRQ feasibility | h+cal | +0.106 [-0.239, +0.452] | — | -0.298 | — | 0.606 | 0.487 | 1.147 |
| FRQ feasibility | h+h2 | -0.001 [-0.287, +0.285] | — | — | 0.032 | 0.606 | 0.488 | 1.147 |

### 4. merged original + extension, base

#### binary — n=13538 items, 2951 events, 10 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | +0.742 [+0.604, +0.881] | 0 / 0* | — | — [—, —] | 1.717 | 2.017 | — |
| h+cal | +0.803 [-0.586, +2.192] | — | -0.061 | — [—, —] | 1.717 | 2.018 | — |
| h+h2 | +0.752 [+0.608, +0.897] | — | — | -0.028 [-0.144, 0.087] | 1.716 | 2.018 | — |
| h+random_slope | +0.730 [+0.570, +0.891] | — | — | — [—, —] | 1.712 | 2.020 | 0.089 |
| event-FE conditional logit, curvature only | quadratic -0.002 [-0.137, +0.132] p=0.974 (n informative strata = 2596) | | | | | | |
#### binary_perturbed — n=21993 items, 4305 events, 10 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.662 [-0.779, -0.546] | 0 / 0* | — | — [—, —] | 2.070 | 1.847 | — |
| h+cal | -0.966 [-2.219, +0.287] | — | 0.306 | — [—, —] | 2.070 | 1.825 | — |
| h+h2 | -0.679 [-0.801, -0.558] | — | — | 0.041 [-0.042, 0.124] | 2.070 | 1.845 | — |
| h+random_slope | -0.666 [-0.805, -0.528] | — | — | — [—, —] | 2.072 | 1.856 | 0.083 |
| event-FE conditional logit, curvature only | quadratic +0.044 [-0.051, +0.140] p=0.363 (n informative strata = 3597) | | | | | | |
#### FRQ by rubric dimension — n=23895 items, 4765 events, 10 models, horizon 1–34 months

| dimension | model | horizon coef (points per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| FRQ total (mean of 4) | h | +0.014 [-0.012, +0.039] | 0.289 / 1 | — | — | 0.472 | 1.393 | 0.695 |
| FRQ total (mean of 4) | h+cal | -0.463 [-1.418, +0.492] | — | 0.477 | — | 0.472 | 1.393 | 0.695 |
| FRQ total (mean of 4) | h+h2 | +0.009 [-0.018, +0.036] | — | — | 0.009 | 0.472 | 1.393 | 0.695 |
| FRQ alignment | h | -0.025 [-0.072, +0.021] | 0.283 / 1 | — | — | 0.944 | 0.951 | 1.112 |
| FRQ alignment | h+cal | -0.363 [-1.015, +0.290] | — | 0.339 | — | 0.944 | 0.951 | 1.112 |
| FRQ alignment | h+h2 | -0.005 [-0.054, +0.044] | — | — | -0.044 | 0.944 | 0.951 | 1.111 |
| FRQ specificity | h | -0.016 [-0.043, +0.011] | 0.237 / 1 | — | — | 0.395 | 1.923 | 0.945 |
| FRQ specificity | h+cal | -0.865 [-2.182, +0.452] | — | 0.849 | — | 0.395 | 1.921 | 0.945 |
| FRQ specificity | h+h2 | -0.030 [-0.060, +0.000] | — | — | 0.028 | 0.395 | 1.923 | 0.945 |
| FRQ novelty | h | +0.067 [+0.039, +0.094] | 2.07e-06 / 4.77e-05* | — | — | 0.404 | 1.905 | 0.960 |
| FRQ novelty | h+cal | -0.647 [-1.953, +0.658] | — | 0.714 | — | 0.404 | 1.905 | 0.960 |
| FRQ novelty | h+h2 | +0.072 [+0.042, +0.103] | — | — | -0.012 | 0.404 | 1.905 | 0.960 |
| FRQ feasibility | h | +0.026 [-0.014, +0.066] | 0.197 / 1 | — | — | 0.672 | 0.784 | 1.255 |
| FRQ feasibility | h+cal | +0.032 [-0.507, +0.570] | — | -0.005 | — | 0.672 | 0.784 | 1.255 |
| FRQ feasibility | h+h2 | -0.000 [-0.044, +0.043] | — | — | 0.056 | 0.674 | 0.988 | 1.255 |

### 3. WS+Cutoff on the pinned 500 subset

#### binary — n=1022 items, 296 events, 7 models, horizon 1–28 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | +0.852 [+0.407, +1.297] | 0.000175 / 0.00368* | — | — [—, —] | 1.405 | 1.766 | — |
| h+cal | +0.998 [-0.565, +2.561] | — | -0.155 | — [—, —] | 1.405 | 1.762 | — |
| h+h2 | +0.841 [+0.378, +1.304] | — | — | 0.040 [-0.448, 0.529] | 1.404 | 1.768 | — |
| h+random_slope | +0.841 [+0.342, +1.339] | — | — | — [—, —] | 1.409 | 1.776 | 0.207 |
| event-FE conditional logit, curvature only | quadratic +0.042 [-0.585, +0.669] p=0.896 (n informative strata = 250) | | | | | | |
#### binary_perturbed — n=1458 items, 394 events, 8 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.603 [-1.022, -0.183] | 0.00484 / 0.0969 | — | — [—, —] | 1.751 | 1.709 | — |
| h+cal | -0.856 [-2.278, +0.565] | — | 0.272 | — [—, —] | 1.750 | 1.677 | — |
| h+h2 | -0.650 [-1.077, -0.223] | — | — | 0.221 [-0.194, 0.635] | 1.746 | 1.691 | — |
| h+random_slope | -0.603 [-1.022, -0.183] | — | — | — [—, —] | 1.751 | 1.708 | 0.002 |
| event-FE conditional logit, curvature only | quadratic +0.038 [-0.470, +0.546] p=0.884 (n informative strata = 317) | | | | | | |
#### FRQ by rubric dimension — n=1565 items, 426 events, 8 models, horizon 1–29 months

| dimension | model | horizon coef (points per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| FRQ total (mean of 4) | h | +0.061 [-0.043, +0.165] | 0.254 / 1 | — | — | 0.453 | 0.672 | 0.762 |
| FRQ total (mean of 4) | h+cal | -0.695 [-0.905, -0.485] | — | 0.777 | — | 0.452 | 0.223 | 0.762 |
| FRQ total (mean of 4) | h+h2 | +0.051 [-0.058, +0.161] | — | — | 0.031 | 0.453 | 0.667 | 0.762 |
| FRQ alignment | h | -0.006 [-0.192, +0.179] | 0.947 / 1 | — | — | 0.928 | 0.918 | 1.171 |
| FRQ alignment | h+cal | -0.508 [-1.273, +0.256] | — | 0.529 | — | 0.927 | 0.918 | 1.172 |
| FRQ alignment | h+h2 | +0.021 [-0.172, +0.214] | — | — | -0.098 | 0.938 | 0.923 | 1.170 |
| FRQ specificity | h | -0.057 [-0.169, +0.056] | 0.326 / 1 | — | — | 0.375 | 1.068 | 0.964 |
| FRQ specificity | h+cal | -1.024 [-2.110, +0.062] | — | 0.980 | — | 0.380 | 1.357 | 0.965 |
| FRQ specificity | h+h2 | -0.062 [-0.183, +0.059] | — | — | 0.018 | 0.375 | 1.066 | 0.964 |
| FRQ novelty | h | +0.242 [+0.135, +0.349] | 9.23e-06 / 0.000203* | — | — | 0.338 | 1.174 | 0.931 |
| FRQ novelty | h+cal | -0.977 [-1.363, -0.591] | — | 1.231 | — | 0.339 | 0.443 | 0.931 |
| FRQ novelty | h+h2 | +0.239 [+0.125, +0.354] | — | — | 0.009 | 0.338 | 1.172 | 0.931 |
| FRQ feasibility | h | +0.074 [-0.085, +0.233] | 0.36 / 1 | — | — | 0.658 | 0.344 | 1.336 |
| FRQ feasibility | h+cal | -0.036 [-0.370, +0.298] | — | 0.133 | — | 0.657 | 0.345 | 1.336 |
| FRQ feasibility | h+h2 | +0.020 [-0.145, +0.185] | — | — | 0.208 | 0.657 | 0.320 | 1.335 |

## 3. Within-model trend tests — merged corpus, base condition
## 4. merged original + extension, base — `base`

| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary | accuracy | 2950 | 3–34 | +0.111 [+0.092, +0.131] | 0.0002 | 0.0754 | +0.0608 (5.08e-28) |
| GPT-4o | binary_perturbed | accuracy | 4303 | 3–34 | -0.104 [-0.121, -0.087] | 0.0002 | 0.0754 | -0.0476 (6.32e-31) |
| GPT-4o | frq | frq_score | 4758 | 3–34 | +0.063 [+0.027, +0.099] | 0.001 | 0.315 | — |
| GPT-4o | frq | frq_alignment | 4758 | 3–34 | -0.035 [-0.092, +0.024] | 0.247 | 1 | — |
| GPT-4o | frq | frq_specificity | 4758 | 3–34 | -0.003 [-0.042, +0.037] | 0.891 | 1 | — |
| GPT-4o | frq | frq_novelty | 4758 | 3–34 | +0.096 [+0.059, +0.131] | 0.0002 | 0.0754 | — |
| GPT-4o | frq | frq_feasibility | 4758 | 3–34 | +0.194 [+0.127, +0.260] | 0.0002 | 0.0754 | — |
| LLaMA 3.3 70B | binary | accuracy | 2930 | 1–32 | +0.044 [+0.031, +0.058] | 0.0002 | 0.0754 | +0.0666 (3.42e-10) |
| LLaMA 3.3 70B | binary_perturbed | accuracy | 4274 | 1–32 | -0.033 [-0.045, -0.020] | 0.0002 | 0.0754 | -0.0349 (1.57e-07) |
| LLaMA 3.3 70B | frq | frq_score | 4723 | 1–32 | -0.041 [-0.071, -0.011] | 0.0064 | 1 | — |
| LLaMA 3.3 70B | frq | frq_alignment | 4723 | 1–32 | -0.064 [-0.117, -0.012] | 0.0152 | 1 | — |
| LLaMA 3.3 70B | frq | frq_specificity | 4723 | 1–32 | -0.056 [-0.088, -0.025] | 0.0004 | 0.128 | — |
| LLaMA 3.3 70B | frq | frq_novelty | 4723 | 1–32 | +0.034 [+0.004, +0.064] | 0.0296 | 1 | — |
| LLaMA 3.3 70B | frq | frq_feasibility | 4723 | 1–32 | -0.077 [-0.135, -0.020] | 0.0078 | 1 | — |
| GPT-OSS 20B | binary | accuracy | 2349 | 1–26 | +0.046 [+0.017, +0.075] | 0.001 | 0.315 | +0.0249 (0.00141) |
| GPT-OSS 20B | binary_perturbed | accuracy | 3687 | 1–26 | -0.063 [-0.086, -0.040] | 0.0002 | 0.0754 | -0.0282 (1.04e-07) |
| GPT-OSS 20B | frq | frq_score | 4018 | 1–26 | +0.028 [-0.018, +0.073] | 0.24 | 1 | — |
| GPT-OSS 20B | frq | frq_alignment | 4018 | 1–26 | -0.007 [-0.077, +0.064] | 0.847 | 1 | — |
| GPT-OSS 20B | frq | frq_specificity | 4018 | 1–26 | +0.115 [+0.053, +0.176] | 0.0004 | 0.128 | — |
| GPT-OSS 20B | frq | frq_novelty | 4018 | 1–26 | +0.087 [+0.025, +0.150] | 0.0082 | 1 | — |
| GPT-OSS 20B | frq | frq_feasibility | 4018 | 1–26 | -0.085 [-0.158, -0.010] | 0.0258 | 1 | — |
| DeepSeek R1 | binary | accuracy | 2014 | 1–20 | +0.130 [+0.085, +0.177] | 0.0002 | 0.0754 | +0.0439 (8.11e-08) |
| DeepSeek R1 | binary_perturbed | accuracy | 2871 | 1–20 | -0.141 [-0.180, -0.102] | 0.0002 | 0.0754 | -0.0476 (6.92e-12) |
| DeepSeek R1 | frq | frq_score | 3231 | 1–20 | +0.060 [-0.003, +0.124] | 0.065 | 1 | — |
| DeepSeek R1 | frq | frq_alignment | 3231 | 1–20 | +0.088 [-0.023, +0.200] | 0.115 | 1 | — |
| DeepSeek R1 | frq | frq_specificity | 3231 | 1–20 | -0.060 [-0.145, +0.027] | 0.171 | 1 | — |
| DeepSeek R1 | frq | frq_novelty | 3231 | 1–20 | +0.132 [+0.046, +0.217] | 0.003 | 0.921 | — |
| DeepSeek R1 | frq | frq_feasibility | 3231 | 1–20 | +0.079 [-0.021, +0.180] | 0.121 | 1 | — |
| Claude S4.5 | binary | accuracy | 1501 | 1–19 | +0.099 [+0.045, +0.153] | 0.0006 | 0.191 | +0.0473 (0.000293) |
| Claude S4.5 | binary_perturbed | accuracy | 2470 | 1–19 | -0.101 [-0.141, -0.062] | 0.0002 | 0.0754 | -0.0415 (1.04e-06) |
| Claude S4.5 | frq | frq_score | 2739 | 1–19 | +0.030 [-0.043, +0.101] | 0.425 | 1 | — |
| Claude S4.5 | frq | frq_alignment | 2739 | 1–19 | +0.041 [-0.074, +0.153] | 0.49 | 1 | — |
| Claude S4.5 | frq | frq_specificity | 2739 | 1–19 | -0.030 [-0.123, +0.061] | 0.521 | 1 | — |
| Claude S4.5 | frq | frq_novelty | 2739 | 1–19 | +0.094 [-0.009, +0.200] | 0.0754 | 1 | — |
| Claude S4.5 | frq | frq_feasibility | 2739 | 1–19 | +0.016 [-0.096, +0.127] | 0.785 | 1 | — |
| GPT-5.4 | binary | accuracy | 808 | 1–12 | +0.107 [-0.018, +0.234] | 0.0888 | 1 | +0.0386 (0.103) |
| GPT-5.4 | binary_perturbed | accuracy | 1583 | 1–12 | -0.079 [-0.160, +0.002] | 0.0548 | 1 | -0.0279 (0.0595) |
| GPT-5.4 | frq | frq_score | 1647 | 1–12 | -0.303 [-0.442, -0.165] | 0.0002 | 0.0754 | — |
| GPT-5.4 | frq | frq_alignment | 1647 | 1–12 | +0.056 [-0.248, +0.347] | 0.744 | 1 | — |
| GPT-5.4 | frq | frq_specificity | 1647 | 1–12 | -0.622 [-0.786, -0.457] | 0.0002 | 0.0754 | — |
| GPT-5.4 | frq | frq_novelty | 1647 | 1–12 | -0.595 [-0.783, -0.404] | 0.0002 | 0.0754 | — |
| GPT-5.4 | frq | frq_feasibility | 1647 | 1–12 | -0.051 [-0.267, +0.153] | 0.626 | 1 | — |
| Claude Sonnet 5 | binary | accuracy | 316 | 1–7 | -0.096 [-0.379, +0.183] | 0.498 | 1 | -0.0378 (0.507) |
| Claude Sonnet 5 | binary_perturbed | accuracy | 822 | 1–7 | -0.010 [-0.184, +0.166] | 0.927 | 1 | -0.0046 (0.91) |
| Claude Sonnet 5 | frq | frq_score | 822 | 1–7 | -0.223 [-0.570, +0.118] | 0.21 | 1 | — |
| Claude Sonnet 5 | frq | frq_alignment | 822 | 1–7 | -0.267 [-0.956, +0.405] | 0.437 | 1 | — |
| Claude Sonnet 5 | frq | frq_specificity | 822 | 1–7 | -0.258 [-0.658, +0.135] | 0.205 | 1 | — |
| Claude Sonnet 5 | frq | frq_novelty | 822 | 1–7 | +0.087 [-0.370, +0.545] | 0.697 | 1 | — |
| Claude Sonnet 5 | frq | frq_feasibility | 822 | 1–7 | -0.453 [-0.970, +0.052] | 0.0812 | 1 | — |
| GPT-5.6 Sol | binary | accuracy | 201 | 1–6 | -0.220 [-0.724, +0.326] | 0.416 | 1 | -0.0924 (0.412) |
| GPT-5.6 Sol | binary_perturbed | accuracy | 661 | 1–6 | -0.101 [-0.414, +0.222] | 0.532 | 1 | -0.0352 (0.533) |
| GPT-5.6 Sol | frq | frq_score | 633 | 1–6 | +0.060 [-0.478, +0.591] | 0.819 | 1 | — |
| GPT-5.6 Sol | frq | frq_alignment | 633 | 1–6 | -0.016 [-1.237, +1.190] | 0.995 | 1 | — |
| GPT-5.6 Sol | frq | frq_specificity | 633 | 1–6 | +0.353 [-0.241, +0.944] | 0.245 | 1 | — |
| GPT-5.6 Sol | frq | frq_novelty | 633 | 1–6 | -0.003 [-0.680, +0.682] | 0.998 | 1 | — |
| GPT-5.6 Sol | frq | frq_feasibility | 633 | 1–6 | -0.095 [-0.899, +0.721] | 0.85 | 1 | — |
| DeepSeek-V4-Pro | binary | accuracy | 155 | 1–4 | -0.133 [-0.580, +0.288] | 0.544 | 1 | -0.1580 (0.551) |
| DeepSeek-V4-Pro | binary_perturbed | accuracy | 506 | 1–4 | -0.164 [-0.510, +0.178] | 0.36 | 1 | -0.1069 (0.346) |
| DeepSeek-V4-Pro | frq | frq_score | 497 | 1–4 | +0.028 [-0.755, +0.821] | 0.947 | 1 | — |
| DeepSeek-V4-Pro | frq | frq_alignment | 497 | 1–4 | +0.018 [-1.537, +1.523] | 0.976 | 1 | — |
| DeepSeek-V4-Pro | frq | frq_specificity | 497 | 1–4 | +0.851 [-0.297, +1.986] | 0.146 | 1 | — |
| DeepSeek-V4-Pro | frq | frq_novelty | 497 | 1–4 | -0.109 [-1.256, +1.042] | 0.851 | 1 | — |
| DeepSeek-V4-Pro | frq | frq_feasibility | 497 | 1–4 | -0.650 [-1.953, +0.658] | 0.348 | 1 | — |
| Claude Opus 4.8 | binary | accuracy | 314 | 1–7 | -0.178 [-0.432, +0.081] | 0.176 | 1 | -0.0845 (0.181) |
| Claude Opus 4.8 | binary_perturbed | accuracy | 816 | 1–7 | +0.063 [-0.108, +0.235] | 0.48 | 1 | +0.0294 (0.471) |
| Claude Opus 4.8 | frq | frq_score | 827 | 1–7 | -0.282 [-0.622, +0.064] | 0.11 | 1 | — |
| Claude Opus 4.8 | frq | frq_alignment | 827 | 1–7 | -0.287 [-0.990, +0.404] | 0.427 | 1 | — |
| Claude Opus 4.8 | frq | frq_specificity | 827 | 1–7 | -0.146 [-0.528, +0.254] | 0.467 | 1 | — |
| Claude Opus 4.8 | frq | frq_novelty | 827 | 1–7 | -0.186 [-0.618, +0.245] | 0.405 | 1 | — |
| Claude Opus 4.8 | frq | frq_feasibility | 827 | 1–7 | -0.508 [-1.015, +0.019] | 0.0604 | 1 | — |



## 4. WS+Cutoff vs base on the pinned 500 subset

Same estimators as `tables/ws_vs_base.md`. Per model: slope of outcome on horizon (per 12 months) under each condition on the SAME items, paired difference by event bootstrap (10k). Pooled: conditional logit stratified by (event, model) for the binary variants; paired-difference OLS with model FE and event-clustered SE for each FRQ dimension.

| model | task | metric | n paired items | horizon | base slope /12mo [CI] | WS+cut slope /12mo [CI] | difference (WS − base) [CI] | p |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary | accuracy | 296 | 3–28 | +0.158 [+0.092, +0.226] | +0.049 [-0.045, +0.143] | -0.110 [-0.206, -0.013] | 0.0258 |
| GPT-4o | binary_perturbed | accuracy | 394 | 3–29 | -0.089 [-0.152, -0.026] | -0.054 [-0.133, +0.025] | +0.035 [-0.037, +0.107] | 0.339 |
| GPT-4o | frq | FRQ total (mean of 4) | 425 | 3–29 | +0.097 [-0.052, +0.247] | -0.026 [-0.187, +0.129] | -0.123 [-0.303, +0.049] | 0.167 |
| GPT-4o | frq | FRQ alignment | 425 | 3–29 | +0.018 [-0.220, +0.258] | -0.294 [-0.564, -0.029] | -0.312 [-0.594, -0.035] | 0.0258 |
| GPT-4o | frq | FRQ specificity | 425 | 3–29 | -0.015 [-0.174, +0.144] | +0.018 [-0.172, +0.205] | +0.032 [-0.187, +0.252] | 0.793 |
| GPT-4o | frq | FRQ novelty | 425 | 3–29 | +0.334 [+0.182, +0.489] | +0.105 [-0.047, +0.258] | -0.229 [-0.424, -0.034] | 0.02 |
| GPT-4o | frq | FRQ feasibility | 425 | 3–29 | +0.051 [-0.220, +0.320] | +0.065 [-0.186, +0.312] | +0.014 [-0.287, +0.309] | 0.928 |
| LLaMA 3.3 70B | binary | accuracy | 294 | 1–26 | +0.026 [-0.022, +0.073] | +0.059 [-0.006, +0.122] | +0.033 [-0.030, +0.096] | 0.3 |
| LLaMA 3.3 70B | binary_perturbed | accuracy | 393 | 1–27 | -0.026 [-0.082, +0.033] | -0.046 [-0.111, +0.018] | -0.020 [-0.097, +0.053] | 0.576 |
| LLaMA 3.3 70B | frq | FRQ total (mean of 4) | 423 | 1–27 | +0.037 [-0.086, +0.163] | -0.021 [-0.158, +0.115] | -0.058 [-0.216, +0.098] | 0.463 |
| LLaMA 3.3 70B | frq | FRQ alignment | 423 | 1–27 | -0.134 [-0.348, +0.083] | -0.105 [-0.382, +0.183] | +0.029 [-0.269, +0.318] | 0.836 |
| LLaMA 3.3 70B | frq | FRQ specificity | 423 | 1–27 | -0.070 [-0.187, +0.049] | -0.047 [-0.188, +0.094] | +0.024 [-0.150, +0.192] | 0.783 |
| LLaMA 3.3 70B | frq | FRQ novelty | 423 | 1–27 | +0.152 [+0.040, +0.263] | +0.123 [-0.012, +0.255] | -0.029 [-0.184, +0.123] | 0.706 |
| LLaMA 3.3 70B | frq | FRQ feasibility | 423 | 1–27 | +0.199 [-0.034, +0.435] | -0.056 [-0.287, +0.180] | -0.255 [-0.554, +0.034] | 0.086 |
| DeepSeek R1 | binary | accuracy | 203 | 1–19 | +0.075 [-0.074, +0.222] | +0.068 [-0.081, +0.222] | -0.007 [-0.137, +0.124] | 0.916 |
| DeepSeek R1 | binary_perturbed | accuracy | 304 | 1–20 | -0.136 [-0.259, -0.013] | +0.030 [-0.095, +0.159] | +0.166 [+0.048, +0.288] | 0.007 |
| DeepSeek R1 | frq | FRQ total (mean of 4) | 319 | 1–20 | +0.129 [-0.094, +0.358] | +0.002 [-0.208, +0.227] | -0.127 [-0.383, +0.127] | 0.336 |
| DeepSeek R1 | frq | FRQ alignment | 319 | 1–20 | +0.346 [-0.073, +0.779] | -0.062 [-0.459, +0.344] | -0.408 [-0.860, +0.036] | 0.069 |
| DeepSeek R1 | frq | FRQ specificity | 319 | 1–20 | -0.064 [-0.367, +0.233] | -0.060 [-0.331, +0.212] | +0.004 [-0.343, +0.353] | 0.975 |
| DeepSeek R1 | frq | FRQ novelty | 319 | 1–20 | +0.211 [-0.059, +0.493] | +0.108 [-0.162, +0.374] | -0.103 [-0.465, +0.257] | 0.562 |
| DeepSeek R1 | frq | FRQ feasibility | 319 | 1–20 | +0.024 [-0.310, +0.356] | +0.024 [-0.280, +0.327] | -0.000 [-0.388, +0.398] | 0.995 |
| Claude S4.5 | binary | accuracy | 136 | 1–13 | +0.256 [+0.014, +0.503] | +0.065 [-0.184, +0.314] | -0.191 [-0.479, +0.094] | 0.196 |
| Claude S4.5 | binary_perturbed | accuracy | 206 | 1–14 | +0.063 [-0.114, +0.232] | -0.133 [-0.325, +0.060] | -0.196 [-0.396, +0.005] | 0.057 |
| Claude S4.5 | frq | FRQ total (mean of 4) | 214 | 1–13 | +0.170 [-0.266, +0.615] | +0.229 [-0.168, +0.621] | +0.058 [-0.424, +0.543] | 0.821 |
| Claude S4.5 | frq | FRQ alignment | 214 | 1–13 | +0.433 [-0.204, +1.114] | +0.181 [-0.445, +0.809] | -0.252 [-0.886, +0.364] | 0.426 |
| Claude S4.5 | frq | FRQ specificity | 214 | 1–13 | -0.150 [-0.721, +0.413] | +0.089 [-0.404, +0.589] | +0.239 [-0.436, +0.938] | 0.507 |
| Claude S4.5 | frq | FRQ novelty | 214 | 1–13 | +0.265 [-0.325, +0.860] | +0.495 [-0.050, +1.048] | +0.230 [-0.490, +0.958] | 0.527 |
| Claude S4.5 | frq | FRQ feasibility | 214 | 1–13 | +0.132 [-0.521, +0.783] | +0.149 [-0.440, +0.742] | +0.017 [-0.695, +0.728] | 0.958 |
| GPT-5.4 | binary | — | 59 | | too thin (n<60 or range<3) | | | |
| GPT-5.4 | binary_perturbed | accuracy | 100 | 1–7 | -0.070 [-0.700, +0.574] | +0.596 [+0.017, +1.193] | +0.666 [-0.031, +1.361] | 0.062 |
| GPT-5.4 | frq | FRQ total (mean of 4) | 106 | 1–7 | -0.344 [-1.365, +0.625] | +0.456 [-0.528, +1.451] | +0.799 [-0.340, +2.013] | 0.173 |
| GPT-5.4 | frq | FRQ alignment | 106 | 1–7 | -0.368 [-2.670, +1.749] | -0.471 [-2.785, +1.784] | -0.103 [-2.406, +2.441] | 0.924 |
| GPT-5.4 | frq | FRQ specificity | 106 | 1–7 | -0.281 [-1.436, +0.935] | +0.500 [-0.658, +1.709] | +0.781 [-0.783, +2.261] | 0.3 |
| GPT-5.4 | frq | FRQ novelty | 106 | 1–7 | +0.290 [-0.876, +1.459] | +0.664 [-0.690, +2.003] | +0.374 [-1.365, +2.136] | 0.673 |
| GPT-5.4 | frq | FRQ feasibility | 106 | 1–7 | -1.015 [-2.658, +0.556] | +1.131 [-0.338, +2.601] | +2.146 [+0.338, +4.112] | 0.0202 |
| Claude Sonnet 5 | binary | — | 14 | | too thin (n<60 or range<3) | | | |
| Claude Sonnet 5 | binary_perturbed | — | 23 | | too thin (n<60 or range<3) | | | |
| Claude Sonnet 5 | frq | — | 24 | | too thin (n<60 or range<3) | | | |
| GPT-5.6 Sol | binary_perturbed | — | 1 | | too thin (n<60 or range<3) | | | |
| GPT-5.6 Sol | frq | — | 1 | | too thin (n<60 or range<3) | | | |
| Claude Opus 4.8 | binary | — | 14 | | too thin (n<60 or range<3) | | | |
| Claude Opus 4.8 | binary_perturbed | — | 22 | | too thin (n<60 or range<3) | | | |
| Claude Opus 4.8 | frq | — | 24 | | too thin (n<60 or range<3) | | | |

### Pooled condition × horizon interaction

| task | n strata / pairs | ws main effect | ws × horizon (per year) [CI] | p |
|---|---|---|---|---|
| binary (conditional logit, event × model strata) | 262 | +0.838 log-odds (se 0.135) | -0.057 [-0.497, +0.383] | 0.8 |
| binary_perturbed (conditional logit, event × model strata) | 343 | -0.418 log-odds (se 0.111) | +0.204 [-0.162, +0.569] | 0.275 |
| FRQ total (mean of 4) (WS − base difference on horizon, model FE, event-clustered) | 1536 | mean diff +0.287 points | -0.083 [-0.196, +0.031] | 0.154 |
| FRQ alignment (WS − base difference on horizon, model FE, event-clustered) | 1536 | mean diff +0.473 points | -0.192 [-0.397, +0.013] | 0.0664 |
| FRQ specificity (WS − base difference on horizon, model FE, event-clustered) | 1536 | mean diff +0.281 points | +0.041 [-0.094, +0.176] | 0.551 |
| FRQ novelty (WS − base difference on horizon, model FE, event-clustered) | 1536 | mean diff +0.117 points | -0.101 [-0.227, +0.024] | 0.112 |
| FRQ feasibility (WS − base difference on horizon, model FE, event-clustered) | 1536 | mean diff +0.278 points | -0.078 [-0.264, +0.108] | 0.411 |



## 5. Continuous shape: spline and broken-stick fits

Curves are for the model-average intercept; 95% band from 500 event-bootstrap refits. The broken-stick model fits `h + max(h − b, 0)` with model FE and picks b by deviance/SSE; its breakpoint CI is a 200-resample event bootstrap over a coarse grid. `bend (curvature)` is the grid month where the spline's second difference is largest. No event effects here: these fits describe the pooled shape, they do not identify horizon from calendar drift.


### 1. original corpus (Jan 2024–Mar 2026), base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary:accuracy | 11844 | 0.0568 | 16 [5, 25] | 0.0471 | 0.0803 | 5.2 (deviance) | 7 |
| binary_perturbed:accuracy | 16454 | -0.0428 | 26 [4, 26] | -0.0410 | -0.1658 | 2.9 (deviance) | 8 |
| frq:frq_score | 18461 | 0.0024 | 4 [4, 24] | 0.0361 | 0.0009 | 8.0 (SSE) | 8 |
| frq:frq_alignment | 18461 | -0.0005 | 8 [4, 23] | 0.0181 | -0.0052 | 18.9 (SSE) | 8 |
| frq:frq_specificity | 18461 | -0.0028 | 4 [4, 24] | 0.0381 | -0.0046 | 11.7 (SSE) | 8 |
| frq:frq_novelty | 18461 | 0.0098 | 4 [4, 26] | 0.0290 | 0.0089 | 2.6 (SSE) | 8 |
| frq:frq_feasibility | 18461 | 0.0032 | 7 [4, 26] | 0.0221 | -0.0003 | 13.4 (SSE) | 8 |

### 2. extension (Apr–Aug 2026), base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary:accuracy | 1694 | -0.0081 | 9 [4, 30] | -0.0589 | 0.0377 | 1.1 (deviance) | 6 |
| binary_perturbed:accuracy | 5539 | -0.0427 | 4 [4, 26] | -0.1773 | -0.0155 | 4.3 (deviance) | 15 |
| frq:frq_score | 5434 | -0.0110 | 7 [4, 30] | 0.0088 | -0.0250 | 2.8 (SSE) | 6 |
| frq:frq_alignment | 5434 | -0.0068 | 7 [4, 28] | 0.0095 | -0.0183 | 1.9 (SSE) | 6 |
| frq:frq_specificity | 5434 | -0.0067 | 7 [8, 28] | 0.0268 | -0.0304 | 7.9 (SSE) | 6 |
| frq:frq_novelty | 5434 | -0.0133 | 17 [4, 28] | 0.0066 | -0.0419 | 5.3 (SSE) | 19 |
| frq:frq_feasibility | 5434 | -0.0171 | 17 [4, 30] | -0.0221 | -0.0098 | 0.3 (SSE) | 6 |

### 4. merged original + extension, base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary:accuracy | 13538 | 0.0481 | 29 [4, 30] | 0.0522 | -0.1426 | 12.0 (deviance) | 7 |
| binary_perturbed:accuracy | 21993 | -0.0396 | 31 [4, 30] | -0.0409 | 0.0525 | 2.6 (deviance) | 7 |
| frq:frq_score | 23895 | 0.0010 | 27 [4, 30] | 0.0004 | 0.0105 | 1.6 (SSE) | 7 |
| frq:frq_alignment | 23895 | -0.0019 | 9 [6, 28] | 0.0093 | -0.0048 | 12.7 (SSE) | 7 |
| frq:frq_specificity | 23895 | -0.0013 | 19 [4, 26] | -0.0036 | 0.0039 | 4.9 (SSE) | 15 |
| frq:frq_novelty | 23895 | 0.0053 | 28 [20, 30] | 0.0072 | -0.0319 | 15.7 (SSE) | 7 |
| frq:frq_feasibility | 23895 | 0.0020 | 27 [26, 30] | -0.0027 | 0.0695 | 81.1 (SSE) | 7 |


## 6. Reviewer's bin-dummy mixed model — omnibus tests (full coefficient tables in `tables/split/binned_coef.md`)
### binary · y · 3m bins — n=11,844 items, 2,755 events, 9 models
Omnibus: GLMM LR χ²(9) = 165.7, p = 4.84e-31; stratified Wald χ²(9) = 17.7, p = 0.0387. Units: log-odds vs reference bin.
### binary · y · 1m bins — n=11,844 items, 2,755 events, 9 models
Omnibus: GLMM LR χ²(27) = 195.7, p = 1.61e-27; stratified Wald χ²(27) = 38.8, p = 0.0661. Units: log-odds vs reference bin.
### binary_perturbed · y · 3m bins — n=16,454 items, 3,656 events, 9 models
Omnibus: GLMM LR χ²(9) = 128.2, p = 2.83e-23; stratified Wald χ²(9) = 11.0, p = 0.276. Units: log-odds vs reference bin.
### binary_perturbed · y · 1m bins — n=16,454 items, 3,656 events, 9 models
Omnibus: GLMM LR χ²(27) = 148.6, p = 9.03e-19; stratified Wald χ²(27) = 36.4, p = 0.107. Units: log-odds vs reference bin.
### frq · frq_score · 3m bins — n=18,461 items, 4,135 events, 9 models
Omnibus: GLMM LR χ²(9) = 19.0, p = 0.0249; stratified Wald χ²(9) = 20.7, p = 0.0138. Units: points (0–10) vs reference bin.
### frq · frq_score · 1m bins — n=18,461 items, 4,135 events, 9 models
Omnibus: GLMM LR χ²(27) = 34.2, p = 0.161; stratified Wald χ²(27) = 36.3, p = 0.109. Units: points (0–10) vs reference bin.
### frq · frq_alignment · 3m bins — n=18,461 items, 4,135 events, 9 models
Omnibus: GLMM LR χ²(9) = 22.1, p = 0.00856; stratified Wald χ²(9) = 25.3, p = 0.00263. Units: points (0–10) vs reference bin.
### frq · frq_alignment · 1m bins — n=18,461 items, 4,135 events, 9 models
Omnibus: GLMM LR χ²(27) = 25.3, p = 0.557; stratified Wald χ²(27) = 31.7, p = 0.244. Units: points (0–10) vs reference bin.
### frq · frq_specificity · 3m bins — n=18,461 items, 4,135 events, 9 models
Omnibus: GLMM LR χ²(9) = 20.0, p = 0.0177; stratified Wald χ²(9) = 18.0, p = 0.0357. Units: points (0–10) vs reference bin.
### frq · frq_specificity · 1m bins — n=18,461 items, 4,135 events, 9 models
Omnibus: GLMM LR χ²(27) = 35.0, p = 0.14; stratified Wald χ²(27) = 33.8, p = 0.173. Units: points (0–10) vs reference bin.
### frq · frq_novelty · 3m bins — n=18,461 items, 4,135 events, 9 models
Omnibus: GLMM LR χ²(9) = 49.5, p = 1.31e-07; stratified Wald χ²(9) = 6.5, p = 0.687. Units: points (0–10) vs reference bin.
### frq · frq_novelty · 1m bins — n=18,461 items, 4,135 events, 9 models
Omnibus: GLMM LR χ²(27) = 66.8, p = 3.12e-05; stratified Wald χ²(27) = 25.8, p = 0.528. Units: points (0–10) vs reference bin.
### frq · frq_feasibility · 3m bins — n=18,461 items, 4,135 events, 9 models
Omnibus: GLMM LR χ²(9) = 14.4, p = 0.107; stratified Wald χ²(9) = 13.6, p = 0.137. Units: points (0–10) vs reference bin.
### frq · frq_feasibility · 1m bins — n=18,461 items, 4,135 events, 9 models
Omnibus: GLMM LR χ²(27) = 22.4, p = 0.719; stratified Wald χ²(27) = 35.1, p = 0.135. Units: points (0–10) vs reference bin.
### binary · y · 3m bins — n=13,538 items, 2,951 events, 10 models
Omnibus: GLMM LR χ²(10) = 167.6, p = 8.78e-31; stratified Wald χ²(10) = 17.8, p = 0.0591. Units: log-odds vs reference bin.
### binary · y · 1m bins — n=13,538 items, 2,951 events, 10 models
Omnibus: GLMM LR χ²(32) = 210.6, p = 3.65e-28; stratified Wald χ²(32) = 54.6, p = 0.00773. Units: log-odds vs reference bin.
### binary_perturbed · y · 3m bins — n=21,993 items, 4,305 events, 10 models
Omnibus: GLMM LR χ²(11) = 180.1, p = 9.78e-33; stratified Wald χ²(11) = 14.9, p = 0.187. Units: log-odds vs reference bin.
### binary_perturbed · y · 1m bins — n=21,993 items, 4,305 events, 10 models
Omnibus: GLMM LR χ²(33) = 209.8, p = 1.3e-27; stratified Wald χ²(33) = 46.7, p = 0.0573. Units: log-odds vs reference bin.
### frq · frq_score · 3m bins — n=23,895 items, 4,765 events, 10 models
Omnibus: GLMM LR χ²(11) = 15.2, p = 0.175; stratified Wald χ²(11) = 31.9, p = 0.000802. Units: points (0–10) vs reference bin.
### frq · frq_score · 1m bins — n=23,895 items, 4,765 events, 10 models
Omnibus: GLMM LR χ²(33) = 33.5, p = 0.442; stratified Wald χ²(33) = nan, p = nan. Units: points (0–10) vs reference bin. **Stratified estimator: design rank-deficient: with event FE, bin membership varies only through the model's cutoff, and 1-month bins are too fine for ten cutoffs; its cells below are not interpretable.**
### frq · frq_alignment · 3m bins — n=23,895 items, 4,765 events, 10 models
Omnibus: GLMM LR χ²(11) = 23.8, p = 0.0134; stratified Wald χ²(11) = 26.5, p = 0.00538. Units: points (0–10) vs reference bin.
### frq · frq_alignment · 1m bins — n=23,895 items, 4,765 events, 10 models
Omnibus: GLMM LR χ²(33) = 39.4, p = 0.206; stratified Wald χ²(33) = nan, p = nan. Units: points (0–10) vs reference bin. **Stratified estimator: design rank-deficient: with event FE, bin membership varies only through the model's cutoff, and 1-month bins are too fine for ten cutoffs; its cells below are not interpretable.**
### frq · frq_specificity · 3m bins — n=23,895 items, 4,765 events, 10 models
Omnibus: GLMM LR χ²(11) = 19.6, p = 0.0504; stratified Wald χ²(11) = 21.3, p = 0.0306. Units: points (0–10) vs reference bin.
### frq · frq_specificity · 1m bins — n=23,895 items, 4,765 events, 10 models
Omnibus: GLMM LR χ²(33) = 43.5, p = 0.105; stratified Wald χ²(33) = nan, p = nan. Units: points (0–10) vs reference bin. **Stratified estimator: design rank-deficient: with event FE, bin membership varies only through the model's cutoff, and 1-month bins are too fine for ten cutoffs; its cells below are not interpretable.**
### frq · frq_novelty · 3m bins — n=23,895 items, 4,765 events, 10 models
Omnibus: GLMM LR χ²(11) = 41.6, p = 1.91e-05; stratified Wald χ²(11) = 15.1, p = 0.177. Units: points (0–10) vs reference bin.
### frq · frq_novelty · 1m bins — n=23,895 items, 4,765 events, 10 models
Omnibus: GLMM LR χ²(33) = 53.7, p = 0.0128; stratified Wald χ²(33) = nan, p = nan. Units: points (0–10) vs reference bin. **Stratified estimator: design rank-deficient: with event FE, bin membership varies only through the model's cutoff, and 1-month bins are too fine for ten cutoffs; its cells below are not interpretable.**
### frq · frq_feasibility · 3m bins — n=23,895 items, 4,765 events, 10 models
Omnibus: GLMM LR χ²(11) = 82.7, p = 4.34e-13; stratified Wald χ²(11) = 94.3, p = 2.33e-15. Units: points (0–10) vs reference bin.
### frq · frq_feasibility · 1m bins — n=23,895 items, 4,765 events, 10 models
Omnibus: GLMM LR χ²(33) = 131.6, p = 1e-13; stratified Wald χ²(33) = nan, p = nan. Units: points (0–10) vs reference bin. **Stratified estimator: design rank-deficient: with event FE, bin membership varies only through the model's cutoff, and 1-month bins are too fine for ten cutoffs; its cells below are not interpretable.**
### binary · y · 3m bins — 1,016 paired items, 296 events, 7 models
WS main effect (reference bin): GLMM +0.733 [+0.153, +1.313]; stratified +0.934 [+0.237, +1.632]. Interaction omnibus: GLMM LR p = 0.045; stratified Wald p = 0.0709. Units: log-odds.
### binary · y · 1m bins — 1,016 paired items, 296 events, 7 models
WS main effect (reference bin): GLMM +1.225 [+0.388, +2.062]; stratified —. Interaction omnibus: GLMM LR p = 0.717; stratified Wald p = nan. Units: log-odds.
### binary_perturbed · y · 3m bins — 1,443 paired items, 394 events, 8 models
WS main effect (reference bin): GLMM -0.838 [-1.332, -0.344]; stratified -1.124 [-1.750, -0.498]. Interaction omnibus: GLMM LR p = 0.421; stratified Wald p = 0.287. Units: log-odds.
### binary_perturbed · y · 1m bins — 1,443 paired items, 394 events, 8 models
WS main effect (reference bin): GLMM -0.723 [-1.439, -0.007]; stratified -1.041 [-1.972, -0.111]. Interaction omnibus: GLMM LR p = 0.891; stratified Wald p = 0.886. Units: log-odds.
### frq · frq_score · 3m bins — 1,536 paired items, 426 events, 8 models
WS main effect (reference bin): GLMM +0.150 [+0.007, +0.294]; stratified +0.074 [-0.147, +0.295]. Interaction omnibus: GLMM LR p = 0.581; stratified Wald p = 0.73. Units: points (0–10).
### frq · frq_score · 1m bins — 1,536 paired items, 426 events, 8 models
WS main effect (reference bin): GLMM +0.118 [-0.087, +0.323]; stratified +0.083 [-0.216, +0.381]. Interaction omnibus: GLMM LR p = 0.602; stratified Wald p = 0.833. Units: points (0–10).
### frq · frq_alignment · 3m bins — 1,536 paired items, 426 events, 8 models
WS main effect (reference bin): GLMM +0.491 [+0.252, +0.730]; stratified +0.257 [-0.039, +0.553]. Interaction omnibus: GLMM LR p = 0.19; stratified Wald p = 0.385. Units: points (0–10).
### frq · frq_alignment · 1m bins — 1,536 paired items, 426 events, 8 models
WS main effect (reference bin): GLMM +0.664 [+0.323, +1.004]; stratified +0.613 [+0.174, +1.053]. Interaction omnibus: GLMM LR p = 0.367; stratified Wald p = 0.173. Units: points (0–10).
### frq · frq_specificity · 3m bins — 1,536 paired items, 426 events, 8 models
WS main effect (reference bin): GLMM +0.118 [-0.062, +0.299]; stratified +0.009 [-0.293, +0.311]. Interaction omnibus: GLMM LR p = 0.0529; stratified Wald p = 0.887. Units: points (0–10).
### frq · frq_specificity · 1m bins — 1,536 paired items, 426 events, 8 models
WS main effect (reference bin): GLMM +0.027 [-0.232, +0.286]; stratified -0.156 [-0.599, +0.287]. Interaction omnibus: GLMM LR p = 0.636; stratified Wald p = 0.896. Units: points (0–10).
### frq · frq_novelty · 3m bins — 1,536 paired items, 426 events, 8 models
WS main effect (reference bin): GLMM +0.031 [-0.144, +0.205]; stratified +0.087 [-0.210, +0.383]. Interaction omnibus: GLMM LR p = 0.858; stratified Wald p = 0.703. Units: points (0–10).
### frq · frq_novelty · 1m bins — 1,536 paired items, 426 events, 8 models
WS main effect (reference bin): GLMM +0.091 [-0.159, +0.341]; stratified +0.149 [-0.262, +0.561]. Interaction omnibus: GLMM LR p = 0.766; stratified Wald p = 0.543. Units: points (0–10).
### frq · frq_feasibility · 3m bins — 1,536 paired items, 426 events, 8 models
WS main effect (reference bin): GLMM -0.039 [-0.283, +0.204]; stratified -0.057 [-0.390, +0.277]. Interaction omnibus: GLMM LR p = 0.224; stratified Wald p = 0.479. Units: points (0–10).
### frq · frq_feasibility · 1m bins — 1,536 paired items, 426 events, 8 models
WS main effect (reference bin): GLMM -0.309 [-0.657, +0.038]; stratified -0.276 [-0.727, +0.175]. Interaction omnibus: GLMM LR p = 0.0514; stratified Wald p = 0.45. Units: points (0–10).

## 7. Binned means by horizon, merged corpus, base condition


## binary — accuracy — condition `base`

| model | 1-3 | 4-6 | 7-12 | 13-24 | 25+ |
|---|---|---|---|---|---|
| GPT-4o | n=19 | 0.055 [0.032, 0.081] n=308 sd=0.23 | 0.119 [0.096, 0.142] n=738 sd=0.32 | 0.223 [0.200, 0.245] n=1256 sd=0.42 | 0.283 [0.248, 0.320] n=629 sd=0.45 |
| LLaMA 3.3 70B | 0.885 [0.839, 0.932] n=192 sd=0.32 | 0.881 [0.849, 0.911] n=404 sd=0.32 | 0.919 [0.897, 0.940] n=632 sd=0.27 | 0.957 [0.946, 0.968] n=1291 sd=0.20 | 0.966 [0.946, 0.983] n=411 sd=0.18 |
| GPT-OSS 20B | 0.145 [0.110, 0.183] n=345 sd=0.35 | 0.154 [0.113, 0.195] n=292 sd=0.36 | 0.200 [0.171, 0.230] n=679 sd=0.40 | 0.206 [0.181, 0.232] n=963 sd=0.40 | 0.214 [0.129, 0.314] n=70 sd=0.41 |
| DeepSeek R1 | 0.372 [0.321, 0.423] n=336 sd=0.48 | 0.462 [0.407, 0.518] n=305 sd=0.50 | 0.548 [0.511, 0.586] n=657 sd=0.50 | 0.529 [0.492, 0.566] n=716 sd=0.50 | n=0 |
| Claude S4.5 | 0.182 [0.140, 0.226] n=314 sd=0.39 | 0.208 [0.164, 0.255] n=318 sd=0.41 | 0.209 [0.176, 0.243] n=575 sd=0.41 | 0.299 [0.248, 0.354] n=294 sd=0.46 | n=0 |
| GPT-5.4 | 0.584 [0.526, 0.643] n=291 sd=0.49 | 0.630 [0.576, 0.684] n=316 sd=0.48 | 0.682 [0.617, 0.746] n=201 sd=0.47 | n=0 | n=0 |
| Claude Sonnet 5 | 0.325 [0.252, 0.399] n=163 sd=0.47 | 0.288 [0.208, 0.368] n=125 sd=0.45 | 0.286 [0.143, 0.464] n=28 sd=0.46 | n=0 | n=0 |
| GPT-5.6 Sol | 0.717 [0.620, 0.804] n=92 sd=0.45 | 0.734 [0.651, 0.817] n=109 sd=0.44 | n=0 | n=0 | n=0 |
| DeepSeek-V4-Pro | 0.087 [0.039, 0.142] n=127 sd=0.28 | 0.036 [0.000, 0.107] n=28 sd=0.19 | n=0 | n=0 | n=0 |
| Claude Opus 4.8 | 0.255 [0.186, 0.323] n=161 sd=0.44 | 0.224 [0.152, 0.304] n=125 sd=0.42 | 0.143 [0.036, 0.286] n=28 sd=0.36 | n=0 | n=0 |

## binary_perturbed — accuracy — condition `base`

| model | 1-3 | 4-6 | 7-12 | 13-24 | 25+ |
|---|---|---|---|---|---|
| GPT-4o | n=15 | 0.924 [0.892, 0.952] n=315 sd=0.27 | 0.836 [0.810, 0.860] n=860 sd=0.37 | 0.736 [0.716, 0.756] n=1834 sd=0.44 | 0.676 [0.650, 0.701] n=1279 sd=0.47 |
| LLaMA 3.3 70B | 0.141 [0.096, 0.192] n=198 sd=0.35 | 0.116 [0.087, 0.148] n=413 sd=0.32 | 0.114 [0.092, 0.136] n=818 sd=0.32 | 0.078 [0.066, 0.090] n=1857 sd=0.27 | 0.058 [0.044, 0.072] n=988 sd=0.23 |
| GPT-OSS 20B | 0.813 [0.775, 0.849] n=417 sd=0.39 | 0.794 [0.755, 0.833] n=408 sd=0.40 | 0.751 [0.724, 0.778] n=967 sd=0.43 | 0.733 [0.711, 0.754] n=1653 sd=0.44 | 0.698 [0.640, 0.756] n=242 sd=0.46 |
| DeepSeek R1 | 0.590 [0.543, 0.637] n=427 sd=0.49 | 0.523 [0.474, 0.570] n=428 sd=0.50 | 0.439 [0.408, 0.472] n=931 sd=0.50 | 0.413 [0.384, 0.442] n=1085 sd=0.49 | n=0 |
| Claude S4.5 | 0.773 [0.735, 0.811] n=471 sd=0.42 | 0.723 [0.680, 0.766] n=415 sd=0.45 | 0.744 [0.714, 0.772] n=858 sd=0.44 | 0.646 [0.612, 0.680] n=726 sd=0.48 | n=0 |
| GPT-5.4 | 0.383 [0.338, 0.429] n=452 sd=0.49 | 0.423 [0.381, 0.468] n=470 sd=0.49 | 0.342 [0.307, 0.378] n=661 sd=0.47 | n=0 | n=0 |
| Claude Sonnet 5 | 0.774 [0.729, 0.819] n=332 sd=0.42 | 0.741 [0.698, 0.784] n=394 sd=0.44 | 0.760 [0.677, 0.844] n=96 sd=0.43 | n=0 | n=0 |
| GPT-5.6 Sol | 0.407 [0.352, 0.466] n=290 sd=0.49 | 0.385 [0.337, 0.434] n=371 sd=0.49 | n=0 | n=0 | n=0 |
| DeepSeek-V4-Pro | 0.855 [0.821, 0.889] n=407 sd=0.35 | 0.828 [0.747, 0.899] n=99 sd=0.38 | n=0 | n=0 | n=0 |
| Claude Opus 4.8 | 0.771 [0.723, 0.816] n=332 sd=0.42 | 0.760 [0.719, 0.802] n=388 sd=0.43 | 0.771 [0.688, 0.854] n=96 sd=0.42 | n=0 | n=0 |

## frq — frq_score — condition `base`

| model | 1-3 | 4-6 | 7-12 | 13-24 | 25+ |
|---|---|---|---|---|---|
| GPT-4o | 3.452 [3.107, 3.810] n=21 sd=0.86 | 3.177 [3.079, 3.273] n=368 sd=0.96 | 3.275 [3.215, 3.336] n=987 sd=0.96 | 3.251 [3.210, 3.291] n=2076 sd=0.93 | 3.358 [3.314, 3.402] n=1306 sd=0.82 |
| LLaMA 3.3 70B | 3.513 [3.409, 3.616] n=226 sd=0.78 | 3.511 [3.445, 3.577] n=497 sd=0.75 | 3.507 [3.461, 3.553] n=912 sd=0.71 | 3.478 [3.447, 3.509] n=2076 sd=0.72 | 3.429 [3.384, 3.475] n=1012 sd=0.72 |
| GPT-OSS 20B | 3.798 [3.716, 3.882] n=461 sd=0.91 | 3.845 [3.761, 3.930] n=461 sd=0.93 | 3.856 [3.801, 3.908] n=1073 sd=0.89 | 3.888 [3.849, 3.926] n=1789 sd=0.85 | 3.810 [3.692, 3.922] n=234 sd=0.89 |
| DeepSeek R1 | 4.124 [4.050, 4.197] n=499 sd=0.84 | 4.177 [4.101, 4.253] n=457 sd=0.83 | 4.191 [4.141, 4.239] n=1081 sd=0.82 | 4.219 [4.173, 4.264] n=1194 sd=0.81 | n=0 |
| Claude S4.5 | 3.900 [3.819, 3.983] n=526 sd=0.97 | 4.021 [3.947, 4.094] n=504 sd=0.85 | 4.072 [4.017, 4.124] n=952 sd=0.84 | 4.015 [3.961, 4.069] n=757 sd=0.76 | n=0 |
| GPT-5.4 | 5.021 [4.950, 5.092] n=507 sd=0.83 | 5.081 [5.014, 5.151] n=502 sd=0.78 | 4.830 [4.764, 4.894] n=638 sd=0.84 | n=0 | n=0 |
| Claude Sonnet 5 | 4.523 [4.427, 4.619] n=333 sd=0.90 | 4.365 [4.283, 4.449] n=386 sd=0.82 | 4.682 [4.539, 4.830] n=103 sd=0.77 | n=0 | n=0 |
| GPT-5.6 Sol | 4.830 [4.732, 4.924] n=268 sd=0.82 | 4.852 [4.766, 4.938] n=365 sd=0.83 | n=0 | n=0 | n=0 |
| DeepSeek-V4-Pro | 3.982 [3.896, 4.066] n=393 sd=0.85 | 4.055 [3.897, 4.214] n=104 sd=0.83 | n=0 | n=0 | n=0 |
| Claude Opus 4.8 | 4.680 [4.583, 4.778] n=334 sd=0.91 | 4.559 [4.481, 4.639] n=389 sd=0.80 | 4.685 [4.522, 4.844] n=104 sd=0.86 | n=0 | n=0 |

## frq — frq_alignment — condition `base`

| model | 1-3 | 4-6 | 7-12 | 13-24 | 25+ |
|---|---|---|---|---|---|
| GPT-4o | 2.857 [2.238, 3.524] n=21 sd=1.53 | 2.234 [2.079, 2.386] n=368 sd=1.51 | 2.312 [2.219, 2.407] n=987 sd=1.51 | 2.218 [2.156, 2.280] n=2076 sd=1.43 | 2.225 [2.154, 2.298] n=1306 sd=1.33 |
| LLaMA 3.3 70B | 2.235 [2.058, 2.420] n=226 sd=1.37 | 2.304 [2.185, 2.425] n=497 sd=1.37 | 2.270 [2.188, 2.354] n=912 sd=1.29 | 2.213 [2.159, 2.268] n=2076 sd=1.28 | 2.157 [2.084, 2.233] n=1012 sd=1.20 |
| GPT-OSS 20B | 1.996 [1.876, 2.121] n=461 sd=1.35 | 2.091 [1.961, 2.221] n=461 sd=1.43 | 2.057 [1.976, 2.136] n=1073 sd=1.36 | 2.052 [1.991, 2.115] n=1789 sd=1.32 | 2.073 [1.902, 2.256] n=234 sd=1.35 |
| DeepSeek R1 | 2.210 [2.086, 2.341] n=499 sd=1.46 | 2.269 [2.136, 2.407] n=457 sd=1.45 | 2.327 [2.242, 2.414] n=1081 sd=1.46 | 2.332 [2.250, 2.416] n=1194 sd=1.47 | n=0 |
| Claude S4.5 | 2.192 [2.080, 2.308] n=526 sd=1.37 | 2.262 [2.143, 2.385] n=504 sd=1.38 | 2.332 [2.243, 2.422] n=952 sd=1.39 | 2.313 [2.217, 2.413] n=757 sd=1.38 | n=0 |
| GPT-5.4 | 3.290 [3.134, 3.446] n=507 sd=1.80 | 3.359 [3.201, 3.522] n=502 sd=1.85 | 3.320 [3.182, 3.459] n=638 sd=1.79 | n=0 | n=0 |
| Claude Sonnet 5 | 2.937 [2.757, 3.120] n=333 sd=1.71 | 2.723 [2.567, 2.881] n=386 sd=1.60 | 3.252 [2.942, 3.583] n=103 sd=1.68 | n=0 | n=0 |
| GPT-5.6 Sol | 3.384 [3.160, 3.601] n=268 sd=1.87 | 3.362 [3.170, 3.556] n=365 sd=1.90 | n=0 | n=0 | n=0 |
| DeepSeek-V4-Pro | 2.046 [1.896, 2.201] n=393 sd=1.57 | 2.154 [1.875, 2.443] n=104 sd=1.51 | n=0 | n=0 | n=0 |
| Claude Opus 4.8 | 3.323 [3.135, 3.518] n=334 sd=1.79 | 3.136 [2.959, 3.314] n=389 sd=1.80 | 3.346 [3.029, 3.673] n=104 sd=1.69 | n=0 | n=0 |

## frq — frq_specificity — condition `base`

| model | 1-3 | 4-6 | 7-12 | 13-24 | 25+ |
|---|---|---|---|---|---|
| GPT-4o | 2.714 [2.332, 3.143] n=21 sd=1.01 | 2.913 [2.815, 3.011] n=368 sd=0.96 | 2.956 [2.895, 3.019] n=987 sd=1.01 | 2.886 [2.842, 2.929] n=2076 sd=1.00 | 2.934 [2.884, 2.984] n=1306 sd=0.93 |
| LLaMA 3.3 70B | 3.412 [3.310, 3.513] n=226 sd=0.77 | 3.374 [3.308, 3.443] n=497 sd=0.76 | 3.360 [3.310, 3.409] n=912 sd=0.76 | 3.314 [3.280, 3.347] n=2076 sd=0.78 | 3.288 [3.241, 3.335] n=1012 sd=0.76 |
| GPT-OSS 20B | 4.859 [4.748, 4.970] n=461 sd=1.22 | 4.931 [4.824, 5.035] n=461 sd=1.16 | 4.847 [4.768, 4.924] n=1073 sd=1.28 | 4.953 [4.898, 5.007] n=1789 sd=1.16 | 5.081 [4.936, 5.218] n=234 sd=1.12 |
| DeepSeek R1 | 5.347 [5.244, 5.445] n=499 sd=1.16 | 5.389 [5.291, 5.488] n=457 sd=1.08 | 5.312 [5.247, 5.377] n=1081 sd=1.08 | 5.321 [5.259, 5.383] n=1194 sd=1.10 | n=0 |
| Claude S4.5 | 4.601 [4.494, 4.703] n=526 sd=1.23 | 4.754 [4.659, 4.851] n=504 sd=1.12 | 4.770 [4.699, 4.837] n=952 sd=1.10 | 4.655 [4.583, 4.728] n=757 sd=1.03 | n=0 |
| GPT-5.4 | 6.112 [6.024, 6.201] n=507 sd=1.04 | 6.191 [6.110, 6.273] n=502 sd=0.94 | 5.730 [5.655, 5.804] n=638 sd=0.97 | n=0 | n=0 |
| Claude Sonnet 5 | 5.336 [5.225, 5.447] n=333 sd=1.04 | 5.130 [5.023, 5.236] n=386 sd=1.05 | 5.408 [5.223, 5.592] n=103 sd=0.99 | n=0 | n=0 |
| GPT-5.6 Sol | 5.877 [5.769, 5.985] n=268 sd=0.90 | 5.923 [5.827, 6.019] n=365 sd=0.93 | n=0 | n=0 | n=0 |
| DeepSeek-V4-Pro | 5.239 [5.122, 5.356] n=393 sd=1.19 | 5.394 [5.163, 5.615] n=104 sd=1.17 | n=0 | n=0 | n=0 |
| Claude Opus 4.8 | 5.428 [5.320, 5.533] n=334 sd=0.99 | 5.314 [5.219, 5.409] n=389 sd=0.97 | 5.481 [5.288, 5.683] n=104 sd=1.04 | n=0 | n=0 |

## frq — frq_novelty — condition `base`

| model | 1-3 | 4-6 | 7-12 | 13-24 | 25+ |
|---|---|---|---|---|---|
| GPT-4o | 2.381 [2.000, 2.762] n=21 sd=0.86 | 2.231 [2.139, 2.326] n=368 sd=0.90 | 2.339 [2.285, 2.397] n=987 sd=0.91 | 2.481 [2.440, 2.522] n=2076 sd=0.93 | 2.506 [2.457, 2.554] n=1306 sd=0.90 |
| LLaMA 3.3 70B | 2.319 [2.226, 2.416] n=226 sd=0.74 | 2.360 [2.298, 2.423] n=497 sd=0.70 | 2.310 [2.264, 2.356] n=912 sd=0.71 | 2.404 [2.370, 2.438] n=2076 sd=0.78 | 2.377 [2.330, 2.425] n=1012 sd=0.77 |
| GPT-OSS 20B | 3.646 [3.531, 3.759] n=461 sd=1.22 | 3.683 [3.575, 3.796] n=461 sd=1.21 | 3.719 [3.649, 3.787] n=1073 sd=1.14 | 3.796 [3.741, 3.850] n=1789 sd=1.20 | 3.684 [3.534, 3.833] n=234 sd=1.18 |
| DeepSeek R1 | 3.958 [3.860, 4.054] n=499 sd=1.10 | 3.972 [3.867, 4.074] n=457 sd=1.14 | 4.137 [4.071, 4.201] n=1081 sd=1.09 | 4.121 [4.059, 4.183] n=1194 sd=1.10 | n=0 |
| Claude S4.5 | 3.909 [3.800, 4.019] n=526 sd=1.28 | 4.093 [3.986, 4.200] n=504 sd=1.26 | 4.069 [3.993, 4.147] n=952 sd=1.20 | 4.098 [4.016, 4.180] n=757 sd=1.17 | n=0 |
| GPT-5.4 | 5.041 [4.941, 5.144] n=507 sd=1.16 | 5.038 [4.938, 5.139] n=502 sd=1.16 | 4.632 [4.545, 4.719] n=638 sd=1.12 | n=0 | n=0 |
| Claude Sonnet 5 | 4.219 [4.102, 4.339] n=333 sd=1.11 | 4.171 [4.060, 4.288] n=386 sd=1.14 | 4.447 [4.223, 4.670] n=103 sd=1.14 | n=0 | n=0 |
| GPT-5.6 Sol | 4.384 [4.254, 4.515] n=268 sd=1.09 | 4.436 [4.332, 4.542] n=365 sd=1.03 | n=0 | n=0 | n=0 |
| DeepSeek-V4-Pro | 3.789 [3.679, 3.901] n=393 sd=1.13 | 3.856 [3.615, 4.096] n=104 sd=1.27 | n=0 | n=0 | n=0 |
| Claude Opus 4.8 | 4.437 [4.320, 4.554] n=334 sd=1.09 | 4.406 [4.301, 4.512] n=389 sd=1.05 | 4.423 [4.212, 4.635] n=104 sd=1.10 | n=0 | n=0 |

## frq — frq_feasibility — condition `base`

| model | 1-3 | 4-6 | 7-12 | 13-24 | 25+ |
|---|---|---|---|---|---|
| GPT-4o | 5.857 [5.190, 6.476] n=21 sd=1.56 | 5.332 [5.149, 5.514] n=368 sd=1.81 | 5.491 [5.379, 5.603] n=987 sd=1.78 | 5.419 [5.347, 5.489] n=2076 sd=1.67 | 5.766 [5.685, 5.847] n=1306 sd=1.52 |
| LLaMA 3.3 70B | 6.088 [5.889, 6.288] n=226 sd=1.51 | 6.006 [5.877, 6.135] n=497 sd=1.45 | 6.088 [6.000, 6.174] n=912 sd=1.36 | 5.981 [5.920, 6.040] n=2076 sd=1.39 | 5.895 [5.810, 5.980] n=1012 sd=1.36 |
| GPT-OSS 20B | 4.692 [4.557, 4.822] n=461 sd=1.47 | 4.677 [4.544, 4.805] n=461 sd=1.44 | 4.800 [4.714, 4.884] n=1073 sd=1.42 | 4.749 [4.685, 4.813] n=1789 sd=1.40 | 4.402 [4.218, 4.581] n=234 sd=1.40 |
| DeepSeek R1 | 4.982 [4.862, 5.104] n=499 sd=1.39 | 5.079 [4.958, 5.199] n=457 sd=1.30 | 4.986 [4.904, 5.067] n=1081 sd=1.35 | 5.102 [5.028, 5.176] n=1194 sd=1.30 | n=0 |
| Claude S4.5 | 4.899 [4.776, 5.021] n=526 sd=1.44 | 4.974 [4.855, 5.091] n=504 sd=1.36 | 5.118 [5.036, 5.197] n=952 sd=1.25 | 4.995 [4.907, 5.083] n=757 sd=1.23 | n=0 |
| GPT-5.4 | 5.641 [5.531, 5.751] n=507 sd=1.27 | 5.737 [5.631, 5.843] n=502 sd=1.21 | 5.636 [5.536, 5.734] n=638 sd=1.27 | n=0 | n=0 |
| Claude Sonnet 5 | 5.598 [5.453, 5.742] n=333 sd=1.34 | 5.438 [5.313, 5.562] n=386 sd=1.26 | 5.621 [5.398, 5.854] n=103 sd=1.17 | n=0 | n=0 |
| GPT-5.6 Sol | 5.675 [5.522, 5.825] n=268 sd=1.26 | 5.688 [5.567, 5.811] n=365 sd=1.19 | n=0 | n=0 | n=0 |
| DeepSeek-V4-Pro | 4.852 [4.712, 4.992] n=393 sd=1.43 | 4.817 [4.558, 5.067] n=104 sd=1.33 | n=0 | n=0 | n=0 |
| Claude Opus 4.8 | 5.530 [5.389, 5.671] n=334 sd=1.31 | 5.380 [5.265, 5.496] n=389 sd=1.17 | 5.490 [5.250, 5.731] n=104 sd=1.28 | n=0 | n=0 |

