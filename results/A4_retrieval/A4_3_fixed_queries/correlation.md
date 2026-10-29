# A4.3 — agreement between the fixed-evidence-packet runs and the original manuscript's retrieval runs

Cell level: one point per model × task × partition (pre/post) with n ≥ 20. FRQ cells are rescaled from 0–10 to 0–1 before pooling so all tasks share a unit scale. Pearson r and Spearman ρ with 10,000 cell-bootstrap 95% CIs; MAD = mean absolute difference between setups, with the same cell-bootstrap 95% CI.

| quantity | cells | Pearson r [CI] | Spearman ρ [CI] | MAD [CI] | mean orig | mean fixed |
|---|---|---|---|---|---|---|
| WS+Cutoff accuracy/score (condition mean), pre + post | 43 | 0.993 [0.988, 0.996] | 0.990 [0.970, 0.995] | 0.020 [0.015, 0.024] | +0.614 | +0.617 |
| WS+Cutoff accuracy/score (condition mean), post only | 23 | 0.989 [0.981, 0.995] | 0.990 [0.952, 1.000] | 0.025 [0.018, 0.031] | +0.531 | +0.532 |
| WS accuracy/score (condition mean), pre + post | 43 | 0.957 [0.902, 0.989] | 0.959 [0.894, 0.985] | 0.037 [0.026, 0.052] | +0.684 | +0.685 |
| WS accuracy/score (condition mean), post only | 23 | 0.946 [0.847, 0.994] | 0.947 [0.802, 0.993] | 0.045 [0.027, 0.069] | +0.652 | +0.650 |
| WS+Cutoff score, FRQ cells only (0–10 units), pre + post | 9 | 0.999 [0.999, 1.000] | 1.000 [1.000, 1.000] | 0.100 [0.065, 0.136] | +5.005 | +5.102 |
| WS+Cutoff score, FRQ cells only (0–10 units), post only | 5 | 1.000 [0.994, 1.000] | 1.000 [1.000, 1.000] | 0.132 [0.097, 0.169] | +4.452 | +4.584 |
| WS score, FRQ cells only (0–10 units), pre + post | 9 | 0.974 [0.930, 0.996] | 0.933 [0.478, 1.000] | 0.228 [0.133, 0.329] | +5.251 | +5.473 |
| WS score, FRQ cells only (0–10 units), post only | 5 | 0.987 [0.963, 1.000] | 1.000 [1.000, 1.000] | 0.305 [0.228, 0.418] | +4.922 | +5.227 |
| knowledge gap (WS+Cutoff − base), pre + post | 43 | 0.986 [0.974, 0.992] | 0.973 [0.927, 0.989] | 0.020 [0.015, 0.024] | +0.089 | +0.092 |
| knowledge gap (WS+Cutoff − base), post only | 23 | 0.970 [0.938, 0.987] | 0.969 [0.892, 0.993] | 0.025 [0.018, 0.031] | +0.026 | +0.028 |
| knowledge gap, four 0–1 tasks only (no FRQ), pre + post | 34 | 0.986 [0.974, 0.993] | 0.977 [0.926, 0.991] | 0.022 [0.017, 0.028] | +0.096 | +0.097 |
| knowledge gap, four 0–1 tasks only (no FRQ), post only | 18 | 0.971 [0.937, 0.988] | 0.975 [0.874, 0.998] | 0.028 [0.021, 0.035] | +0.025 | +0.023 |
| knowledge gap, FRQ cells only (0–10 units), pre + post | 9 | 0.993 [0.977, 0.999] | 0.967 [0.737, 1.000] | 0.100 [0.065, 0.136] | +0.634 | +0.731 |
| knowledge gap, FRQ cells only (0–10 units), post only | 5 | 0.966 [0.938, 1.000] | 0.900 [0.111, 1.000] | 0.132 [0.097, 0.169] | +0.306 | +0.438 |
| forecasting gap (WS − WS+Cutoff), pre + post | 43 | 0.870 [0.657, 0.960] | 0.681 [0.395, 0.875] | 0.039 [0.026, 0.054] | +0.071 | +0.068 |
| forecasting gap (WS − WS+Cutoff), post only | 23 | 0.873 [0.651, 0.972] | 0.844 [0.594, 0.963] | 0.050 [0.031, 0.074] | +0.122 | +0.118 |
| forecasting gap, four 0–1 tasks only (no FRQ), pre + post | 34 | 0.868 [0.655, 0.959] | 0.663 [0.329, 0.876] | 0.046 [0.030, 0.063] | +0.083 | +0.076 |
| forecasting gap, four 0–1 tasks only (no FRQ), post only | 18 | 0.868 [0.662, 0.971] | 0.880 [0.651, 0.985] | 0.059 [0.035, 0.089] | +0.142 | +0.133 |
| forecasting gap, FRQ cells only (0–10 units), pre + post | 9 | 0.895 [0.698, 0.995] | 0.967 [0.737, 1.000] | 0.144 [0.077, 0.232] | +0.247 | +0.372 |
| forecasting gap, FRQ cells only (0–10 units), post only | 5 | 0.671 [0.138, 1.000] | 0.900 [0.111, 1.000] | 0.173 [0.100, 0.306] | +0.470 | +0.643 |
| forecasting gap, excluding GPT-4o (native-tool WS run), pre + post | 38 | 0.911 [0.692, 0.972] | 0.673 [0.367, 0.876] | 0.032 [0.022, 0.044] | +0.053 | +0.061 |
| forecasting gap, excluding GPT-4o (native-tool WS run), post only | 18 | 0.953 [0.830, 0.986] | 0.889 [0.676, 0.977] | 0.039 [0.024, 0.055] | +0.098 | +0.117 |

Item level: same event, same model, same condition, original run vs fixed-packet run. Binary/MCQ scores are 0/1, so agreement and Cohen's κ are reported; date (0–1) and FRQ (0–10) scores are continuous, so Pearson r (agreement = exact equality). Pooled rows combine every model with that condition.

| model | partition | task | n (WS+Cutoff / WS if different) | WS+Cutoff: agreement | WS+Cutoff: κ / r | WS: agreement | WS: κ / r |
|---|---|---|---|---|---|---|---|
| GPT-4o | post | Binary | 291 | 0.739 | κ=0.477 | 0.759 | κ=0.112 |
| GPT-4o | post | Binary (pert.) | 388 | 0.768 | κ=0.507 | 0.624 | κ=0.263 |
| GPT-4o | post | MCQ | 426 | 0.777 | κ=0.532 | 0.810 | κ=0.243 |
| GPT-4o | post | FRQ (0-10) | 414 | 0.097 | r=0.384 | 0.072 | r=0.093 |
| GPT-4o | post | Date (0-1) | 291 | 0.354 | r=0.596 | 0.124 | r=-0.010 |
| GPT-5.4 | post | Binary | 58 | 0.879 | κ=0.562 | 0.948 | κ=-0.024 |
| GPT-5.4 | post | Binary (pert.) | 99 | 0.828 | κ=0.582 | 0.697 | κ=0.309 |
| GPT-5.4 | post | MCQ | 104 | 0.837 | κ=0.546 | 0.875 | κ=0.249 |
| GPT-5.4 | post | FRQ (0-10) | 103 | 0.107 | r=0.456 | 0.087 | r=0.281 |
| GPT-5.4 | post | Date (0-1) | 58 | 0.224 | r=0.495 | 0.379 | r=0.331 |
| GPT-5.4 | pre | Binary | 237 | 0.907 | κ=0.371 | 0.911 | κ=0.048 |
| GPT-5.4 | pre | Binary (pert.) | 294 | 0.782 | κ=0.548 | 0.680 | κ=0.332 |
| GPT-5.4 | pre | MCQ | 330 | 0.933 | κ=0.415 | 0.927 | κ=0.165 |
| GPT-5.4 | pre | FRQ (0-10) | 317 | 0.101 | r=0.454 | 0.107 | r=0.236 |
| GPT-5.4 | pre | Date (0-1) | 237 | 0.464 | r=0.503 | 0.397 | r=0.166 |
| LLaMA 3.3 70B | post | Binary | 294 | 0.871 | κ=0.426 | 0.912 | κ=0.195 |
| LLaMA 3.3 70B | post | Binary (pert.) | 392 | 0.821 | κ=0.405 | 0.895 | κ=0.664 |
| LLaMA 3.3 70B | post | MCQ | 430 | 0.816 | κ=0.629 | 0.835 | κ=0.468 |
| LLaMA 3.3 70B | post | FRQ (0-10) | 420 | 0.136 | r=0.361 | 0.129 | r=0.433 |
| LLaMA 3.3 70B | post | Date (0-1) | 294 | 0.463 | r=0.511 | 0.289 | r=0.421 |
| Claude S4.5 | post | Binary | 130 | 0.762 | κ=0.477 | 0.808 | κ=0.425 |
| Claude S4.5 | post | Binary (pert.) | 186 | 0.860 | κ=0.625 | 0.817 | κ=0.606 |
| Claude S4.5 | post | MCQ | 185 | 0.805 | κ=0.529 | 0.822 | κ=0.369 |
| Claude S4.5 | post | FRQ (0-10) | 196 | 0.173 | r=0.432 | 0.133 | r=0.322 |
| Claude S4.5 | post | Date (0-1) | 128 | 0.273 | r=0.377 | 0.258 | r=0.261 |
| Claude S4.5 | pre | Binary | 129 | 0.829 | κ=0.576 | 0.822 | κ=0.483 |
| Claude S4.5 | pre | Binary (pert.) | 137 | 0.854 | κ=0.673 | 0.818 | κ=0.589 |
| Claude S4.5 | pre | MCQ | 152 | 0.730 | κ=0.115 | 0.743 | κ=0.201 |
| Claude S4.5 | pre | FRQ (0-10) | 142 | 0.148 | r=0.471 | 0.183 | r=0.539 |
| Claude S4.5 | pre | Date (0-1) | 129 | 0.434 | r=0.418 | 0.326 | r=0.251 |
| Claude Sonnet 5 | post | Binary (pert.) | 24 | 0.792 | κ=0.545 | 0.958 | κ=0.915 |
| Claude Sonnet 5 | post | MCQ | 24 | 0.958 | κ=0.833 | 0.958 | κ=0.778 |
| Claude Sonnet 5 | post | FRQ (0-10) | 25 | 0.040 | r=0.233 | 0.040 | r=0.512 |
| Claude Sonnet 5 | pre | Binary | 266 | 0.831 | κ=0.524 | 0.838 | κ=0.524 |
| Claude Sonnet 5 | pre | Binary (pert.) | 349 | 0.842 | κ=0.654 | 0.840 | κ=0.637 |
| Claude Sonnet 5 | pre | MCQ | 371 | 0.951 | κ=0.501 | 0.962 | κ=0.480 |
| Claude Sonnet 5 | pre | FRQ (0-10) | 381 | 0.118 | r=0.534 | 0.108 | r=0.479 |
| Claude Sonnet 5 | pre | Date (0-1) | 268 | 0.530 | r=0.602 | 0.556 | r=0.597 |
| GPT-5.6 Sol | pre | Binary | 294 | 0.908 | κ=0.476 | 0.929 | κ=0.533 |
| GPT-5.6 Sol | pre | Binary (pert.) | 388 | 0.807 | κ=0.613 | 0.809 | κ=0.619 |
| GPT-5.6 Sol | pre | MCQ | 423 | 0.953 | κ=0.575 | 0.957 | κ=0.505 |
| GPT-5.6 Sol | pre | FRQ (0-10) | 407 | 0.113 | r=0.400 | 0.128 | r=0.480 |
| GPT-5.6 Sol | pre | Date (0-1) | 295 | 0.624 | r=0.652 | 0.624 | r=0.576 |
| pooled (all models) | post | Binary | 788 | 0.801 | κ=0.571 | 0.840 | κ=0.240 |
| pooled (all models) | post | Binary (pert.) | 1093 | 0.809 | κ=0.615 | 0.769 | κ=0.533 |
| pooled (all models) | post | MCQ | 1172 | 0.805 | κ=0.585 | 0.830 | κ=0.371 |
| pooled (all models) | post | FRQ (0-10) | 1161 | 0.123 | r=0.511 | 0.103 | r=0.321 |
| pooled (all models) | post | Date (0-1) | 786 | 0.370 | r=0.552 | 0.230 | r=0.207 |
| pooled (all models) | pre | Binary | 926 | 0.875 | κ=0.526 | 0.883 | κ=0.490 |
| pooled (all models) | pre | Binary (pert.) | 1168 | 0.817 | κ=0.632 | 0.787 | κ=0.571 |
| pooled (all models) | pre | MCQ | 1276 | 0.921 | κ=0.411 | 0.926 | κ=0.355 |
| pooled (all models) | pre | FRQ (0-10) | 1247 | 0.115 | r=0.560 | 0.123 | r=0.508 |
| pooled (all models) | pre | Date (0-1) | 929 | 0.530 | r=0.575 | 0.505 | r=0.433 |
| pooled (all models) | pre + post | Binary | 1714 | 0.841 | κ=0.579 | 0.863 | κ=0.381 |
| pooled (all models) | pre + post | Binary (pert.) | 2261 | 0.813 | κ=0.626 | 0.778 | κ=0.556 |
| pooled (all models) | pre + post | MCQ | 2448 | 0.866 | κ=0.604 | 0.880 | κ=0.382 |
| pooled (all models) | pre + post | FRQ (0-10) | 2408 | 0.119 | r=0.736 | 0.113 | r=0.541 |
| pooled (all models) | pre + post | Date (0-1) | 1715 | 0.457 | r=0.654 | 0.379 | r=0.366 |

Containment: fixed-setup gap inside the original gap's paired 95% CI.

- knowledge gap: 38 of 43 cells inside; outside: GPT-4o post MCQ (+0.045 → +0.094); GPT-4o post FRQ (0-10) (+0.434 → +0.634); LLaMA 3.3 70B post MCQ (+0.044 → +0.093); LLaMA 3.3 70B post FRQ (0-10) (+0.458 → +0.599); Claude S4.5 post FRQ (0-10) (+0.102 → +0.247)
- forecasting gap: 31 of 43 cells inside; outside: GPT-4o post Binary (pert.) (+0.106 → -0.137); GPT-4o post MCQ (+0.286 → +0.197); GPT-4o post Date (0-1) (+0.235 → +0.132); GPT-5.4 pre Binary (pert.) (-0.061 → +0.020); GPT-5.4 pre MCQ (+0.030 → +0.000); GPT-5.4 pre FRQ (0-10) (-0.294 → -0.019); GPT-5.4 post FRQ (0-10) (+0.187 → +0.624); LLaMA 3.3 70B post Date (0-1) (+0.062 → +0.105); Claude S4.5 pre Date (0-1) (+0.083 → -0.072); Claude S4.5 post Date (0-1) (+0.118 → +0.235); Claude Sonnet 5 post MCQ (+0.000 → +0.083); GPT-5.6 Sol pre Binary (-0.007 → +0.034)
