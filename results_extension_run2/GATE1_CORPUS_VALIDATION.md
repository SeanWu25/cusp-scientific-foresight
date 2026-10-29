# Gate 1 — validation of the April–August 2026 extension corpus

File `benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026.jsonl`
md5 `a86dd048a55900e2e0f049e9de95cc66`, 815 events, 2,277 task instances.

**Status after remediation: two of three blockers CLEARED.** See the
"Resolution" section at the end. Remaining constraint: the date task is not
comparable across corpora and must be reported against a constant baseline.

This corpus is **not prospective**. Every outcome resolved before the models
were run. It is uncontaminated by training data, but it is not the Time Capsule
and must not be described as a prospective forecast.

## Blocker 1 — the binary question template changed

| | day-level deadline | month-level |
|---|---|---|
| Extension | 99 / 196 (50.5%) | 49.5% |
| Original | 0 / 2,755 (0.0%) | 100% |

The original asks "By April 2026, will a method …". Half the extension asks
"By April 6, **2026**, will a method …". That is a categorical template change,
not drift. A day-level deadline is a different question with different
difficulty, and binary accuracy cannot be differenced across the two corpora.

MCQ and FRQ templates are unchanged: 100% of extension MCQs open "Given the
challenge of" (98.6% original) and 100% of FRQ prompts contain "propose a
concrete method" (100% original).

## Blocker 2 — generator provenance is unverifiable

Neither corpus records which model produced its events, distractors,
perturbations or validation. The build scripts read it from the environment at
run time:

- `create_bench.py`: `AZURE_OPENAI_DEPLOYMENT`, defaulting to `gpt-4o`
- `verifier.py`: hard-coded `gpt-4o-mini`
- `check_mcq.py` / `check_binary.py`: `AZURE_OPENAI_DEPLOYMENT`, no default;
  `check_binary.py`'s own docstring example shows `grok-3`

`AZURE_OPENAI_DEPLOYMENT` currently resolves to `gpt-5.4-mini`. So the
generator is environment-dependent and unrecorded, and **I cannot confirm from
the artifacts that the same model built both corpora.** The reviewer concern
about distractor comparability cannot be closed from the data. Ask whoever
built the extension to state the deployment name and prompt version used.

## Blocker 3 — the date window is compressed, and it inflates scores

Extension targets span 5 months (2026-04 … 2026-08); the original spans 27.

| | best constant guess | score |
|---|---|---|
| Extension | 2026-06 | **0.893** |
| Original | 2025-01 | 0.568 |

A model with no forecasting ability that always answers "June 2026" scores
0.893 on the extension. Every published model scores 0.178–0.500 on the
original, and the two new models 0.370–0.426. Date scores are therefore not
comparable across corpora and must be reported against the constant baseline.

## What is clean

- IDs: 815/815 unique, all UUIDv4, **zero collisions** with the original.
- Duplicates: none against the original on paper link, problem statement, MCQ
  or binary text. 3 duplicate `paper_link` values within the extension.
- Label balance: structurally 1:1 in both, by construction.
- MCQ structure: 4 options in both; within-item option length spread identical
  (mean 12 chars, p=0.92); answer key always index 0 pre-shuffle in both.
- Month coverage is even: 176 / 166 / 170 / 173 / 130 for Apr–Aug.

## Secondary issues

- **Domain mix differs** (chi2 p=4.6e-24): AI 16.3% vs 24.0%, "Other" 6.6% vs
  1.3%, Physics and Materials up ~3pp each.
- **Venue mix differs** (p=3.9e-13): the extension has no `top_ai_papers`
  (6.2% of original) and no `leaderboard_questions` (1.2%).
- **Task mix differs sharply**: binary and date cover 24.0% of extension events
  against 57.9% of the original. Only 196 binary and 196 date items exist.
- **`first_date_found` adds nothing.** It equals `publication_date` for all 708
  events that have it (gap = 0 months, every case), and 677 of 708 come from
  "Crossref (created)", a DOI registration date, not a preprint date. Only 28
  are genuine preprint sources. 107 events (13%) lack it entirely. Horizon
  stratification will be identical whether it or `publication_date` is used.
- Text lengths differ significantly but slightly: MCQ question 275 vs 256 chars
  (p=7e-25), binary question 238 vs 194 (p=4e-16), abstract 1320 vs 1293
  (p=0.03). FRQ and date prompts do not differ.
- 3 of 196 `date_prediction_prompt` values are a bare "YYYY-MM" string instead
  of a question. Exclude them.
- **Pre-existing in both corpora**: the longest MCQ option is the correct answer
  45.4% of the time in the extension and 47.0% in the original, against 25%
  chance. Consistent across corpora, so it does not break comparability, but it
  is a benchmark validity issue worth a sentence.

## If you proceed

Report the extension as its own 100%-post-cutoff table. Difference against the
original only for **MCQ**. Report binary side by side, or restrict to the 97
month-level items. Report date only alongside the 0.893 constant baseline.


---

# Resolution (post-validation)

## Blocker 1 — CLEARED by normalisation

Day-level deadlines were rewritten to month level with a regex over every task
field (`April 6, 2026` -> `April 2026`). The original corpus uses day-level
dates in **no** task field, so normalising MCQ and FRQ as well as binary is
correct rather than over-reach.

| corpus | binary | perturbed | MCQ | FRQ |
|---|---|---|---|---|
| extension, raw | 99/196 | 350/649 | 337/606 | 338/630 |
| extension, normalised | 0 | 0 | 0 | 0 |
| original | 0 | 0 | 0 | 0 |

433 of 815 events touched. Output:
`benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl`
md5 `52a9ef10b180015d3b9743946a292330`. The raw file is kept unmodified.
Binary questions now open "By &lt;Month&gt; &lt;Year&gt;," in 100% of extension items
against 97.9% of the original.

## Blocker 2 — CLEARED by the stated build flow

The team's pipeline, compared against the original as recorded in the repo:

| Stage | Extension | Original (from repo scripts) | Same? |
|---|---|---|---|
| Screening | GPT-4o-mini | `verifier.py` hard-codes gpt-4o-mini | yes |
| **Question + distractor generation** | **GPT-4o** | `create_bench.py` default gpt-4o | **yes** |
| Categorisation | GPT-4o-mini | `categorize.py` hard-codes gpt-4o-mini | yes |
| Independent validation | Grok-4 | `check_binary.py` documents grok-3 | **no** |

The generator is the same, which closes the reviewer's distractor-comparability
concern: MCQ difficulty and stylistic artifacts come from the same model under
the same prompts. Supporting evidence from the text itself — identical MCQ and
FRQ templates, identical option count, identical within-item option length
spread (p=0.92), and a near-identical longest-option-is-key rate (45.4% vs
47.0%).

The validator differs, grok-3 to grok-4. This is a **filter**, not a generator:
it changes which items survive, not how they are written. Worth one sentence in
the methods; not a blocker. If the surviving-item rate differed sharply between
the two runs that would be worth checking, but it cannot bias question style.

## Blocker 3 — STANDS

Unchanged. A constant guess of 2026-06 scores 0.893 on the extension against
0.568 for the best constant on the original. Date scores must be reported
against that baseline and never differenced across corpora.

## Correction to the first-observable-date finding

The earlier note that `first_date_found` "adds nothing" was too harsh. The
pipeline (`find_first_date.py`) queries Crossref, Semantic Scholar, OpenAlex,
Europe PMC, arXiv and bioRxiv, and the gap of 0 months for all 708 events means
**no earlier public version was found**, which is a positive verification
rather than a missing field. Independent check: all 131 arXiv-linked events
have arXiv IDs of 2026-04 or later, so no preprint predates the window among
them. Residual risk is a preprint indexed by none of those six APIs. Note also
that inclusion was by journal publication date and earlier preprints were not
excluded by rule, so this verification is what rules them out empirically.
