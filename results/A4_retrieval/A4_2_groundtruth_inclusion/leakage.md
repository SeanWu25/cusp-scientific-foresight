# Document-level leakage under WS+Cutoff (A4.2 supplement)

Share of retrieved evidence first made public on or after the run's date ceiling, using the exact URL list each model received. Documents are dated from their identifiers (arXiv id, bioRxiv/medRxiv DOI, Crossref for DOIs / Nature / eLife / ScienceDirect and Cell PIIs, NCBI for PubMed / PMC), earliest public date. **Event leak rate** = events with at least one retrieved document dated on or after the ceiling. **Document leak rate** = share of dated documents on or after the ceiling (event-bootstrap CI). URL dating cannot see snippet-level leaks (e.g. a 2022 ResearchGate page whose snippet carries a 2026 abstract); those are measured by the judge-based outcome leakage in `results.md`, repeated in the last column.


## Pre-cutoff events

| model | ceiling | events | URLs | dated | event leak rate [95% CI] | document leak rate [95% CI] | median lag of leaking docs (months) | outcome leak by judge (post-cutoff only) |
|---|---|---|---|---|---|---|---|---|
| DeepSeek R1 | 2024-07 | 81 | 810 | 487 (60%) | 1.2% [0.2%, 6.7%] | 0.2% [0.0%, 0.6%] | 6 | — |
| Claude S4.5 | 2025-01 | 185 | 1846 | 1040 (56%) | 1.1% [0.3%, 3.9%] | 0.2% [0.0%, 0.5%] | 0 | — |
| GPT-5.4 | 2025-08 | 356 | 3553 | 2031 (57%) | 0.6% [0.2%, 2.0%] | 0.1% [0.0%, 0.2%] | 0 | — |
| Claude Sonnet 5 | 2026-01 | 383 | 3813 | 1833 (48%) | 0.0% [0.0%, 1.0%] | 0.0% [0.0%, 0.0%] | — | — |
| GPT-5.6 Sol | 2026-02 | 469 | 4202 | 1996 (48%) | 0.9% [0.3%, 2.2%] | 0.2% [0.0%, 0.4%] | 0 | — |

## Post-cutoff events

| model | ceiling | events | URLs | dated | event leak rate [95% CI] | document leak rate [95% CI] | median lag of leaking docs (months) | outcome leak by judge (post-cutoff only) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 500 | 4955 | 2976 (60%) | 0.4% [0.1%, 1.4%] | 0.1% [0.0%, 0.2%] | 1 | 24.6% |
| LLaMA 3.3 70B | 2023-12 | 499 | 4938 | 2649 (54%) | 0.2% [0.0%, 1.1%] | 0.0% [0.0%, 0.1%] | 0 | 19.8% |
| DeepSeek R1 | 2024-07 | 317 | 3150 | 2018 (64%) | 1.6% [0.7%, 3.6%] | 0.3% [0.1%, 0.6%] | 0 | 23.7% |
| Claude S4.5 | 2025-01 | 278 | 2758 | 1694 (61%) | 0.4% [0.1%, 2.0%] | 0.1% [0.0%, 0.2%] | 0 | 27.0% |
| GPT-5.4 | 2025-08 | 144 | 1428 | 928 (65%) | 1.4% [0.4%, 4.9%] | 0.2% [0.0%, 0.6%] | 0 | 33.3% |
| Claude Sonnet 5 | 2026-01 | 44 | 435 | 267 (61%) | 2.3% [0.4%, 11.8%] | 0.4% [0.0%, 1.2%] | 0 | 34.1% |
| GPT-5.6 Sol | 2026-02 | 31 | 269 | 160 (59%) | 0.0% [0.0%, 11.0%] | 0.0% [0.0%, 0.0%] | — | 35.5% |

## All events

| model | ceiling | events | URLs | dated | event leak rate [95% CI] | document leak rate [95% CI] | median lag of leaking docs (months) | outcome leak by judge (post-cutoff only) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 500 | 4955 | 2976 (60%) | 0.4% [0.1%, 1.4%] | 0.1% [0.0%, 0.2%] | 1 | — |
| LLaMA 3.3 70B | 2023-12 | 499 | 4938 | 2649 (54%) | 0.2% [0.0%, 1.1%] | 0.0% [0.0%, 0.1%] | 0 | — |
| DeepSeek R1 | 2024-07 | 398 | 3960 | 2505 (63%) | 1.5% [0.7%, 3.2%] | 0.3% [0.1%, 0.5%] | 0 | — |
| Claude S4.5 | 2025-01 | 463 | 4604 | 2734 (59%) | 0.6% [0.2%, 1.9%] | 0.1% [0.0%, 0.3%] | 0 | — |
| GPT-5.4 | 2025-08 | 500 | 4981 | 2959 (59%) | 0.8% [0.3%, 2.0%] | 0.1% [0.0%, 0.3%] | 0 | — |
| Claude Sonnet 5 | 2026-01 | 427 | 4248 | 2100 (49%) | 0.2% [0.0%, 1.3%] | 0.0% [0.0%, 0.1%] | 0 | — |
| GPT-5.6 Sol | 2026-02 | 500 | 4471 | 2156 (48%) | 0.8% [0.3%, 2.0%] | 0.2% [0.0%, 0.4%] | 0 | — |

## Which identifiers the dated and leaking documents come from (all models, all events)

| identifier type | URLs | dated | leaking |
|---|---|---|---|
| arxiv | 3624 | 3624 | 13 |
| b/medrxiv | 615 | 615 | 0 |
| doi | 4650 | 4650 | 6 |
| nature | 4045 | 4045 | 0 |
| pii | 2915 | 2915 | 0 |
| elife | 243 | 243 | 0 |
| pubmed | 1722 | 1722 | 1 |
| pmc | 265 | 265 | 2 |
| undated | 14078 | — | 0 |
