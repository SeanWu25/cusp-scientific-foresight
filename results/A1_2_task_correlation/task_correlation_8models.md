# A1.2 — relationships among the four CUSP tasks (8models)

Panel: 8 models — GPT-4o, LLaMA 3.3 70B, GPT-OSS 20B, DeepSeek-R1, Claude S4.5, GPT-5.4, Claude Sonnet 5, GPT-5.6 Sol. Entire dataset (original + extension; DeepSeek-R1 original only).

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

## Model-level Pearson correlation (n = 8 models)

Cell: r [Fisher-z 95% CI over models] {event-bootstrap 95% CI}. With n = 9 the Fisher CIs are wide by construction.

| | Binary (feasibility) | MCQ (mechanism) | FRQ (solution) | Date |
|---|---|---|---|---|
| **Binary (feasibility)** | 1 | 0.73 [+0.04, +0.95] {+0.68, +0.77} | 0.68 [-0.05, +0.94] {+0.62, +0.73} | 0.52 [-0.29, +0.90] {+0.45, +0.57} |
| **MCQ (mechanism)** | 0.73 [+0.04, +0.95] {+0.68, +0.77} | 1 | 0.86 [+0.39, +0.97] {+0.84, +0.87} | -0.02 [-0.71, +0.70] {-0.07, +0.03} |
| **FRQ (solution)** | 0.68 [-0.05, +0.94] {+0.62, +0.73} | 0.86 [+0.39, +0.97] {+0.84, +0.87} | 1 | 0.01 [-0.70, +0.71] {-0.03, +0.06} |
| **Date** | 0.52 [-0.29, +0.90] {+0.45, +0.57} | -0.02 [-0.71, +0.70] {-0.07, +0.03} | 0.01 [-0.70, +0.71] {-0.03, +0.06} | 1 |

## Model-level Spearman correlation (n = 8 models)

Cell: r [Fisher-z 95% CI over models] {event-bootstrap 95% CI}. With n = 9 the Fisher CIs are wide by construction.

| | Binary (feasibility) | MCQ (mechanism) | FRQ (solution) | Date |
|---|---|---|---|---|
| **Binary (feasibility)** | 1 | 0.74 [+0.07, +0.95] {+0.55, +0.74} | 0.71 [+0.02, +0.94] {+0.48, +0.79} | 0.43 [-0.40, +0.87] {+0.36, +0.69} |
| **MCQ (mechanism)** | 0.74 [+0.07, +0.95] {+0.55, +0.74} | 1 | 0.81 [+0.24, +0.96] {+0.81, +0.81} | 0.00 [-0.70, +0.70] {+0.00, +0.05} |
| **FRQ (solution)** | 0.71 [+0.02, +0.94] {+0.48, +0.79} | 0.81 [+0.24, +0.96] {+0.81, +0.81} | 1 | 0.05 [-0.68, +0.73] {+0.05, +0.14} |
| **Date** | 0.43 [-0.40, +0.87] {+0.36, +0.69} | 0.00 [-0.70, +0.70] {+0.00, +0.05} | 0.05 [-0.68, +0.73] {+0.05, +0.14} | 1 |

## Sensitivity: binary metric choice (model-level Pearson with the other three tasks)

| binary metric | vs MCQ | vs FRQ | vs Date |
|---|---|---|---|
| balanced accuracy (primary) | +0.73 | +0.68 | +0.52 |
| MCC | +0.69 | +0.66 | +0.55 |
| raw merged accuracy (NOT recommended) | +0.65 | +0.39 | -0.15 |

## Item-level: within each model, across events (does success on one task predict success on another for the same paper?)

Spearman ρ per model; table shows median across models, range, and the pooled within-model (demeaned) Pearson r with its n.

| pair | median ρ | min | max | models | pooled within-model r | pooled n |
|---|---|---|---|---|---|---|
| Binary (feasibility) × MCQ (mechanism) | -0.000 | -0.024 | +0.051 | 8 | +0.005 | 31,924 |
| Binary (feasibility) × FRQ (solution) | +0.006 | -0.002 | +0.059 | 8 | +0.018 | 32,767 |
| Binary (feasibility) × Date | +0.099 | -0.004 | +0.146 | 8 | +0.080 | 23,098 |
| MCQ (mechanism) × FRQ (solution) | +0.061 | +0.028 | +0.136 | 8 | +0.063 | 30,578 |
| MCQ (mechanism) × Date | +0.036 | -0.011 | +0.097 | 8 | +0.030 | 19,815 |
| FRQ (solution) × Date | +0.095 | +0.016 | +0.148 | 8 | +0.090 | 19,685 |
