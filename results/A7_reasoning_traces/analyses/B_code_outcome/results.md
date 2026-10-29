# Analysis B — does a code predict the outcome?

For each task, a random-intercept model of the outcome on the code: binary, perturbed binary and MCQ use a logistic GLMM with random intercepts for event and model (so item difficulty is absorbed); date and FRQ use the Gaussian analogue on the graded score. `beta` is the coefficient on the code, in log-odds for the binomial fits and in score units for the Gaussian ones. The raw difference in means (event-cluster bootstrap) is shown alongside for interpretation. p-values are Holm-adjusted across codes within each task. Only codes that passed the reliability rule are modelled.

**This is observational.** A code is a property of what the model wrote, not a treatment. These associations describe which stated justifications accompany success or failure; they do not establish that reasoning one way causes the outcome.

## Pooled across models

| task | code | n | with code | without | raw difference [95% CI] | beta [95% CI] | p (Holm) |
|---|---|---|---|---|---|---|---|
| binary_merged | EVIDENCE_CITED | 3,292 | 0.524 (n=529) | 0.502 (n=2,763) | 0.022 [-0.024, 0.069] | 0.072 [-0.118, 0.263] | 0.743 |
| binary_merged | KNOWLEDGE_GAP_ADMITTED | 3,292 | 0.608 (n=51) | 0.504 (n=3,241) | 0.104 [-0.035, 0.231] | 0.422 [-0.154, 0.998] | 0.604 |
| binary_merged | ABSENCE_AS_EVIDENCE | 3,292 | 0.524 (n=483) | 0.502 (n=2,809) | 0.021 [-0.026, 0.070] | 0.122 [-0.085, 0.329] | 0.743 |
| binary_merged | RATE_OF_PROGRESS | 3,292 | 0.408 (n=49) | 0.507 (n=3,243) | -0.099 [-0.233, 0.027] | -0.319 [-0.903, 0.264] | 0.743 |
| binary_merged | PROVENANCE_INFERRED | 3,292 | 0.708 (n=185) | 0.493 (n=3,107) | 0.215 [0.147, 0.281] | 0.880 [0.550, 1.210] | <0.001 **|
| binary_merged | FIELD_MOMENTUM | 3,292 | 0.469 (n=866) | 0.519 (n=2,426) | -0.050 [-0.089, -0.010] | -0.182 [-0.346, -0.017] | 0.151 |
| binary | EVIDENCE_CITED | 1,645 | 0.647 (n=258) | 0.387 (n=1,387) | 0.260 [0.194, 0.322] | 1.418 [1.081, 1.756] | <0.001 **|
| binary | KNOWLEDGE_GAP_ADMITTED | 1,645 | 0.261 (n=23) | 0.430 (n=1,622) | -0.169 [-0.330, 0.030] | -0.691 [-1.707, 0.324] | 0.364 |
| binary | ABSENCE_AS_EVIDENCE | 1,645 | 0.004 (n=230) | 0.497 (n=1,415) | -0.492 [-0.520, -0.466] | -5.545 [-7.542, -3.549] | <0.001 **|
| binary | RATE_OF_PROGRESS | 1,645 | 0.308 (n=26) | 0.430 (n=1,619) | -0.122 [-0.298, 0.060] | -0.236 [-1.175, 0.703] | 0.622 |
| binary | PROVENANCE_INFERRED | 1,645 | 0.860 (n=143) | 0.387 (n=1,502) | 0.473 [0.403, 0.531] | 2.494 [1.944, 3.045] | <0.001 **|
| binary | FIELD_MOMENTUM | 1,645 | 0.655 (n=420) | 0.350 (n=1,225) | 0.305 [0.251, 0.361] | 1.684 [1.366, 2.002] | <0.001 **|
| binary_perturbed | EVIDENCE_CITED | 1,647 | 0.406 (n=271) | 0.618 (n=1,376) | -0.212 [-0.273, -0.151] | -1.186 [-1.490, -0.882] | <0.001 **|
| binary_perturbed | KNOWLEDGE_GAP_ADMITTED | 1,647 | 0.893 (n=28) | 0.578 (n=1,619) | 0.315 [0.183, 0.428] | 1.557 [0.316, 2.798] | 0.028 **|
| binary_perturbed | ABSENCE_AS_EVIDENCE | 1,647 | 0.996 (n=253) | 0.508 (n=1,394) | 0.488 [0.459, 0.517] | 5.625 [3.644, 7.605] | <0.001 **|
| binary_perturbed | RATE_OF_PROGRESS | 1,647 | 0.522 (n=23) | 0.584 (n=1,624) | -0.062 [-0.275, 0.151] | -0.473 [-1.385, 0.440] | 0.310 |
| binary_perturbed | PROVENANCE_INFERRED | 1,647 | 0.190 (n=42) | 0.593 (n=1,605) | -0.403 [-0.512, -0.282] | -1.899 [-2.739, -1.059] | <0.001 **|
| binary_perturbed | FIELD_MOMENTUM | 1,647 | 0.294 (n=446) | 0.690 (n=1,201) | -0.397 [-0.449, -0.347] | -1.894 [-2.199, -1.590] | <0.001 **|
| mcq | EVIDENCE_CITED | 1,638 | 0.724 (n=192) | 0.723 (n=1,446) | 0.001 [-0.069, 0.068] | -0.241 [-0.652, 0.171] | 0.252 |
| mcq | PROVENANCE_INFERRED | 1,638 | 0.919 (n=123) | 0.708 (n=1,515) | 0.211 [0.153, 0.260] | 0.899 [0.177, 1.620] | 0.029 **|
| date | EVIDENCE_CITED | 3,179 | 0.376 (n=291) | 0.310 (n=2,888) | 0.066 [0.025, 0.105] | 0.067 [0.031, 0.103] | <0.001 **|
| date | RATE_OF_PROGRESS | 3,179 | 0.259 (n=941) | 0.340 (n=2,238) | -0.081 [-0.103, -0.060] | -0.026 [-0.053, 0.001] | 0.057 |
| date | ROUND_ANCHOR | 3,179 | 0.249 (n=761) | 0.337 (n=2,418) | -0.088 [-0.110, -0.065] | -0.036 [-0.065, -0.007] | 0.032 **|
| date | PROVENANCE_INFERRED | 3,179 | 0.423 (n=504) | 0.296 (n=2,675) | 0.127 [0.093, 0.162] | 0.107 [0.075, 0.138] | <0.001 **|
| date | FIELD_MOMENTUM | 3,179 | 0.348 (n=1,091) | 0.300 (n=2,088) | 0.048 [0.027, 0.071] | 0.055 [0.032, 0.079] | <0.001 **|
| frq | EVIDENCE_CITED | 1,638 | 4.562 (n=20) | 4.344 (n=1,618) | 0.219 [-0.131, 0.570] | 0.178 [-0.197, 0.553] | 0.353 |

**Codes that predict success** (10 pooled task-code pairs at Holm p < 0.05): PROVENANCE_INFERRED on binary_merged (beta +0.88), EVIDENCE_CITED on binary (beta +1.42), PROVENANCE_INFERRED on binary (beta +2.49), FIELD_MOMENTUM on binary (beta +1.68), KNOWLEDGE_GAP_ADMITTED on binary_perturbed (beta +1.56), ABSENCE_AS_EVIDENCE on binary_perturbed (beta +5.62), PROVENANCE_INFERRED on mcq (beta +0.90), EVIDENCE_CITED on date (beta +0.07), PROVENANCE_INFERRED on date (beta +0.11), FIELD_MOMENTUM on date (beta +0.06).

**Codes that predict failure** (5): ABSENCE_AS_EVIDENCE on binary (beta -5.55), EVIDENCE_CITED on binary_perturbed (beta -1.19), PROVENANCE_INFERRED on binary_perturbed (beta -1.90), FIELD_MOMENTUM on binary_perturbed (beta -1.89), ROUND_ANCHOR on date (beta -0.04).

## Per model

Full per-model table: `tables/B_code_outcome.csv` (rows with scope = per_model). Cells shown here are the code-task pairs significant after Holm adjustment within that model and task.

| model | task | code | with code | without | beta [95% CI] | p (Holm) |
|---|---|---|---|---|---|---|
| Claude S4.5 | binary_merged | PROVENANCE_INFERRED | 0.750 | 0.444 | 1.324 [0.377, 2.272] | 0.037 |
| GPT-5.6 Sol | binary_merged | FIELD_MOMENTUM | 0.355 | 0.596 | -0.987 [-1.753, -0.220] | 0.046 |
| Claude Opus 4.8 | binary | EVIDENCE_CITED | 0.857 | 0.310 | 2.653 [1.571, 3.736] | <0.001 |
| Claude Opus 4.8 | binary | PROVENANCE_INFERRED | 0.806 | 0.333 | 2.177 [1.139, 3.215] | <0.001 |
| Claude S4.5 | binary | EVIDENCE_CITED | 0.549 | 0.187 | 1.708 [0.929, 2.486] | <0.001 |
| Claude S4.5 | binary | ABSENCE_AS_EVIDENCE | 0.048 | 0.314 | -2.210 [-4.302, -0.119] | 0.038 |
| Claude S4.5 | binary | PROVENANCE_INFERRED | 0.810 | 0.219 | 2.786 [1.536, 4.037] | <0.001 |
| Claude S4.5 | binary | FIELD_MOMENTUM | 0.472 | 0.240 | 1.068 [0.220, 1.915] | 0.027 |
| Claude Sonnet 5 | binary | EVIDENCE_CITED | 0.615 | 0.319 | 1.271 [0.520, 2.021] | 0.003 |
| Claude Sonnet 5 | binary | PROVENANCE_INFERRED | 0.783 | 0.277 | 2.304 [1.434, 3.175] | <0.001 |
| DeepSeek-R1 | binary | FIELD_MOMENTUM | 0.712 | 0.220 | 2.235 [1.479, 2.991] | <0.001 |
| GPT-4o | binary | FIELD_MOMENTUM | 0.266 | 0.067 | 1.620 [0.260, 2.980] | 0.020 |
| GPT-5.4 | binary | FIELD_MOMENTUM | 0.852 | 0.461 | 1.950 [1.180, 2.721] | <0.001 |
| GPT-OSS 20B | binary | EVIDENCE_CITED | 0.455 | 0.145 | 1.621 [0.542, 2.701] | 0.006 |
| Claude Opus 4.8 | binary_perturbed | EVIDENCE_CITED | 0.333 | 0.758 | -1.890 [-2.768, -1.011] | <0.001 |
| Claude Opus 4.8 | binary_perturbed | FIELD_MOMENTUM | 0.364 | 0.719 | -1.544 [-2.592, -0.495] | 0.008 |
| Claude S4.5 | binary_perturbed | EVIDENCE_CITED | 0.426 | 0.713 | -1.249 [-2.019, -0.480] | 0.004 |
| Claude S4.5 | binary_perturbed | FIELD_MOMENTUM | 0.481 | 0.703 | -0.967 [-1.707, -0.227] | 0.021 |
| Claude Sonnet 5 | binary_perturbed | EVIDENCE_CITED | 0.471 | 0.775 | -1.394 [-2.157, -0.630] | 0.001 |
| Claude Sonnet 5 | binary_perturbed | FIELD_MOMENTUM | 0.370 | 0.747 | -1.661 [-2.625, -0.697] | 0.001 |
| DeepSeek-R1 | binary_perturbed | FIELD_MOMENTUM | 0.179 | 0.689 | -2.375 [-3.176, -1.574] | <0.001 |
| DeepSeek-V4-Pro | binary_perturbed | EVIDENCE_CITED | 0.579 | 0.901 | -1.908 [-3.092, -0.724] | 0.003 |
| DeepSeek-V4-Pro | binary_perturbed | FIELD_MOMENTUM | 0.645 | 0.915 | -1.786 [-2.836, -0.736] | 0.003 |
| GPT-4o | binary_perturbed | FIELD_MOMENTUM | 0.621 | 0.977 | -3.263 [-5.347, -1.179] | 0.002 |
| GPT-5.4 | binary_perturbed | FIELD_MOMENTUM | 0.127 | 0.586 | -2.324 [-3.148, -1.499] | <0.001 |
| Claude S4.5 | date | RATE_OF_PROGRESS | 0.206 | 0.324 | -0.119 [-0.184, -0.053] | 0.002 |
| Claude Sonnet 5 | date | PROVENANCE_INFERRED | 0.288 | 0.451 | -0.163 [-0.227, -0.099] | <0.001 |
| Claude Sonnet 5 | date | FIELD_MOMENTUM | 0.549 | 0.349 | 0.200 [0.115, 0.285] | <0.001 |
| DeepSeek-V4-Pro | date | ROUND_ANCHOR | 0.163 | 0.267 | -0.104 [-0.174, -0.034] | 0.017 |
| GPT-4o | date | ROUND_ANCHOR | 0.052 | 0.241 | -0.189 [-0.300, -0.078] | 0.002 |
| GPT-4o | date | FIELD_MOMENTUM | 0.270 | 0.090 | 0.180 [0.112, 0.249] | <0.001 |
| GPT-5.4 | date | PROVENANCE_INFERRED | 0.403 | 0.203 | 0.200 [0.116, 0.283] | <0.001 |
| GPT-5.6 Sol | date | EVIDENCE_CITED | 0.584 | 0.340 | 0.244 [0.090, 0.398] | 0.006 |
| GPT-5.6 Sol | date | RATE_OF_PROGRESS | 0.079 | 0.418 | -0.339 [-0.431, -0.247] | <0.001 |
| GPT-5.6 Sol | date | ROUND_ANCHOR | 0.498 | 0.335 | 0.163 [0.051, 0.275] | 0.009 |
| GPT-5.6 Sol | date | PROVENANCE_INFERRED | 0.739 | 0.238 | 0.501 [0.429, 0.573] | <0.001 |
| GPT-5.6 Sol | date | FIELD_MOMENTUM | 0.244 | 0.372 | -0.128 [-0.243, -0.013] | 0.029 |

## Response bias versus discrimination

Ground truth is Yes for every original binary item and No for every perturbed one. A code that simply pushes a model toward "No" therefore scores near 0 on one variant and near 1 on the other, which is what the two single-variant rows above show for several codes. The merged-binary rows pool both variants of the same event, so that cancels and only genuine discrimination survives. The table below makes the bias explicit: the effect of each code on the probability of answering Yes, over both variants pooled.

| code | P(answer Yes) with code | without | difference [95% CI] | beta log-odds [95% CI] | p (Holm) |
|---|---|---|---|---|---|
| EVIDENCE_CITED | 0.620 (n=529) | 0.385 | +0.235 [+0.191, +0.285] | 1.295 [1.067, 1.524] | <0.001 |
| KNOWLEDGE_GAP_ADMITTED | 0.176 (n=51) | 0.426 | -0.250 [-0.353, -0.136] | -1.057 [-1.823, -0.291] | 0.014 |
| ABSENCE_AS_EVIDENCE | 0.004 (n=483) | 0.494 | -0.490 [-0.511, -0.470] | -5.600 [-7.006, -4.194] | <0.001 |
| RATE_OF_PROGRESS | 0.388 (n=49) | 0.423 | -0.035 [-0.160, +0.100] | 0.102 [-0.547, 0.751] | 0.757 |
| PROVENANCE_INFERRED | 0.849 (n=185) | 0.397 | +0.451 [+0.394, +0.506] | 2.328 [1.874, 2.783] | <0.001 |
| FIELD_MOMENTUM | 0.681 (n=866) | 0.330 | +0.351 [+0.316, +0.388] | 1.788 [1.566, 2.010] | <0.001 |

**On merged binary accuracy, 1 of 6 codes retain a significant association**: PROVENANCE_INFERRED (beta +0.88).
