# Document-level leakage under WS+Cutoff (A4.2 supplement)

Share of retrieved evidence first made public on or after the run's date ceiling, using the exact URL list each model received. Documents are dated from their identifiers (arXiv id, bioRxiv/medRxiv DOI, Crossref for DOIs / Nature / eLife / ScienceDirect and Cell PIIs, NCBI for PubMed / PMC), earliest public date. **Event leak rate** = events with at least one retrieved document dated on or after the ceiling. **Document leak rate** = share of dated documents on or after the ceiling (event-bootstrap CI). **Cutoff-month rule: an event published in the ceiling month counts as PRE-cutoff (post iff publication month > ceiling month).** URL dating cannot see snippet-level leaks (e.g. a 2022 ResearchGate page whose snippet carries a 2026 abstract); those are measured by the judge-based outcome leakage in `results.md`, repeated in the last column.


## Pre-cutoff events

| model | ceiling | events | URLs | dated | event leak rate [95% CI] | document leak rate [95% CI] | median lag of leaking docs (months) | outcome leak by judge (post-cutoff only) |
|---|---|---|---|---|---|---|---|---|
| DeepSeek R1 | 2024-07 | 101 | 1010 | 609 (60%) | 1.0% [0.2%, 5.4%] | 0.2% [0.0%, 0.5%] | 6 | — |
| Claude S4.5 | 2025-01 | 199 | 1978 | 1118 (57%) | 1.0% [0.3%, 3.6%] | 0.2% [0.0%, 0.4%] | 0 | — |
| GPT-5.4 | 2025-08 | 377 | 3763 | 2154 (57%) | 0.8% [0.3%, 2.3%] | 0.1% [0.0%, 0.3%] | 0 | — |
| Claude Sonnet 5 | 2026-01 | 398 | 3959 | 1922 (49%) | 0.0% [0.0%, 1.0%] | 0.0% [0.0%, 0.0%] | — | — |
| GPT-5.6 Sol | 2026-02 | 496 | 4431 | 2133 (48%) | 0.8% [0.3%, 2.1%] | 0.2% [0.0%, 0.4%] | 0 | — |

## Post-cutoff events

| model | ceiling | events | URLs | dated | event leak rate [95% CI] | document leak rate [95% CI] | median lag of leaking docs (months) | outcome leak by judge (post-cutoff only) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 500 | 4955 | 2976 (60%) | 0.4% [0.1%, 1.4%] | 0.1% [0.0%, 0.2%] | 1 | 24.6% |
| LLaMA 3.3 70B | 2023-12 | 499 | 4938 | 2649 (54%) | 0.2% [0.0%, 1.1%] | 0.0% [0.0%, 0.1%] | 0 | 19.8% |
| DeepSeek R1 | 2024-07 | 297 | 2950 | 1896 (64%) | 1.7% [0.7%, 3.9%] | 0.3% [0.1%, 0.6%] | 0 | 22.6% |
| Claude S4.5 | 2025-01 | 264 | 2626 | 1616 (62%) | 0.4% [0.1%, 2.1%] | 0.1% [0.0%, 0.2%] | 0 | 26.5% |
| GPT-5.4 | 2025-08 | 123 | 1218 | 805 (66%) | 0.8% [0.1%, 4.5%] | 0.1% [0.0%, 0.4%] | 0 | 32.5% |
| Claude Sonnet 5 | 2026-01 | 29 | 289 | 178 (62%) | 3.4% [0.6%, 17.2%] | 0.6% [0.0%, 1.8%] | 0 | 27.6% |
| GPT-5.6 Sol | 2026-02 | 4 | 40 | 23 (57%) | 0.0% [0.0%, 49.0%] | 0.0% [0.0%, 0.0%] | — | 0.0% |

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
