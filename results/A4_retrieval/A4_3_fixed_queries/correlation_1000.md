# A4.3 — agreement between the fixed-evidence-packet runs and the original manuscript's retrieval runs

Cell level: one point per model × task × partition (pre/post) with n ≥ 20. FRQ cells are rescaled from 0–10 to 0–1 before pooling so all tasks share a unit scale. Pearson r and Spearman ρ with 10,000 cell-bootstrap 95% CIs; MAD = mean absolute difference between setups, with the same cell-bootstrap 95% CI.

| quantity | cells | Pearson r [CI] | Spearman ρ [CI] | MAD [CI] | mean orig | mean fixed |
|---|---|---|---|---|---|---|
| WS+Cutoff accuracy/score (condition mean), pre + post | 50 | 0.996 [0.993, 0.998] | 0.992 [0.975, 0.997] | 0.015 [0.012, 0.019] | +0.596 | +0.599 |
| WS+Cutoff accuracy/score (condition mean), post only | 30 | 0.995 [0.990, 0.998] | 0.986 [0.945, 0.997] | 0.016 [0.011, 0.020] | +0.521 | +0.523 |
| WS accuracy/score (condition mean), pre + post | 50 | 0.955 [0.906, 0.988] | 0.941 [0.864, 0.977] | 0.037 [0.025, 0.052] | +0.696 | +0.689 |
| WS accuracy/score (condition mean), post only | 30 | 0.949 [0.874, 0.993] | 0.918 [0.762, 0.980] | 0.043 [0.025, 0.065] | +0.680 | +0.666 |
| WS+Cutoff score, FRQ cells only (0–10 units), pre + post | 10 | 0.997 [0.993, 0.999] | 1.000 [1.000, 1.000] | 0.081 [0.055, 0.111] | +4.984 | +5.037 |
| WS+Cutoff score, FRQ cells only (0–10 units), post only | 6 | 0.997 [0.990, 1.000] | 1.000 [1.000, 1.000] | 0.095 [0.063, 0.136] | +4.510 | +4.563 |
| WS score, FRQ cells only (0–10 units), pre + post | 10 | 0.969 [0.909, 0.996] | 0.891 [0.450, 1.000] | 0.184 [0.105, 0.271] | +5.307 | +5.462 |
| WS score, FRQ cells only (0–10 units), post only | 6 | 0.965 [0.876, 1.000] | 0.829 [0.000, 1.000] | 0.218 [0.136, 0.326] | +5.069 | +5.248 |
| knowledge gap (WS+Cutoff − base), pre + post | 50 | 0.988 [0.976, 0.994] | 0.970 [0.923, 0.987] | 0.015 [0.012, 0.019] | +0.083 | +0.087 |
| knowledge gap (WS+Cutoff − base), post only | 30 | 0.970 [0.922, 0.989] | 0.956 [0.869, 0.983] | 0.016 [0.011, 0.020] | +0.031 | +0.033 |
| knowledge gap, four 0–1 tasks only (no FRQ), pre + post | 40 | 0.988 [0.976, 0.994] | 0.969 [0.914, 0.988] | 0.017 [0.013, 0.021] | +0.089 | +0.091 |
| knowledge gap, four 0–1 tasks only (no FRQ), post only | 24 | 0.971 [0.925, 0.990] | 0.950 [0.836, 0.983] | 0.017 [0.012, 0.023] | +0.031 | +0.032 |
| knowledge gap, FRQ cells only (0–10 units), pre + post | 10 | 0.981 [0.904, 0.997] | 0.842 [0.337, 1.000] | 0.081 [0.055, 0.111] | +0.617 | +0.671 |
| knowledge gap, FRQ cells only (0–10 units), post only | 6 | 0.561 [-0.844, 0.960] | 0.314 [-1.000, 1.000] | 0.095 [0.063, 0.136] | +0.333 | +0.387 |
| forecasting gap (WS − WS+Cutoff), pre + post | 50 | 0.906 [0.788, 0.969] | 0.825 [0.628, 0.947] | 0.037 [0.024, 0.053] | +0.100 | +0.090 |
| forecasting gap (WS − WS+Cutoff), post only | 30 | 0.901 [0.773, 0.976] | 0.916 [0.756, 0.986] | 0.044 [0.025, 0.066] | +0.159 | +0.143 |
| forecasting gap, four 0–1 tasks only (no FRQ), pre + post | 40 | 0.904 [0.792, 0.969] | 0.821 [0.609, 0.941] | 0.043 [0.027, 0.061] | +0.117 | +0.101 |
| forecasting gap, four 0–1 tasks only (no FRQ), post only | 24 | 0.896 [0.773, 0.975] | 0.910 [0.735, 0.982] | 0.051 [0.029, 0.079] | +0.184 | +0.161 |
| forecasting gap, FRQ cells only (0–10 units), pre + post | 10 | 0.890 [0.673, 0.990] | 0.964 [0.779, 1.000] | 0.125 [0.051, 0.225] | +0.323 | +0.424 |
| forecasting gap, FRQ cells only (0–10 units), post only | 6 | 0.684 [0.198, 1.000] | 0.886 [0.200, 1.000] | 0.136 [0.038, 0.290] | +0.559 | +0.685 |
| forecasting gap, excluding GPT-4o (native-tool WS run), pre + post | 45 | 0.952 [0.892, 0.982] | 0.853 [0.666, 0.953] | 0.028 [0.019, 0.038] | +0.085 | +0.086 |
| forecasting gap, excluding GPT-4o (native-tool WS run), post only | 25 | 0.969 [0.946, 0.991] | 0.974 [0.899, 0.995] | 0.030 [0.019, 0.043] | +0.143 | +0.146 |

Item level: same event, same model, same condition, original run vs fixed-packet run. Binary/MCQ scores are 0/1, so agreement and Cohen's κ are reported; date (0–1) and FRQ (0–10) scores are continuous, so Pearson r (agreement = exact equality). Pooled rows combine every model with that condition.

| model | partition | task | n (WS+Cutoff / WS if different) | WS+Cutoff: agreement | WS+Cutoff: κ / r | WS: agreement | WS: κ / r |
|---|---|---|---|---|---|---|---|
| GPT-4o | post | Binary | 421 | 0.751 | κ=0.501 | 0.789 | κ=0.153 |
| GPT-4o | post | Binary (pert.) | 789 | 0.772 | κ=0.533 | 0.598 | κ=0.233 |
| GPT-4o | post | MCQ | 805 | 0.789 | κ=0.573 | 0.801 | κ=0.220 |
| GPT-4o | post | FRQ (0-10) | 799 | 0.105 | r=0.375 | 0.070 | r=0.106 |
| GPT-4o | post | Date (0-1) | 421 | 0.321 | r=0.497 | 0.143 | r=-0.009 |
| GPT-5.4 | post | Binary | 188 | 0.883 | κ=0.630 | 0.947 | κ=-0.010 |
| GPT-5.4 | post | Binary (pert.) | 500 | 0.830 | κ=0.583 | 0.738 | κ=0.344 |
| GPT-5.4 | post | MCQ | 483 | 0.876 | κ=0.632 | 0.903 | κ=0.131 |
| GPT-5.4 | post | FRQ (0-10) | 484 | 0.140 | r=0.457 | 0.110 | r=0.268 |
| GPT-5.4 | post | Date (0-1) | 188 | 0.207 | r=0.488 | 0.404 | r=0.179 |
| GPT-5.4 | pre | Binary | 237 | 0.907 | κ=0.371 | 0.911 | κ=0.048 |
| GPT-5.4 | pre | Binary (pert.) | 294 | 0.782 | κ=0.548 | 0.680 | κ=0.332 |
| GPT-5.4 | pre | MCQ | 330 | 0.933 | κ=0.415 | 0.927 | κ=0.165 |
| GPT-5.4 | pre | FRQ (0-10) | 317 | 0.101 | r=0.454 | 0.107 | r=0.236 |
| GPT-5.4 | pre | Date (0-1) | 237 | 0.464 | r=0.503 | 0.397 | r=0.166 |
| LLaMA 3.3 70B | post | Binary | 424 | 0.877 | κ=0.389 | 0.917 | κ=0.148 |
| LLaMA 3.3 70B | post | Binary (pert.) | 793 | 0.830 | κ=0.465 | 0.874 | κ=0.605 |
| LLaMA 3.3 70B | post | MCQ | 809 | 0.828 | κ=0.656 | 0.838 | κ=0.501 |
| LLaMA 3.3 70B | post | FRQ (0-10) | 805 | 0.140 | r=0.401 | 0.132 | r=0.466 |
| LLaMA 3.3 70B | post | Date (0-1) | 424 | 0.441 | r=0.605 | 0.295 | r=0.489 |
| Claude S4.5 | post | Binary | 247 | 0.761 | κ=0.488 | 0.830 | κ=0.409 |
| Claude S4.5 | post | Binary (pert.) | 509 | 0.841 | κ=0.619 | 0.806 | κ=0.605 |
| Claude S4.5 | post | MCQ | 475 | 0.789 | κ=0.474 | 0.834 | κ=0.343 |
| Claude S4.5 | post | FRQ (0-10) | 539 | 0.141 | r=0.370 | 0.111 | r=0.292 |
| Claude S4.5 | post | Date (0-1) | 244 | 0.270 | r=0.348 | 0.316 | r=0.318 |
| Claude S4.5 | pre | Binary | 129 | 0.829 | κ=0.576 | 0.822 | κ=0.483 |
| Claude S4.5 | pre | Binary (pert.) | 137 | 0.854 | κ=0.673 | 0.818 | κ=0.589 |
| Claude S4.5 | pre | MCQ | 152 | 0.730 | κ=0.115 | 0.743 | κ=0.201 |
| Claude S4.5 | pre | FRQ (0-10) | 142 | 0.148 | r=0.471 | 0.183 | r=0.539 |
| Claude S4.5 | pre | Date (0-1) | 129 | 0.434 | r=0.418 | 0.326 | r=0.251 |
| Claude Sonnet 5 | post | Binary | 143 | 0.804 | κ=0.606 | 0.874 | κ=0.399 |
| Claude Sonnet 5 | post | Binary (pert.) | 399 | 0.865 | κ=0.690 | 0.855 | κ=0.698 |
| Claude Sonnet 5 | post | MCQ | 367 | 0.935 | κ=0.696 | 0.937 | κ=0.347 |
| Claude Sonnet 5 | post | FRQ (0-10) | 396 | 0.106 | r=0.489 | 0.139 | r=0.501 |
| Claude Sonnet 5 | post | Date (0-1) | 143 | 0.287 | r=0.589 | 0.573 | r=0.700 |
| Claude Sonnet 5 | pre | Binary | 266 | 0.831 | κ=0.524 | 0.838 | κ=0.524 |
| Claude Sonnet 5 | pre | Binary (pert.) | 349 | 0.842 | κ=0.654 | 0.840 | κ=0.637 |
| Claude Sonnet 5 | pre | MCQ | 371 | 0.951 | κ=0.501 | 0.962 | κ=0.480 |
| Claude Sonnet 5 | pre | FRQ (0-10) | 381 | 0.118 | r=0.534 | 0.108 | r=0.479 |
| Claude Sonnet 5 | pre | Date (0-1) | 268 | 0.530 | r=0.602 | 0.556 | r=0.597 |
| GPT-5.6 Sol | post | Binary | 131 | 0.885 | κ=0.635 | 0.969 | κ=0.484 |
| GPT-5.6 Sol | post | Binary (pert.) | 403 | 0.787 | κ=0.550 | 0.789 | κ=0.578 |
| GPT-5.6 Sol | post | MCQ | 378 | 0.905 | κ=0.605 | 0.926 | κ=0.295 |
| GPT-5.6 Sol | post | FRQ (0-10) | 380 | 0.113 | r=0.513 | 0.113 | r=0.432 |
| GPT-5.6 Sol | post | Date (0-1) | 131 | 0.237 | r=0.463 | 0.573 | r=0.661 |
| GPT-5.6 Sol | pre | Binary | 294 | 0.908 | κ=0.476 | 0.929 | κ=0.533 |
| GPT-5.6 Sol | pre | Binary (pert.) | 388 | 0.807 | κ=0.613 | 0.809 | κ=0.619 |
| GPT-5.6 Sol | pre | MCQ | 423 | 0.953 | κ=0.575 | 0.957 | κ=0.505 |
| GPT-5.6 Sol | pre | FRQ (0-10) | 407 | 0.113 | r=0.400 | 0.128 | r=0.480 |
| GPT-5.6 Sol | pre | Date (0-1) | 295 | 0.624 | r=0.652 | 0.624 | r=0.576 |
| pooled (all models) | post | Binary | 1554 | 0.819 | κ=0.605 | 0.873 | κ=0.278 |
| pooled (all models) | post | Binary (pert.) | 3393 | 0.817 | κ=0.631 | 0.767 | κ=0.528 |
| pooled (all models) | post | MCQ | 3317 | 0.841 | κ=0.637 | 0.859 | κ=0.366 |
| pooled (all models) | post | FRQ (0-10) | 3403 | 0.125 | r=0.611 | 0.110 | r=0.458 |
| pooled (all models) | post | Date (0-1) | 1551 | 0.322 | r=0.515 | 0.319 | r=0.327 |
| pooled (all models) | pre | Binary | 926 | 0.875 | κ=0.526 | 0.883 | κ=0.490 |
| pooled (all models) | pre | Binary (pert.) | 1168 | 0.817 | κ=0.632 | 0.787 | κ=0.571 |
| pooled (all models) | pre | MCQ | 1276 | 0.921 | κ=0.411 | 0.926 | κ=0.355 |
| pooled (all models) | pre | FRQ (0-10) | 1247 | 0.115 | r=0.560 | 0.123 | r=0.508 |
| pooled (all models) | pre | Date (0-1) | 929 | 0.530 | r=0.575 | 0.505 | r=0.433 |
| pooled (all models) | pre + post | Binary | 2480 | 0.840 | κ=0.604 | 0.877 | κ=0.372 |
| pooled (all models) | pre + post | Binary (pert.) | 4561 | 0.817 | κ=0.633 | 0.772 | κ=0.542 |
| pooled (all models) | pre + post | MCQ | 4593 | 0.863 | κ=0.639 | 0.877 | κ=0.370 |
| pooled (all models) | pre + post | FRQ (0-10) | 4650 | 0.123 | r=0.714 | 0.113 | r=0.522 |
| pooled (all models) | pre + post | Date (0-1) | 2480 | 0.400 | r=0.663 | 0.389 | r=0.395 |

Containment: fixed-setup gap inside the original gap's paired 95% CI.

- knowledge gap: 47 of 50 cells inside; outside: GPT-4o post MCQ (+0.045 → +0.097); GPT-4o post FRQ (0-10) (+0.297 → +0.485); LLaMA 3.3 70B post FRQ (0-10) (+0.409 → +0.507)
- forecasting gap: 34 of 50 cells inside; outside: GPT-4o post Binary (pert.) (+0.151 → -0.127); GPT-4o post MCQ (+0.340 → +0.243); GPT-4o post Date (0-1) (+0.273 → +0.104); GPT-5.4 pre Binary (pert.) (-0.061 → +0.020); GPT-5.4 pre MCQ (+0.030 → +0.000); GPT-5.4 pre FRQ (0-10) (-0.294 → -0.019); GPT-5.4 post MCQ (+0.182 → +0.130); GPT-5.4 post FRQ (0-10) (+0.163 → +0.668); GPT-5.4 post Date (0-1) (+0.538 → +0.389); LLaMA 3.3 70B post FRQ (0-10) (+0.648 → +0.733); Claude S4.5 pre Date (0-1) (+0.083 → -0.072); Claude S4.5 post MCQ (+0.158 → +0.097); Claude S4.5 post FRQ (0-10) (+0.333 → +0.464); Claude S4.5 post Date (0-1) (+0.111 → +0.182); Claude Sonnet 5 post Binary (pert.) (-0.108 → -0.058); GPT-5.6 Sol pre Binary (-0.007 → +0.034)
