# Sensitivity checks

## 1. DOI / journal dates instead of first-observable dates

Horizon and the date-task errors recomputed against the DOI date. Sign/CI agreement of within-model slopes:

| dataset | model | task:metric | slope first-obs /12mo [CI] | slope DOI /12mo [CI] | same sign | CI-excludes-0 agreement |
|---|---|---|---|---|---|---|
| orig | Claude S4.5 | binary_merged:accuracy | -0.001 [-0.046, +0.045] | +0.000 [-0.041, +0.043] | NO | yes |
| orig | Claude S4.5 | date:signed_err | -4.680 [-12.193, +4.439] | -5.670 [-13.416, +2.770] | yes | yes |
| orig | Claude S4.5 | date:abs_err | -8.162 [-15.091, -0.326] | -8.476 [-15.759, -0.826] | yes | yes |
| orig | Claude S4.5 | date:date_score | +0.128 [+0.086, +0.170] | +0.110 [+0.068, +0.152] | yes | yes |
| orig | Claude S4.5 | mcq:accuracy | -0.027 [-0.088, +0.037] | -0.018 [-0.078, +0.038] | yes | yes |
| orig | DeepSeek R1 | binary_merged:accuracy | -0.029 [-0.056, -0.003] | -0.012 [-0.037, +0.015] | yes | NO |
| orig | DeepSeek R1 | date:signed_err | -12.769 [-17.530, -9.023] | -12.324 [-17.022, -8.838] | yes | yes |
| orig | DeepSeek R1 | date:abs_err | -8.635 [-13.353, -4.996] | -8.187 [-12.974, -4.847] | yes | yes |
| orig | DeepSeek R1 | date:date_score | +0.199 [+0.176, +0.222] | +0.181 [+0.158, +0.202] | yes | yes |
| orig | DeepSeek R1 | mcq:accuracy | -0.014 [-0.054, +0.026] | -0.023 [-0.059, +0.013] | yes | yes |
| orig | GPT-4o | binary_merged:accuracy | +0.024 [+0.007, +0.039] | +0.018 [+0.002, +0.034] | yes | yes |
| orig | GPT-4o | date:signed_err | -12.810 [-14.897, -10.662] | -12.268 [-14.583, -10.054] | yes | yes |
| orig | GPT-4o | date:abs_err | -11.118 [-13.162, -9.062] | -10.549 [-12.839, -8.433] | yes | yes |
| orig | GPT-4o | date:date_score | +0.134 [+0.120, +0.147] | +0.124 [+0.111, +0.138] | yes | yes |
| orig | GPT-4o | mcq:accuracy | -0.041 [-0.065, -0.014] | -0.026 [-0.050, +0.001] | yes | NO |
| orig | GPT-5.4 | binary_merged:accuracy | +0.110 [-0.042, +0.255] | +0.135 [-0.003, +0.268] | yes | yes |
| orig | GPT-5.4 | date:signed_err | +10.329 [-23.406, +42.624] | -5.759 [-31.143, +20.295] | NO | yes |
| orig | GPT-5.4 | date:abs_err | -10.933 [-35.960, +18.201] | -8.493 [-28.340, +12.836] | yes | yes |
| orig | GPT-5.4 | date:date_score | -0.056 [-0.225, +0.106] | -0.004 [-0.147, +0.135] | yes | yes |
| orig | GPT-5.4 | mcq:accuracy | -0.174 [-0.344, -0.003] | -0.146 [-0.289, +0.014] | yes | NO |
| orig | GPT-OSS 20B | binary_merged:accuracy | +0.016 [-0.007, +0.038] | +0.024 [+0.002, +0.045] | yes | NO |
| orig | GPT-OSS 20B | date:signed_err | -11.999 [-15.024, -8.867] | -11.618 [-14.544, -8.647] | yes | yes |
| orig | GPT-OSS 20B | date:abs_err | -8.426 [-11.316, -5.596] | -7.815 [-10.687, -5.042] | yes | yes |
| orig | GPT-OSS 20B | date:date_score | +0.176 [+0.153, +0.200] | +0.160 [+0.138, +0.183] | yes | yes |
| orig | GPT-OSS 20B | mcq:accuracy | -0.031 [-0.064, +0.004] | -0.011 [-0.047, +0.021] | yes | yes |
| orig | LLaMA 3.3 70B | binary_merged:accuracy | -0.043 [-0.058, -0.029] | -0.037 [-0.053, -0.023] | yes | yes |
| orig | LLaMA 3.3 70B | date:signed_err | -11.250 [-12.508, -10.016] | -11.574 [-12.958, -10.191] | yes | yes |
| orig | LLaMA 3.3 70B | date:abs_err | -5.262 [-6.421, -4.157] | -4.496 [-5.831, -3.251] | yes | yes |
| orig | LLaMA 3.3 70B | date:date_score | +0.181 [+0.166, +0.195] | +0.143 [+0.128, +0.157] | yes | yes |
| orig | LLaMA 3.3 70B | mcq:accuracy | -0.033 [-0.059, -0.006] | -0.022 [-0.048, +0.005] | yes | NO |
| merged | Claude S4.5 | binary_merged:accuracy | +0.022 [-0.010, +0.054] | +0.024 [-0.007, +0.054] | yes | yes |
| merged | Claude S4.5 | date:signed_err | -6.735 [-12.497, -0.718] | -6.946 [-12.679, -1.239] | yes | yes |
| merged | Claude S4.5 | date:abs_err | -7.968 [-12.905, -2.929] | -8.292 [-13.489, -3.501] | yes | yes |
| merged | Claude S4.5 | date:date_score | +0.094 [+0.061, +0.128] | +0.091 [+0.060, +0.123] | yes | yes |
| merged | Claude S4.5 | mcq:accuracy | +0.021 [-0.020, +0.059] | +0.022 [-0.019, +0.060] | yes | yes |
| merged | DeepSeek R1 | binary_merged:accuracy | -0.029 [-0.056, -0.003] | -0.012 [-0.037, +0.015] | yes | NO |
| merged | DeepSeek R1 | date:signed_err | -12.769 [-17.530, -9.023] | -12.324 [-17.022, -8.838] | yes | yes |
| merged | DeepSeek R1 | date:abs_err | -8.635 [-13.353, -4.996] | -8.187 [-12.974, -4.847] | yes | yes |
| merged | DeepSeek R1 | date:date_score | +0.199 [+0.176, +0.222] | +0.181 [+0.158, +0.202] | yes | yes |
| merged | DeepSeek R1 | mcq:accuracy | -0.014 [-0.054, +0.026] | -0.023 [-0.059, +0.013] | yes | yes |
| merged | DeepSeek-V4-Pro | binary_merged:accuracy | -0.055 [-0.393, +0.293] | -0.102 [-0.415, +0.213] | yes | yes |
| merged | DeepSeek-V4-Pro | date:signed_err | -35.677 [-122.170, +50.905] | -22.317 [-98.217, +53.493] | yes | yes |
| merged | DeepSeek-V4-Pro | date:abs_err | +18.280 [-61.126, +97.087] | +18.725 [-48.126, +86.139] | yes | yes |
| merged | DeepSeek-V4-Pro | date:date_score | +0.183 [-0.463, +0.877] | +0.113 [-0.501, +0.728] | yes | yes |
| merged | DeepSeek-V4-Pro | mcq:accuracy | +0.071 [-0.413, +0.558] | -0.107 [-0.563, +0.354] | NO | yes |
| merged | GPT-4o | binary_merged:accuracy | +0.028 [+0.014, +0.041] | +0.025 [+0.011, +0.038] | yes | yes |
| merged | GPT-4o | date:signed_err | -14.848 [-16.650, -12.993] | -14.435 [-16.374, -12.514] | yes | yes |
| merged | GPT-4o | date:abs_err | -12.347 [-14.118, -10.537] | -11.809 [-13.630, -9.957] | yes | yes |
| merged | GPT-4o | date:date_score | +0.160 [+0.146, +0.173] | +0.149 [+0.136, +0.162] | yes | yes |
| merged | GPT-4o | mcq:accuracy | -0.046 [-0.066, -0.026] | -0.037 [-0.058, -0.017] | yes | yes |
| merged | GPT-5.4 | binary_merged:accuracy | -0.083 [-0.149, -0.017] | -0.068 [-0.126, -0.009] | yes | yes |
| merged | GPT-5.4 | date:signed_err | -11.220 [-22.913, +0.712] | -14.701 [-25.066, -4.191] | yes | NO |
| merged | GPT-5.4 | date:abs_err | -14.467 [-23.696, -5.741] | -13.600 [-21.583, -6.079] | yes | yes |
| merged | GPT-5.4 | date:date_score | -0.101 [-0.174, -0.028] | -0.066 [-0.130, -0.004] | yes | yes |
| merged | GPT-5.4 | mcq:accuracy | +0.074 [+0.013, +0.138] | +0.064 [+0.007, +0.121] | yes | yes |
| merged | GPT-OSS 20B | binary_merged:accuracy | +0.025 [+0.007, +0.042] | +0.031 [+0.014, +0.048] | yes | yes |
| merged | GPT-OSS 20B | date:signed_err | -12.768 [-15.231, -10.177] | -12.421 [-14.927, -9.993] | yes | yes |
| merged | GPT-OSS 20B | date:abs_err | -7.924 [-10.287, -5.571] | -7.430 [-9.749, -5.159] | yes | yes |
| merged | GPT-OSS 20B | date:date_score | +0.124 [+0.105, +0.144] | +0.114 [+0.095, +0.133] | yes | yes |
| merged | GPT-OSS 20B | mcq:accuracy | +0.001 [-0.024, +0.027] | +0.010 [-0.016, +0.035] | yes | yes |
| merged | LLaMA 3.3 70B | binary_merged:accuracy | -0.078 [-0.090, -0.066] | -0.075 [-0.087, -0.063] | yes | yes |
| merged | LLaMA 3.3 70B | date:signed_err | -11.235 [-12.415, -10.014] | -11.498 [-12.783, -10.154] | yes | yes |
| merged | LLaMA 3.3 70B | date:abs_err | -3.042 [-4.135, -1.964] | -2.399 [-3.585, -1.212] | yes | yes |
| merged | LLaMA 3.3 70B | date:date_score | +0.096 [+0.082, +0.110] | +0.065 [+0.051, +0.079] | yes | yes |
| merged | LLaMA 3.3 70B | mcq:accuracy | -0.019 [-0.040, +0.003] | -0.012 [-0.034, +0.009] | yes | yes |
| merged | GPT-5.6 Sol | binary_merged:accuracy | -0.145 [-0.407, +0.114] | +0.009 [-0.222, +0.241] | NO | yes |
| merged | GPT-5.6 Sol | date:signed_err | -20.814 [-52.803, +7.961] | -17.512 [-42.518, +7.266] | yes | yes |
| merged | GPT-5.6 Sol | date:abs_err | +6.617 [-12.899, +28.079] | +12.981 [-3.005, +29.148] | yes | yes |
| merged | GPT-5.6 Sol | date:date_score | -0.133 [-0.330, +0.056] | -0.225 [-0.402, -0.049] | yes | NO |
| merged | GPT-5.6 Sol | mcq:accuracy | +0.018 [-0.204, +0.238] | -0.001 [-0.235, +0.232] | NO | yes |
| merged | Claude Sonnet 5 | binary_merged:accuracy | +0.118 [-0.028, +0.261] | +0.122 [-0.004, +0.237] | yes | yes |
| merged | Claude Sonnet 5 | date:signed_err | -28.558 [-52.066, -7.555] | -20.451 [-39.797, -2.571] | yes | yes |
| merged | Claude Sonnet 5 | date:abs_err | +25.285 [+4.795, +48.413] | +17.973 [+0.796, +36.873] | yes | yes |
| merged | Claude Sonnet 5 | date:date_score | -0.325 [-0.489, -0.149] | -0.265 [-0.410, -0.118] | yes | yes |
| merged | Claude Sonnet 5 | mcq:accuracy | +0.099 [-0.020, +0.213] | +0.076 [-0.035, +0.192] | yes | yes |

Summary: 70/75 slopes keep their sign; 67/75 keep their CI-excludes-zero status.

Pooled GLMM horizon coefficient (per year) under DOI dates: orig binary_merged: -0.016 [-0.062, +0.031]; orig mcq: -0.182 [-0.333, -0.031]; orig date:abs_err: -5.390 [-6.476, -4.304]; merged binary_merged: -0.043 [-0.083, -0.002]; merged mcq: -0.124 [-0.243, -0.004]; merged date:abs_err: -5.161 [-6.075, -4.248]

## 2. Alternative cutoffs (Claude S4.5 → 2025-07 training-data cutoff; DeepSeek R1 → 2023-12 self-reported)

| dataset | model | task:metric | n (primary → alt) | slope primary /12mo [CI] | slope alt /12mo [CI] |
|---|---|---|---|---|---|
| orig | Claude S4.5 | binary_merged:accuracy | 3259 → 1741 | -0.001 [-0.046, +0.045] | -0.017 [-0.133, +0.098] |
| orig | Claude S4.5 | date:signed_err | 1293 → 677 | -4.680 [-12.193, +4.439] | -0.973 [-21.029, +19.545] |
| orig | Claude S4.5 | date:abs_err | 1293 → 677 | -8.162 [-15.091, -0.326] | -11.474 [-28.655, +6.800] |
| orig | Claude S4.5 | date:date_score | 1293 → 677 | +0.128 [+0.086, +0.170] | +0.005 [-0.128, +0.136] |
| orig | Claude S4.5 | mcq:accuracy | 2129 → 1117 | -0.027 [-0.088, +0.037] | -0.107 [-0.254, +0.049] |
| orig | DeepSeek R1 | binary_merged:accuracy | 4885 → 6347 | -0.029 [-0.056, -0.003] | -0.019 [-0.037, +0.000] |
| orig | DeepSeek R1 | date:signed_err | 1702 → 2326 | -12.769 [-17.530, -9.023] | -11.036 [-13.038, -9.255] |
| orig | DeepSeek R1 | date:abs_err | 1702 → 2326 | -8.635 [-13.353, -4.996] | -8.329 [-10.265, -6.601] |
| orig | DeepSeek R1 | date:date_score | 1702 → 2326 | +0.199 [+0.176, +0.222] | +0.208 [+0.192, +0.223] |
| orig | DeepSeek R1 | mcq:accuracy | 2818 → 3598 | -0.014 [-0.054, +0.026] | -0.026 [-0.053, +0.002] |
| merged | Claude S4.5 | binary_merged:accuracy | 3971 → 2453 | +0.022 [-0.010, +0.054] | +0.033 [-0.024, +0.089] |
| merged | Claude S4.5 | date:signed_err | 1462 → 846 | -6.735 [-12.497, -0.718] | -8.022 [-18.015, +1.676] |
| merged | Claude S4.5 | date:abs_err | 1462 → 846 | -7.968 [-12.905, -2.929] | -7.560 [-15.768, +1.050] |
| merged | Claude S4.5 | date:date_score | 1462 → 846 | +0.094 [+0.061, +0.128] | +0.004 [-0.067, +0.072] |
| merged | Claude S4.5 | mcq:accuracy | 2602 → 1590 | +0.021 [-0.020, +0.059] | +0.044 [-0.028, +0.120] |
| merged | DeepSeek R1 | binary_merged:accuracy | 4885 → 6347 | -0.029 [-0.056, -0.003] | -0.019 [-0.037, +0.000] |
| merged | DeepSeek R1 | date:signed_err | 1702 → 2326 | -12.769 [-17.530, -9.023] | -11.036 [-13.038, -9.255] |
| merged | DeepSeek R1 | date:abs_err | 1702 → 2326 | -8.635 [-13.353, -4.996] | -8.329 [-10.265, -6.601] |
| merged | DeepSeek R1 | date:date_score | 1702 → 2326 | +0.199 [+0.176, +0.222] | +0.208 [+0.192, +0.223] |
| merged | DeepSeek R1 | mcq:accuracy | 2818 → 3598 | -0.014 [-0.054, +0.026] | -0.026 [-0.053, +0.002] |

## 3. Including the cutoff month (h = 0) as post-cutoff

| dataset | model | task:metric | n (h≥1 → h≥0) | slope h≥1 /12mo [CI] | slope h≥0 /12mo [CI] |
|---|---|---|---|---|---|
| orig | Claude S4.5 | binary_merged:accuracy | 3259 → 3554 | -0.001 [-0.046, +0.045] | -0.012 [-0.051, +0.028] |
| orig | Claude S4.5 | date:signed_err | 1293 → 1415 | -4.680 [-12.193, +4.439] | -5.987 [-13.087, +1.822] |
| orig | Claude S4.5 | date:abs_err | 1293 → 1415 | -8.162 [-15.091, -0.326] | -9.042 [-15.443, -2.166] |
| orig | Claude S4.5 | date:date_score | 1293 → 1415 | +0.128 [+0.086, +0.170] | +0.128 [+0.089, +0.166] |
| orig | Claude S4.5 | mcq:accuracy | 2129 → 2309 | -0.027 [-0.088, +0.037] | +0.004 [-0.054, +0.058] |
| orig | DeepSeek R1 | binary_merged:accuracy | 4885 → 5147 | -0.029 [-0.056, -0.003] | -0.029 [-0.053, -0.004] |
| orig | DeepSeek R1 | date:signed_err | 1702 → 1806 | -12.769 [-17.530, -9.023] | -11.869 [-15.624, -8.623] |
| orig | DeepSeek R1 | date:abs_err | 1702 → 1806 | -8.635 [-13.353, -4.996] | -8.282 [-12.012, -5.165] |
| orig | DeepSeek R1 | date:date_score | 1702 → 1806 | +0.199 [+0.176, +0.222] | +0.196 [+0.173, +0.218] |
| orig | DeepSeek R1 | mcq:accuracy | 2818 → 2960 | -0.014 [-0.054, +0.026] | -0.023 [-0.058, +0.014] |
| orig | GPT-5.4 | binary_merged:accuracy | 1546 → 1821 | +0.110 [-0.042, +0.255] | +0.020 [-0.102, +0.139] |
| orig | GPT-5.4 | date:signed_err | 612 → 723 | +10.329 [-23.406, +42.624] | +7.868 [-16.149, +30.717] |
| orig | GPT-5.4 | date:abs_err | 612 → 723 | -10.933 [-35.960, +18.201] | -13.773 [-31.522, +5.667] |
| orig | GPT-5.4 | date:date_score | 612 → 723 | -0.056 [-0.225, +0.106] | -0.063 [-0.194, +0.063] |
| orig | GPT-5.4 | mcq:accuracy | 1014 → 1186 | -0.174 [-0.344, -0.003] | -0.105 [-0.240, +0.032] |
| orig | GPT-OSS 20B | binary_merged:accuracy | 5191 → 5459 | +0.016 [-0.007, +0.038] | +0.018 [-0.002, +0.038] |
| orig | GPT-OSS 20B | date:signed_err | 2126 → 2256 | -11.999 [-15.024, -8.867] | -10.793 [-13.664, -7.972] |
| orig | GPT-OSS 20B | date:abs_err | 2126 → 2256 | -8.426 [-11.316, -5.596] | -7.447 [-10.249, -4.824] |
| orig | GPT-OSS 20B | date:date_score | 2126 → 2256 | +0.176 [+0.153, +0.200] | +0.178 [+0.157, +0.201] |
| orig | GPT-OSS 20B | mcq:accuracy | 3380 → 3545 | -0.031 [-0.064, +0.004] | -0.017 [-0.052, +0.014] |
| merged | Claude S4.5 | binary_merged:accuracy | 3971 → 4266 | +0.022 [-0.010, +0.054] | +0.013 [-0.015, +0.041] |
| merged | Claude S4.5 | date:signed_err | 1462 → 1584 | -6.735 [-12.497, -0.718] | -7.391 [-12.460, -2.241] |
| merged | Claude S4.5 | date:abs_err | 1462 → 1584 | -7.968 [-12.905, -2.929] | -8.591 [-13.070, -4.144] |
| merged | Claude S4.5 | date:date_score | 1462 → 1584 | +0.094 [+0.061, +0.128] | +0.098 [+0.068, +0.126] |
| merged | Claude S4.5 | mcq:accuracy | 2602 → 2782 | +0.021 [-0.020, +0.059] | +0.035 [-0.001, +0.071] |
| merged | DeepSeek R1 | binary_merged:accuracy | 4885 → 5147 | -0.029 [-0.056, -0.003] | -0.029 [-0.053, -0.004] |
| merged | DeepSeek R1 | date:signed_err | 1702 → 1806 | -12.769 [-17.530, -9.023] | -11.869 [-15.624, -8.623] |
| merged | DeepSeek R1 | date:abs_err | 1702 → 1806 | -8.635 [-13.353, -4.996] | -8.282 [-12.012, -5.165] |
| merged | DeepSeek R1 | date:date_score | 1702 → 1806 | +0.199 [+0.176, +0.222] | +0.196 [+0.173, +0.218] |
| merged | DeepSeek R1 | mcq:accuracy | 2818 → 2960 | -0.014 [-0.054, +0.026] | -0.023 [-0.058, +0.014] |
| merged | DeepSeek-V4-Pro | binary_merged:accuracy | 661 → 845 | -0.055 [-0.393, +0.293] | -0.082 [-0.320, +0.175] |
| merged | DeepSeek-V4-Pro | date:signed_err | 153 → 194 | -35.677 [-122.170, +50.905] | +10.924 [-51.394, +79.484] |
| merged | DeepSeek-V4-Pro | date:abs_err | 153 → 194 | +18.280 [-61.126, +97.087] | +13.530 [-38.687, +70.887] |
| merged | DeepSeek-V4-Pro | date:date_score | 153 → 194 | +0.183 [-0.463, +0.877] | +0.064 [-0.406, +0.515] |
| merged | DeepSeek-V4-Pro | mcq:accuracy | 478 → 606 | +0.071 [-0.413, +0.558] | +0.038 [-0.303, +0.375] |
| merged | GPT-5.4 | binary_merged:accuracy | 2391 → 2666 | -0.083 [-0.149, -0.017] | -0.092 [-0.148, -0.037] |
| merged | GPT-5.4 | date:signed_err | 765 → 876 | -11.220 [-22.913, +0.712] | -8.786 [-18.862, +1.690] |
| merged | GPT-5.4 | date:abs_err | 765 → 876 | -14.467 [-23.696, -5.741] | -15.241 [-23.033, -7.638] |
| merged | GPT-5.4 | date:date_score | 765 → 876 | -0.101 [-0.174, -0.028] | -0.098 [-0.162, -0.034] |
| merged | GPT-5.4 | mcq:accuracy | 1620 → 1792 | +0.074 [+0.013, +0.138] | +0.069 [+0.011, +0.125] |
| merged | GPT-OSS 20B | binary_merged:accuracy | 6036 → 6304 | +0.025 [+0.007, +0.042] | +0.025 [+0.008, +0.042] |
| merged | GPT-OSS 20B | date:signed_err | 2316 → 2446 | -12.768 [-15.231, -10.177] | -11.743 [-13.968, -9.485] |
| merged | GPT-OSS 20B | date:abs_err | 2316 → 2446 | -7.924 [-10.287, -5.571] | -7.196 [-9.241, -5.055] |
| merged | GPT-OSS 20B | date:date_score | 2316 → 2446 | +0.124 [+0.105, +0.144] | +0.131 [+0.113, +0.149] |
| merged | GPT-OSS 20B | mcq:accuracy | 3986 → 4151 | +0.001 [-0.024, +0.027] | +0.008 [-0.016, +0.031] |
| merged | GPT-5.6 Sol | binary_merged:accuracy | 862 → 1173 | -0.145 [-0.407, +0.114] | -0.164 [-0.306, -0.022] |
| merged | GPT-5.6 Sol | date:signed_err | 199 → 319 | -20.814 [-52.803, +7.961] | -15.020 [-30.010, +0.291] |
| merged | GPT-5.6 Sol | date:abs_err | 199 → 319 | +6.617 [-12.899, +28.079] | +2.176 [-8.255, +13.467] |
| merged | GPT-5.6 Sol | date:date_score | 199 → 319 | -0.133 [-0.330, +0.056] | -0.091 [-0.194, +0.013] |
| merged | GPT-5.6 Sol | mcq:accuracy | 609 → 807 | +0.018 [-0.204, +0.238] | +0.047 [-0.095, +0.184] |
| merged | Claude Sonnet 5 | binary_merged:accuracy | 1138 → 1367 | +0.118 [-0.028, +0.261] | +0.133 [+0.026, +0.239] |
| merged | Claude Sonnet 5 | date:signed_err | 315 → 403 | -28.558 [-52.066, -7.555] | -25.922 [-45.014, -9.680] |
| merged | Claude Sonnet 5 | date:abs_err | 315 → 403 | +25.285 [+4.795, +48.413] | +22.475 [+7.362, +41.261] |
| merged | Claude Sonnet 5 | date:date_score | 315 → 403 | -0.325 [-0.489, -0.149] | -0.253 [-0.379, -0.114] |
| merged | Claude Sonnet 5 | mcq:accuracy | 759 → 918 | +0.099 [-0.020, +0.213] | +0.096 [+0.003, +0.188] |

## 4. Bin-width dependence

Direction = sign(last populated bin − first populated bin) among bins with n ≥ 20, per scheme (P = primary, 2 = 2-month, 6 = 6-month); `monotone` = fraction of adjacent populated-bin steps that move in the direction of the overall slope.

| dataset | model | task:metric | P: first→last (dir) | 2m | 6m | agree |
|---|---|---|---|---|---|---|
| orig | Claude S4.5 | binary_merged:accuracy | -0.017 (−, 4 bins, mono 0.67) | -0.016 (−, 7 bins, mono 0.67) | +0.001 (+, 3 bins, mono 0.50) | NO |
| orig | Claude S4.5 | date:abs_err | -7.080 (−, 4 bins, mono 0.67) | -7.250 (−, 7 bins, mono 0.50) | -12.143 (−, 3 bins, mono 1.00) | yes |
| orig | Claude S4.5 | date:date_score | +0.118 (+, 4 bins, mono 1.00) | +0.123 (+, 7 bins, mono 0.67) | +0.115 (+, 3 bins, mono 1.00) | yes |
| orig | Claude S4.5 | date:signed_err | -7.217 (−, 4 bins, mono 0.67) | -9.153 (−, 7 bins, mono 0.33) | -7.492 (−, 3 bins, mono 1.00) | yes |
| orig | Claude S4.5 | mcq:accuracy | -0.040 (−, 4 bins, mono 0.67) | -0.028 (−, 7 bins, mono 0.50) | -0.041 (−, 3 bins, mono 1.00) | yes |
| orig | DeepSeek R1 | binary_merged:accuracy | -0.035 (−, 4 bins, mono 0.67) | -0.038 (−, 10 bins, mono 0.67) | -0.053 (−, 4 bins, mono 1.00) | yes |
| orig | DeepSeek R1 | date:abs_err | -11.795 (−, 4 bins, mono 1.00) | -15.838 (−, 10 bins, mono 0.67) | -10.029 (−, 4 bins, mono 1.00) | yes |
| orig | DeepSeek R1 | date:date_score | +0.255 (+, 4 bins, mono 1.00) | +0.246 (+, 10 bins, mono 0.78) | +0.207 (+, 4 bins, mono 0.67) | yes |
| orig | DeepSeek R1 | date:signed_err | -16.398 (−, 4 bins, mono 1.00) | -22.202 (−, 10 bins, mono 0.67) | -16.217 (−, 4 bins, mono 1.00) | yes |
| orig | DeepSeek R1 | mcq:accuracy | -0.027 (−, 4 bins, mono 1.00) | -0.004 (−, 10 bins, mono 0.44) | +0.022 (+, 4 bins, mono 0.33) | NO |
| orig | GPT-4o | binary_merged:accuracy | +0.119 (+, 5 bins, mono 1.00) | +0.078 (+, 13 bins, mono 0.50) | +0.040 (+, 5 bins, mono 0.75) | yes |
| orig | GPT-4o | date:abs_err | -18.655 (−, 4 bins, mono 1.00) | -21.365 (−, 13 bins, mono 0.83) | -19.295 (−, 5 bins, mono 1.00) | yes |
| orig | GPT-4o | date:date_score | +0.206 (+, 4 bins, mono 1.00) | +0.237 (+, 13 bins, mono 0.92) | +0.209 (+, 5 bins, mono 1.00) | yes |
| orig | GPT-4o | date:signed_err | -21.724 (−, 4 bins, mono 1.00) | -24.195 (−, 13 bins, mono 0.83) | -22.364 (−, 5 bins, mono 1.00) | yes |
| orig | GPT-4o | mcq:accuracy | -0.237 (−, 5 bins, mono 1.00) | -0.092 (−, 13 bins, mono 0.67) | -0.073 (−, 5 bins, mono 1.00) | yes |
| orig | GPT-5.4 | binary_merged:accuracy | +0.045 (+, 2 bins, mono 1.00) | +0.033 (+, 3 bins, mono 0.50) | — | yes |
| orig | GPT-5.4 | date:abs_err | -1.145 (−, 2 bins, mono 1.00) | -2.703 (−, 3 bins, mono 0.50) | — | yes |
| orig | GPT-5.4 | date:date_score | -0.024 (−, 2 bins, mono 1.00) | -0.037 (−, 3 bins, mono 0.50) | — | yes |
| orig | GPT-5.4 | date:signed_err | +5.504 (+, 2 bins, mono 1.00) | +6.135 (+, 3 bins, mono 1.00) | — | yes |
| orig | GPT-5.4 | mcq:accuracy | -0.047 (−, 2 bins, mono 1.00) | -0.065 (−, 3 bins, mono 1.00) | — | yes |
| orig | GPT-OSS 20B | binary_merged:accuracy | +0.024 (+, 4 bins, mono 0.67) | +0.023 (+, 10 bins, mono 0.44) | +0.023 (+, 4 bins, mono 1.00) | yes |
| orig | GPT-OSS 20B | date:abs_err | -10.963 (−, 4 bins, mono 1.00) | -8.581 (−, 10 bins, mono 0.56) | -6.588 (−, 4 bins, mono 0.67) | yes |
| orig | GPT-OSS 20B | date:date_score | +0.241 (+, 4 bins, mono 1.00) | +0.187 (+, 10 bins, mono 0.78) | +0.160 (+, 4 bins, mono 0.67) | yes |
| orig | GPT-OSS 20B | date:signed_err | -14.602 (−, 4 bins, mono 1.00) | -14.059 (−, 10 bins, mono 0.56) | -11.989 (−, 4 bins, mono 0.67) | yes |
| orig | GPT-OSS 20B | mcq:accuracy | -0.073 (−, 4 bins, mono 0.67) | -0.076 (−, 10 bins, mono 0.67) | -0.046 (−, 4 bins, mono 0.67) | yes |
| orig | LLaMA 3.3 70B | binary_merged:accuracy | -0.102 (−, 5 bins, mono 1.00) | -0.140 (−, 13 bins, mono 0.67) | -0.093 (−, 5 bins, mono 1.00) | yes |
| orig | LLaMA 3.3 70B | date:abs_err | -8.741 (−, 5 bins, mono 0.75) | -7.722 (−, 13 bins, mono 0.58) | -7.405 (−, 5 bins, mono 0.50) | yes |
| orig | LLaMA 3.3 70B | date:date_score | +0.197 (+, 5 bins, mono 0.75) | +0.215 (+, 13 bins, mono 0.67) | +0.156 (+, 5 bins, mono 0.50) | yes |
| orig | LLaMA 3.3 70B | date:signed_err | -24.411 (−, 5 bins, mono 1.00) | -22.321 (−, 13 bins, mono 0.75) | -20.645 (−, 5 bins, mono 1.00) | yes |
| orig | LLaMA 3.3 70B | mcq:accuracy | -0.046 (−, 5 bins, mono 0.75) | -0.040 (−, 13 bins, mono 0.58) | -0.025 (−, 5 bins, mono 0.75) | yes |
| ext | DeepSeek-V4-Pro | binary_merged:accuracy | -0.019 (−, 2 bins, mono 1.00) | +0.002 (+, 2 bins, mono 1.00) | — | NO |
| ext | DeepSeek-V4-Pro | date:abs_err | +7.607 (+, 2 bins, mono 1.00) | +4.188 (+, 2 bins, mono 1.00) | — | yes |
| ext | DeepSeek-V4-Pro | date:date_score | +0.016 (+, 2 bins, mono 1.00) | -0.004 (−, 2 bins, mono 1.00) | — | NO |
| ext | DeepSeek-V4-Pro | date:signed_err | +1.290 (+, 2 bins, mono 1.00) | -5.931 (−, 2 bins, mono 1.00) | — | NO |
| ext | DeepSeek-V4-Pro | mcq:accuracy | -0.050 (−, 2 bins, mono 1.00) | +0.028 (+, 2 bins, mono 1.00) | — | NO |
| ext | GPT-OSS 20B | binary_merged:accuracy | +0.036 (+, 2 bins, mono 1.00) | -0.008 (−, 3 bins, mono 0.50) | +0.036 (+, 2 bins, mono 1.00) | NO |
| ext | GPT-OSS 20B | date:abs_err | -1.931 (−, 2 bins, mono 1.00) | -7.402 (−, 3 bins, mono 0.50) | -1.931 (−, 2 bins, mono 1.00) | yes |
| ext | GPT-OSS 20B | date:date_score | -0.033 (−, 2 bins, mono 1.00) | +0.012 (+, 3 bins, mono 0.50) | -0.033 (−, 2 bins, mono 1.00) | NO |
| ext | GPT-OSS 20B | date:signed_err | -4.766 (−, 2 bins, mono 1.00) | -12.346 (−, 3 bins, mono 1.00) | -4.766 (−, 2 bins, mono 1.00) | yes |
| ext | GPT-OSS 20B | mcq:accuracy | -0.061 (−, 2 bins, mono 1.00) | -0.075 (−, 3 bins, mono 1.00) | -0.061 (−, 2 bins, mono 1.00) | yes |
| ext | GPT-5.6 Sol | binary_merged:accuracy | -0.018 (−, 2 bins, mono 1.00) | -0.060 (−, 3 bins, mono 0.50) | — | yes |
| ext | GPT-5.6 Sol | date:abs_err | -0.347 (−, 2 bins, mono 1.00) | -0.409 (−, 3 bins, mono 1.00) | — | yes |
| ext | GPT-5.6 Sol | date:date_score | -0.003 (−, 2 bins, mono 1.00) | -0.014 (−, 3 bins, mono 1.00) | — | yes |
| ext | GPT-5.6 Sol | date:signed_err | -5.193 (−, 2 bins, mono 1.00) | -7.234 (−, 3 bins, mono 1.00) | — | yes |
| ext | GPT-5.6 Sol | mcq:accuracy | +0.002 (+, 2 bins, mono 1.00) | -0.002 (−, 3 bins, mono 0.50) | — | NO |
| ext | Claude Sonnet 5 | binary_merged:accuracy | -0.071 (−, 3 bins, mono 0.50) | -0.023 (−, 3 bins, mono 0.50) | -0.002 (−, 2 bins, mono 1.00) | yes |
| ext | Claude Sonnet 5 | date:abs_err | +15.111 (+, 3 bins, mono 1.00) | +12.152 (+, 3 bins, mono 0.50) | +14.287 (+, 2 bins, mono 1.00) | yes |
| ext | Claude Sonnet 5 | date:date_score | -0.056 (−, 3 bins, mono 1.00) | -0.054 (−, 3 bins, mono 0.50) | -0.055 (−, 2 bins, mono 1.00) | yes |
| ext | Claude Sonnet 5 | date:signed_err | -19.711 (−, 3 bins, mono 1.00) | -15.292 (−, 3 bins, mono 0.50) | -16.675 (−, 2 bins, mono 1.00) | yes |
| ext | Claude Sonnet 5 | mcq:accuracy | +0.067 (+, 3 bins, mono 1.00) | +0.055 (+, 3 bins, mono 0.50) | +0.056 (+, 2 bins, mono 1.00) | yes |
| merged | Claude S4.5 | binary_merged:accuracy | +0.010 (+, 4 bins, mono 0.67) | +0.036 (+, 10 bins, mono 0.44) | +0.053 (+, 4 bins, mono 1.00) | yes |
| merged | Claude S4.5 | date:abs_err | -5.666 (−, 4 bins, mono 0.67) | -5.819 (−, 10 bins, mono 0.44) | -10.711 (−, 4 bins, mono 0.67) | yes |
| merged | Claude S4.5 | date:date_score | +0.101 (+, 4 bins, mono 1.00) | +0.088 (+, 10 bins, mono 0.56) | +0.079 (+, 4 bins, mono 0.67) | yes |
| merged | Claude S4.5 | date:signed_err | -8.216 (−, 4 bins, mono 0.67) | -2.320 (−, 10 bins, mono 0.33) | -0.659 (−, 4 bins, mono 0.67) | yes |
| merged | Claude S4.5 | mcq:accuracy | +0.021 (+, 4 bins, mono 0.67) | +0.071 (+, 10 bins, mono 0.56) | +0.058 (+, 4 bins, mono 0.67) | yes |
| merged | DeepSeek R1 | binary_merged:accuracy | -0.035 (−, 4 bins, mono 0.67) | -0.038 (−, 10 bins, mono 0.67) | -0.053 (−, 4 bins, mono 1.00) | yes |
| merged | DeepSeek R1 | date:abs_err | -11.795 (−, 4 bins, mono 1.00) | -15.838 (−, 10 bins, mono 0.67) | -10.029 (−, 4 bins, mono 1.00) | yes |
| merged | DeepSeek R1 | date:date_score | +0.255 (+, 4 bins, mono 1.00) | +0.246 (+, 10 bins, mono 0.78) | +0.207 (+, 4 bins, mono 0.67) | yes |
| merged | DeepSeek R1 | date:signed_err | -16.398 (−, 4 bins, mono 1.00) | -22.202 (−, 10 bins, mono 0.67) | -16.217 (−, 4 bins, mono 1.00) | yes |
| merged | DeepSeek R1 | mcq:accuracy | -0.027 (−, 4 bins, mono 1.00) | -0.004 (−, 10 bins, mono 0.44) | +0.022 (+, 4 bins, mono 0.33) | NO |
| merged | DeepSeek-V4-Pro | binary_merged:accuracy | -0.019 (−, 2 bins, mono 1.00) | +0.002 (+, 2 bins, mono 1.00) | — | NO |
| merged | DeepSeek-V4-Pro | date:abs_err | +7.607 (+, 2 bins, mono 1.00) | +4.188 (+, 2 bins, mono 1.00) | — | yes |
| merged | DeepSeek-V4-Pro | date:date_score | +0.016 (+, 2 bins, mono 1.00) | -0.004 (−, 2 bins, mono 1.00) | — | NO |
| merged | DeepSeek-V4-Pro | date:signed_err | +1.290 (+, 2 bins, mono 1.00) | -5.931 (−, 2 bins, mono 1.00) | — | NO |
| merged | DeepSeek-V4-Pro | mcq:accuracy | -0.050 (−, 2 bins, mono 1.00) | +0.028 (+, 2 bins, mono 1.00) | — | NO |
| merged | GPT-4o | binary_merged:accuracy | +0.134 (+, 5 bins, mono 1.00) | +0.119 (+, 15 bins, mono 0.50) | +0.071 (+, 6 bins, mono 0.80) | yes |
| merged | GPT-4o | date:abs_err | -22.400 (−, 4 bins, mono 1.00) | -33.607 (−, 15 bins, mono 0.79) | -29.899 (−, 6 bins, mono 1.00) | yes |
| merged | GPT-4o | date:date_score | +0.280 (+, 4 bins, mono 1.00) | +0.510 (+, 15 bins, mono 0.93) | +0.425 (+, 6 bins, mono 1.00) | yes |
| merged | GPT-4o | date:signed_err | -26.838 (−, 4 bins, mono 1.00) | -39.848 (−, 15 bins, mono 0.79) | -37.334 (−, 6 bins, mono 1.00) | yes |
| merged | GPT-4o | mcq:accuracy | -0.250 (−, 5 bins, mono 1.00) | -0.134 (−, 15 bins, mono 0.64) | -0.120 (−, 6 bins, mono 1.00) | yes |
| merged | GPT-5.4 | binary_merged:accuracy | -0.041 (−, 3 bins, mono 0.50) | -0.043 (−, 6 bins, mono 0.60) | -0.064 (−, 2 bins, mono 1.00) | yes |
| merged | GPT-5.4 | date:abs_err | -9.772 (−, 3 bins, mono 1.00) | -13.049 (−, 6 bins, mono 0.60) | -9.176 (−, 2 bins, mono 1.00) | yes |
| merged | GPT-5.4 | date:date_score | -0.070 (−, 3 bins, mono 1.00) | -0.061 (−, 6 bins, mono 0.60) | -0.058 (−, 2 bins, mono 1.00) | yes |
| merged | GPT-5.4 | date:signed_err | -7.502 (−, 3 bins, mono 0.50) | -9.564 (−, 6 bins, mono 0.40) | -10.368 (−, 2 bins, mono 1.00) | yes |
| merged | GPT-5.4 | mcq:accuracy | +0.040 (+, 3 bins, mono 0.50) | +0.035 (+, 6 bins, mono 0.40) | +0.064 (+, 2 bins, mono 1.00) | yes |
| merged | GPT-OSS 20B | binary_merged:accuracy | +0.079 (+, 5 bins, mono 0.75) | +0.072 (+, 13 bins, mono 0.50) | +0.071 (+, 5 bins, mono 1.00) | yes |
| merged | GPT-OSS 20B | date:abs_err | -15.429 (−, 5 bins, mono 1.00) | -15.750 (−, 13 bins, mono 0.58) | -13.367 (−, 5 bins, mono 0.75) | yes |
| merged | GPT-OSS 20B | date:date_score | +0.149 (+, 5 bins, mono 0.75) | +0.154 (+, 13 bins, mono 0.67) | +0.127 (+, 5 bins, mono 0.50) | yes |
| merged | GPT-OSS 20B | date:signed_err | -27.264 (−, 5 bins, mono 1.00) | -27.809 (−, 13 bins, mono 0.67) | -25.063 (−, 5 bins, mono 1.00) | yes |
| merged | GPT-OSS 20B | mcq:accuracy | -0.058 (−, 5 bins, mono 0.75) | -0.058 (−, 13 bins, mono 0.67) | -0.028 (−, 5 bins, mono 0.50) | yes |
| merged | LLaMA 3.3 70B | binary_merged:accuracy | -0.183 (−, 5 bins, mono 1.00) | -0.287 (−, 16 bins, mono 0.67) | -0.236 (−, 6 bins, mono 1.00) | yes |
| merged | LLaMA 3.3 70B | date:abs_err | -5.916 (−, 5 bins, mono 0.75) | +1.502 (+, 16 bins, mono 0.53) | +1.718 (+, 6 bins, mono 0.60) | NO |
| merged | LLaMA 3.3 70B | date:date_score | +0.128 (+, 5 bins, mono 0.75) | +0.026 (+, 16 bins, mono 0.53) | -0.029 (−, 6 bins, mono 0.60) | NO |
| merged | LLaMA 3.3 70B | date:signed_err | -25.919 (−, 5 bins, mono 1.00) | -24.792 (−, 16 bins, mono 0.73) | -22.956 (−, 6 bins, mono 1.00) | yes |
| merged | LLaMA 3.3 70B | mcq:accuracy | -0.027 (−, 5 bins, mono 0.50) | -0.038 (−, 16 bins, mono 0.60) | -0.024 (−, 6 bins, mono 0.60) | yes |
| merged | GPT-5.6 Sol | binary_merged:accuracy | -0.017 (−, 2 bins, mono 1.00) | -0.055 (−, 3 bins, mono 0.50) | — | yes |
| merged | GPT-5.6 Sol | date:abs_err | +0.248 (+, 2 bins, mono 1.00) | +0.764 (+, 3 bins, mono 0.50) | — | yes |
| merged | GPT-5.6 Sol | date:date_score | -0.013 (−, 2 bins, mono 1.00) | -0.033 (−, 3 bins, mono 1.00) | — | yes |
| merged | GPT-5.6 Sol | date:signed_err | -4.310 (−, 2 bins, mono 1.00) | -5.514 (−, 3 bins, mono 0.50) | — | yes |
| merged | GPT-5.6 Sol | mcq:accuracy | +0.003 (+, 2 bins, mono 1.00) | -0.001 (−, 3 bins, mono 0.50) | — | NO |
| merged | Claude Sonnet 5 | binary_merged:accuracy | +0.027 (+, 3 bins, mono 1.00) | +0.082 (+, 4 bins, mono 0.67) | +0.024 (+, 2 bins, mono 1.00) | yes |
| merged | Claude Sonnet 5 | date:abs_err | +19.276 (+, 3 bins, mono 1.00) | +20.642 (+, 4 bins, mono 0.67) | +16.989 (+, 2 bins, mono 1.00) | yes |
| merged | Claude Sonnet 5 | date:date_score | -0.143 (−, 3 bins, mono 1.00) | -0.172 (−, 4 bins, mono 0.67) | -0.105 (−, 2 bins, mono 1.00) | yes |
| merged | Claude Sonnet 5 | date:signed_err | -21.931 (−, 3 bins, mono 1.00) | -22.659 (−, 4 bins, mono 0.67) | -19.219 (−, 2 bins, mono 1.00) | yes |
| merged | Claude Sonnet 5 | mcq:accuracy | +0.071 (+, 3 bins, mono 1.00) | +0.073 (+, 4 bins, mono 0.67) | +0.061 (+, 2 bins, mono 1.00) | yes |

Summary: direction agrees across all three bin schemes in 78/95 model × task × metric × dataset cells.

