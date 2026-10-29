# Within-model horizon trends (slope of outcome on horizon, per 12 months)

Descriptive: within a single model horizon is collinear with calendar date, so these slopes mix horizon and corpus drift. Slope = OLS per month × 12, with 95% event-bootstrap CI (10k) and two-sided bootstrap p; logistic slope (log-odds/month, event-clustered SE) as a check. Holm–Bonferroni across the whole family of 355 tests (datasets × conditions × models × tasks × metrics); `*` = Holm p < 0.05. Models with < 100 items or < 3 months of horizon range are skipped.


## 1. original corpus (Jan 2024–Mar 2026), base — `base`

| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary | accuracy | 2754 | 3–29 | +0.145 [+0.122, +0.169] | 0.0002 | 0.071 | +0.0820 (9.29e-33) |
| GPT-4o | binary_perturbed | accuracy | 3654 | 3–29 | -0.127 [-0.148, -0.105] | 0.0002 | 0.071 | -0.0612 (9.25e-28) |
| GPT-4o | date | signed_err | 2573 | 3–29 | -12.810 [-14.978, -10.657] | 0.0002 | 0.071 | — |
| GPT-4o | date | abs_err | 2573 | 3–29 | -11.118 [-13.233, -9.037] | 0.0002 | 0.071 | — |
| GPT-4o | date | date_score | 2573 | 3–29 | +0.134 [+0.120, +0.148] | 0.0002 | 0.071 | — |
| GPT-4o | frq | frq_score | 4128 | 3–29 | +0.037 [-0.011, +0.084] | 0.131 | 1 | — |
| GPT-4o | frq | frq_alignment | 4128 | 3–29 | -0.045 [-0.120, +0.030] | 0.24 | 1 | — |
| GPT-4o | frq | frq_specificity | 4128 | 3–29 | -0.029 [-0.079, +0.021] | 0.269 | 1 | — |
| GPT-4o | frq | frq_novelty | 4128 | 3–29 | +0.167 [+0.119, +0.215] | 0.0002 | 0.071 | — |
| GPT-4o | frq | frq_feasibility | 4128 | 3–29 | +0.054 [-0.035, +0.141] | 0.232 | 1 | — |
| GPT-4o | mcq | accuracy | 4126 | 3–29 | -0.041 [-0.066, -0.015] | 0.0028 | 0.801 | -0.0137 (0.00187) |
| LLaMA 3.3 70B | binary | accuracy | 2734 | 1–27 | +0.046 [+0.030, +0.062] | 0.0002 | 0.071 | +0.0634 (6.4e-08) |
| LLaMA 3.3 70B | binary_perturbed | accuracy | 3625 | 1–27 | -0.035 [-0.051, -0.019] | 0.0002 | 0.071 | -0.0353 (2.63e-05) |
| LLaMA 3.3 70B | date | signed_err | 2731 | 1–27 | -11.250 [-12.504, -9.997] | 0.0002 | 0.071 | — |
| LLaMA 3.3 70B | date | abs_err | 2731 | 1–27 | -5.262 [-6.428, -4.147] | 0.0002 | 0.071 | — |
| LLaMA 3.3 70B | date | date_score | 2731 | 1–27 | +0.181 [+0.166, +0.195] | 0.0002 | 0.071 | — |
| LLaMA 3.3 70B | frq | frq_score | 4093 | 1–27 | -0.033 [-0.071, +0.005] | 0.0982 | 1 | — |
| LLaMA 3.3 70B | frq | frq_alignment | 4093 | 1–27 | -0.066 [-0.136, +0.002] | 0.057 | 1 | — |
| LLaMA 3.3 70B | frq | frq_specificity | 4093 | 1–27 | -0.066 [-0.105, -0.026] | 0.001 | 0.293 | — |
| LLaMA 3.3 70B | frq | frq_novelty | 4093 | 1–27 | +0.077 [+0.037, +0.116] | 0.0002 | 0.071 | — |
| LLaMA 3.3 70B | frq | frq_feasibility | 4093 | 1–27 | -0.077 [-0.148, -0.004] | 0.0416 | 1 | — |
| LLaMA 3.3 70B | mcq | accuracy | 4087 | 1–27 | -0.033 [-0.058, -0.007] | 0.0138 | 1 | -0.0113 (0.0114) |
| GPT-OSS 20B | binary | accuracy | 2153 | 1–21 | +0.053 [+0.018, +0.087] | 0.0026 | 0.746 | +0.0292 (0.00244) |
| GPT-OSS 20B | binary_perturbed | accuracy | 3038 | 1–21 | -0.042 [-0.073, -0.011] | 0.009 | 1 | -0.0195 (0.00848) |
| GPT-OSS 20B | date | signed_err | 2126 | 1–21 | -11.999 [-15.075, -8.952] | 0.0002 | 0.071 | — |
| GPT-OSS 20B | date | abs_err | 2126 | 1–21 | -8.426 [-11.352, -5.558] | 0.0002 | 0.071 | — |
| GPT-OSS 20B | date | date_score | 2126 | 1–21 | +0.176 [+0.153, +0.200] | 0.0002 | 0.071 | — |
| GPT-OSS 20B | frq | frq_score | 3390 | 1–21 | +0.065 [+0.000, +0.128] | 0.049 | 1 | — |
| GPT-OSS 20B | frq | frq_alignment | 3390 | 1–21 | +0.036 [-0.063, +0.132] | 0.469 | 1 | — |
| GPT-OSS 20B | frq | frq_specificity | 3390 | 1–21 | +0.013 [-0.072, +0.100] | 0.767 | 1 | — |
| GPT-OSS 20B | frq | frq_novelty | 3390 | 1–21 | +0.085 [+0.001, +0.170] | 0.047 | 1 | — |
| GPT-OSS 20B | frq | frq_feasibility | 3390 | 1–21 | +0.128 [+0.023, +0.230] | 0.0182 | 1 | — |
| GPT-OSS 20B | mcq | accuracy | 3380 | 1–21 | -0.031 [-0.065, +0.004] | 0.0884 | 1 | -0.0102 (0.0889) |
| DeepSeek R1 | binary | accuracy | 2014 | 1–20 | +0.130 [+0.085, +0.177] | 0.0002 | 0.071 | +0.0439 (8.11e-08) |
| DeepSeek R1 | binary_perturbed | accuracy | 2871 | 1–20 | -0.141 [-0.180, -0.102] | 0.0002 | 0.071 | -0.0476 (6.92e-12) |
| DeepSeek R1 | date | signed_err | 1702 | 1–20 | -12.769 [-17.378, -9.054] | 0.0002 | 0.071 | — |
| DeepSeek R1 | date | abs_err | 1702 | 1–20 | -8.635 [-13.145, -5.058] | 0.0002 | 0.071 | — |
| DeepSeek R1 | date | date_score | 1702 | 1–20 | +0.199 [+0.175, +0.223] | 0.0002 | 0.071 | — |
| DeepSeek R1 | frq | frq_score | 3231 | 1–20 | +0.060 [-0.003, +0.124] | 0.065 | 1 | — |
| DeepSeek R1 | frq | frq_alignment | 3231 | 1–20 | +0.088 [-0.023, +0.200] | 0.115 | 1 | — |
| DeepSeek R1 | frq | frq_specificity | 3231 | 1–20 | -0.060 [-0.145, +0.027] | 0.171 | 1 | — |
| DeepSeek R1 | frq | frq_novelty | 3231 | 1–20 | +0.132 [+0.046, +0.217] | 0.003 | 0.855 | — |
| DeepSeek R1 | frq | frq_feasibility | 3231 | 1–20 | +0.079 [-0.021, +0.180] | 0.121 | 1 | — |
| DeepSeek R1 | mcq | accuracy | 2818 | 1–20 | -0.014 [-0.054, +0.026] | 0.472 | 1 | -0.0049 (0.487) |
| Claude S4.5 | binary | accuracy | 1327 | 1–14 | +0.073 [+0.003, +0.143] | 0.0374 | 1 | +0.0371 (0.0396) |
| Claude S4.5 | binary_perturbed | accuracy | 1932 | 1–14 | -0.064 [-0.125, -0.002] | 0.0432 | 1 | -0.0275 (0.0424) |
| Claude S4.5 | date | signed_err | 1293 | 1–14 | -4.680 [-12.626, +4.163] | 0.269 | 1 | — |
| Claude S4.5 | date | abs_err | 1293 | 1–14 | -8.162 [-15.508, -0.074] | 0.0486 | 1 | — |
| Claude S4.5 | date | date_score | 1293 | 1–14 | +0.128 [+0.084, +0.171] | 0.0002 | 0.071 | — |
| Claude S4.5 | frq | frq_score | 2181 | 1–14 | +0.144 [+0.025, +0.267] | 0.0202 | 1 | — |
| Claude S4.5 | frq | frq_alignment | 2181 | 1–14 | +0.175 [-0.012, +0.369] | 0.066 | 1 | — |
| Claude S4.5 | frq | frq_specificity | 2181 | 1–14 | +0.056 [-0.098, +0.208] | 0.488 | 1 | — |
| Claude S4.5 | frq | frq_novelty | 2181 | 1–14 | +0.149 [-0.015, +0.315] | 0.0742 | 1 | — |
| Claude S4.5 | frq | frq_feasibility | 2181 | 1–14 | +0.197 [+0.012, +0.384] | 0.0368 | 1 | — |
| Claude S4.5 | mcq | accuracy | 2129 | 1–14 | -0.027 [-0.090, +0.036] | 0.386 | 1 | -0.0108 (0.392) |
| GPT-5.4 | binary | accuracy | 612 | 1–7 | +0.090 [-0.176, +0.356] | 0.515 | 1 | +0.0315 (0.51) |
| GPT-5.4 | binary_perturbed | accuracy | 934 | 1–7 | +0.111 [-0.100, +0.324] | 0.293 | 1 | +0.0385 (0.302) |
| GPT-5.4 | date | signed_err | 612 | 1–7 | +10.329 [-22.361, +40.931] | 0.508 | 1 | — |
| GPT-5.4 | date | abs_err | 612 | 1–7 | -10.933 [-36.016, +16.313] | 0.403 | 1 | — |
| GPT-5.4 | date | date_score | 612 | 1–7 | -0.056 [-0.227, +0.111] | 0.518 | 1 | — |
| GPT-5.4 | frq | frq_score | 1019 | 1–7 | +0.242 [-0.098, +0.583] | 0.166 | 1 | — |
| GPT-5.4 | frq | frq_alignment | 1019 | 1–7 | +0.399 [-0.370, +1.170] | 0.308 | 1 | — |
| GPT-5.4 | frq | frq_specificity | 1019 | 1–7 | +0.096 [-0.309, +0.510] | 0.647 | 1 | — |
| GPT-5.4 | frq | frq_novelty | 1019 | 1–7 | +0.033 [-0.445, +0.513] | 0.9 | 1 | — |
| GPT-5.4 | frq | frq_feasibility | 1019 | 1–7 | +0.439 [-0.088, +0.942] | 0.096 | 1 | — |
| GPT-5.4 | mcq | accuracy | 1014 | 1–7 | -0.174 [-0.344, -0.006] | 0.0442 | 1 | -0.0883 (0.0452) |
| Claude Sonnet 5 | binary | — | 123 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | binary_perturbed | — | 194 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | date | — | 122 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | frq | — | 204 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | mcq | — | 190 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | binary | — | 5 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | binary_perturbed | — | 12 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | date | — | 5 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | frq | — | 10 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | mcq | — | 7 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | binary | — | 122 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | binary_perturbed | — | 194 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | date | — | 121 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | frq | — | 205 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | mcq | — | 190 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |

## 2. extension (Apr–Aug 2026), base — `base`

| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary | accuracy | 196 | 30–34 | +0.004 [-0.487, +0.488] | 0.98 | 1 | +0.0021 (0.987) |
| GPT-4o | binary_perturbed | accuracy | 649 | 30–34 | -0.049 [-0.366, +0.257] | 0.747 | 1 | -0.0185 (0.759) |
| GPT-4o | date | signed_err | 193 | 30–34 | +13.117 [-17.681, +44.115] | 0.404 | 1 | — |
| GPT-4o | date | abs_err | 193 | 30–34 | +20.429 [-5.848, +47.262] | 0.125 | 1 | — |
| GPT-4o | date | date_score | 193 | 30–34 | -0.497 [-0.911, -0.084] | 0.0152 | 1 | — |
| GPT-4o | frq | frq_score | 630 | 30–34 | -0.192 [-0.703, +0.317] | 0.45 | 1 | — |
| GPT-4o | frq | frq_alignment | 630 | 30–34 | -0.102 [-0.976, +0.747] | 0.815 | 1 | — |
| GPT-4o | frq | frq_specificity | 630 | 30–34 | -0.282 [-0.885, +0.319] | 0.353 | 1 | — |
| GPT-4o | frq | frq_novelty | 630 | 30–34 | -0.487 [-1.049, +0.073] | 0.0906 | 1 | — |
| GPT-4o | frq | frq_feasibility | 630 | 30–34 | +0.104 [-0.834, +1.044] | 0.846 | 1 | — |
| GPT-4o | mcq | accuracy | 606 | 30–34 | -0.380 [-0.719, -0.042] | 0.0292 | 1 | -0.1281 (0.0328) |
| LLaMA 3.3 70B | binary | accuracy | 196 | 28–32 | +0.018 [-0.116, +0.177] | 0.951 | 1 | +0.1010 (0.805) |
| LLaMA 3.3 70B | binary_perturbed | accuracy | 649 | 28–32 | -0.015 [-0.181, +0.153] | 0.87 | 1 | -0.0242 (0.861) |
| LLaMA 3.3 70B | date | signed_err | 195 | 28–32 | +2.373 [-17.327, +33.374] | 0.934 | 1 | — |
| LLaMA 3.3 70B | date | abs_err | 195 | 28–32 | +19.536 [+3.830, +47.152] | 0.0048 | 1 | — |
| LLaMA 3.3 70B | date | date_score | 195 | 28–32 | -0.321 [-0.464, -0.183] | 0.0002 | 0.071 | — |
| LLaMA 3.3 70B | frq | frq_score | 630 | 28–32 | -0.331 [-0.833, +0.184] | 0.194 | 1 | — |
| LLaMA 3.3 70B | frq | frq_alignment | 630 | 28–32 | -0.379 [-1.207, +0.450] | 0.36 | 1 | — |
| LLaMA 3.3 70B | frq | frq_specificity | 630 | 28–32 | -0.347 [-0.884, +0.191] | 0.201 | 1 | — |
| LLaMA 3.3 70B | frq | frq_novelty | 630 | 28–32 | -0.059 [-0.571, +0.463] | 0.822 | 1 | — |
| LLaMA 3.3 70B | frq | frq_feasibility | 630 | 28–32 | -0.541 [-1.520, +0.438] | 0.271 | 1 | — |
| LLaMA 3.3 70B | mcq | accuracy | 606 | 28–32 | -0.182 [-0.525, +0.165] | 0.306 | 1 | -0.0616 (0.302) |
| GPT-OSS 20B | binary | accuracy | 196 | 22–26 | +0.153 [-0.374, +0.691] | 0.576 | 1 | +0.0743 (0.57) |
| GPT-OSS 20B | binary_perturbed | accuracy | 649 | 22–26 | +0.027 [-0.279, +0.327] | 0.861 | 1 | +0.0101 (0.866) |
| GPT-OSS 20B | date | signed_err | 190 | 22–26 | -40.993 [-82.448, +0.000] | 0.0504 | 1 | — |
| GPT-OSS 20B | date | abs_err | 190 | 22–26 | -23.850 [-60.066, +10.553] | 0.168 | 1 | — |
| GPT-OSS 20B | date | date_score | 190 | 22–26 | +0.021 [-0.337, +0.371] | 0.913 | 1 | — |
| GPT-OSS 20B | frq | frq_score | 628 | 22–26 | -0.398 [-0.984, +0.176] | 0.181 | 1 | — |
| GPT-OSS 20B | frq | frq_alignment | 628 | 22–26 | +0.078 [-0.840, +1.016] | 0.863 | 1 | — |
| GPT-OSS 20B | frq | frq_specificity | 628 | 22–26 | -0.654 [-1.392, +0.094] | 0.092 | 1 | — |
| GPT-OSS 20B | frq | frq_novelty | 628 | 22–26 | -0.999 [-1.877, -0.124] | 0.0244 | 1 | — |
| GPT-OSS 20B | frq | frq_feasibility | 628 | 22–26 | -0.017 [-0.920, +0.885] | 0.962 | 1 | — |
| GPT-OSS 20B | mcq | accuracy | 606 | 22–26 | -0.283 [-0.623, +0.068] | 0.108 | 1 | -0.0947 (0.111) |
| Claude S4.5 | binary | accuracy | 174 | 15–19 | +0.110 [-0.489, +0.714] | 0.734 | 1 | +0.0423 (0.721) |
| Claude S4.5 | binary_perturbed | accuracy | 538 | 15–19 | -0.109 [-0.460, +0.243] | 0.543 | 1 | -0.0393 (0.544) |
| Claude S4.5 | date | signed_err | 169 | 15–19 | +5.973 [-36.717, +51.273] | 0.812 | 1 | — |
| Claude S4.5 | date | abs_err | 169 | 15–19 | -23.988 [-59.940, +12.338] | 0.188 | 1 | — |
| Claude S4.5 | date | date_score | 169 | 15–19 | +0.114 [-0.246, +0.489] | 0.534 | 1 | — |
| Claude S4.5 | frq | frq_score | 558 | 15–19 | -0.278 [-0.804, +0.242] | 0.298 | 1 | — |
| Claude S4.5 | frq | frq_alignment | 558 | 15–19 | -0.617 [-1.547, +0.301] | 0.18 | 1 | — |
| Claude S4.5 | frq | frq_specificity | 558 | 15–19 | -0.197 [-0.948, +0.534] | 0.599 | 1 | — |
| Claude S4.5 | frq | frq_novelty | 558 | 15–19 | -0.203 [-1.072, +0.666] | 0.646 | 1 | — |
| Claude S4.5 | frq | frq_feasibility | 558 | 15–19 | -0.094 [-0.958, +0.766] | 0.826 | 1 | — |
| Claude S4.5 | mcq | accuracy | 473 | 15–19 | -0.052 [-0.391, +0.287] | 0.796 | 1 | -0.0233 (0.764) |
| GPT-5.4 | binary | accuracy | 196 | 8–12 | -0.027 [-0.596, +0.549] | 0.943 | 1 | -0.0101 (0.929) |
| GPT-5.4 | binary_perturbed | accuracy | 649 | 8–12 | -0.198 [-0.517, +0.122] | 0.224 | 1 | -0.0732 (0.23) |
| GPT-5.4 | date | signed_err | 153 | 8–12 | -18.967 [-58.563, +21.735] | 0.352 | 1 | — |
| GPT-5.4 | date | abs_err | 153 | 8–12 | -3.194 [-26.957, +21.448] | 0.789 | 1 | — |
| GPT-5.4 | date | date_score | 153 | 8–12 | +0.063 [-0.186, +0.311] | 0.631 | 1 | — |
| GPT-5.4 | frq | frq_score | 628 | 8–12 | -0.298 [-0.806, +0.213] | 0.261 | 1 | — |
| GPT-5.4 | frq | frq_alignment | 628 | 8–12 | -0.127 [-1.291, +1.087] | 0.83 | 1 | — |
| GPT-5.4 | frq | frq_specificity | 628 | 8–12 | -0.327 [-0.930, +0.277] | 0.294 | 1 | — |
| GPT-5.4 | frq | frq_novelty | 628 | 8–12 | -0.020 [-0.762, +0.748] | 0.959 | 1 | — |
| GPT-5.4 | frq | frq_feasibility | 628 | 8–12 | -0.718 [-1.560, +0.116] | 0.097 | 1 | — |
| GPT-5.4 | mcq | accuracy | 606 | 8–12 | +0.061 [-0.178, +0.306] | 0.603 | 1 | +0.0415 (0.626) |
| Claude Sonnet 5 | binary | accuracy | 193 | 3–7 | -0.150 [-0.737, +0.425] | 0.604 | 1 | -0.0603 (0.608) |
| Claude Sonnet 5 | binary_perturbed | accuracy | 628 | 3–7 | -0.224 [-0.499, +0.055] | 0.117 | 1 | -0.1040 (0.114) |
| Claude Sonnet 5 | date | signed_err | 193 | 3–7 | -36.108 [-92.121, +9.811] | 0.146 | 1 | — |
| Claude Sonnet 5 | date | abs_err | 193 | 3–7 | +22.884 [-22.187, +77.145] | 0.384 | 1 | — |
| Claude Sonnet 5 | date | date_score | 193 | 3–7 | -0.119 [-0.427, +0.189] | 0.454 | 1 | — |
| Claude Sonnet 5 | frq | frq_score | 618 | 3–7 | +0.104 [-0.464, +0.662] | 0.727 | 1 | — |
| Claude Sonnet 5 | frq | frq_alignment | 618 | 3–7 | +0.186 [-0.965, +1.330] | 0.758 | 1 | — |
| Claude Sonnet 5 | frq | frq_specificity | 618 | 3–7 | +0.035 [-0.692, +0.755] | 0.916 | 1 | — |
| Claude Sonnet 5 | frq | frq_novelty | 618 | 3–7 | +0.423 [-0.347, +1.188] | 0.29 | 1 | — |
| Claude Sonnet 5 | frq | frq_feasibility | 618 | 3–7 | -0.229 [-1.054, +0.603] | 0.584 | 1 | — |
| Claude Sonnet 5 | mcq | accuracy | 569 | 3–7 | +0.127 [-0.071, +0.319] | 0.198 | 1 | +0.1310 (0.203) |
| GPT-5.6 Sol | binary | accuracy | 196 | 2–6 | -0.114 [-0.675, +0.466] | 0.694 | 1 | -0.0471 (0.697) |
| GPT-5.6 Sol | binary_perturbed | accuracy | 649 | 2–6 | -0.157 [-0.485, +0.169] | 0.343 | 1 | -0.0548 (0.352) |
| GPT-5.6 Sol | date | signed_err | 194 | 2–6 | -29.181 [-63.007, +2.534] | 0.0708 | 1 | — |
| GPT-5.6 Sol | date | abs_err | 194 | 2–6 | +2.442 [-18.728, +25.703] | 0.879 | 1 | — |
| GPT-5.6 Sol | date | date_score | 194 | 2–6 | -0.064 [-0.269, +0.134] | 0.53 | 1 | — |
| GPT-5.6 Sol | frq | frq_score | 623 | 2–6 | +0.074 [-0.483, +0.645] | 0.795 | 1 | — |
| GPT-5.6 Sol | frq | frq_alignment | 623 | 2–6 | +0.080 [-1.197, +1.381] | 0.895 | 1 | — |
| GPT-5.6 Sol | frq | frq_specificity | 623 | 2–6 | +0.229 [-0.385, +0.852] | 0.456 | 1 | — |
| GPT-5.6 Sol | frq | frq_novelty | 623 | 2–6 | +0.111 [-0.604, +0.815] | 0.75 | 1 | — |
| GPT-5.6 Sol | frq | frq_feasibility | 623 | 2–6 | -0.126 [-0.975, +0.709] | 0.76 | 1 | — |
| GPT-5.6 Sol | mcq | accuracy | 602 | 2–6 | +0.016 [-0.218, +0.246] | 0.888 | 1 | +0.0118 (0.891) |
| Claude Opus 4.8 | binary | accuracy | 192 | 3–7 | -0.052 [-0.524, +0.435] | 0.835 | 1 | -0.0267 (0.831) |
| Claude Opus 4.8 | binary_perturbed | accuracy | 622 | 3–7 | -0.018 [-0.294, +0.267] | 0.899 | 1 | -0.0086 (0.899) |
| Claude Opus 4.8 | date | signed_err | 193 | 3–7 | -33.489 [-80.365, +7.640] | 0.111 | 1 | — |
| Claude Opus 4.8 | date | abs_err | 193 | 3–7 | +15.299 [-22.086, +58.688] | 0.454 | 1 | — |
| Claude Opus 4.8 | date | date_score | 193 | 3–7 | -0.196 [-0.489, +0.093] | 0.187 | 1 | — |
| Claude Opus 4.8 | frq | frq_score | 622 | 3–7 | +0.179 [-0.395, +0.749] | 0.56 | 1 | — |
| Claude Opus 4.8 | frq | frq_alignment | 622 | 3–7 | +0.123 [-1.035, +1.262] | 0.832 | 1 | — |
| Claude Opus 4.8 | frq | frq_specificity | 622 | 3–7 | +0.435 [-0.274, +1.126] | 0.223 | 1 | — |
| Claude Opus 4.8 | frq | frq_novelty | 622 | 3–7 | -0.063 [-0.800, +0.701] | 0.869 | 1 | — |
| Claude Opus 4.8 | frq | frq_feasibility | 622 | 3–7 | +0.221 [-0.642, +1.068] | 0.625 | 1 | — |
| Claude Opus 4.8 | mcq | accuracy | 569 | 3–7 | +0.161 [-0.027, +0.348] | 0.0906 | 1 | +0.2045 (0.0959) |

## 4. merged original + extension, base — `base`

| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary | accuracy | 2950 | 3–34 | +0.111 [+0.092, +0.131] | 0.0002 | 0.071 | +0.0608 (5.08e-28) |
| GPT-4o | binary_perturbed | accuracy | 4303 | 3–34 | -0.104 [-0.121, -0.087] | 0.0002 | 0.071 | -0.0476 (6.32e-31) |
| GPT-4o | date | signed_err | 2766 | 3–34 | -14.848 [-16.707, -13.064] | 0.0002 | 0.071 | — |
| GPT-4o | date | abs_err | 2766 | 3–34 | -12.347 [-14.155, -10.627] | 0.0002 | 0.071 | — |
| GPT-4o | date | date_score | 2766 | 3–34 | +0.160 [+0.146, +0.174] | 0.0002 | 0.071 | — |
| GPT-4o | frq | frq_score | 4758 | 3–34 | +0.063 [+0.027, +0.099] | 0.001 | 0.293 | — |
| GPT-4o | frq | frq_alignment | 4758 | 3–34 | -0.035 [-0.092, +0.024] | 0.247 | 1 | — |
| GPT-4o | frq | frq_specificity | 4758 | 3–34 | -0.003 [-0.042, +0.037] | 0.891 | 1 | — |
| GPT-4o | frq | frq_novelty | 4758 | 3–34 | +0.096 [+0.059, +0.131] | 0.0002 | 0.071 | — |
| GPT-4o | frq | frq_feasibility | 4758 | 3–34 | +0.194 [+0.127, +0.260] | 0.0002 | 0.071 | — |
| GPT-4o | mcq | accuracy | 4732 | 3–34 | -0.046 [-0.066, -0.026] | 0.0002 | 0.071 | -0.0155 (7.63e-06) |
| LLaMA 3.3 70B | binary | accuracy | 2930 | 1–32 | +0.044 [+0.031, +0.058] | 0.0002 | 0.071 | +0.0666 (3.42e-10) |
| LLaMA 3.3 70B | binary_perturbed | accuracy | 4274 | 1–32 | -0.033 [-0.045, -0.020] | 0.0002 | 0.071 | -0.0349 (1.57e-07) |
| LLaMA 3.3 70B | date | signed_err | 2926 | 1–32 | -11.235 [-12.415, -10.037] | 0.0002 | 0.071 | — |
| LLaMA 3.3 70B | date | abs_err | 2926 | 1–32 | -3.042 [-4.173, -1.944] | 0.0002 | 0.071 | — |
| LLaMA 3.3 70B | date | date_score | 2926 | 1–32 | +0.096 [+0.082, +0.109] | 0.0002 | 0.071 | — |
| LLaMA 3.3 70B | frq | frq_score | 4723 | 1–32 | -0.041 [-0.071, -0.011] | 0.0064 | 1 | — |
| LLaMA 3.3 70B | frq | frq_alignment | 4723 | 1–32 | -0.064 [-0.117, -0.012] | 0.0152 | 1 | — |
| LLaMA 3.3 70B | frq | frq_specificity | 4723 | 1–32 | -0.056 [-0.088, -0.025] | 0.0004 | 0.119 | — |
| LLaMA 3.3 70B | frq | frq_novelty | 4723 | 1–32 | +0.034 [+0.004, +0.064] | 0.0296 | 1 | — |
| LLaMA 3.3 70B | frq | frq_feasibility | 4723 | 1–32 | -0.077 [-0.135, -0.020] | 0.0078 | 1 | — |
| LLaMA 3.3 70B | mcq | accuracy | 4693 | 1–32 | -0.019 [-0.039, +0.002] | 0.0726 | 1 | -0.0063 (0.0711) |
| GPT-OSS 20B | binary | accuracy | 2349 | 1–26 | +0.046 [+0.017, +0.075] | 0.001 | 0.293 | +0.0249 (0.00141) |
| GPT-OSS 20B | binary_perturbed | accuracy | 3687 | 1–26 | -0.063 [-0.086, -0.040] | 0.0002 | 0.071 | -0.0282 (1.04e-07) |
| GPT-OSS 20B | date | signed_err | 2316 | 1–26 | -12.768 [-15.288, -10.251] | 0.0002 | 0.071 | — |
| GPT-OSS 20B | date | abs_err | 2316 | 1–26 | -7.924 [-10.298, -5.612] | 0.0002 | 0.071 | — |
| GPT-OSS 20B | date | date_score | 2316 | 1–26 | +0.124 [+0.105, +0.144] | 0.0002 | 0.071 | — |
| GPT-OSS 20B | frq | frq_score | 4018 | 1–26 | +0.028 [-0.018, +0.073] | 0.24 | 1 | — |
| GPT-OSS 20B | frq | frq_alignment | 4018 | 1–26 | -0.007 [-0.077, +0.064] | 0.847 | 1 | — |
| GPT-OSS 20B | frq | frq_specificity | 4018 | 1–26 | +0.115 [+0.053, +0.176] | 0.0004 | 0.119 | — |
| GPT-OSS 20B | frq | frq_novelty | 4018 | 1–26 | +0.087 [+0.025, +0.150] | 0.0082 | 1 | — |
| GPT-OSS 20B | frq | frq_feasibility | 4018 | 1–26 | -0.085 [-0.158, -0.010] | 0.0258 | 1 | — |
| GPT-OSS 20B | mcq | accuracy | 3986 | 1–26 | +0.001 [-0.024, +0.027] | 0.91 | 1 | +0.0004 (0.925) |
| DeepSeek R1 | binary | accuracy | 2014 | 1–20 | +0.130 [+0.085, +0.177] | 0.0002 | 0.071 | +0.0439 (8.11e-08) |
| DeepSeek R1 | binary_perturbed | accuracy | 2871 | 1–20 | -0.141 [-0.180, -0.102] | 0.0002 | 0.071 | -0.0476 (6.92e-12) |
| DeepSeek R1 | date | signed_err | 1702 | 1–20 | -12.769 [-17.378, -9.054] | 0.0002 | 0.071 | — |
| DeepSeek R1 | date | abs_err | 1702 | 1–20 | -8.635 [-13.145, -5.058] | 0.0002 | 0.071 | — |
| DeepSeek R1 | date | date_score | 1702 | 1–20 | +0.199 [+0.175, +0.223] | 0.0002 | 0.071 | — |
| DeepSeek R1 | frq | frq_score | 3231 | 1–20 | +0.060 [-0.003, +0.124] | 0.065 | 1 | — |
| DeepSeek R1 | frq | frq_alignment | 3231 | 1–20 | +0.088 [-0.023, +0.200] | 0.115 | 1 | — |
| DeepSeek R1 | frq | frq_specificity | 3231 | 1–20 | -0.060 [-0.145, +0.027] | 0.171 | 1 | — |
| DeepSeek R1 | frq | frq_novelty | 3231 | 1–20 | +0.132 [+0.046, +0.217] | 0.003 | 0.855 | — |
| DeepSeek R1 | frq | frq_feasibility | 3231 | 1–20 | +0.079 [-0.021, +0.180] | 0.121 | 1 | — |
| DeepSeek R1 | mcq | accuracy | 2818 | 1–20 | -0.014 [-0.054, +0.026] | 0.472 | 1 | -0.0049 (0.487) |
| Claude S4.5 | binary | accuracy | 1501 | 1–19 | +0.099 [+0.045, +0.153] | 0.0006 | 0.178 | +0.0473 (0.000293) |
| Claude S4.5 | binary_perturbed | accuracy | 2470 | 1–19 | -0.101 [-0.141, -0.062] | 0.0002 | 0.071 | -0.0415 (1.04e-06) |
| Claude S4.5 | date | signed_err | 1462 | 1–19 | -6.735 [-12.538, -0.922] | 0.0264 | 1 | — |
| Claude S4.5 | date | abs_err | 1462 | 1–19 | -7.968 [-13.054, -2.965] | 0.0012 | 0.348 | — |
| Claude S4.5 | date | date_score | 1462 | 1–19 | +0.094 [+0.061, +0.127] | 0.0002 | 0.071 | — |
| Claude S4.5 | frq | frq_score | 2739 | 1–19 | +0.030 [-0.043, +0.101] | 0.425 | 1 | — |
| Claude S4.5 | frq | frq_alignment | 2739 | 1–19 | +0.041 [-0.074, +0.153] | 0.49 | 1 | — |
| Claude S4.5 | frq | frq_specificity | 2739 | 1–19 | -0.030 [-0.123, +0.061] | 0.521 | 1 | — |
| Claude S4.5 | frq | frq_novelty | 2739 | 1–19 | +0.094 [-0.009, +0.200] | 0.0754 | 1 | — |
| Claude S4.5 | frq | frq_feasibility | 2739 | 1–19 | +0.016 [-0.096, +0.127] | 0.785 | 1 | — |
| Claude S4.5 | mcq | accuracy | 2602 | 1–19 | +0.021 [-0.019, +0.059] | 0.313 | 1 | +0.0085 (0.309) |
| GPT-5.4 | binary | accuracy | 808 | 1–12 | +0.107 [-0.018, +0.234] | 0.0888 | 1 | +0.0386 (0.103) |
| GPT-5.4 | binary_perturbed | accuracy | 1583 | 1–12 | -0.079 [-0.160, +0.002] | 0.0548 | 1 | -0.0279 (0.0595) |
| GPT-5.4 | date | signed_err | 765 | 1–12 | -11.220 [-22.866, +0.930] | 0.0712 | 1 | — |
| GPT-5.4 | date | abs_err | 765 | 1–12 | -14.467 [-23.520, -5.791] | 0.0016 | 0.461 | — |
| GPT-5.4 | date | date_score | 765 | 1–12 | -0.101 [-0.172, -0.030] | 0.0062 | 1 | — |
| GPT-5.4 | frq | frq_score | 1647 | 1–12 | -0.303 [-0.442, -0.165] | 0.0002 | 0.071 | — |
| GPT-5.4 | frq | frq_alignment | 1647 | 1–12 | +0.056 [-0.248, +0.347] | 0.744 | 1 | — |
| GPT-5.4 | frq | frq_specificity | 1647 | 1–12 | -0.622 [-0.786, -0.457] | 0.0002 | 0.071 | — |
| GPT-5.4 | frq | frq_novelty | 1647 | 1–12 | -0.595 [-0.783, -0.404] | 0.0002 | 0.071 | — |
| GPT-5.4 | frq | frq_feasibility | 1647 | 1–12 | -0.051 [-0.267, +0.153] | 0.626 | 1 | — |
| GPT-5.4 | mcq | accuracy | 1620 | 1–12 | +0.074 [+0.012, +0.136] | 0.0158 | 1 | +0.0417 (0.0208) |
| Claude Sonnet 5 | binary | accuracy | 316 | 1–7 | -0.096 [-0.379, +0.183] | 0.498 | 1 | -0.0378 (0.507) |
| Claude Sonnet 5 | binary_perturbed | accuracy | 822 | 1–7 | -0.010 [-0.184, +0.166] | 0.927 | 1 | -0.0046 (0.91) |
| Claude Sonnet 5 | date | signed_err | 315 | 1–7 | -28.558 [-52.708, -7.890] | 0.0084 | 1 | — |
| Claude Sonnet 5 | date | abs_err | 315 | 1–7 | +25.285 [+5.105, +49.281] | 0.014 | 1 | — |
| Claude Sonnet 5 | date | date_score | 315 | 1–7 | -0.325 [-0.489, -0.160] | 0.0006 | 0.178 | — |
| Claude Sonnet 5 | frq | frq_score | 822 | 1–7 | -0.223 [-0.570, +0.118] | 0.21 | 1 | — |
| Claude Sonnet 5 | frq | frq_alignment | 822 | 1–7 | -0.267 [-0.956, +0.405] | 0.437 | 1 | — |
| Claude Sonnet 5 | frq | frq_specificity | 822 | 1–7 | -0.258 [-0.658, +0.135] | 0.205 | 1 | — |
| Claude Sonnet 5 | frq | frq_novelty | 822 | 1–7 | +0.087 [-0.370, +0.545] | 0.697 | 1 | — |
| Claude Sonnet 5 | frq | frq_feasibility | 822 | 1–7 | -0.453 [-0.970, +0.052] | 0.0812 | 1 | — |
| Claude Sonnet 5 | mcq | accuracy | 759 | 1–7 | +0.099 [-0.019, +0.218] | 0.106 | 1 | +0.0948 (0.103) |
| GPT-5.6 Sol | binary | accuracy | 201 | 1–6 | -0.220 [-0.724, +0.326] | 0.416 | 1 | -0.0924 (0.412) |
| GPT-5.6 Sol | binary_perturbed | accuracy | 661 | 1–6 | -0.101 [-0.414, +0.222] | 0.532 | 1 | -0.0352 (0.533) |
| GPT-5.6 Sol | date | signed_err | 199 | 1–6 | -20.814 [-52.997, +7.494] | 0.163 | 1 | — |
| GPT-5.6 Sol | date | abs_err | 199 | 1–6 | +6.617 [-12.555, +27.927] | 0.54 | 1 | — |
| GPT-5.6 Sol | date | date_score | 199 | 1–6 | -0.133 [-0.322, +0.054] | 0.164 | 1 | — |
| GPT-5.6 Sol | frq | frq_score | 633 | 1–6 | +0.060 [-0.478, +0.591] | 0.819 | 1 | — |
| GPT-5.6 Sol | frq | frq_alignment | 633 | 1–6 | -0.016 [-1.237, +1.190] | 0.995 | 1 | — |
| GPT-5.6 Sol | frq | frq_specificity | 633 | 1–6 | +0.353 [-0.241, +0.944] | 0.245 | 1 | — |
| GPT-5.6 Sol | frq | frq_novelty | 633 | 1–6 | -0.003 [-0.680, +0.682] | 0.998 | 1 | — |
| GPT-5.6 Sol | frq | frq_feasibility | 633 | 1–6 | -0.095 [-0.899, +0.721] | 0.85 | 1 | — |
| GPT-5.6 Sol | mcq | accuracy | 609 | 1–6 | +0.018 [-0.207, +0.242] | 0.875 | 1 | +0.0129 (0.878) |
| Claude Opus 4.8 | binary | accuracy | 314 | 1–7 | -0.178 [-0.432, +0.081] | 0.176 | 1 | -0.0845 (0.181) |
| Claude Opus 4.8 | binary_perturbed | accuracy | 816 | 1–7 | +0.063 [-0.108, +0.235] | 0.48 | 1 | +0.0294 (0.471) |
| Claude Opus 4.8 | date | signed_err | 314 | 1–7 | -23.818 [-43.633, -5.207] | 0.0126 | 1 | — |
| Claude Opus 4.8 | date | abs_err | 314 | 1–7 | +20.341 [+3.101, +39.213] | 0.0234 | 1 | — |
| Claude Opus 4.8 | date | date_score | 314 | 1–7 | -0.333 [-0.471, -0.187] | 0.0002 | 0.071 | — |
| Claude Opus 4.8 | frq | frq_score | 827 | 1–7 | -0.282 [-0.622, +0.064] | 0.11 | 1 | — |
| Claude Opus 4.8 | frq | frq_alignment | 827 | 1–7 | -0.287 [-0.990, +0.404] | 0.427 | 1 | — |
| Claude Opus 4.8 | frq | frq_specificity | 827 | 1–7 | -0.146 [-0.528, +0.254] | 0.467 | 1 | — |
| Claude Opus 4.8 | frq | frq_novelty | 827 | 1–7 | -0.186 [-0.618, +0.245] | 0.405 | 1 | — |
| Claude Opus 4.8 | frq | frq_feasibility | 827 | 1–7 | -0.508 [-1.015, +0.019] | 0.0604 | 1 | — |
| Claude Opus 4.8 | mcq | accuracy | 759 | 1–7 | +0.055 [-0.044, +0.158] | 0.275 | 1 | +0.0683 (0.282) |

## 3. WS+Cutoff on the pinned 500 subset — `base`

| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary | accuracy | 296 | 3–28 | +0.158 [+0.092, +0.226] | 0.0002 | 0.071 | +0.0902 (7.13e-06) |
| GPT-4o | binary_perturbed | accuracy | 394 | 3–29 | -0.089 [-0.152, -0.026] | 0.0058 | 1 | -0.0466 (0.00671) |
| GPT-4o | date | signed_err | 275 | 3–28 | -9.729 [-16.076, -2.906] | 0.006 | 1 | — |
| GPT-4o | date | abs_err | 275 | 3–28 | -8.675 [-14.923, -2.047] | 0.0124 | 1 | — |
| GPT-4o | date | date_score | 275 | 3–28 | +0.108 [+0.068, +0.149] | 0.0002 | 0.071 | — |
| GPT-4o | frq | frq_score | 426 | 3–29 | +0.102 [-0.052, +0.254] | 0.18 | 1 | — |
| GPT-4o | frq | frq_alignment | 426 | 3–29 | +0.024 [-0.217, +0.258] | 0.821 | 1 | — |
| GPT-4o | frq | frq_specificity | 426 | 3–29 | -0.010 [-0.169, +0.150] | 0.907 | 1 | — |
| GPT-4o | frq | frq_novelty | 426 | 3–29 | +0.335 [+0.178, +0.488] | 0.0002 | 0.071 | — |
| GPT-4o | frq | frq_feasibility | 426 | 3–29 | +0.057 [-0.210, +0.339] | 0.663 | 1 | — |
| GPT-4o | mcq | accuracy | 435 | 3–28 | -0.057 [-0.132, +0.020] | 0.149 | 1 | -0.0193 (0.15) |
| LLaMA 3.3 70B | binary | accuracy | 294 | 1–26 | +0.026 [-0.022, +0.073] | 0.293 | 1 | +0.0353 (0.291) |
| LLaMA 3.3 70B | binary_perturbed | accuracy | 393 | 1–27 | -0.026 [-0.082, +0.033] | 0.398 | 1 | -0.0232 (0.383) |
| LLaMA 3.3 70B | date | signed_err | 292 | 1–26 | -7.752 [-10.906, -3.720] | 0.0008 | 0.235 | — |
| LLaMA 3.3 70B | date | abs_err | 292 | 1–26 | -3.521 [-6.413, +0.070] | 0.0542 | 1 | — |
| LLaMA 3.3 70B | date | date_score | 292 | 1–26 | +0.183 [+0.137, +0.231] | 0.0002 | 0.071 | — |
| LLaMA 3.3 70B | frq | frq_score | 423 | 1–27 | +0.037 [-0.086, +0.163] | 0.561 | 1 | — |
| LLaMA 3.3 70B | frq | frq_alignment | 423 | 1–27 | -0.134 [-0.348, +0.083] | 0.237 | 1 | — |
| LLaMA 3.3 70B | frq | frq_specificity | 423 | 1–27 | -0.070 [-0.187, +0.049] | 0.252 | 1 | — |
| LLaMA 3.3 70B | frq | frq_novelty | 423 | 1–27 | +0.152 [+0.040, +0.263] | 0.0084 | 1 | — |
| LLaMA 3.3 70B | frq | frq_feasibility | 423 | 1–27 | +0.199 [-0.034, +0.435] | 0.0972 | 1 | — |
| LLaMA 3.3 70B | mcq | accuracy | 433 | 1–26 | -0.085 [-0.164, -0.006] | 0.0374 | 1 | -0.0284 (0.0359) |
| DeepSeek R1 | binary | accuracy | 204 | 1–19 | +0.078 [-0.076, +0.227] | 0.327 | 1 | +0.0261 (0.314) |
| DeepSeek R1 | binary_perturbed | accuracy | 305 | 1–20 | -0.138 [-0.258, -0.014] | 0.0294 | 1 | -0.0468 (0.0318) |
| DeepSeek R1 | date | signed_err | 174 | 1–19 | -9.416 [-17.049, -2.432] | 0.0078 | 1 | — |
| DeepSeek R1 | date | abs_err | 174 | 1–19 | -5.822 [-13.050, +0.691] | 0.0798 | 1 | — |
| DeepSeek R1 | date | date_score | 174 | 1–19 | +0.155 [+0.076, +0.231] | 0.0002 | 0.071 | — |
| DeepSeek R1 | frq | frq_score | 329 | 1–20 | +0.154 [-0.074, +0.379] | 0.173 | 1 | — |
| DeepSeek R1 | frq | frq_alignment | 329 | 1–20 | +0.387 [-0.027, +0.820] | 0.0692 | 1 | — |
| DeepSeek R1 | frq | frq_specificity | 329 | 1–20 | -0.051 [-0.345, +0.251] | 0.748 | 1 | — |
| DeepSeek R1 | frq | frq_novelty | 329 | 1–20 | +0.236 [-0.030, +0.504] | 0.0836 | 1 | — |
| DeepSeek R1 | frq | frq_feasibility | 329 | 1–20 | +0.045 [-0.292, +0.370] | 0.785 | 1 | — |
| DeepSeek R1 | mcq | accuracy | 294 | 1–19 | +0.069 [-0.058, +0.196] | 0.296 | 1 | +0.0237 (0.289) |
| Claude S4.5 | binary | accuracy | 141 | 1–13 | +0.245 [+0.010, +0.481] | 0.0386 | 1 | +0.1124 (0.0472) |
| Claude S4.5 | binary_perturbed | accuracy | 219 | 1–14 | +0.033 [-0.145, +0.205] | 0.727 | 1 | +0.0158 (0.712) |
| Claude S4.5 | date | signed_err | 139 | 1–13 | -4.542 [-19.505, +9.404] | 0.527 | 1 | — |
| Claude S4.5 | date | abs_err | 139 | 1–13 | -11.257 [-24.607, -0.608] | 0.0362 | 1 | — |
| Claude S4.5 | date | date_score | 139 | 1–13 | +0.129 [+0.016, +0.245] | 0.0252 | 1 | — |
| Claude S4.5 | frq | frq_score | 231 | 1–14 | +0.287 [-0.160, +0.749] | 0.208 | 1 | — |
| Claude S4.5 | frq | frq_alignment | 231 | 1–14 | +0.529 [-0.113, +1.214] | 0.112 | 1 | — |
| Claude S4.5 | frq | frq_specificity | 231 | 1–14 | -0.113 [-0.669, +0.471] | 0.691 | 1 | — |
| Claude S4.5 | frq | frq_novelty | 231 | 1–14 | +0.467 [-0.107, +1.040] | 0.107 | 1 | — |
| Claude S4.5 | frq | frq_feasibility | 231 | 1–14 | +0.265 [-0.364, +0.911] | 0.418 | 1 | — |
| Claude S4.5 | mcq | accuracy | 220 | 1–13 | -0.039 [-0.238, +0.165] | 0.703 | 1 | -0.0159 (0.701) |
| GPT-5.4 | binary | — | 59 | 1–6 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.4 | binary_perturbed | accuracy | 100 | 1–7 | -0.070 [-0.700, +0.574] | 0.834 | 1 | -0.0234 (0.829) |
| GPT-5.4 | date | — | 59 | 1–6 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.4 | frq | frq_score | 107 | 1–7 | -0.356 [-1.361, +0.610] | 0.472 | 1 | — |
| GPT-5.4 | frq | frq_alignment | 107 | 1–7 | -0.335 [-2.606, +1.780] | 0.762 | 1 | — |
| GPT-5.4 | frq | frq_specificity | 107 | 1–7 | -0.242 [-1.398, +0.976] | 0.69 | 1 | — |
| GPT-5.4 | frq | frq_novelty | 107 | 1–7 | +0.191 [-0.950, +1.371] | 0.743 | 1 | — |
| GPT-5.4 | frq | frq_feasibility | 107 | 1–7 | -1.037 [-2.657, +0.510] | 0.191 | 1 | — |
| GPT-5.4 | mcq | accuracy | 105 | 1–6 | -0.459 [-0.917, -0.015] | 0.0434 | 1 | -0.2725 (0.0522) |
| Claude Sonnet 5 | binary | — | 14 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | binary_perturbed | — | 23 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | date | — | 14 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | frq | — | 24 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | mcq | — | 23 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | binary_perturbed | — | 1 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | frq | — | 1 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | binary | — | 14 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | binary_perturbed | — | 23 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | date | — | 13 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | frq | — | 24 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | mcq | — | 22 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |

## 3. WS+Cutoff on the pinned 500 subset — `ws_cutoff`

| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | binary | accuracy | 296 | 3–28 | +0.049 [-0.045, +0.143] | 0.307 | 1 | +0.0162 (0.305) |
| GPT-4o | binary_perturbed | accuracy | 394 | 3–29 | -0.054 [-0.133, +0.025] | 0.185 | 1 | -0.0192 (0.191) |
| GPT-4o | date | signed_err | 295 | 3–28 | -11.734 [-18.987, -4.651] | 0.0012 | 0.348 | — |
| GPT-4o | date | abs_err | 295 | 3–28 | -3.936 [-10.560, +2.572] | 0.237 | 1 | — |
| GPT-4o | date | date_score | 295 | 3–28 | +0.141 [+0.089, +0.193] | 0.0002 | 0.071 | — |
| GPT-4o | frq | frq_score | 425 | 3–29 | -0.026 [-0.187, +0.129] | 0.743 | 1 | — |
| GPT-4o | frq | frq_alignment | 425 | 3–29 | -0.294 [-0.564, -0.029] | 0.0302 | 1 | — |
| GPT-4o | frq | frq_specificity | 425 | 3–29 | +0.018 [-0.172, +0.205] | 0.875 | 1 | — |
| GPT-4o | frq | frq_novelty | 425 | 3–29 | +0.105 [-0.047, +0.258] | 0.18 | 1 | — |
| GPT-4o | frq | frq_feasibility | 425 | 3–29 | +0.065 [-0.186, +0.312] | 0.611 | 1 | — |
| GPT-4o | mcq | accuracy | 435 | 3–28 | -0.058 [-0.133, +0.020] | 0.148 | 1 | -0.0200 (0.139) |
| LLaMA 3.3 70B | binary | accuracy | 296 | 1–26 | +0.058 [-0.006, +0.122] | 0.0756 | 1 | +0.0426 (0.0775) |
| LLaMA 3.3 70B | binary_perturbed | accuracy | 394 | 1–27 | -0.043 [-0.108, +0.021] | 0.195 | 1 | -0.0245 (0.189) |
| LLaMA 3.3 70B | date | signed_err | 296 | 1–26 | -12.924 [-19.357, -7.380] | 0.0002 | 0.071 | — |
| LLaMA 3.3 70B | date | abs_err | 296 | 1–26 | +0.596 [-5.592, +5.867] | 0.807 | 1 | — |
| LLaMA 3.3 70B | date | date_score | 296 | 1–26 | +0.013 [-0.033, +0.059] | 0.584 | 1 | — |
| LLaMA 3.3 70B | frq | frq_score | 426 | 1–27 | -0.026 [-0.160, +0.111] | 0.705 | 1 | — |
| LLaMA 3.3 70B | frq | frq_alignment | 426 | 1–27 | -0.109 [-0.380, +0.176] | 0.445 | 1 | — |
| LLaMA 3.3 70B | frq | frq_specificity | 426 | 1–27 | -0.050 [-0.187, +0.093] | 0.494 | 1 | — |
| LLaMA 3.3 70B | frq | frq_novelty | 426 | 1–27 | +0.117 [-0.013, +0.247] | 0.0776 | 1 | — |
| LLaMA 3.3 70B | frq | frq_feasibility | 426 | 1–27 | -0.064 [-0.294, +0.172] | 0.585 | 1 | — |
| LLaMA 3.3 70B | mcq | accuracy | 435 | 1–26 | -0.056 [-0.133, +0.024] | 0.165 | 1 | -0.0187 (0.163) |
| DeepSeek R1 | binary | accuracy | 204 | 1–19 | +0.074 [-0.077, +0.222] | 0.335 | 1 | +0.0252 (0.338) |
| DeepSeek R1 | binary_perturbed | accuracy | 307 | 1–20 | +0.040 [-0.086, +0.166] | 0.539 | 1 | +0.0135 (0.54) |
| DeepSeek R1 | date | signed_err | 193 | 1–19 | -8.996 [-16.189, -1.726] | 0.0184 | 1 | — |
| DeepSeek R1 | date | abs_err | 193 | 1–19 | +1.743 [-4.309, +7.685] | 0.566 | 1 | — |
| DeepSeek R1 | date | date_score | 193 | 1–19 | +0.012 [-0.068, +0.091] | 0.777 | 1 | — |
| DeepSeek R1 | frq | frq_score | 320 | 1–20 | +0.011 [-0.206, +0.227] | 0.933 | 1 | — |
| DeepSeek R1 | frq | frq_alignment | 320 | 1–20 | -0.069 [-0.475, +0.326] | 0.733 | 1 | — |
| DeepSeek R1 | frq | frq_specificity | 320 | 1–20 | -0.055 [-0.321, +0.220] | 0.682 | 1 | — |
| DeepSeek R1 | frq | frq_novelty | 320 | 1–20 | +0.152 [-0.132, +0.429] | 0.293 | 1 | — |
| DeepSeek R1 | frq | frq_feasibility | 320 | 1–20 | +0.014 [-0.292, +0.323] | 0.933 | 1 | — |
| DeepSeek R1 | mcq | accuracy | 327 | 1–19 | +0.002 [-0.115, +0.119] | 0.973 | 1 | +0.0007 (0.975) |
| Claude S4.5 | binary | accuracy | 140 | 1–13 | +0.085 [-0.159, +0.340] | 0.5 | 1 | +0.0325 (0.504) |
| Claude S4.5 | binary_perturbed | accuracy | 213 | 1–14 | -0.170 [-0.357, +0.016] | 0.0744 | 1 | -0.0740 (0.0807) |
| Claude S4.5 | date | signed_err | 110 | 1–13 | -9.851 [-31.019, +11.159] | 0.355 | 1 | — |
| Claude S4.5 | date | abs_err | 110 | 1–13 | +15.650 [+0.921, +32.057] | 0.0356 | 1 | — |
| Claude S4.5 | date | date_score | 110 | 1–13 | -0.025 [-0.190, +0.143] | 0.762 | 1 | — |
| Claude S4.5 | frq | frq_score | 224 | 1–13 | +0.173 [-0.204, +0.551] | 0.357 | 1 | — |
| Claude S4.5 | frq | frq_alignment | 224 | 1–13 | +0.092 [-0.514, +0.714] | 0.76 | 1 | — |
| Claude S4.5 | frq | frq_specificity | 224 | 1–13 | +0.067 [-0.417, +0.555] | 0.782 | 1 | — |
| Claude S4.5 | frq | frq_novelty | 224 | 1–13 | +0.450 [-0.073, +0.978] | 0.0904 | 1 | — |
| Claude S4.5 | frq | frq_feasibility | 224 | 1–13 | +0.084 [-0.480, +0.649] | 0.766 | 1 | — |
| Claude S4.5 | mcq | accuracy | 216 | 1–13 | -0.018 [-0.217, +0.178] | 0.86 | 1 | -0.0072 (0.859) |
| GPT-5.4 | binary | — | 59 | 1–6 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.4 | binary_perturbed | accuracy | 100 | 1–7 | +0.596 [+0.017, +1.193] | 0.0432 | 1 | +0.2456 (0.0606) |
| GPT-5.4 | date | — | 59 | 1–6 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.4 | frq | frq_score | 106 | 1–7 | +0.456 [-0.528, +1.451] | 0.363 | 1 | — |
| GPT-5.4 | frq | frq_alignment | 106 | 1–7 | -0.471 [-2.785, +1.784] | 0.673 | 1 | — |
| GPT-5.4 | frq | frq_specificity | 106 | 1–7 | +0.500 [-0.658, +1.709] | 0.402 | 1 | — |
| GPT-5.4 | frq | frq_novelty | 106 | 1–7 | +0.664 [-0.690, +2.003] | 0.325 | 1 | — |
| GPT-5.4 | frq | frq_feasibility | 106 | 1–7 | +1.131 [-0.338, +2.601] | 0.126 | 1 | — |
| GPT-5.4 | mcq | accuracy | 105 | 1–6 | -0.457 [-0.992, +0.079] | 0.0904 | 1 | -0.2240 (0.108) |
| Claude Sonnet 5 | binary | — | 15 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | binary_perturbed | — | 23 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | date | — | 15 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | frq | — | 24 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Sonnet 5 | mcq | — | 23 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | binary_perturbed | — | 1 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| GPT-5.6 Sol | frq | — | 1 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | binary | — | 14 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | binary_perturbed | — | 22 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | date | — | 13 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | frq | — | 24 | 1–2 | skipped (n<100 or horizon range<3 months) | | | |
| Claude Opus 4.8 | mcq | — | 22 | 1–1 | skipped (n<100 or horizon range<3 months) | | | |
