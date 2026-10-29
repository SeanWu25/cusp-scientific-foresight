# Pre- vs post-cutoff performance on the entire dataset

Original + extension, 5,575 events (DeepSeek-R1: original only, 4,760). Partition rule: `main` — an event published in the cutoff month counts as POST. GPT-4o and LLaMA 3.3 have cutoffs before the corpus starts, so they have no pre-cutoff rows. DeepSeek-V4-Pro (cutoff 2026-04) is the inverse profile: under this rule its 4,760 original-corpus events are all pre-cutoff and the 815 extension events (April included) are post; §2 of RUN2_RESULTS.md reports it May–Aug only, and the April choice moves MCC by 0.003.

Binary is **balanced accuracy** (mean of recall on the real question and specificity on the perturbed twin): raw merged accuracy is confounded by class balance × response bias, and its pre/post ratio would mislead. FRQ is the published-rubric mean; every model is graded. Refusals excluded. Ratio = post / pre (the retrospective ceiling); a ratio near 1 means the task does not distinguish seen from unseen material.


## Binary (balanced accuracy, bias-corrected)

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 0.472 [0.458, 0.485] n=7,253 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 0.511 [0.502, 0.519] n=7,204 | — | — |
| GPT-OSS 20B | 2024-06 | 0.475 [0.442, 0.508] n=949 | 0.470 [0.456, 0.485] n=6,306 | -0.004 | 0.991 |
| DeepSeek-R1 | 2024-07 | 0.487 [0.449, 0.526] n=1,198 | 0.482 [0.462, 0.501] n=5,149 | -0.006 | 0.989 |
| Claude S4.5 | 2025-01 | 0.484 [0.458, 0.510] n=2,516 | 0.472 [0.453, 0.491] n=4,270 | -0.012 | 0.975 |
| GPT-5.4 | 2025-08 | 0.517 [0.497, 0.537] n=4,577 | 0.505 [0.478, 0.532] n=2,679 | -0.012 | 0.976 |
| Claude Sonnet 5 | 2026-01 | 0.560 [0.542, 0.579] n=5,647 | 0.527 [0.492, 0.563] n=1,387 | -0.033 | 0.940 |
| GPT-5.6 Sol | 2026-02 | 0.605 [0.591, 0.619] n=6,070 | 0.574 [0.534, 0.612] n=1,183 | -0.031 | 0.949 |
| DeepSeek-V4-Pro | 2026-04 | 0.489 [0.478, 0.500] n=6,411 | 0.465 [0.436, 0.501] n=845 | -0.024 | 0.951 |
| Claude Opus 4.8 | 2026-01 | 0.563 [0.545, 0.582] n=5,619 | 0.491 [0.459, 0.525] n=1,374 | -0.072 | 0.872 |

## MCQ accuracy

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 0.521 [0.507, 0.535] n=4,732 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 0.435 [0.421, 0.449] n=4,693 | — | — |
| GPT-OSS 20B | 2024-06 | 0.497 [0.456, 0.537] n=580 | 0.474 [0.459, 0.489] n=4,153 | -0.023 | 0.954 |
| DeepSeek-R1 | 2024-07 | 0.619 [0.581, 0.656] n=636 | 0.589 [0.571, 0.606] n=2,962 | -0.031 | 0.950 |
| Claude S4.5 | 2025-01 | 0.762 [0.740, 0.783] n=1,546 | 0.708 [0.691, 0.725] n=2,784 | -0.054 | 0.930 |
| GPT-5.4 | 2025-08 | 0.830 [0.816, 0.843] n=2,933 | 0.814 [0.795, 0.831] n=1,801 | -0.016 | 0.980 |
| Claude Sonnet 5 | 2026-01 | 0.912 [0.902, 0.921] n=3,420 | 0.900 [0.879, 0.918] n=930 | -0.012 | 0.987 |
| GPT-5.6 Sol | 2026-02 | 0.879 [0.869, 0.889] n=3,891 | 0.864 [0.839, 0.886] n=815 | -0.015 | 0.982 |
| DeepSeek-V4-Pro | 2026-04 | 0.668 [0.653, 0.682] n=4,128 | 0.665 [0.627, 0.701] n=606 | -0.003 | 0.996 |
| Claude Opus 4.8 | 2026-01 | 0.935 [0.927, 0.943] n=3,376 | 0.928 [0.910, 0.943] n=922 | -0.007 | 0.993 |

## FRQ mean score (0–10, published rubric)

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 3.28 [3.25, 3.31] n=4,758 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 3.48 [3.46, 3.50] n=4,723 | — | — |
| GPT-OSS 20B | 2024-06 | 3.88 [3.80, 3.96] n=569 | 3.86 [3.83, 3.88] n=4,182 | -0.03 | 0.993 |
| DeepSeek-R1 | 2024-07 | 4.17 [4.11, 4.23] n=724 | 4.18 [4.15, 4.21] n=3,376 | +0.01 | 1.003 |
| Claude S4.5 | 2025-01 | 3.95 [3.91, 4.00] n=1,557 | 4.01 [3.98, 4.05] n=2,909 | +0.06 | 1.015 |
| GPT-5.4 | 2025-08 | 5.04 [5.01, 5.07] n=2,914 | 4.96 [4.93, 5.00] n=1,842 | -0.07 | 0.985 |
| Claude Sonnet 5 | 2026-01 | 4.54 [4.51, 4.57] n=3,636 | 4.47 [4.42, 4.52] n=1,008 | -0.07 | 0.984 |
| GPT-5.6 Sol | 2026-02 | 4.97 [4.94, 5.00] n=3,859 | 4.88 [4.82, 4.94] n=836 | -0.09 | 0.981 |
| DeepSeek-V4-Pro | 2026-04 | 3.97 [3.94, 4.00] n=4,132 | 3.99 [3.92, 4.06] n=629 | +0.02 | 1.005 |
| Claude Opus 4.8 | 2026-01 | 4.80 [4.77, 4.83] n=3,639 | 4.64 [4.59, 4.69] n=1,013 | -0.16 | 0.966 |

## Date score

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 0.199 [0.190, 0.209] n=2,950 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 0.485 [0.476, 0.495] n=2,930 | — | — |
| GPT-OSS 20B | 2024-06 | 0.126 [0.115, 0.137] n=472 | 0.337 [0.325, 0.350] n=2,479 | +0.211 | 2.675 |
| DeepSeek-R1 | 2024-07 | 0.145 [0.133, 0.157] n=599 | 0.328 [0.316, 0.340] n=2,143 | +0.183 | 2.264 |
| Claude S4.5 | 2025-01 | 0.201 [0.185, 0.218] n=1,166 | 0.275 [0.261, 0.288] n=1,624 | +0.073 | 1.364 |
| GPT-5.4 | 2025-08 | 0.231 [0.218, 0.244] n=2,027 | 0.245 [0.227, 0.264] n=924 | +0.014 | 1.062 |
| Claude Sonnet 5 | 2026-01 | 0.434 [0.421, 0.446] n=2,431 | 0.288 [0.261, 0.315] n=410 | -0.146 | 0.664 |
| GPT-5.6 Sol | 2026-02 | 0.376 [0.361, 0.391] n=2,624 | 0.233 [0.214, 0.252] n=327 | -0.143 | 0.620 |
| DeepSeek-V4-Pro | 2026-04 | 0.191 [0.182, 0.200] n=2,755 | 0.346 [0.293, 0.399] n=196 | +0.155 | 1.813 |
| Claude Opus 4.8 | 2026-01 | 0.492 [0.479, 0.505] n=2,412 | 0.249 [0.226, 0.271] n=407 | -0.243 | 0.505 |

CIs: Wilson for proportions (balanced-accuracy CI is the mean of the two Wilson halves, conservative), normal approximation for means. Pre-cutoff rows are retrospective: the model may have seen the paper in training.

