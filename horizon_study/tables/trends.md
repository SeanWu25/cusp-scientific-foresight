# Within-model horizon trends (slope of outcome on horizon, per 12 months)

Descriptive: within a single model horizon is collinear with calendar date, so these slopes mix horizon and corpus drift. Slope = OLS per month × 12, with 95% event-bootstrap CI (10k) and two-sided bootstrap p; logistic slope (log-odds/month, event-clustered SE) as a check. Holm–Bonferroni across the whole family of 159 tests (datasets × conditions × models × tasks × metrics); `*` = Holm p < 0.05. Models with < 100 items or < 3 months of horizon range are skipped.


## 1. original corpus (Jan 2024–Mar 2026), base — `base`

| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary_merged | accuracy | 6408 | 3–29 | +0.024 [+0.008, +0.039] | 0.0038 | 0.437 | +0.0079 (0.00326) |
| GPT-4o | date | signed_err | 2573 | 3–29 | -12.810 [-14.978, -10.657] | 0.0002 | 0.0318* | — |
| GPT-4o | date | abs_err | 2573 | 3–29 | -11.118 [-13.233, -9.037] | 0.0002 | 0.0318* | — |
| GPT-4o | date | date_score | 2573 | 3–29 | +0.134 [+0.120, +0.148] | 0.0002 | 0.0318* | — |
| GPT-4o | mcq | accuracy | 4126 | 3–29 | -0.041 [-0.066, -0.015] | 0.0028 | 0.325 | -0.0137 (0.00187) |
| LLaMA 3.3 70B | binary_merged | accuracy | 6359 | 1–27 | -0.043 [-0.057, -0.028] | 0.0002 | 0.0318* | -0.0145 (7.73e-09) |
| LLaMA 3.3 70B | date | signed_err | 2731 | 1–27 | -11.250 [-12.504, -9.997] | 0.0002 | 0.0318* | — |
| LLaMA 3.3 70B | date | abs_err | 2731 | 1–27 | -5.262 [-6.428, -4.147] | 0.0002 | 0.0318* | — |
| LLaMA 3.3 70B | date | date_score | 2731 | 1–27 | +0.181 [+0.166, +0.195] | 0.0002 | 0.0318* | — |
| LLaMA 3.3 70B | mcq | accuracy | 4087 | 1–27 | -0.033 [-0.058, -0.007] | 0.0138 | 1 | -0.0113 (0.0114) |
| GPT-OSS 20B | binary_merged | accuracy | 5191 | 1–21 | +0.016 [-0.007, +0.038] | 0.167 | 1 | +0.0053 (0.164) |
| GPT-OSS 20B | date | signed_err | 2126 | 1–21 | -11.999 [-15.075, -8.952] | 0.0002 | 0.0318* | — |
| GPT-OSS 20B | date | abs_err | 2126 | 1–21 | -8.426 [-11.352, -5.558] | 0.0002 | 0.0318* | — |
| GPT-OSS 20B | date | date_score | 2126 | 1–21 | +0.176 [+0.153, +0.200] | 0.0002 | 0.0318* | — |
| GPT-OSS 20B | mcq | accuracy | 3380 | 1–21 | -0.031 [-0.065, +0.004] | 0.0884 | 1 | -0.0102 (0.0889) |
| DeepSeek R1 | binary_merged | accuracy | 4885 | 1–20 | -0.029 [-0.056, -0.003] | 0.0354 | 1 | -0.0097 (0.0327) |
| DeepSeek R1 | date | signed_err | 1702 | 1–20 | -12.769 [-17.378, -9.054] | 0.0002 | 0.0318* | — |
| DeepSeek R1 | date | abs_err | 1702 | 1–20 | -8.635 [-13.145, -5.058] | 0.0002 | 0.0318* | — |
| DeepSeek R1 | date | date_score | 1702 | 1–20 | +0.199 [+0.175, +0.223] | 0.0002 | 0.0318* | — |
| DeepSeek R1 | mcq | accuracy | 2818 | 1–20 | -0.014 [-0.054, +0.026] | 0.472 | 1 | -0.0049 (0.487) |
| Claude S4.5 | binary_merged | accuracy | 3259 | 1–14 | -0.001 [-0.046, +0.044] | 0.972 | 1 | -0.0002 (0.977) |
| Claude S4.5 | date | signed_err | 1293 | 1–14 | -4.680 [-12.626, +4.163] | 0.269 | 1 | — |
| Claude S4.5 | date | abs_err | 1293 | 1–14 | -8.162 [-15.508, -0.074] | 0.0486 | 1 | — |
| Claude S4.5 | date | date_score | 1293 | 1–14 | +0.128 [+0.084, +0.171] | 0.0002 | 0.0318* | — |
| Claude S4.5 | mcq | accuracy | 2129 | 1–14 | -0.027 [-0.090, +0.036] | 0.386 | 1 | -0.0108 (0.392) |
| GPT-5.4 | binary_merged | accuracy | 1546 | 1–7 | +0.110 [-0.041, +0.256] | 0.141 | 1 | +0.0366 (0.149) |
| GPT-5.4 | date | signed_err | 612 | 1–7 | +10.329 [-22.361, +40.931] | 0.508 | 1 | — |
| GPT-5.4 | date | abs_err | 612 | 1–7 | -10.933 [-36.016, +16.313] | 0.403 | 1 | — |
| GPT-5.4 | date | date_score | 612 | 1–7 | -0.056 [-0.227, +0.111] | 0.518 | 1 | — |
| GPT-5.4 | mcq | accuracy | 1014 | 1–7 | -0.174 [-0.344, -0.006] | 0.0442 | 1 | -0.0883 (0.0452) |
| Claude Sonnet 5 | binary_merged | — | 317 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | date | — | 122 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | mcq | — | 190 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | binary_merged | — | 17 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | date | — | 5 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | mcq | — | 7 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |

## 2. extension (Apr–Aug 2026), base — `base`

| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary_merged | accuracy | 845 | 30–34 | -0.021 [-0.287, +0.242] | 0.862 | 1 | -0.0071 (0.877) |
| GPT-4o | date | signed_err | 193 | 30–34 | +13.117 [-17.681, +44.115] | 0.404 | 1 | — |
| GPT-4o | date | abs_err | 193 | 30–34 | +20.429 [-5.848, +47.262] | 0.125 | 1 | — |
| GPT-4o | date | date_score | 193 | 30–34 | -0.497 [-0.911, -0.084] | 0.0152 | 1 | — |
| GPT-4o | mcq | accuracy | 606 | 30–34 | -0.380 [-0.719, -0.042] | 0.0292 | 1 | -0.1281 (0.0328) |
| LLaMA 3.3 70B | binary_merged | accuracy | 845 | 28–32 | -0.039 [-0.261, +0.180] | 0.728 | 1 | -0.0165 (0.729) |
| LLaMA 3.3 70B | date | signed_err | 195 | 28–32 | +2.373 [-17.327, +33.374] | 0.934 | 1 | — |
| LLaMA 3.3 70B | date | abs_err | 195 | 28–32 | +19.536 [+3.830, +47.152] | 0.0048 | 0.547 | — |
| LLaMA 3.3 70B | date | date_score | 195 | 28–32 | -0.321 [-0.464, -0.183] | 0.0002 | 0.0318* | — |
| LLaMA 3.3 70B | mcq | accuracy | 606 | 28–32 | -0.182 [-0.525, +0.165] | 0.306 | 1 | -0.0616 (0.302) |
| GPT-OSS 20B | binary_merged | accuracy | 845 | 22–26 | +0.070 [-0.199, +0.331] | 0.607 | 1 | +0.0239 (0.602) |
| GPT-OSS 20B | date | signed_err | 190 | 22–26 | -40.993 [-82.448, +0.000] | 0.0504 | 1 | — |
| GPT-OSS 20B | date | abs_err | 190 | 22–26 | -23.850 [-60.066, +10.553] | 0.168 | 1 | — |
| GPT-OSS 20B | date | date_score | 190 | 22–26 | +0.021 [-0.337, +0.371] | 0.913 | 1 | — |
| GPT-OSS 20B | mcq | accuracy | 606 | 22–26 | -0.283 [-0.623, +0.068] | 0.108 | 1 | -0.0947 (0.111) |
| Claude S4.5 | binary_merged | accuracy | 712 | 15–19 | -0.057 [-0.357, +0.234] | 0.705 | 1 | -0.0191 (0.709) |
| Claude S4.5 | date | signed_err | 169 | 15–19 | +5.973 [-36.717, +51.273] | 0.812 | 1 | — |
| Claude S4.5 | date | abs_err | 169 | 15–19 | -23.988 [-59.940, +12.338] | 0.188 | 1 | — |
| Claude S4.5 | date | date_score | 169 | 15–19 | +0.114 [-0.246, +0.489] | 0.534 | 1 | — |
| Claude S4.5 | mcq | accuracy | 473 | 15–19 | -0.052 [-0.391, +0.287] | 0.796 | 1 | -0.0233 (0.764) |
| GPT-5.4 | binary_merged | accuracy | 845 | 8–12 | -0.170 [-0.453, +0.107] | 0.232 | 1 | -0.0583 (0.231) |
| GPT-5.4 | date | signed_err | 153 | 8–12 | -18.967 [-58.563, +21.735] | 0.352 | 1 | — |
| GPT-5.4 | date | abs_err | 153 | 8–12 | -3.194 [-26.957, +21.448] | 0.789 | 1 | — |
| GPT-5.4 | date | date_score | 153 | 8–12 | +0.063 [-0.186, +0.311] | 0.631 | 1 | — |
| GPT-5.4 | mcq | accuracy | 606 | 8–12 | +0.061 [-0.178, +0.306] | 0.603 | 1 | +0.0415 (0.626) |
| Claude Sonnet 5 | binary_merged | accuracy | 821 | 3–7 | -0.193 [-0.444, +0.058] | 0.136 | 1 | -0.0711 (0.134) |
| Claude Sonnet 5 | date | signed_err | 193 | 3–7 | -36.108 [-92.121, +9.811] | 0.146 | 1 | — |
| Claude Sonnet 5 | date | abs_err | 193 | 3–7 | +22.884 [-22.187, +77.145] | 0.384 | 1 | — |
| Claude Sonnet 5 | date | date_score | 193 | 3–7 | -0.119 [-0.427, +0.189] | 0.454 | 1 | — |
| Claude Sonnet 5 | mcq | accuracy | 569 | 3–7 | +0.127 [-0.071, +0.319] | 0.198 | 1 | +0.1310 (0.203) |
| GPT-5.6 Sol | binary_merged | accuracy | 845 | 2–6 | -0.158 [-0.431, +0.120] | 0.253 | 1 | -0.0530 (0.255) |
| GPT-5.6 Sol | date | signed_err | 194 | 2–6 | -29.181 [-63.007, +2.534] | 0.0708 | 1 | — |
| GPT-5.6 Sol | date | abs_err | 194 | 2–6 | +2.442 [-18.728, +25.703] | 0.879 | 1 | — |
| GPT-5.6 Sol | date | date_score | 194 | 2–6 | -0.064 [-0.269, +0.134] | 0.53 | 1 | — |
| GPT-5.6 Sol | mcq | accuracy | 602 | 2–6 | +0.016 [-0.218, +0.246] | 0.888 | 1 | +0.0118 (0.891) |
| DeepSeek-V4-Pro | binary_merged | accuracy | 661 | 1–4 | -0.055 [-0.401, +0.284] | 0.753 | 1 | -0.0205 (0.756) |
| DeepSeek-V4-Pro | date | signed_err | 153 | 1–4 | -35.677 [-119.921, +53.841] | 0.416 | 1 | — |
| DeepSeek-V4-Pro | date | abs_err | 153 | 1–4 | +18.280 [-56.747, +97.601] | 0.631 | 1 | — |
| DeepSeek-V4-Pro | date | date_score | 153 | 1–4 | +0.183 [-0.460, +0.816] | 0.585 | 1 | — |
| DeepSeek-V4-Pro | mcq | accuracy | 478 | 1–4 | +0.071 [-0.413, +0.556] | 0.767 | 1 | +0.0266 (0.773) |

## 4. merged original + extension, base — `base`

| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary_merged | accuracy | 7253 | 3–34 | +0.028 [+0.014, +0.041] | 0.0002 | 0.0318* | +0.0093 (2.33e-05) |
| GPT-4o | date | signed_err | 2766 | 3–34 | -14.848 [-16.707, -13.064] | 0.0002 | 0.0318* | — |
| GPT-4o | date | abs_err | 2766 | 3–34 | -12.347 [-14.155, -10.627] | 0.0002 | 0.0318* | — |
| GPT-4o | date | date_score | 2766 | 3–34 | +0.160 [+0.146, +0.174] | 0.0002 | 0.0318* | — |
| GPT-4o | mcq | accuracy | 4732 | 3–34 | -0.046 [-0.066, -0.026] | 0.0002 | 0.0318* | -0.0155 (7.63e-06) |
| LLaMA 3.3 70B | binary_merged | accuracy | 7204 | 1–32 | -0.078 [-0.090, -0.066] | 0.0002 | 0.0318* | -0.0267 (9.74e-37) |
| LLaMA 3.3 70B | date | signed_err | 2926 | 1–32 | -11.235 [-12.415, -10.037] | 0.0002 | 0.0318* | — |
| LLaMA 3.3 70B | date | abs_err | 2926 | 1–32 | -3.042 [-4.173, -1.944] | 0.0002 | 0.0318* | — |
| LLaMA 3.3 70B | date | date_score | 2926 | 1–32 | +0.096 [+0.082, +0.109] | 0.0002 | 0.0318* | — |
| LLaMA 3.3 70B | mcq | accuracy | 4693 | 1–32 | -0.019 [-0.039, +0.002] | 0.0726 | 1 | -0.0063 (0.0711) |
| GPT-OSS 20B | binary_merged | accuracy | 6036 | 1–26 | +0.025 [+0.007, +0.042] | 0.0072 | 0.799 | +0.0083 (0.00598) |
| GPT-OSS 20B | date | signed_err | 2316 | 1–26 | -12.768 [-15.288, -10.251] | 0.0002 | 0.0318* | — |
| GPT-OSS 20B | date | abs_err | 2316 | 1–26 | -7.924 [-10.298, -5.612] | 0.0002 | 0.0318* | — |
| GPT-OSS 20B | date | date_score | 2316 | 1–26 | +0.124 [+0.105, +0.144] | 0.0002 | 0.0318* | — |
| GPT-OSS 20B | mcq | accuracy | 3986 | 1–26 | +0.001 [-0.024, +0.027] | 0.91 | 1 | +0.0004 (0.925) |
| DeepSeek R1 | binary_merged | accuracy | 4885 | 1–20 | -0.029 [-0.056, -0.003] | 0.0354 | 1 | -0.0097 (0.0327) |
| DeepSeek R1 | date | signed_err | 1702 | 1–20 | -12.769 [-17.378, -9.054] | 0.0002 | 0.0318* | — |
| DeepSeek R1 | date | abs_err | 1702 | 1–20 | -8.635 [-13.145, -5.058] | 0.0002 | 0.0318* | — |
| DeepSeek R1 | date | date_score | 1702 | 1–20 | +0.199 [+0.175, +0.223] | 0.0002 | 0.0318* | — |
| DeepSeek R1 | mcq | accuracy | 2818 | 1–20 | -0.014 [-0.054, +0.026] | 0.472 | 1 | -0.0049 (0.487) |
| Claude S4.5 | binary_merged | accuracy | 3971 | 1–19 | +0.022 [-0.010, +0.054] | 0.18 | 1 | +0.0072 (0.182) |
| Claude S4.5 | date | signed_err | 1462 | 1–19 | -6.735 [-12.538, -0.922] | 0.0264 | 1 | — |
| Claude S4.5 | date | abs_err | 1462 | 1–19 | -7.968 [-13.054, -2.965] | 0.0012 | 0.145 | — |
| Claude S4.5 | date | date_score | 1462 | 1–19 | +0.094 [+0.061, +0.127] | 0.0002 | 0.0318* | — |
| Claude S4.5 | mcq | accuracy | 2602 | 1–19 | +0.021 [-0.019, +0.059] | 0.313 | 1 | +0.0085 (0.309) |
| GPT-5.4 | binary_merged | accuracy | 2391 | 1–12 | -0.083 [-0.148, -0.020] | 0.008 | 0.872 | -0.0281 (0.0116) |
| GPT-5.4 | date | signed_err | 765 | 1–12 | -11.220 [-22.866, +0.930] | 0.0712 | 1 | — |
| GPT-5.4 | date | abs_err | 765 | 1–12 | -14.467 [-23.520, -5.791] | 0.0016 | 0.19 | — |
| GPT-5.4 | date | date_score | 765 | 1–12 | -0.101 [-0.172, -0.030] | 0.0062 | 0.694 | — |
| GPT-5.4 | mcq | accuracy | 1620 | 1–12 | +0.074 [+0.012, +0.136] | 0.0158 | 1 | +0.0417 (0.0208) |
| Claude Sonnet 5 | binary_merged | accuracy | 1138 | 1–7 | +0.118 [-0.024, +0.255] | 0.0982 | 1 | +0.0422 (0.0964) |
| Claude Sonnet 5 | date | signed_err | 315 | 1–7 | -28.558 [-52.708, -7.890] | 0.0084 | 0.907 | — |
| Claude Sonnet 5 | date | abs_err | 315 | 1–7 | +25.285 [+5.105, +49.281] | 0.014 | 1 | — |
| Claude Sonnet 5 | date | date_score | 315 | 1–7 | -0.325 [-0.489, -0.160] | 0.0006 | 0.0738 | — |
| Claude Sonnet 5 | mcq | accuracy | 759 | 1–7 | +0.099 [-0.019, +0.218] | 0.106 | 1 | +0.0948 (0.103) |
| GPT-5.6 Sol | binary_merged | accuracy | 862 | 1–6 | -0.145 [-0.399, +0.112] | 0.27 | 1 | -0.0486 (0.265) |
| GPT-5.6 Sol | date | signed_err | 199 | 1–6 | -20.814 [-52.997, +7.494] | 0.163 | 1 | — |
| GPT-5.6 Sol | date | abs_err | 199 | 1–6 | +6.617 [-12.555, +27.927] | 0.54 | 1 | — |
| GPT-5.6 Sol | date | date_score | 199 | 1–6 | -0.133 [-0.322, +0.054] | 0.164 | 1 | — |
| GPT-5.6 Sol | mcq | accuracy | 609 | 1–6 | +0.018 [-0.207, +0.242] | 0.875 | 1 | +0.0129 (0.878) |
| DeepSeek-V4-Pro | binary_merged | accuracy | 661 | 1–4 | -0.055 [-0.401, +0.284] | 0.753 | 1 | -0.0205 (0.756) |
| DeepSeek-V4-Pro | date | signed_err | 153 | 1–4 | -35.677 [-119.921, +53.841] | 0.416 | 1 | — |
| DeepSeek-V4-Pro | date | abs_err | 153 | 1–4 | +18.280 [-56.747, +97.601] | 0.631 | 1 | — |
| DeepSeek-V4-Pro | date | date_score | 153 | 1–4 | +0.183 [-0.460, +0.816] | 0.585 | 1 | — |
| DeepSeek-V4-Pro | mcq | accuracy | 478 | 1–4 | +0.071 [-0.413, +0.556] | 0.767 | 1 | +0.0266 (0.773) |

## 3. WS+Cutoff on the pinned 500 subset — `base`

| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary_merged | accuracy | 690 | 3–29 | +0.072 [+0.025, +0.118] | 0.0018 | 0.212 | +0.0241 (0.00257) |
| GPT-4o | date | signed_err | 275 | 3–28 | -9.729 [-16.076, -2.906] | 0.006 | 0.678 | — |
| GPT-4o | date | abs_err | 275 | 3–28 | -8.675 [-14.923, -2.047] | 0.0124 | 1 | — |
| GPT-4o | date | date_score | 275 | 3–28 | +0.108 [+0.068, +0.149] | 0.0002 | 0.0318* | — |
| GPT-4o | mcq | accuracy | 435 | 3–28 | -0.057 [-0.132, +0.020] | 0.149 | 1 | -0.0193 (0.15) |
| LLaMA 3.3 70B | binary_merged | accuracy | 687 | 1–27 | -0.069 [-0.115, -0.023] | 0.0022 | 0.257 | -0.0231 (0.00358) |
| LLaMA 3.3 70B | date | signed_err | 292 | 1–26 | -7.752 [-10.906, -3.720] | 0.0008 | 0.0976 | — |
| LLaMA 3.3 70B | date | abs_err | 292 | 1–26 | -3.521 [-6.413, +0.070] | 0.0542 | 1 | — |
| LLaMA 3.3 70B | date | date_score | 292 | 1–26 | +0.183 [+0.137, +0.231] | 0.0002 | 0.0318* | — |
| LLaMA 3.3 70B | mcq | accuracy | 433 | 1–26 | -0.085 [-0.164, -0.006] | 0.0374 | 1 | -0.0284 (0.0359) |
| DeepSeek R1 | binary_merged | accuracy | 509 | 1–20 | -0.052 [-0.137, +0.034] | 0.231 | 1 | -0.0174 (0.226) |
| DeepSeek R1 | date | signed_err | 174 | 1–19 | -9.416 [-17.049, -2.432] | 0.0078 | 0.858 | — |
| DeepSeek R1 | date | abs_err | 174 | 1–19 | -5.822 [-13.050, +0.691] | 0.0798 | 1 | — |
| DeepSeek R1 | date | date_score | 174 | 1–19 | +0.155 [+0.076, +0.231] | 0.0002 | 0.0318* | — |
| DeepSeek R1 | mcq | accuracy | 294 | 1–19 | +0.069 [-0.058, +0.196] | 0.296 | 1 | +0.0237 (0.289) |
| Claude S4.5 | binary_merged | accuracy | 360 | 1–14 | +0.126 [-0.012, +0.266] | 0.0764 | 1 | +0.0430 (0.0808) |
| Claude S4.5 | date | signed_err | 139 | 1–13 | -4.542 [-19.505, +9.404] | 0.527 | 1 | — |
| Claude S4.5 | date | abs_err | 139 | 1–13 | -11.257 [-24.607, -0.608] | 0.0362 | 1 | — |
| Claude S4.5 | date | date_score | 139 | 1–13 | +0.129 [+0.016, +0.245] | 0.0252 | 1 | — |
| Claude S4.5 | mcq | accuracy | 220 | 1–13 | -0.039 [-0.238, +0.165] | 0.703 | 1 | -0.0159 (0.701) |
| GPT-5.4 | binary_merged | accuracy | 159 | 1–7 | -0.073 [-0.534, +0.379] | 0.757 | 1 | -0.0244 (0.752) |
| GPT-5.4 | date | — | 59 | 1–6 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.4 | mcq | accuracy | 105 | 1–6 | -0.459 [-0.917, -0.015] | 0.0434 | 1 | -0.2725 (0.0522) |
| Claude Sonnet 5 | binary_merged | — | 37 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | date | — | 14 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | mcq | — | 23 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | binary_merged | — | 1 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |

## 3. WS+Cutoff on the pinned 500 subset — `ws_cutoff`

| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary_merged | accuracy | 690 | 3–29 | +0.005 [-0.047, +0.057] | 0.847 | 1 | +0.0017 (0.85) |
| GPT-4o | date | signed_err | 295 | 3–28 | -11.734 [-18.987, -4.651] | 0.0012 | 0.145 | — |
| GPT-4o | date | abs_err | 295 | 3–28 | -3.936 [-10.560, +2.572] | 0.237 | 1 | — |
| GPT-4o | date | date_score | 295 | 3–28 | +0.141 [+0.089, +0.193] | 0.0002 | 0.0318* | — |
| GPT-4o | mcq | accuracy | 435 | 3–28 | -0.058 [-0.133, +0.020] | 0.148 | 1 | -0.0200 (0.139) |
| LLaMA 3.3 70B | binary_merged | accuracy | 690 | 1–27 | -0.053 [-0.100, -0.005] | 0.0286 | 1 | -0.0179 (0.0271) |
| LLaMA 3.3 70B | date | signed_err | 296 | 1–26 | -12.924 [-19.357, -7.380] | 0.0002 | 0.0318* | — |
| LLaMA 3.3 70B | date | abs_err | 296 | 1–26 | +0.596 [-5.592, +5.867] | 0.807 | 1 | — |
| LLaMA 3.3 70B | date | date_score | 296 | 1–26 | +0.013 [-0.033, +0.059] | 0.584 | 1 | — |
| LLaMA 3.3 70B | mcq | accuracy | 435 | 1–26 | -0.056 [-0.133, +0.024] | 0.165 | 1 | -0.0187 (0.163) |
| DeepSeek R1 | binary_merged | accuracy | 511 | 1–20 | +0.049 [-0.037, +0.139] | 0.275 | 1 | +0.0163 (0.287) |
| DeepSeek R1 | date | signed_err | 193 | 1–19 | -8.996 [-16.189, -1.726] | 0.0184 | 1 | — |
| DeepSeek R1 | date | abs_err | 193 | 1–19 | +1.743 [-4.309, +7.685] | 0.566 | 1 | — |
| DeepSeek R1 | date | date_score | 193 | 1–19 | +0.012 [-0.068, +0.091] | 0.777 | 1 | — |
| DeepSeek R1 | mcq | accuracy | 327 | 1–19 | +0.002 [-0.115, +0.119] | 0.973 | 1 | +0.0007 (0.975) |
| Claude S4.5 | binary_merged | accuracy | 353 | 1–14 | -0.067 [-0.211, +0.076] | 0.372 | 1 | -0.0229 (0.361) |
| Claude S4.5 | date | signed_err | 110 | 1–13 | -9.851 [-31.019, +11.159] | 0.355 | 1 | — |
| Claude S4.5 | date | abs_err | 110 | 1–13 | +15.650 [+0.921, +32.057] | 0.0356 | 1 | — |
| Claude S4.5 | date | date_score | 110 | 1–13 | -0.025 [-0.190, +0.143] | 0.762 | 1 | — |
| Claude S4.5 | mcq | accuracy | 216 | 1–13 | -0.018 [-0.217, +0.178] | 0.86 | 1 | -0.0072 (0.859) |
| GPT-5.4 | binary_merged | accuracy | 159 | 1–7 | +0.273 [-0.168, +0.733] | 0.22 | 1 | +0.0915 (0.233) |
| GPT-5.4 | date | — | 59 | 1–6 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.4 | mcq | accuracy | 105 | 1–6 | -0.457 [-0.992, +0.079] | 0.0904 | 1 | -0.2240 (0.108) |
| Claude Sonnet 5 | binary_merged | — | 38 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | date | — | 15 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | mcq | — | 23 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | binary_merged | — | 1 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
