# Analysis G — trace length and correctness

Does a longer stated justification accompany a better answer once item difficulty is held fixed? Predictor is log word count, standardised within task. Random intercepts for event and model.

| task | model | n | beta per SD of log length [95% CI] | p (Holm) | mean words, correct | mean words, wrong |
|---|---|---|---|---|---|---|
| binary_merged | all (pooled) | 3,292 | -0.161 [-0.245, -0.077] | 0.008 | 45 | 48 |
| binary_merged | Claude Opus 4.8 | 379 | -0.249 [-0.455, -0.042] | 0.804 | 35 | 37 |
| binary_merged | Claude S4.5 | 380 | 0.115 [-0.088, 0.318] | 1.000 | 76 | 73 |
| binary_merged | Claude Sonnet 5 | 376 | -0.157 [-0.362, 0.048] | 1.000 | 42 | 43 |
| binary_merged | DeepSeek-R1 | 378 | -0.065 [-0.268, 0.138] | 1.000 | 43 | 43 |
| binary_merged | DeepSeek-V4-Pro | 320 | -0.341 [-0.569, -0.113] | 0.162 | 41 | 44 |
| binary_merged | GPT-4o | 219 | -0.083 [-0.384, 0.219] | 1.000 | 43 | 44 |
| binary_merged | GPT-5.4 | 380 | -0.191 [-0.424, 0.042] | 1.000 | 58 | 59 |
| binary_merged | GPT-5.6 Sol | 380 | -0.273 [-0.482, -0.063] | 0.495 | 34 | 36 |
| binary_merged | GPT-OSS 20B | 320 | -0.181 [-0.489, 0.128] | 1.000 | 35 | 49 |
| binary_merged | LLaMA 3.3 70B | 160 | 0.007 [-0.346, 0.360] | 1.000 | 46 | 46 |
| binary | all (pooled) | 1,645 | -0.559 [-0.763, -0.355] | <0.001 | 45 | 51 |
| binary | Claude Opus 4.8 | 190 | -0.822 [-1.198, -0.446] | <0.001 | 33 | 38 |
| binary | Claude S4.5 | 190 | -0.091 [-0.454, 0.272] | 1.000 | 75 | 76 |
| binary | Claude Sonnet 5 | 187 | -0.243 [-0.577, 0.090] | 1.000 | 42 | 44 |
| binary | DeepSeek-R1 | 189 | -0.136 [-0.470, 0.198] | 1.000 | 43 | 45 |
| binary | DeepSeek-V4-Pro | 160 | -0.304 [-0.830, 0.221] | 1.000 | 41 | 44 |
| binary | GPT-5.4 | 190 | -0.561 [-0.953, -0.168] | 0.240 | 58 | 61 |
| binary | GPT-5.6 Sol | 190 | -1.432 [-2.025, -0.840] | <0.001 | 33 | 41 |
| binary | GPT-OSS 20B | 160 | -0.041 [-0.515, 0.432] | 1.000 | 38 | 53 |
| binary_perturbed | all (pooled) | 1,647 | 0.216 [0.046, 0.386] | 0.571 | 46 | 45 |
| binary_perturbed | Claude Opus 4.8 | 189 | 0.276 [-0.069, 0.620] | 1.000 | 36 | 35 |
| binary_perturbed | Claude S4.5 | 190 | 0.586 [0.094, 1.077] | 0.836 | 77 | 67 |
| binary_perturbed | Claude Sonnet 5 | 189 | -0.023 [-0.367, 0.321] | 1.000 | 42 | 42 |
| binary_perturbed | DeepSeek-R1 | 189 | 0.057 [-0.268, 0.381] | 1.000 | 42 | 42 |
| binary_perturbed | DeepSeek-V4-Pro | 160 | -0.187 [-0.656, 0.282] | 1.000 | 41 | 43 |
| binary_perturbed | GPT-5.4 | 190 | 0.004 [-0.327, 0.334] | 1.000 | 58 | 58 |
| binary_perturbed | GPT-5.6 Sol | 190 | 0.131 [-0.216, 0.478] | 1.000 | 35 | 35 |
| binary_perturbed | GPT-OSS 20B | 160 | 0.225 [-0.188, 0.638] | 1.000 | 34 | 33 |
| mcq | all (pooled) | 1,638 | -0.063 [-0.275, 0.148] | 1.000 | 41 | 45 |
| mcq | Claude Opus 4.8 | 188 | 0.280 [-0.274, 0.833] | 1.000 | 27 | 26 |
| mcq | Claude S4.5 | 185 | -0.285 [-0.643, 0.072] | 1.000 | 57 | 59 |
| mcq | Claude Sonnet 5 | 190 | 0.155 [-0.366, 0.675] | 1.000 | 32 | 31 |
| mcq | DeepSeek-R1 | 189 | -0.013 [-0.346, 0.319] | 1.000 | 57 | 56 |
| mcq | DeepSeek-V4-Pro | 160 | 0.364 [-0.020, 0.749] | 1.000 | 40 | 37 |
| mcq | GPT-5.4 | 188 | -0.314 [-0.705, 0.078] | 1.000 | 53 | 56 |
| mcq | GPT-5.6 Sol | 188 | -0.039 [-0.495, 0.417] | 1.000 | 35 | 36 |
| mcq | GPT-OSS 20B | 160 | -0.072 [-0.426, 0.281] | 1.000 | 35 | 36 |
| date | all (pooled) | 3,179 | -0.048 [-0.063, -0.034] | <0.001 | 30 | 41 |
| date | Claude Opus 4.8 | 328 | -0.059 [-0.093, -0.024] | 0.042 | 27 | 29 |
| date | Claude S4.5 | 326 | -0.017 [-0.047, 0.013] | 1.000 | 47 | 53 |
| date | Claude Sonnet 5 | 325 | 0.033 [0.000, 0.065] | 1.000 | 28 | 31 |
| date | DeepSeek-R1 | 323 | -0.022 [-0.050, 0.006] | 1.000 | 39 | 43 |
| date | DeepSeek-V4-Pro | 300 | -0.009 [-0.042, 0.024] | 1.000 | 35 | 41 |
| date | GPT-4o | 324 | -0.025 [-0.056, 0.005] | 1.000 | 44 | 41 |
| date | GPT-5.4 | 327 | -0.077 [-0.109, -0.046] | <0.001 | 43 | 52 |
| date | GPT-5.6 Sol | 326 | -0.162 [-0.196, -0.128] | <0.001 | 21 | 26 |
| date | GPT-OSS 20B | 300 | -0.025 [-0.057, 0.007] | 1.000 | 40 | 47 |
| date | LLaMA 3.3 70B | 300 | 0.004 [-0.025, 0.033] | 1.000 | 45 | 42 |
| frq | all (pooled) | 1,638 | 0.072 [0.005, 0.139] | 1.000 | 120 | 110 |
| frq | Claude Opus 4.8 | 188 | 0.222 [0.097, 0.347] | 0.025 | 143 | 138 |
| frq | Claude S4.5 | 187 | 0.093 [-0.019, 0.205] | 1.000 | 135 | 135 |
| frq | Claude Sonnet 5 | 187 | 0.113 [-0.010, 0.235] | 1.000 | 132 | 132 |
| frq | DeepSeek-R1 | 187 | 0.205 [0.089, 0.321] | 0.027 | 116 | 107 |
| frq | DeepSeek-V4-Pro | 160 | -0.015 [-0.154, 0.123] | 1.000 | 83 | 85 |
| frq | GPT-5.4 | 189 | 0.040 [-0.071, 0.151] | 1.000 | 139 | 138 |
| frq | GPT-5.6 Sol | 190 | 0.063 [-0.055, 0.181] | 1.000 | 95 | 94 |
| frq | GPT-OSS 20B | 160 | -0.131 [-0.282, 0.020] | 1.000 | 93 | 116 |

`binary_merged` pools the original and perturbed variants of each event and is the row to read for the binary task: the single-variant rows confound length with the direction of the answer, because ground truth is Yes for every original item and No for every perturbed one.


A positive beta means longer justifications accompany better outcomes at equal item difficulty. Length is a property of the model's style as much as of the item, so the pooled fits carry a model random intercept and the per-model fits hold style fixed by construction.

