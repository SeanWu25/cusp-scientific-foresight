# Response to Reviewer 2, Comment C1 — the four-task taxonomy (A1.2)

Supporting files in this directory: `task_correlation.md` (all tables, with CIs),
`task_correlation_{pearson,spearman}.csv`, `item_level_correlation.csv`,
`model_task_performance.csv` (the model × task inputs), `task_correlation_heatmap.{png,pdf}`,
`MANIFEST.json` (git SHA, report paths, which FRQ scores). `*_9models.*` and `*_8models.*` are robustness
runs without Claude Opus 4.8, and without Opus 4.8 and DeepSeek-V4-Pro. Reproduce with `compute_task_correlation.py`; no inference.

---

## 1. The reviewer's comment

> "The proposed four-part taxonomy also needs stronger justification. Feasibility,
> mechanism, solution, and date are reasonable dimensions, but they are not obviously
> complete or independent... The paper should present this framework as one
> operationalization rather than a complete decomposition of scientific forecasting, and
> ideally examine the relationships among the four tasks empirically."

## 2. Our response

We agree, and we will change the framing. The four tasks — binary feasibility, mechanism
(MCQ), solution (FRQ), and date — are one *operationalization* of scientific forecasting,
chosen because each maps to a question a scientist can be asked before a result is
published and each can be scored against the published record. We do not claim they are
complete, and nothing in our data could establish completeness. We will remove the
language of "decomposition" and present the framework as one realization among several
possible, with its choices motivated but not privileged.

On independence we can now say something empirical. We examined the relationships among
the four tasks at two levels on the full corpus (5,575 events, ten models: the six in the
paper plus Claude Sonnet 5, GPT-5.6 Sol, DeepSeek-V4-Pro and Claude Opus 4.8): across models, and within
each model across papers. The two levels answer different questions and give different
answers, and both are informative.

## 3. Empirical result

**Metrics.** Binary is reported as balanced accuracy (mean of recall on the real question
and specificity on the perturbed twin), because raw merged accuracy is dominated by class
balance interacting with response bias; using it would reverse the sign of the
binary–date correlation (see sensitivity below). FRQ scores are the published rubric's,
now graded for every model (`judge_frq_combined`, sha256 `fc24e69d…`), not the archived
legacy scores. Refusals are excluded from denominators, as in the published tables.

**Inputs — model-level performance on the entire dataset:**

| model | cutoff | binary bal. acc | MCQ acc | FRQ (0–10) | date score | n events |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.472 | 0.521 | 3.28 | 0.199 | 5,575 |
| LLaMA 3.3 70B | 2023-12 | 0.511 | 0.435 | 3.48 | 0.485 | 5,575 |
| GPT-OSS 20B | 2024-06 | 0.470 | 0.477 | 3.86 | 0.303 | 5,575 |
| DeepSeek-R1 | 2024-07 | 0.480 | 0.594 | 4.18 | 0.288 | 4,760 |
| Claude S4.5 | 2025-01 | 0.480 | 0.727 | 3.99 | 0.244 | 5,575 |
| GPT-5.4 | 2025-08 | 0.513 | 0.824 | 5.01 | 0.235 | 5,575 |
| Claude Sonnet 5 | 2026-01 | 0.562 | 0.909 | 4.53 | 0.413 | 5,575 |
| GPT-5.6 Sol | 2026-02 | 0.604 | 0.877 | 4.96 | 0.360 | 5,575 |
| DeepSeek-V4-Pro | 2026-04 | 0.486 | 0.668 | 3.97 | 0.201 | 5,575 |
| Claude Opus 4.8 | 2026-01 | 0.561 | 0.934 | 4.77 | 0.457 | 5,575 |

### 3a. Across models (n = 10): three tasks share a capability factor; date largely does not

Pearson r with Fisher-z 95% CI over models (Spearman in `task_correlation.md`, same
pattern):

| | Binary | MCQ | FRQ | Date |
|---|---|---|---|---|
| **Binary (feasibility)** | 1 | 0.76 [+0.24, +0.94] | 0.72 [+0.16, +0.93] | 0.61 [−0.03, +0.90] |
| **MCQ (mechanism)** | | 1 | **0.87 [+0.53, +0.97]** | **0.20 [−0.49, +0.74]** |
| **FRQ (solution)** | | | 1 | **0.20 [−0.50, +0.73]** |
| **Date** | | | | 1 |

Binary, MCQ and FRQ are positively correlated across models — most strongly MCQ–FRQ at
0.87 — which is the expected signature of a shared general-capability factor: newer,
stronger models are better at all three. **Date is different.** Its correlation with MCQ
(0.20) and FRQ (0.20) is weak and its CIs span zero widely, and with binary (0.61) the CI
still includes zero. (With nine models, before Claude Opus 4.8 was added, the MCQ–date and
FRQ–date correlations were −0.01 and 0.05; Opus 4.8 has an unusually good date score for a
recent model and pulls them to 0.20. The conclusion is unchanged; the nine-model matrix is
kept in `task_correlation_9models.md`.) Being a stronger model does not reliably make a model better at predicting *when*.
This is consistent with an independent finding in our revision: no model in the panel
beats a constant-month guess on the date task, on either corpus.

With ten models the Fisher CIs are wide by construction; an event-level bootstrap
(resampling papers within each model, 2,000 draws) gives much tighter intervals on the
same point estimates — e.g. MCQ–FRQ {+0.86, +0.88}, MCQ–date {+0.16, +0.24} — confirming
the pattern is not measurement noise in the aggregates, whatever one thinks of n = 10.

*Sensitivity.* Substituting MCC for balanced accuracy changes nothing material. Using
raw merged accuracy instead flips the binary–date sign negative — the response-bias
artefact, and the reason we report the bias-corrected metric. The nine-model
(without Opus 4.8) and eight-model (also without DeepSeek-V4-Pro) matrices are in the
`*_9models.*` and `*_8models.*` files; no conclusion changes across the three panels.

### 3b. Within models, across papers: the four tasks are near-independent

For each model, Spearman ρ between per-event outcomes on each pair of tasks, over every
paper carrying both (25,000–41,000 pairs pooled across models):

| pair | median ρ across models | range | pooled within-model r |
|---|---|---|---|
| Binary × MCQ | −0.00 | [−0.02, +0.05] | +0.00 |
| Binary × FRQ | +0.01 | [−0.00, +0.06] | +0.02 |
| MCQ × FRQ | +0.05 | [+0.03, +0.14] | +0.06 |
| MCQ × Date | +0.04 | [−0.01, +0.10] | +0.03 |
| Binary × Date | +0.10 | [−0.00, +0.15] | +0.08 |
| FRQ × Date | +0.10 | [+0.02, +0.17] | +0.10 |

Holding the model fixed, whether it gets one task right about a paper says almost nothing
about whether it gets another task right about the *same* paper: every median |ρ| ≤ 0.10.
(With these n the small positive values are statistically distinguishable from zero, but
they are practically negligible — an r of 0.06 explains 0.4% of variance.)

### 3c. What this shows

- **Not redundant.** At the level of individual papers the four tasks measure different
  things; success on one does not predict success on another. A benchmark that dropped
  any of them would lose information about each paper.
- **Not independent at the aggregate level, for three of them.** Binary, mechanism and
  solution all rise with general model capability. That is a statement about models, not
  about the tasks being the same construct — the item-level result rules that out.
- **Date is the outlier at both levels.** It is at most weakly related to the other three
  in the aggregate (no CI excludes zero), and it is the task where the panel fails to beat a trivial baseline. It
  behaves as a distinct, and currently unsolved, dimension.
- **Nothing here bears on completeness**, and we will not claim it does.

*Limitations of this analysis.* n = 10 at the model level; the four later models
(Sonnet 5, Sol, DeepSeek-V4-Pro, Opus 4.8) were added in revision and their original-corpus results
are not retrospectively clean for the same reason as the paper's models. Two Claude
models' FRQ responses are truncated at their token caps (direction of effect on scores not
established). The FRQ judge's single-item reproducibility is ±1.0 at 98% (MAD 0.39),
which does not affect correlations over thousands of items but bounds comparisons of
model-level FRQ means. DeepSeek-R1 covers the original corpus only (4,760 events).

## 4. Proposed manuscript changes

The manuscript source is not in this repository, so these are standalone replacements
to be placed where the taxonomy is introduced (Methods) and discussed (Limitations).

**[PROPOSED — Methods, where the four tasks are introduced; replaces any sentence
describing them as a decomposition or taxonomy of scientific forecasting]**

> We operationalize scientific forecasting through four tasks — binary feasibility,
> mechanism (multiple choice), solution (free response), and date — each corresponding to
> a question that can be posed before a result is published and scored against the
> published record. This is one realization of the forecasting problem rather than a
> complete decomposition of it; other operationalizations are possible, and we make no
> claim that these four dimensions are exhaustive.

**[PROPOSED — Results or Methods, new paragraph after the task descriptions]**

> The four tasks are empirically distinct at the level of individual papers. Within each
> model, success on one task is essentially unrelated to success on another task about
> the same paper (median Spearman |ρ| ≤ 0.10 across all six task pairs, over
> 25,000–41,000 paper-pairs per task pair; Supplementary Table SX). Across models, binary,
> mechanism and solution performance rise together with general capability (pairwise
> r = 0.72–0.87, n = 10 models), whereas date performance is only weakly related to the other
> three (r = 0.20–0.61, all CIs including zero): stronger models are not better at
> predicting when a result will appear.

**[PROPOSED — Limitations]**

> Our four tasks are one operationalization of scientific forecasting. They are not
> redundant — at the paper level they behave as near-independent measurements — but we
> cannot show that they are complete, and dimensions we do not measure (for example, the
> magnitude of an effect, or which group will report it) may matter as much as those we
> do.

**[PROPOSED — Supplementary Table SX caption]**

> Relationships among the four CUSP tasks. (Left, centre) Pearson and Spearman correlation
> of model-level performance across the ten evaluated models on the full corpus; binary
> is balanced accuracy. (Right) Median within-model Spearman correlation of per-paper
> outcomes across the same models. Confidence intervals and the model × task inputs are in
> the supplementary data.
