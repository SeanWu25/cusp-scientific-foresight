# Retrieval-constrained (WS+Cutoff) vs base on the pinned 500 subset, post-cutoff

Per model: slope of outcome on horizon (per 12 months) under each condition on the SAME items, and the paired difference (event bootstrap, 10k). Pooled: conditional logit stratified by (event, model) — within a stratum only the condition varies, so `ws × horizon` is identified without any calendar confound.

| model | task | metric | n paired items | horizon | base slope /12mo [CI] | WS+cut slope /12mo [CI] | difference (WS − base) [CI] | p |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary_merged | accuracy | 690 | 3–29 | +0.072 [+0.025, +0.118] | +0.005 [-0.047, +0.057] | -0.067 [-0.121, -0.012] | 0.0168 |
| GPT-4o | mcq | accuracy | 435 | 3–28 | -0.057 [-0.132, +0.020] | -0.058 [-0.133, +0.020] | -0.001 [-0.075, +0.073] | 0.978 |
| GPT-4o | date | signed_err | 275 | 3–28 | -9.729 [-16.076, -2.906] | -9.380 [-15.284, -2.992] | +0.349 [-5.513, +6.313] | 0.9 |
| GPT-4o | date | abs_err | 275 | 3–28 | -8.675 [-14.923, -2.047] | -1.168 [-6.281, +4.339] | +7.507 [+2.039, +13.241] | 0.0054 |
| GPT-4o | date | date_score | 275 | 3–28 | +0.108 [+0.068, +0.149] | +0.127 [+0.073, +0.180] | +0.019 [-0.036, +0.074] | 0.508 |
| LLaMA 3.3 70B | binary_merged | accuracy | 687 | 1–27 | -0.069 [-0.115, -0.023] | -0.054 [-0.101, -0.007] | +0.015 [-0.032, +0.062] | 0.522 |
| LLaMA 3.3 70B | mcq | accuracy | 433 | 1–26 | -0.085 [-0.164, -0.006] | -0.055 [-0.133, +0.023] | +0.030 [-0.049, +0.110] | 0.45 |
| LLaMA 3.3 70B | date | signed_err | 292 | 1–26 | -7.752 [-10.906, -3.720] | -10.761 [-14.816, -6.285] | -3.009 [-6.765, +0.546] | 0.0974 |
| LLaMA 3.3 70B | date | abs_err | 292 | 1–26 | -3.521 [-6.413, +0.070] | +2.774 [-0.873, +6.889] | +6.294 [+2.944, +9.772] | 0.0006 |
| LLaMA 3.3 70B | date | date_score | 292 | 1–26 | +0.183 [+0.137, +0.231] | +0.007 [-0.039, +0.054] | -0.176 [-0.227, -0.125] | 0.0002 |
| DeepSeek R1 | binary_merged | accuracy | 507 | 1–20 | -0.052 [-0.135, +0.033] | +0.040 [-0.049, +0.129] | +0.092 [+0.009, +0.176] | 0.0288 |
| DeepSeek R1 | mcq | accuracy | 293 | 1–19 | +0.068 [-0.059, +0.197] | +0.031 [-0.091, +0.156] | -0.037 [-0.176, +0.108] | 0.619 |
| DeepSeek R1 | date | signed_err | 173 | 1–19 | -9.145 [-16.854, -1.886] | -8.634 [-16.415, -0.900] | +0.510 [-7.916, +9.467] | 0.927 |
| DeepSeek R1 | date | abs_err | 173 | 1–19 | -5.527 [-12.998, +1.251] | +2.875 [-3.632, +9.446] | +8.403 [+1.128, +16.354] | 0.0258 |
| DeepSeek R1 | date | date_score | 173 | 1–19 | +0.149 [+0.069, +0.227] | +0.007 [-0.079, +0.089] | -0.142 [-0.228, -0.054] | 0.0012 |
| Claude S4.5 | binary_merged | accuracy | 342 | 1–14 | +0.150 [+0.007, +0.297] | -0.046 [-0.193, +0.103] | -0.196 [-0.349, -0.043] | 0.0122 |
| Claude S4.5 | mcq | accuracy | 206 | 1–13 | -0.048 [-0.258, +0.160] | -0.012 [-0.215, +0.188] | +0.035 [-0.166, +0.239] | 0.721 |
| Claude S4.5 | date | signed_err | 105 | 1–13 | -3.709 [-23.002, +13.548] | -4.833 [-25.235, +17.071] | -1.124 [-22.005, +21.094] | 0.897 |
| Claude S4.5 | date | abs_err | 105 | 1–13 | -11.287 [-28.584, +3.018] | +13.226 [-1.619, +30.523] | +24.513 [+9.247, +43.775] | 0.0006 |
| Claude S4.5 | date | date_score | 105 | 1–13 | +0.169 [+0.019, +0.319] | +0.000 [-0.170, +0.175] | -0.169 [-0.340, +0.000] | 0.051 |
| GPT-5.4 | binary_merged | accuracy | 159 | 1–7 | -0.073 [-0.534, +0.379] | +0.273 [-0.168, +0.733] | +0.346 [-0.127, +0.840] | 0.155 |
| GPT-5.4 | mcq | accuracy | 105 | 1–6 | -0.459 [-0.917, -0.015] | -0.457 [-0.992, +0.079] | +0.002 [-0.540, +0.532] | 1 |
| GPT-5.4 | date | — | 59 | | too thin (n<60 or range<3) | | | |
| Claude Sonnet 5 | binary_merged | — | 37 | | too thin (n<60 or range<3) | | | |
| Claude Sonnet 5 | mcq | — | 23 | | too thin (n<60 or range<3) | | | |
| Claude Sonnet 5 | date | — | 14 | | too thin (n<60 or range<3) | | | |
| GPT-5.6 Sol | binary_merged | — | 1 | | too thin (n<60 or range<3) | | | |

## Pooled condition × horizon interaction (stratified by event × model)

| task | n strata | ws main effect (log-odds) | ws × horizon (per year) [CI] | p |
|---|---|---|---|---|
| binary_merged | 597 | +0.124 (se 0.082) | -0.005 [-0.277, +0.267] | 0.969 |
| mcq | 364 | +0.270 (se 0.106) | +0.185 [-0.149, +0.519] | 0.278 |
| date:abs_err (WS − base difference on horizon, model FE, event-clustered) | 918 | mean diff -6.395 | +7.882 [+4.545, +11.219] | 3.67e-06 |
| date:date_score (WS − base difference on horizon, model FE, event-clustered) | 918 | mean diff +0.077 | -0.094 [-0.128, -0.060] | 4.38e-08 |
| date:signed_err (WS − base difference on horizon, model FE, event-clustered) | 918 | mean diff -13.770 | -1.282 [-4.983, +2.420] | 0.497 |
