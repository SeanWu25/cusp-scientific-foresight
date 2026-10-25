# Pre- vs post-cutoff performance on the entire dataset

Original + extension, 5,575 events (DeepSeek-R1: original only, 4,760). Partition rule: `gap` — an event published in the cutoff month counts as PRE. GPT-4o and LLaMA 3.3 have cutoffs before the corpus starts, so they have no pre-cutoff rows. Models excluded: DeepSeek-V4-Pro.

Binary is **balanced accuracy** (mean of recall on the real question and specificity on the perturbed twin): raw merged accuracy is confounded by class balance × response bias, and its pre/post ratio would mislead. FRQ is the published-rubric mean; every model is graded. Refusals excluded. Ratio = post / pre (the retrospective ceiling); a ratio near 1 means the task does not distinguish seen from unseen material.


## Binary (balanced accuracy, bias-corrected)

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 0.472 [0.458, 0.485] n=7,253 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 0.511 [0.502, 0.519] n=7,204 | — | — |
| GPT-OSS 20B | 2024-06 | 0.479 [0.450, 0.508] n=1,217 | 0.470 [0.455, 0.485] n=6,038 | -0.009 | 0.982 |
| DeepSeek-R1 | 2024-07 | 0.489 [0.454, 0.524] n=1,461 | 0.482 [0.462, 0.502] n=4,886 | -0.007 | 0.985 |
| Claude S4.5 | 2025-01 | 0.488 [0.463, 0.512] n=2,806 | 0.469 [0.450, 0.489] n=3,980 | -0.018 | 0.962 |
| GPT-5.4 | 2025-08 | 0.519 [0.500, 0.538] n=4,862 | 0.502 [0.473, 0.530] n=2,394 | -0.017 | 0.967 |
| Claude Sonnet 5 | 2026-01 | 0.560 [0.542, 0.578] n=5,886 | 0.530 [0.490, 0.570] n=1,148 | -0.030 | 0.946 |
| GPT-5.6 Sol | 2026-02 | 0.605 [0.591, 0.618] n=6,350 | 0.560 [0.511, 0.606] n=903 | -0.045 | 0.926 |
| Claude Opus 4.8 | 2026-01 | 0.561 [0.543, 0.579] n=5,853 | 0.498 [0.462, 0.537] n=1,140 | -0.062 | 0.889 |

## MCQ accuracy

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 0.521 [0.507, 0.535] n=4,732 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 0.435 [0.421, 0.449] n=4,693 | — | — |
| GPT-OSS 20B | 2024-06 | 0.478 [0.442, 0.514] n=745 | 0.476 [0.461, 0.492] n=3,988 | -0.001 | 0.997 |
| DeepSeek-R1 | 2024-07 | 0.623 [0.589, 0.656] n=780 | 0.586 [0.568, 0.604] n=2,818 | -0.037 | 0.941 |
| Claude S4.5 | 2025-01 | 0.748 [0.727, 0.768] n=1,725 | 0.714 [0.696, 0.731] n=2,605 | -0.034 | 0.955 |
| GPT-5.4 | 2025-08 | 0.828 [0.814, 0.841] n=3,113 | 0.817 [0.797, 0.835] n=1,621 | -0.011 | 0.987 |
| Claude Sonnet 5 | 2026-01 | 0.910 [0.901, 0.919] n=3,583 | 0.905 [0.882, 0.924] n=767 | -0.006 | 0.994 |
| GPT-5.6 Sol | 2026-02 | 0.878 [0.868, 0.888] n=4,071 | 0.866 [0.837, 0.890] n=635 | -0.012 | 0.986 |
| Claude Opus 4.8 | 2026-01 | 0.935 [0.927, 0.943] n=3,531 | 0.928 [0.908, 0.944] n=767 | -0.007 | 0.993 |

## FRQ mean score (0–10, published rubric)

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 3.28 [3.25, 3.31] n=4,758 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 3.48 [3.46, 3.50] n=4,723 | — | — |
| GPT-OSS 20B | 2024-06 | 3.86 [3.80, 3.93] n=731 | 3.86 [3.83, 3.89] n=4,020 | -0.00 | 0.999 |
| DeepSeek-R1 | 2024-07 | 4.15 [4.09, 4.20] n=869 | 4.19 [4.16, 4.22] n=3,231 | +0.04 | 1.010 |
| Claude S4.5 | 2025-01 | 3.96 [3.92, 4.01] n=1,723 | 4.01 [3.98, 4.05] n=2,743 | +0.05 | 1.013 |
| GPT-5.4 | 2025-08 | 5.03 [5.01, 5.06] n=3,107 | 4.96 [4.92, 5.00] n=1,649 | -0.07 | 0.986 |
| Claude Sonnet 5 | 2026-01 | 4.54 [4.51, 4.57] n=3,813 | 4.47 [4.41, 4.53] n=831 | -0.07 | 0.985 |
| GPT-5.6 Sol | 2026-02 | 4.97 [4.94, 5.00] n=4,035 | 4.86 [4.80, 4.93] n=660 | -0.11 | 0.978 |
| Claude Opus 4.8 | 2026-01 | 4.80 [4.77, 4.83] n=3,816 | 4.63 [4.57, 4.68] n=836 | -0.17 | 0.964 |

## Date score

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 0.199 [0.190, 0.209] n=2,950 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 0.485 [0.476, 0.495] n=2,930 | — | — |
| GPT-OSS 20B | 2024-06 | 0.139 [0.128, 0.150] n=602 | 0.346 [0.333, 0.359] n=2,349 | +0.207 | 2.490 |
| DeepSeek-R1 | 2024-07 | 0.155 [0.143, 0.168] n=724 | 0.336 [0.323, 0.349] n=2,018 | +0.180 | 2.159 |
| Claude S4.5 | 2025-01 | 0.201 [0.185, 0.216] n=1,287 | 0.281 [0.267, 0.295] n=1,503 | +0.080 | 1.399 |
| GPT-5.4 | 2025-08 | 0.235 [0.222, 0.247] n=2,142 | 0.238 [0.218, 0.257] n=809 | +0.003 | 1.013 |
| Claude Sonnet 5 | 2026-01 | 0.430 [0.418, 0.442] n=2,524 | 0.277 [0.246, 0.308] n=317 | -0.153 | 0.645 |
| GPT-5.6 Sol | 2026-02 | 0.370 [0.356, 0.385] n=2,736 | 0.233 [0.211, 0.256] n=215 | -0.137 | 0.630 |
| Claude Opus 4.8 | 2026-01 | 0.483 [0.470, 0.496] n=2,503 | 0.245 [0.219, 0.271] n=316 | -0.238 | 0.507 |

CIs: Wilson for proportions (balanced-accuracy CI is the mean of the two Wilson halves, conservative), normal approximation for means. Pre-cutoff rows are retrospective: the model may have seen the paper in training.

