# Pooled mixed-effects results (post-cutoff, base condition)

Crossed random intercepts for EVENT and MODEL, horizon in years (centred), Laplace-approximated GLMM (logistic for binary/MCQ, Gaussian for date and FRQ metrics), fixed-effect SE from the inverse augmented Hessian. `h+cal` adds calendar month of the event (years, centred). `h+h2` adds a quadratic. `event_fe_h2` is a conditional logit stratified by event with model fixed effects; there a LINEAR horizon term is exactly collinear (h = calendar − cutoff, both absorbed), so only curvature is reported. Holm across the family of pooled linear-horizon coefficients (`h` model); `*` = Holm p < 0.05.

**Identification note.** With one cutoff per model, horizon = calendar − cutoff. Adding calendar as a covariate leaves the linear horizon coefficient identified only through the between-model relation between cutoff date and model random intercept (ten models). Where `h+cal` moves the horizon coefficient far from the `h` fit, that is the collinearity speaking, not new information. The `h` fit answers 'does performance fall with horizon, allowing each event its own difficulty and each model its own level'; it cannot separate horizon from calendar drift. The quadratic term and the event-FE curvature ARE identified and answer the reviewer's shape question.


## 1. original corpus (Jan 2024–Mar 2026), base

### binary_merged — n=28298 items, 4287 events, 9 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.037 [-0.083, +0.010] | 0.121 / 1 | — | — [—, —] | 0.189 | 0.120 | — |
| h+cal | -0.102 [-0.214, +0.010] | — | 0.072 | — [—, —] | 0.188 | 0.113 | — |
| h+h2 | -0.043 [-0.092, +0.007] | — | — | 0.023 [-0.044, 0.091] | 0.189 | 0.118 | — |
| h+random_slope | -0.049 [-0.147, +0.050] | — | — | — [—, —] | 0.190 | 0.101 | 0.106 |
| event-FE conditional logit, curvature only | quadratic +0.021 [-0.054, +0.095] p=0.591 (n informative strata = 3918) | | | | | | |
### mcq — n=17941 items, 4128 events, 9 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.256 [-0.406, -0.106] | 0.000801 / 0.0128* | — | — [—, —] | 2.425 | 1.472 | — |
| h+cal | -1.724 [-2.171, -1.277] | — | 1.490 | — [—, —] | 2.425 | 0.503 | — |
| h+h2 | -0.252 [-0.404, -0.099] | — | — | -0.019 [-0.142, 0.105] | 2.425 | 1.474 | — |
| h+random_slope | -0.913 [-1.468, -0.359] | — | — | — [—, —] | 2.413 | 0.531 | 0.711 |
| event-FE conditional logit, curvature only | quadratic -0.061 [-0.200, +0.078] p=0.391 (n informative strata = 2030) | | | | | | |
### date — n=11285 items, 2752 events, 9 models, horizon 1–29 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| signed_err | h | -2.537 [-4.254, -0.820] | 0.00377 / 0.0528 | — | — | 9.004 | 0.002 | 54.598 |
| signed_err | h+cal | +5.027 [+3.584, +6.469] | — | -15.980 | — | 1.468 | 0.072 | 39.461 |
| signed_err | h+h2 | -1.306 [-3.162, +0.551] | — | — | -5.030 | 8.628 | 0.002 | 54.598 |
| abs_err | h | -5.368 [-6.513, -4.222] | 0 / 0* | — | — | 1.457 | 0.075 | 36.953 |
| abs_err | h+cal | -3.318 [-4.668, -1.969] | — | -4.033 | — | 1.457 | 0.075 | 36.911 |
| abs_err | h+h2 | -5.876 [-7.120, -4.633] | — | — | 1.979 | 1.457 | 0.075 | 36.955 |
| date_score | h | +0.173 [+0.162, +0.185] | 0 / 0* | — | — | 0.128 | 1.249 | 0.231 |
| date_score | h+cal | +0.062 [-0.875, +0.999] | — | 0.111 | — | 0.128 | 1.249 | 0.231 |
| date_score | h+h2 | +0.199 [+0.187, +0.211] | — | — | -0.092 | 0.126 | 1.582 | 0.229 |
### frq — n=18461 items, 4135 events, 9 models, horizon 1–29 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| frq_score | h | +0.026 [-0.006, +0.059] | 0.115 / 1 | — | — | 0.472 | 1.444 | 0.706 |
| frq_score | h+cal | -0.611 [-1.696, +0.475] | — | 0.638 | — | 0.472 | 1.444 | 0.706 |
| frq_score | h+h2 | +0.038 [+0.005, +0.072] | — | — | -0.050 | 0.472 | 1.870 | 0.705 |

## 2. extension (Apr–Aug 2026), base

### binary_merged — n=6572 items, 680 events, 8 models, horizon 2–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.293 [-0.671, +0.084] | 0.128 / 1 | — | — [—, —] | 1.045 | 0.546 | — |
| h+cal | -0.247 [-0.668, +0.175] | — | -0.230 | — [—, —] | 1.045 | 0.544 | — |
| h+h2 | -0.325 [-0.709, +0.059] | — | — | 0.147 [-0.095, 0.389] | 1.045 | 0.552 | — |
| h+random_slope | -0.293 [-0.671, +0.084] | — | — | — [—, —] | 1.045 | 0.546 | 0.002 |
| event-FE conditional logit, curvature only | quadratic +0.169 [-0.095, +0.434] p=0.21 (n informative strata = 615) | | | | | | |
### mcq — n=4637 items, 606 events, 8 models, horizon 2–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -1.704 [-1.999, -1.409] | 0 / 0* | — | — [—, —] | 2.304 | 0.357 | — |
| h+cal | -1.734 [-2.032, -1.436] | — | 1.209 | — [—, —] | 2.299 | 0.356 | — |
| h+h2 | -1.567 [-1.949, -1.186] | — | — | -0.436 [-0.835, -0.038] | 2.313 | 0.460 | — |
| h+random_slope | -1.704 [-1.999, -1.409] | — | — | — [—, —] | 2.305 | 0.357 | 0.002 |
| event-FE conditional logit, curvature only | quadratic -0.894 [-1.504, -0.285] p=0.00401 (n informative strata = 417) | | | | | | |
### date — n=1480 items, 196 events, 8 models, horizon 2–34 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| signed_err | h | +5.548 [+3.792, +7.304] | 5.94e-10 / 1.07e-08* | — | — | 1.434 | 0.083 | 31.876 |
| signed_err | h+cal | +5.868 [+4.105, +7.630] | — | -22.833 | — | 1.433 | 0.084 | 31.775 |
| signed_err | h+h2 | +6.677 [+4.776, +8.578] | — | — | -4.654 | 1.433 | 0.084 | 31.772 |
| abs_err | h | -3.584 [-4.956, -2.213] | 3.03e-07 / 5.15e-06* | — | — | 1.400 | 0.100 | 24.877 |
| abs_err | h+cal | -3.698 [-5.078, -2.317] | — | 8.145 | — | 1.400 | 0.100 | 24.867 |
| abs_err | h+h2 | -3.261 [-4.751, -1.771] | — | — | -1.334 | 1.400 | 0.100 | 24.875 |
| date_score | h | +0.071 [+0.027, +0.115] | 0.00166 / 0.0249* | — | — | 0.078 | 0.058 | 0.232 |
| date_score | h+cal | +0.092 [+0.048, +0.136] | — | -0.223 | — | 0.075 | 0.055 | 0.232 |
| date_score | h+h2 | +0.085 [+0.071, +0.100] | — | — | 0.015 | 0.076 | 0.002 | 0.239 |
### frq — n=4937 items, 630 events, 8 models, horizon 2–34 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| frq_score | h | -0.187 [-0.523, +0.149] | 0.276 / 1 | — | — | 0.461 | 1.519 | 0.653 |
| frq_score | h+cal | -0.578 [-1.744, +0.589] | — | 0.426 | — | 0.461 | 1.519 | 0.653 |
| frq_score | h+h2 | -0.192 [-0.524, +0.139] | — | — | -0.084 | 0.461 | 1.339 | 0.652 |

## 4. merged original + extension, base

### binary_merged — n=34870 items, 4967 events, 9 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.058 [-0.098, -0.017] | 0.00552 / 0.0663 | — | — [—, —] | 0.395 | 0.257 | — |
| h+cal | -0.168 [-0.350, +0.015] | — | 0.113 | — [—, —] | 0.395 | 0.237 | — |
| h+h2 | -0.042 [-0.088, +0.003] | — | — | -0.033 [-0.079, 0.012] | 0.395 | 0.260 | — |
| h+random_slope | +0.032 [-0.846, +0.911] | — | — | — [—, —] | 0.405 | 1.136 | 1.319 |
| event-FE conditional logit, curvature only | quadratic -0.041 [-0.092, +0.010] p=0.114 (n informative strata = 4533) | | | | | | |
### mcq — n=22578 items, 4734 events, 9 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.170 [-0.286, -0.053] | 0.00435 / 0.0566 | — | — [—, —] | 2.401 | 1.578 | — |
| h+cal | -1.692 [-2.059, -1.326] | — | 1.536 | — [—, —] | 2.401 | 0.472 | — |
| h+h2 | -0.105 [-0.227, +0.018] | — | — | -0.141 [-0.223, -0.058] | 2.405 | 1.603 | — |
| h+random_slope | -0.131 [-0.616, +0.354] | — | — | — [—, —] | 2.408 | 1.016 | 0.621 |
| event-FE conditional logit, curvature only | quadratic -0.189 [-0.284, -0.094] p=9.99e-05 (n informative strata = 2447) | | | | | | |
### date — n=12765 items, 2948 events, 9 models, horizon 1–34 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| signed_err | h | -2.034 [-3.509, -0.559] | 0.00689 / 0.0757 | — | — | 10.508 | 0.002 | 54.598 |
| signed_err | h+cal | +5.556 [+4.384, +6.728] | — | -17.716 | — | 1.462 | 0.073 | 38.657 |
| signed_err | h+h2 | -0.072 [-1.750, +1.606] | — | — | -5.368 | 9.792 | 0.002 | 54.598 |
| abs_err | h | -5.070 [-6.020, -4.120] | 0 / 0* | — | — | 1.453 | 0.077 | 35.765 |
| abs_err | h+cal | -3.547 [-4.630, -2.464] | — | -3.184 | — | 1.453 | 0.077 | 35.718 |
| abs_err | h+h2 | -5.469 [-6.555, -4.383] | — | — | 1.025 | 1.453 | 0.077 | 35.762 |
| date_score | h | +0.136 [+0.126, +0.146] | 0 / 0* | — | — | 0.128 | 3.464 | 0.237 |
| date_score | h+cal | +0.099 [-2.498, +2.696] | — | 0.037 | — | 0.128 | 3.464 | 0.237 |
| date_score | h+h2 | +0.159 [+0.148, +0.170] | — | — | -0.055 | 0.124 | 3.890 | 0.237 |
### frq — n=23398 items, 4765 events, 9 models, horizon 1–34 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| frq_score | h | +0.014 [-0.012, +0.039] | 0.288 / 1 | — | — | 0.472 | 1.785 | 0.695 |
| frq_score | h+cal | -0.581 [-1.920, +0.757] | — | 0.595 | — | 0.472 | 1.785 | 0.695 |
| frq_score | h+h2 | +0.009 [-0.017, +0.036] | — | — | 0.010 | 0.472 | 1.631 | 0.695 |

## 3. WS+Cutoff on the pinned 500 subset

### binary_merged — n=2480 items, 456 events, 8 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.038 [-0.179, +0.102] | 0.593 / 1 | — | — [—, —] | 0.002 | 0.131 | — |
| h+cal | -0.123 [-0.313, +0.067] | — | 0.124 | — [—, —] | 0.002 | 0.118 | — |
| h+h2 | -0.086 [-0.236, +0.065] | — | — | 0.172 [-0.042, 0.386] | 0.002 | 0.120 | — |
| h+random_slope | -0.081 [-0.299, +0.138] | — | — | — [—, —] | 0.002 | 0.109 | 0.186 |
| event-FE conditional logit, curvature only | quadratic +0.126 [-0.120, +0.372] p=0.316 (n informative strata = 419) | | | | | | |
### mcq — n=1532 items, 435 events, 7 models, horizon 1–28 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.507 [-0.925, -0.088] | 0.0177 / 0.177 | — | — [—, —] | 2.266 | 1.190 | — |
| h+cal | -1.466 [-1.937, -0.996] | — | 1.128 | — [—, —] | 2.249 | 0.346 | — |
| h+h2 | -0.444 [-0.880, -0.007] | — | — | -0.174 [-0.581, 0.234] | 2.269 | 1.275 | — |
| h+random_slope | -0.878 [-1.590, -0.166] | — | — | — [—, —] | 2.278 | 0.640 | 0.675 |
| event-FE conditional logit, curvature only | quadratic -0.373 [-0.856, +0.111] p=0.131 (n informative strata = 188) | | | | | | |
### date — n=966 items, 294 events, 7 models, horizon 1–28 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| signed_err | h | -0.674 [-6.410, +5.061] | 0.818 / 1 | — | — | 16.633 | 0.002 | 54.598 |
| signed_err | h+cal | +3.509 [-2.873, +9.891] | — | -10.865 | — | 15.840 | 0.002 | 54.598 |
| signed_err | h+h2 | +0.012 [-6.316, +6.340] | — | — | -2.490 | 16.555 | 0.002 | 54.598 |
| abs_err | h | -3.737 [-9.410, +1.937] | 0.197 / 1 | — | — | 12.919 | 0.002 | 54.598 |
| abs_err | h+cal | -2.500 [-8.870, +3.869] | — | -2.989 | — | 12.864 | 0.002 | 54.598 |
| abs_err | h+h2 | -4.885 [-11.159, +1.388] | — | — | 4.088 | 12.985 | 0.002 | 54.598 |
| date_score | h | +0.158 [+0.122, +0.194] | 0 / 0* | — | — | 0.126 | 1.106 | 0.222 |
| date_score | h+cal | +0.060 [-0.040, +0.159] | — | 0.098 | — | 0.127 | 0.108 | 0.221 |
| date_score | h+h2 | +0.196 [+0.159, +0.233] | — | — | -0.129 | 0.122 | 0.151 | 0.218 |
### frq — n=1565 items, 426 events, 8 models, horizon 1–29 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| frq_score | h | +0.061 [-0.043, +0.165] | 0.254 / 1 | — | — | 0.453 | 0.672 | 0.762 |
| frq_score | h+cal | -0.695 [-0.905, -0.485] | — | 0.777 | — | 0.452 | 0.223 | 0.762 |
| frq_score | h+h2 | +0.051 [-0.058, +0.161] | — | — | 0.031 | 0.453 | 0.667 | 0.762 |
