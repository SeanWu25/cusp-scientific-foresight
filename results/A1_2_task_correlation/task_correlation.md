# A1.2 — relationships among the four CUSP tasks

Panel: 10 models — GPT-4o, LLaMA 3.3 70B, GPT-OSS 20B, DeepSeek-R1, Claude S4.5, GPT-5.4, Claude Sonnet 5, GPT-5.6 Sol, DeepSeek-V4-Pro, Claude Opus 4.8. Entire dataset (original + extension; DeepSeek-R1 original only).

Binary = **balanced accuracy** (bias-corrected merged binary). FRQ = finalized **published-rubric** scores (judge_frq_combined, sha256 fc24e69d…), not the legacy archive. Refusals excluded from denominators.

## Model-level performance (inputs to the correlation)

| model | cutoff | binary bal. acc | MCC | MCQ acc | FRQ (0–10) | date score | n events |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.472 | -0.067 | 0.521 | 3.28 | 0.199 | 5,575 |
| LLaMA 3.3 70B | 2023-12 | 0.511 | +0.040 | 0.435 | 3.48 | 0.485 | 5,575 |
| GPT-OSS 20B | 2024-06 | 0.470 | -0.073 | 0.477 | 3.86 | 0.303 | 5,575 |
| DeepSeek-R1 | 2024-07 | 0.480 | -0.040 | 0.594 | 4.18 | 0.288 | 4,760 |
| Claude S4.5 | 2025-01 | 0.480 | -0.043 | 0.727 | 3.99 | 0.244 | 5,575 |
| GPT-5.4 | 2025-08 | 0.513 | +0.027 | 0.824 | 5.01 | 0.235 | 5,575 |
| Claude Sonnet 5 | 2026-01 | 0.562 | +0.125 | 0.909 | 4.53 | 0.413 | 5,575 |
| GPT-5.6 Sol | 2026-02 | 0.604 | +0.233 | 0.877 | 4.96 | 0.360 | 5,575 |
| DeepSeek-V4-Pro | 2026-04 | 0.486 | -0.042 | 0.668 | 3.97 | 0.201 | 5,575 |
| Claude Opus 4.8 | 2026-01 | 0.561 | +0.122 | 0.934 | 4.77 | 0.457 | 5,575 |

## Model-level Pearson correlation (n = 10 models)

Cell: r [Fisher-z 95% CI over models] {event-bootstrap 95% CI}. With n = 9 the Fisher CIs are wide by construction.

| | Binary (feasibility) | MCQ (mechanism) | FRQ (solution) | Date |
|---|---|---|---|---|
| **Binary (feasibility)** | 1 | 0.76 [+0.24, +0.94] {+0.71, +0.79} | 0.72 [+0.16, +0.93] {+0.67, +0.76} | 0.61 [-0.03, +0.90] {+0.56, +0.66} |
| **MCQ (mechanism)** | 0.76 [+0.24, +0.94] {+0.71, +0.79} | 1 | 0.87 [+0.53, +0.97] {+0.86, +0.88} | 0.20 [-0.49, +0.74] {+0.16, +0.24} |
| **FRQ (solution)** | 0.72 [+0.16, +0.93] {+0.67, +0.76} | 0.87 [+0.53, +0.97] {+0.86, +0.88} | 1 | 0.20 [-0.50, +0.73] {+0.16, +0.23} |
| **Date** | 0.61 [-0.03, +0.90] {+0.56, +0.66} | 0.20 [-0.49, +0.74] {+0.16, +0.24} | 0.20 [-0.50, +0.73] {+0.16, +0.23} | 1 |

## Model-level Spearman correlation (n = 10 models)

Cell: r [Fisher-z 95% CI over models] {event-bootstrap 95% CI}. With n = 9 the Fisher CIs are wide by construction.

| | Binary (feasibility) | MCQ (mechanism) | FRQ (solution) | Date |
|---|---|---|---|---|
| **Binary (feasibility)** | 1 | 0.76 [+0.24, +0.94] {+0.61, +0.77} | 0.72 [+0.17, +0.93] {+0.56, +0.78} | 0.50 [-0.19, +0.86] {+0.44, +0.70} |
| **MCQ (mechanism)** | 0.76 [+0.24, +0.94] {+0.61, +0.77} | 1 | 0.82 [+0.39, +0.96] {+0.81, +0.82} | 0.19 [-0.50, +0.73] {+0.16, +0.20} |
| **FRQ (solution)** | 0.72 [+0.17, +0.93] {+0.56, +0.78} | 0.82 [+0.39, +0.96] {+0.81, +0.82} | 1 | 0.19 [-0.50, +0.73] {+0.12, +0.25} |
| **Date** | 0.50 [-0.19, +0.86] {+0.44, +0.70} | 0.19 [-0.50, +0.73] {+0.16, +0.20} | 0.19 [-0.50, +0.73] {+0.12, +0.25} | 1 |

## Sensitivity: binary metric choice (model-level Pearson with the other three tasks)

| binary metric | vs MCQ | vs FRQ | vs Date |
|---|---|---|---|
| balanced accuracy (primary) | +0.76 | +0.72 | +0.61 |
| MCC | +0.72 | +0.70 | +0.63 |
| raw merged accuracy (NOT recommended) | +0.68 | +0.42 | -0.03 |

## Item-level: within each model, across events (does success on one task predict success on another for the same paper?)

Spearman ρ per model; table shows median across models, range, and the pooled within-model (demeaned) Pearson r with its n.

| pair | median ρ | min | max | models | pooled within-model r | pooled n |
|---|---|---|---|---|---|---|
| Binary (feasibility) × MCQ (mechanism) | -0.001 | -0.024 | +0.051 | 10 | +0.001 | 39,947 |
| Binary (feasibility) × FRQ (solution) | +0.006 | -0.002 | +0.063 | 10 | +0.018 | 41,071 |
| Binary (feasibility) × Date | +0.095 | -0.004 | +0.146 | 10 | +0.084 | 28,860 |
| MCQ (mechanism) × FRQ (solution) | +0.053 | +0.028 | +0.136 | 10 | +0.058 | 38,291 |
| MCQ (mechanism) × Date | +0.044 | -0.011 | +0.097 | 10 | +0.033 | 24,757 |
| FRQ (solution) × Date | +0.095 | +0.016 | +0.172 | 10 | +0.097 | 24,605 |
