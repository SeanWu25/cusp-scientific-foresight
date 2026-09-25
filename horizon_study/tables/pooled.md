# Pooled mixed-effects results (post-cutoff, base condition)

Crossed random intercepts for EVENT and MODEL, horizon in years (centred), Laplace-approximated GLMM (logistic for binary/MCQ, Gaussian for date and FRQ metrics), fixed-effect SE from the inverse augmented Hessian. `h+cal` adds calendar month of the event (years, centred). `h+h2` adds a quadratic. `event_fe_h2` is a conditional logit stratified by event with model fixed effects; there a LINEAR horizon term is exactly collinear (h = calendar − cutoff, both absorbed), so only curvature is reported. Holm across the family of pooled linear-horizon coefficients (`h` model); `*` = Holm p < 0.05.

**Identification note.** With one cutoff per model, horizon = calendar − cutoff. Adding calendar as a covariate leaves the linear horizon coefficient identified only through the between-model relation between cutoff date and model random intercept (ten models). Where `h+cal` moves the horizon coefficient far from the `h` fit, that is the collinearity speaking, not new information. The `h` fit answers 'does performance fall with horizon, allowing each event its own difficulty and each model its own level'; it cannot separate horizon from calendar drift. The quadratic term and the event-FE curvature ARE identified and answer the reviewer's shape question.


## 1. original corpus (Jan 2024–Mar 2026), base

### binary_merged — n=28298 items, 4287 events, 9 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.037 [-0.083, +0.010] | 0.121 / 0.922 | — | — [—, —] | 0.189 | 0.120 | — |
| h+cal | -0.102 [-0.214, +0.010] | — | 0.072 | — [—, —] | 0.188 | 0.113 | — |
| h+h2 | -0.043 [-0.092, +0.007] | — | — | 0.023 [-0.044, 0.091] | 0.189 | 0.118 | — |
| h+random_slope | -0.049 [-0.147, +0.050] | — | — | — [—, —] | 0.190 | 0.101 | 0.106 |
| event-FE conditional logit, curvature only | quadratic +0.021 [-0.054, +0.095] p=0.591 (n informative strata = 3918) | | | | | | |
### mcq — n=17941 items, 4128 events, 9 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.256 [-0.406, -0.106] | 0.000801 / 0.0136* | — | — [—, —] | 2.425 | 1.472 | — |
| h+cal | -1.724 [-2.171, -1.277] | — | 1.490 | — [—, —] | 2.425 | 0.503 | — |
| h+h2 | -0.252 [-0.404, -0.099] | — | — | -0.019 [-0.142, 0.105] | 2.425 | 1.474 | — |
| h+random_slope | -0.913 [-1.468, -0.359] | — | — | — [—, —] | 2.413 | 0.531 | 0.711 |
| event-FE conditional logit, curvature only | quadratic -0.061 [-0.200, +0.078] p=0.391 (n informative strata = 2030) | | | | | | |
### date — n=11285 items, 2752 events, 9 models, horizon 1–29 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| signed_err | h | -2.537 [-4.254, -0.820] | 0.00377 / 0.0566 | — | — | 9.004 | 0.002 | 54.598 |
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
| frq_score | h | +0.026 [-0.006, +0.059] | 0.115 / 0.922 | — | — | 0.472 | 1.444 | 0.706 |
| frq_score | h+cal | -0.611 [-1.696, +0.475] | — | 0.638 | — | 0.472 | 1.444 | 0.706 |
| frq_score | h+h2 | +0.038 [+0.005, +0.072] | — | — | -0.050 | 0.472 | 1.870 | 0.705 |

## 2. extension (Apr–Aug 2026), base

### binary_merged — n=7233 items, 680 events, 9 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.329 [-0.672, +0.014] | 0.0599 / 0.539 | — | — [—, —] | 1.018 | 0.528 | — |
| h+cal | -0.308 [-0.684, +0.069] | — | -0.123 | — [—, —] | 1.018 | 0.528 | — |
| h+h2 | -0.380 [-0.730, -0.030] | — | — | 0.157 [-0.072, 0.387] | 1.019 | 0.527 | — |
| h+random_slope | -0.330 [-0.676, +0.016] | — | — | — [—, —] | 1.018 | 0.505 | 0.134 |
| event-FE conditional logit, curvature only | quadratic +0.183 [-0.071, +0.436] p=0.158 (n informative strata = 634) | | | | | | |
### mcq — n=5115 items, 606 events, 9 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -1.299 [-1.920, -0.679] | 4.05e-05 / 0.000729* | — | — [—, —] | 2.340 | 0.922 | — |
| h+cal | -1.411 [-2.066, -0.755] | — | 0.977 | — [—, —] | 2.338 | 0.918 | — |
| h+h2 | -1.022 [-1.637, -0.408] | — | — | -0.696 [-1.111, -0.281] | 2.349 | 0.872 | — |
| h+random_slope | -1.255 [-1.902, -0.607] | — | — | — [—, —] | 2.335 | 0.721 | 0.543 |
| event-FE conditional logit, curvature only | quadratic -0.910 [-1.437, -0.383] p=0.000707 (n informative strata = 422) | | | | | | |
### date — n=1633 items, 196 events, 9 models, horizon 1–34 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| signed_err | h | +1.888 [+0.111, +3.665] | 0.0373 / 0.411 | — | — | 1.448 | 0.079 | 34.451 |
| signed_err | h+cal | +1.995 [+0.214, +3.775] | — | -12.032 | — | 1.448 | 0.079 | 34.425 |
| signed_err | h+h2 | +1.089 [-1.030, +3.209] | — | — | 2.122 | 1.448 | 0.079 | 34.421 |
| abs_err | h | -4.349 [-5.719, -2.980] | 4.88e-10 / 9.27e-09* | — | — | 1.409 | 0.095 | 26.537 |
| abs_err | h+cal | -4.449 [-5.822, -3.077] | — | 11.332 | — | 1.409 | 0.095 | 26.515 |
| abs_err | h+h2 | -4.346 [-5.981, -2.710] | — | — | -0.010 | 1.409 | 0.095 | 26.537 |
| date_score | h | +0.051 [+0.002, +0.100] | 0.0434 / 0.434 | — | — | 0.083 | 0.072 | 0.247 |
| date_score | h+cal | +0.070 [+0.019, +0.121] | — | -0.178 | — | 0.081 | 0.070 | 0.247 |
| date_score | h+h2 | +0.056 [-0.001, +0.113] | — | — | -0.030 | 0.083 | 0.081 | 0.247 |
### frq — n=5434 items, 630 events, 9 models, horizon 1–34 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| frq_score | h | -0.150 [-0.503, +0.203] | 0.406 / 1 | — | — | 0.470 | 4.823 | 0.658 |
| frq_score | h+cal | -0.467 [-3.871, +2.937] | — | 0.321 | — | 0.470 | 4.822 | 0.658 |
| frq_score | h+h2 | -0.157 [-0.498, +0.184] | — | — | -0.080 | 0.464 | 1.985 | 0.658 |

## 4. merged original + extension, base

### binary_merged — n=35531 items, 4967 events, 10 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.057 [-0.098, -0.016] | 0.00662 / 0.086 | — | — [—, —] | 0.409 | 0.307 | — |
| h+cal | -0.231 [-0.413, -0.048] | — | 0.178 | — [—, —] | 0.409 | 0.260 | — |
| h+h2 | -0.041 [-0.088, +0.005] | — | — | -0.031 [-0.077, 0.014] | 0.409 | 0.312 | — |
| h+random_slope | +0.001 [-0.835, +0.837] | — | — | — [—, —] | 0.419 | 1.131 | 1.305 |
| event-FE conditional logit, curvature only | quadratic -0.040 [-0.091, +0.011] p=0.123 (n informative strata = 4552) | | | | | | |
### mcq — n=23056 items, 4734 events, 10 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.171 [-0.288, -0.054] | 0.00414 / 0.058 | — | — [—, —] | 2.407 | 1.517 | — |
| h+cal | -1.368 [-1.981, -0.755] | — | 1.210 | — [—, —] | 2.408 | 0.886 | — |
| h+h2 | -0.096 [-0.220, +0.027] | — | — | -0.150 [-0.233, -0.068] | 2.410 | 1.539 | — |
| h+random_slope | -0.076 [-0.553, +0.401] | — | — | — [—, —] | 2.414 | 1.016 | 0.621 |
| event-FE conditional logit, curvature only | quadratic -0.209 [-0.304, -0.115] p=1.48e-05 (n informative strata = 2452) | | | | | | |
### date — n=12918 items, 2948 events, 10 models, horizon 1–34 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| signed_err | h | -2.306 [-3.765, -0.847] | 0.00195 / 0.0312* | — | — | 10.358 | 0.002 | 54.598 |
| signed_err | h+cal | +4.214 [+3.069, +5.359] | — | -16.240 | — | 1.466 | 0.072 | 38.870 |
| signed_err | h+h2 | -0.407 [-2.076, +1.263] | — | — | -5.051 | 9.672 | 0.002 | 54.598 |
| abs_err | h | -5.160 [-6.103, -4.217] | 0 / 0* | — | — | 1.454 | 0.077 | 35.812 |
| abs_err | h+cal | -3.925 [-4.979, -2.872] | — | -2.758 | — | 1.453 | 0.077 | 35.766 |
| abs_err | h+h2 | -5.600 [-6.682, -4.518] | — | — | 1.111 | 1.454 | 0.077 | 35.798 |
| date_score | h | +0.136 [+0.126, +0.146] | 0 / 0* | — | — | 0.127 | 2.207 | 0.239 |
| date_score | h+cal | +0.081 [-1.431, +1.594] | — | 0.055 | — | 0.127 | 2.207 | 0.239 |
| date_score | h+h2 | +0.160 [+0.149, +0.171] | — | — | -0.055 | 0.124 | 2.432 | 0.239 |
### frq — n=23895 items, 4765 events, 10 models, horizon 1–34 months

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| frq_score | h | +0.014 [-0.012, +0.039] | 0.289 / 1 | — | — | 0.472 | 1.393 | 0.695 |
| frq_score | h+cal | -0.463 [-1.418, +0.492] | — | 0.477 | — | 0.472 | 1.393 | 0.695 |
| frq_score | h+h2 | +0.009 [-0.018, +0.036] | — | — | 0.009 | 0.472 | 1.393 | 0.695 |

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
| h | -0.507 [-0.925, -0.088] | 0.0177 / 0.213 | — | — [—, —] | 2.266 | 1.190 | — |
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
