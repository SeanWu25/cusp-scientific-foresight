# Split analysis — WS+Cutoff vs base on the pinned 500 subset, post-cutoff

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

## Pooled condition × horizon interaction

| task | n strata / pairs | ws main effect | ws × horizon (per year) [CI] | p |
|---|---|---|---|---|
| binary (conditional logit, event × model strata) | 262 | +0.838 log-odds (se 0.135) | -0.057 [-0.497, +0.383] | 0.8 |
| binary_perturbed (conditional logit, event × model strata) | 343 | -0.418 log-odds (se 0.111) | +0.204 [-0.162, +0.569] | 0.275 |
| FRQ total (mean of 4) (WS − base difference on horizon, model FE, event-clustered) | 1536 | mean diff +0.287 points | -0.083 [-0.196, +0.031] | 0.154 |
| FRQ alignment (WS − base difference on horizon, model FE, event-clustered) | 1536 | mean diff +0.473 points | -0.192 [-0.397, +0.013] | 0.0664 |
| FRQ specificity (WS − base difference on horizon, model FE, event-clustered) | 1536 | mean diff +0.281 points | +0.041 [-0.094, +0.176] | 0.551 |
| FRQ novelty (WS − base difference on horizon, model FE, event-clustered) | 1536 | mean diff +0.117 points | -0.101 [-0.227, +0.024] | 0.112 |
| FRQ feasibility (WS − base difference on horizon, model FE, event-clustered) | 1536 | mean diff +0.278 points | -0.078 [-0.264, +0.108] | 0.411 |
