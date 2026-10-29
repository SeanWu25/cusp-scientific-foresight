# Split analysis — pooled mixed-effects results (post-cutoff, base condition)

Same estimator as `tables/pooled.md`: crossed random intercepts for EVENT and MODEL, horizon in years (centred), Laplace GLMM (logistic for the two binary variants, Gaussian for the FRQ total and each rubric dimension). Holm across the family of pooled linear-horizon coefficients in this file; `*` = Holm p < 0.05. The identification note of the main table applies unchanged.


## 1. original corpus (Jan 2024–Mar 2026), base

### binary — n=11844 items, 2755 events, 9 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | +0.859 [+0.700, +1.019] | 0 / 0* | — | — [—, —] | 1.693 | 2.030 | — |
| h+cal | +0.427 [-1.146, +1.999] | — | 0.436 | — [—, —] | 1.693 | 2.013 | — |
| h+h2 | +0.826 [+0.662, +0.990] | — | — | 0.160 [0.001, 0.318] | 1.698 | 2.027 | — |
| h+random_slope | +0.779 [+0.522, +1.036] | — | — | — [—, —] | 1.695 | 2.042 | 0.221 |
| event-FE conditional logit, curvature only | quadratic +0.255 [+0.065, +0.445] p=0.00838 (n informative strata = 2403) | | | | | | |
### binary_perturbed — n=16454 items, 3656 events, 9 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.711 [-0.860, -0.562] | 0 / 0* | — | — [—, —] | 2.009 | 1.797 | — |
| h+cal | -0.653 [-2.024, +0.718] | — | -0.058 | — [—, —] | 2.009 | 1.797 | — |
| h+h2 | -0.697 [-0.849, -0.545] | — | — | -0.071 [-0.204, 0.062] | 2.011 | 1.798 | — |
| h+random_slope | -0.632 [-0.899, -0.365] | — | — | — [—, —] | 2.016 | 1.813 | 0.249 |
| event-FE conditional logit, curvature only | quadratic -0.173 [-0.329, -0.017] p=0.0302 (n informative strata = 3002) | | | | | | |
### FRQ by rubric dimension — n=18461 items, 4135 events, 9 models, horizon 1–29 months

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

## 2. extension (Apr–Aug 2026), base

### binary — n=1539 items, 196 events, 8 models, horizon 2–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | +0.358 [-1.192, +1.907] | 0.651 / 1 | — | — [—, —] | 1.853 | 2.478 | — |
| h+cal | +0.449 [-1.466, +2.364] | — | -0.264 | — [—, —] | 1.853 | 2.476 | — |
| h+h2 | +0.345 [-1.202, +1.892] | — | — | 0.453 [-0.284, 1.189] | 1.862 | 2.465 | — |
| h+random_slope | +0.392 [-1.188, +1.971] | — | — | — [—, —] | 1.859 | 2.345 | 0.684 |
| event-FE conditional logit, curvature only | quadratic +0.622 [-0.215, +1.460] p=0.145 (n informative strata = 187) | | | | | | |
### binary_perturbed — n=5033 items, 649 events, 8 models, horizon 2–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.711 [-1.848, +0.427] | 0.221 / 1 | — | — [—, —] | 2.276 | 2.001 | — |
| h+cal | -0.687 [-2.226, +0.852] | — | -0.052 | — [—, —] | 2.276 | 2.000 | — |
| h+h2 | -0.728 [-1.871, +0.415] | — | — | 0.243 [-0.150, 0.636] | 2.277 | 2.017 | — |
| h+random_slope | -0.722 [-1.898, +0.453] | — | — | — [—, —] | 2.279 | 1.927 | 0.513 |
| event-FE conditional logit, curvature only | quadratic +0.337 [-0.099, +0.773] p=0.13 (n informative strata = 574) | | | | | | |
### FRQ by rubric dimension — n=4937 items, 630 events, 8 models, horizon 2–34 months

| dimension | model | horizon coef (points per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| FRQ total (mean of 4) | h | -0.187 [-0.523, +0.149] | 0.276 / 1 | — | — | 0.461 | 1.519 | 0.653 |
| FRQ total (mean of 4) | h+cal | -0.578 [-1.744, +0.589] | — | 0.426 | — | 0.461 | 1.519 | 0.653 |
| FRQ total (mean of 4) | h+h2 | -0.192 [-0.524, +0.139] | — | — | -0.084 | 0.461 | 1.339 | 0.652 |
| FRQ alignment | h | -0.320 [-0.829, +0.188] | 0.217 / 1 | — | — | 1.003 | 0.911 | 1.187 |
| FRQ alignment | h+cal | -0.514 [-1.214, +0.187] | — | 0.409 | — | 1.003 | 0.911 | 1.187 |
| FRQ alignment | h+h2 | -0.311 [-0.820, +0.198] | — | — | -0.062 | 1.003 | 0.911 | 1.186 |
| FRQ specificity | h | -0.364 [-0.658, -0.070] | 0.0153 / 0.292 | — | — | 0.389 | 0.754 | 0.894 |
| FRQ specificity | h+cal | -0.992 [-1.374, -0.610] | — | 0.847 | — | 0.388 | 0.497 | 0.894 |
| FRQ specificity | h+h2 | -0.383 [-0.670, -0.096] | — | — | -0.143 | 0.389 | 0.687 | 0.894 |
| FRQ novelty | h | -0.245 [-0.607, +0.117] | 0.184 / 1 | — | — | 0.446 | 1.431 | 0.968 |
| FRQ novelty | h+cal | -0.838 [-1.936, +0.261] | — | 0.664 | — | 0.446 | 1.431 | 0.968 |
| FRQ novelty | h+h2 | -0.578 [-0.803, -0.352] | — | — | -0.178 | 0.447 | 0.359 | 0.967 |
| FRQ feasibility | h | -0.044 [-0.346, +0.258] | 0.774 / 1 | — | — | 0.605 | 0.494 | 1.133 |
| FRQ feasibility | h+cal | +0.034 [-0.343, +0.411] | — | -0.210 | — | 0.605 | 0.489 | 1.133 |
| FRQ feasibility | h+h2 | -0.048 [-0.346, +0.251] | — | — | 0.032 | 0.605 | 0.482 | 1.133 |

## 4. merged original + extension, base

### binary — n=13383 items, 2951 events, 9 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | +0.741 [+0.602, +0.880] | 0 / 0* | — | — [—, —] | 1.722 | 1.993 | — |
| h+cal | +0.464 [-1.019, +1.946] | — | 0.279 | — [—, —] | 1.722 | 1.972 | — |
| h+h2 | +0.750 [+0.606, +0.895] | — | — | -0.028 [-0.144, 0.088] | 1.721 | 1.992 | — |
| h+random_slope | +0.728 [+0.567, +0.890] | — | — | — [—, —] | 1.717 | 1.994 | 0.089 |
| event-FE conditional logit, curvature only | quadratic -0.002 [-0.137, +0.132] p=0.972 (n informative strata = 2590) | | | | | | |
### binary_perturbed — n=21487 items, 4305 events, 9 models, horizon 1–34 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.658 [-0.775, -0.541] | 0 / 0* | — | — [—, —] | 2.076 | 1.844 | — |
| h+cal | -0.727 [-2.111, +0.657] | — | 0.069 | — [—, —] | 2.076 | 1.844 | — |
| h+h2 | -0.673 [-0.794, -0.552] | — | — | 0.038 [-0.045, 0.122] | 2.076 | 1.844 | — |
| h+random_slope | -0.661 [-0.800, -0.523] | — | — | — [—, —] | 2.078 | 1.855 | 0.082 |
| event-FE conditional logit, curvature only | quadratic +0.044 [-0.052, +0.140] p=0.372 (n informative strata = 3576) | | | | | | |
### FRQ by rubric dimension — n=23398 items, 4765 events, 9 models, horizon 1–34 months

| dimension | model | horizon coef (points per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |
|---|---|---|---|---|---|---|---|---|
| FRQ total (mean of 4) | h | +0.014 [-0.012, +0.039] | 0.288 / 1 | — | — | 0.472 | 1.785 | 0.695 |
| FRQ total (mean of 4) | h+cal | -0.581 [-1.920, +0.757] | — | 0.595 | — | 0.472 | 1.785 | 0.695 |
| FRQ total (mean of 4) | h+h2 | +0.009 [-0.017, +0.036] | — | — | 0.010 | 0.472 | 1.631 | 0.695 |
| FRQ alignment | h | -0.026 [-0.072, +0.021] | 0.276 / 1 | — | — | 0.945 | 0.952 | 1.109 |
| FRQ alignment | h+cal | -0.520 [-0.708, -0.332] | — | 0.496 | — | 0.935 | 0.248 | 1.108 |
| FRQ alignment | h+h2 | -0.007 [-0.055, +0.042] | — | — | -0.045 | 0.946 | 0.952 | 1.109 |
| FRQ specificity | h | -0.017 [-0.044, +0.010] | 0.207 / 1 | — | — | 0.390 | 1.003 | 0.943 |
| FRQ specificity | h+cal | -0.965 [-1.393, -0.537] | — | 0.948 | — | 0.390 | 0.570 | 0.943 |
| FRQ specificity | h+h2 | -0.030 [-0.060, -0.001] | — | — | 0.029 | 0.390 | 1.001 | 0.942 |
| FRQ novelty | h | +0.067 [+0.039, +0.094] | 1.95e-06 / 4.48e-05* | — | — | 0.401 | 1.852 | 0.959 |
| FRQ novelty | h+cal | -0.781 [-2.149, +0.587] | — | 0.848 | — | 0.401 | 1.824 | 0.959 |
| FRQ novelty | h+h2 | +0.072 [+0.042, +0.102] | — | — | -0.012 | 0.400 | 1.852 | 0.959 |
| FRQ feasibility | h | +0.026 [-0.014, +0.066] | 0.199 / 1 | — | — | 0.675 | 1.178 | 1.255 |
| FRQ feasibility | h+cal | -0.051 [-0.935, +0.832] | — | 0.078 | — | 0.675 | 1.178 | 1.255 |
| FRQ feasibility | h+h2 | +0.001 [-0.041, +0.044] | — | — | 0.056 | 0.672 | 0.690 | 1.254 |

## 3. WS+Cutoff on the pinned 500 subset

### binary — n=1022 items, 296 events, 7 models, horizon 1–28 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | +0.852 [+0.407, +1.297] | 0.000175 / 0.00368* | — | — [—, —] | 1.405 | 1.766 | — |
| h+cal | +0.998 [-0.565, +2.561] | — | -0.155 | — [—, —] | 1.405 | 1.762 | — |
| h+h2 | +0.841 [+0.378, +1.304] | — | — | 0.040 [-0.448, 0.529] | 1.404 | 1.768 | — |
| h+random_slope | +0.841 [+0.342, +1.339] | — | — | — [—, —] | 1.409 | 1.776 | 0.207 |
| event-FE conditional logit, curvature only | quadratic +0.042 [-0.585, +0.669] p=0.896 (n informative strata = 250) | | | | | | |
### binary_perturbed — n=1458 items, 394 events, 8 models, horizon 1–29 months

| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |
|---|---|---|---|---|---|---|---|
| h | -0.603 [-1.022, -0.183] | 0.00484 / 0.0969 | — | — [—, —] | 1.751 | 1.709 | — |
| h+cal | -0.856 [-2.278, +0.565] | — | 0.272 | — [—, —] | 1.750 | 1.677 | — |
| h+h2 | -0.650 [-1.077, -0.223] | — | — | 0.221 [-0.194, 0.635] | 1.746 | 1.691 | — |
| h+random_slope | -0.603 [-1.022, -0.183] | — | — | — [—, —] | 1.751 | 1.708 | 0.002 |
| event-FE conditional logit, curvature only | quadratic +0.038 [-0.470, +0.546] p=0.884 (n informative strata = 317) | | | | | | |
### FRQ by rubric dimension — n=1565 items, 426 events, 8 models, horizon 1–29 months

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
