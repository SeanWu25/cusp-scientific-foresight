# Pooled mixed-effects results (post-cutoff, base condition)

Crossed random intercepts for EVENT and MODEL, horizon in years (centred), Laplace-approximated GLMM (logistic for binary/MCQ, Gaussian for date metrics), fixed-effect SE from the inverse augmented Hessian. `h+cal` adds calendar month of the event (years, centred). `h+h2` adds a quadratic. `event_fe_h2` is a conditional logit stratified by event with model fixed effects; there a LINEAR horizon term is exactly collinear (h = calendar − cutoff, both absorbed), so only curvature is reported. Holm across the family of pooled linear-horizon coefficients (`h` model); `*` = Holm p < 0.05.

**Identification note.** With one cutoff per model, horizon = calendar − cutoff. Adding calendar as a covariate leaves the linear horizon coefficient identified only through the between-model relation between cutoff date and model random intercept (nine models). Where `h+cal` moves the horizon coefficient far from the `h` fit, that is the collinearity speaking, not new information. The `h` fit answers 'does performance fall with horizon, allowing each event its own difficulty and each model its own level'; it cannot separate horizon from calendar drift. The quadratic term and the event-FE curvature ARE identified and answer the reviewer's shape question.


## 1. original corpus (Jan 2024–Mar 2026), base

### binary_merged — n=27982 items, 4287 events, 8 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.033 [-0.080, +0.013] | 0.157 / 0.783 | — | — [—, —] | 0.150 | 0.116 | — |
| h+cal | -0.082 [-0.207, +0.044] | — | 0.052 | — [—, —] | 0.150 | 0.113 | — |
| h+h2 | -0.038 [-0.087, +0.011] | — | — | 0.020 [-0.048, 0.087] | 0.150 | 0.115 | — |
| h+random_slope | -0.037 [-0.136, +0.063] | — | — | — [—, —] | 0.151 | 0.100 | 0.104 |
| event-FE conditional logit, curvature only | quadratic +0.021 [-0.054, +0.096] p=0.585 (n informative strata = 3917) | | | | | | |
### mcq — n=17751 items, 4128 events, 8 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.256 [-0.405, -0.106] | 0.000826 / 0.00908* | — | — [—, —] | 2.428 | 1.236 | — |
| h+cal | -1.562 [-2.026, -1.097] | — | 1.328 | — [—, —] | 2.428 | 0.463 | — |
| h+h2 | -0.251 [-0.403, -0.099] | — | — | -0.021 [-0.145, 0.103] | 2.428 | 1.239 | — |
| h+random_slope | -0.256 [-0.405, -0.106] | — | — | — [—, —] | 2.428 | 1.236 | 0.002 |
| event-FE conditional logit, curvature only | quadratic -0.066 [-0.205, +0.074] p=0.355 (n informative strata = 2025) | | | | | | |
### date — n=11164 items, 2752 events, 8 models

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| signed_err | h | -3.576 [-5.310, -1.842] | 5.3e-05 / 0.000689* | — | — | 8.150 | 0.002 | 54.598 |
| signed_err | h+cal | +4.089 [+2.587, +5.591] | — | -15.008 | — | 1.468 | 0.072 | 39.533 |
| signed_err | h+h2 | -2.694 [-4.569, -0.820] | — | — | -3.589 | 7.965 | 0.002 | 54.598 |
| abs_err | h | -5.635 [-6.797, -4.473] | 0 / 0* | — | — | 1.457 | 0.075 | 37.054 |
| abs_err | h+cal | -3.619 [-5.026, -2.212] | — | -3.721 | — | 1.457 | 0.075 | 37.005 |
| abs_err | h+h2 | -6.287 [-7.547, -5.027] | — | — | 2.560 | 1.457 | 0.075 | 37.043 |
| date_score | h | +0.173 [+0.161, +0.185] | 0 / 0* | — | — | 0.128 | 0.786 | 0.231 |
| date_score | h+cal | +0.063 [-0.580, +0.706] | — | 0.110 | — | 0.128 | 0.786 | 0.231 |
| date_score | h+h2 | +0.197 [+0.185, +0.209] | — | — | -0.092 | 0.126 | 8.568 | 0.230 |

## 2. extension (Apr–Aug 2026), base

### binary_merged — n=6419 items, 680 events, 8 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.305 [-0.666, +0.055] | 0.0965 / 0.675 | — | — [—, —] | 0.938 | 0.541 | — |
| h+cal | -0.272 [-0.675, +0.132] | — | -0.162 | — [—, —] | 0.937 | 0.540 | — |
| h+h2 | -0.335 [-0.698, +0.028] | — | — | 0.183 [-0.058, 0.423] | 0.938 | 0.542 | — |
| h+random_slope | -0.305 [-0.666, +0.057] | — | — | — [—, —] | 0.938 | 0.530 | 0.094 |
| event-FE conditional logit, curvature only | quadratic +0.217 [-0.049, +0.483] p=0.11 (n informative strata = 629) | | | | | | |
### mcq — n=4546 items, 606 events, 8 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -1.205 [-1.818, -0.592] | 0.000117 / 0.0014* | — | — [—, —] | 2.333 | 0.868 | — |
| h+cal | -1.281 [-1.930, -0.632] | — | 0.682 | — [—, —] | 2.332 | 0.867 | — |
| h+h2 | -1.073 [-1.645, -0.501] | — | — | -0.638 [-1.056, -0.220] | 2.341 | 0.791 | — |
| h+random_slope | -1.187 [-1.859, -0.515] | — | — | — [—, —] | 2.335 | 0.721 | 0.543 |
| event-FE conditional logit, curvature only | quadratic -0.852 [-1.390, -0.313] p=0.00193 (n informative strata = 415) | | | | | | |
### date — n=1440 items, 196 events, 8 models

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| signed_err | h | -0.611 [-2.451, +1.229] | 0.515 / 1 | — | — | 1.445 | 0.080 | 33.806 |
| signed_err | h+cal | -0.548 [-2.391, +1.295] | — | -8.420 | — | 1.443 | 0.080 | 33.796 |
| signed_err | h+h2 | -1.093 [-3.007, +0.822] | — | — | 2.750 | 1.443 | 0.080 | 33.771 |
| abs_err | h | -4.321 [-5.746, -2.896] | 2.76e-09 / 4.15e-08* | — | — | 1.405 | 0.096 | 26.155 |
| abs_err | h+cal | -4.396 [-5.822, -2.970] | — | 10.171 | — | 1.405 | 0.096 | 26.124 |
| abs_err | h+h2 | -4.349 [-5.833, -2.866] | — | — | 0.162 | 1.405 | 0.096 | 26.155 |
| date_score | h | +0.045 [-0.008, +0.098] | 0.0967 / 0.675 | — | — | 0.075 | 0.074 | 0.255 |
| date_score | h+cal | +0.065 [+0.033, +0.097] | — | -0.158 | — | 0.092 | 0.039 | 0.253 |
| date_score | h+h2 | +0.044 [-0.018, +0.107] | — | — | -0.045 | 0.075 | 0.089 | 0.254 |

## 4. merged original + extension, base

### binary_merged — n=34401 items, 4967 events, 9 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.059 [-0.099, -0.019] | 0.00372 / 0.0335* | — | — [—, —] | 0.353 | 0.296 | — |
| h+cal | -0.207 [-0.401, -0.013] | — | 0.151 | — [—, —] | 0.353 | 0.262 | — |
| h+h2 | -0.048 [-0.093, -0.003] | — | — | -0.026 [-0.071, 0.020] | 0.353 | 0.300 | — |
| h+random_slope | -0.081 [-0.225, +0.064] | — | — | — [—, —] | 0.357 | 0.279 | 0.177 |
| event-FE conditional logit, curvature only | quadratic -0.029 [-0.080, +0.022] p=0.266 (n informative strata = 4546) | | | | | | |
### mcq — n=22297 items, 4734 events, 9 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.170 [-0.287, -0.053] | 0.00444 / 0.0355* | — | — [—, —] | 2.410 | 1.357 | — |
| h+cal | -1.220 [-1.811, -0.628] | — | 1.063 | — [—, —] | 2.410 | 0.811 | — |
| h+h2 | -0.103 [-0.225, +0.020] | — | — | -0.150 [-0.233, -0.067] | 2.414 | 1.377 | — |
| h+random_slope | -0.050 [-0.535, +0.434] | — | — | — [—, —] | 2.419 | 1.016 | 0.620 |
| event-FE conditional logit, curvature only | quadratic -0.211 [-0.306, -0.115] p=1.48e-05 (n informative strata = 2440) | | | | | | |
### date — n=12604 items, 2948 events, 9 models

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| signed_err | h | -4.034 [-5.511, -2.558] | 8.52e-08 / 1.19e-06* | — | — | 8.407 | 0.002 | 54.598 |
| signed_err | h+cal | +2.666 [+1.464, +3.868] | — | -14.533 | — | 1.464 | 0.072 | 38.926 |
| signed_err | h+h2 | -2.514 [-4.187, -0.842] | — | — | -4.174 | 7.918 | 0.002 | 54.598 |
| abs_err | h | -5.386 [-6.347, -4.424] | 0 / 0* | — | — | 1.454 | 0.076 | 35.966 |
| abs_err | h+cal | -4.052 [-5.162, -2.942] | — | -2.690 | — | 1.454 | 0.077 | 35.934 |
| abs_err | h+h2 | -5.958 [-7.051, -4.865] | — | — | 1.506 | 1.454 | 0.076 | 35.970 |
| date_score | h | +0.137 [+0.126, +0.147] | 0 / 0* | — | — | 0.126 | 6.961 | 0.240 |
| date_score | h+cal | +0.079 [-4.945, +5.104] | — | 0.057 | — | 0.126 | 6.961 | 0.240 |
| date_score | h+h2 | +0.161 [+0.150, +0.171] | — | — | -0.060 | 0.122 | 6.370 | 0.240 |

## 3. WS+Cutoff on the pinned 500 subset

### binary_merged — n=2443 items, 456 events, 7 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.028 [-0.170, +0.114] | 0.698 / 1 | — | — [—, —] | 0.002 | 0.132 | — |
| h+cal | -0.106 [-0.311, +0.100] | — | 0.107 | — [—, —] | 0.002 | 0.120 | — |
| h+h2 | -0.070 [-0.222, +0.082] | — | — | 0.158 [-0.060, 0.377] | 0.002 | 0.123 | — |
| h+random_slope | -0.059 [-0.284, +0.165] | — | — | — [—, —] | 0.002 | 0.112 | 0.187 |
| event-FE conditional logit, curvature only | quadratic +0.124 [-0.122, +0.369] p=0.323 (n informative strata = 419) | | | | | | |
### mcq — n=1510 items, 435 events, 6 models, horizon 1–28 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.593 [-0.985, -0.201] | 0.00304 / 0.0304* | — | — [—, —] | 2.279 | 0.623 | — |
| h+cal | -1.290 [-1.730, -0.850] | — | 0.949 | — [—, —] | 2.262 | 0.285 | — |
| h+h2 | -0.539 [-0.946, -0.132] | — | — | -0.168 [-0.574, 0.238] | 2.282 | 0.659 | — |
| h+random_slope | -0.672 [-1.400, +0.055] | — | — | — [—, —] | 2.318 | 0.634 | 0.669 |
| event-FE conditional logit, curvature only | quadratic -0.373 [-0.856, +0.111] p=0.131 (n informative strata = 186) | | | | | | |
### date — n=953 items, 294 events, 6 models

| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| signed_err | h | -1.611 [-7.445, +4.224] | 0.588 / 1 | — | — | 16.652 | 0.002 | 54.598 |
| signed_err | h+cal | +2.536 [-4.089, +9.161] | — | -9.909 | — | 16.123 | 0.002 | 54.598 |
| signed_err | h+h2 | -1.302 [-7.713, +5.109] | — | — | -1.141 | 16.631 | 0.002 | 54.598 |
| abs_err | h | -4.161 [-9.930, +1.608] | 0.157 / 0.783 | — | — | 13.158 | 0.002 | 54.598 |
| abs_err | h+cal | -3.080 [-9.698, +3.537] | — | -2.415 | — | 13.140 | 0.002 | 54.598 |
| abs_err | h+h2 | -5.521 [-11.877, +0.835] | — | — | 4.931 | 13.197 | 0.002 | 54.598 |
| date_score | h | +0.158 [+0.122, +0.194] | 0 / 0* | — | — | 0.128 | 3.668 | 0.222 |
| date_score | h+cal | +0.067 [-3.498, +3.632] | — | 0.091 | — | 0.128 | 3.668 | 0.222 |
| date_score | h+h2 | +0.199 [+0.162, +0.236] | — | — | -0.133 | 0.118 | 0.347 | 0.219 |
