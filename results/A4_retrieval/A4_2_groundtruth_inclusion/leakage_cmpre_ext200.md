# Document-level leakage under WS+Cutoff (A4.2 supplement)

Share of retrieved evidence first made public on or after the run's date ceiling, using the exact URL list each model received. Documents are dated from their identifiers (arXiv id, bioRxiv/medRxiv DOI, Crossref for DOIs / Nature / eLife / ScienceDirect and Cell PIIs, NCBI for PubMed / PMC), earliest public date. **Event leak rate** = events with at least one retrieved document dated on or after the ceiling. **Document leak rate** = share of dated documents on or after the ceiling (event-bootstrap CI). **Cutoff-month rule: an event published in the ceiling month counts as PRE-cutoff (post iff publication month > ceiling month).** **Events: the original 500-event subset plus 200 extension-corpus events (Apr-Aug 2026; ids in `ext200_leakage_ids.txt`), using the stored WS+Cutoff URL lists of each model's original-design run on those events; DeepSeek R1 has original-subset events only. The judge column covers the original subset only.** URL dating cannot see snippet-level leaks (e.g. a 2022 ResearchGate page whose snippet carries a 2026 abstract); those are measured by the judge-based outcome leakage in `results.md`, repeated in the last column.


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
| GPT-4o | 2023-10 | 699 | 6940 | 3993 (58%) | 0.3% [0.1%, 1.0%] | 0.1% [0.0%, 0.1%] | 1 | 24.6% (n=500) |
| LLaMA 3.3 70B | 2023-12 | 699 | 6925 | 3658 (53%) | 0.1% [0.0%, 0.8%] | 0.0% [0.0%, 0.1%] | 0 | 19.8% (n=499) |
| DeepSeek R1 | 2024-07 | 297 | 2950 | 1896 (64%) | 1.7% [0.7%, 3.9%] | 0.3% [0.1%, 0.6%] | 0 | 22.6% (n=297) |
| Claude S4.5 | 2025-01 | 424 | 4221 | 2469 (58%) | 0.9% [0.4%, 2.4%] | 0.2% [0.0%, 0.3%] | 0 | 26.5% (n=264) |
| GPT-5.4 | 2025-08 | 323 | 3212 | 1913 (60%) | 0.6% [0.2%, 2.2%] | 0.1% [0.0%, 0.3%] | 0 | 32.5% (n=123) |
| Claude Sonnet 5 | 2026-01 | 217 | 2157 | 1188 (55%) | 2.3% [1.0%, 5.3%] | 0.4% [0.1%, 0.8%] | 0 | 27.6% (n=29) |
| GPT-5.6 Sol | 2026-02 | 204 | 1841 | 1046 (57%) | 1.0% [0.3%, 3.5%] | 0.2% [0.0%, 0.5%] | 0 | 0.0% (n=4) |

## All events

| model | ceiling | events | URLs | dated | event leak rate [95% CI] | document leak rate [95% CI] | median lag of leaking docs (months) | outcome leak by judge (post-cutoff only) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 699 | 6940 | 3993 (58%) | 0.3% [0.1%, 1.0%] | 0.1% [0.0%, 0.1%] | 1 | — |
| LLaMA 3.3 70B | 2023-12 | 699 | 6925 | 3658 (53%) | 0.1% [0.0%, 0.8%] | 0.0% [0.0%, 0.1%] | 0 | — |
| DeepSeek R1 | 2024-07 | 398 | 3960 | 2505 (63%) | 1.5% [0.7%, 3.2%] | 0.3% [0.1%, 0.5%] | 0 | — |
| Claude S4.5 | 2025-01 | 623 | 6199 | 3587 (58%) | 1.0% [0.4%, 2.1%] | 0.2% [0.1%, 0.3%] | 0 | — |
| GPT-5.4 | 2025-08 | 700 | 6975 | 4067 (58%) | 0.7% [0.3%, 1.7%] | 0.1% [0.0%, 0.2%] | 0 | — |
| Claude Sonnet 5 | 2026-01 | 615 | 6116 | 3110 (51%) | 0.8% [0.3%, 1.9%] | 0.2% [0.0%, 0.3%] | 0 | — |
| GPT-5.6 Sol | 2026-02 | 700 | 6272 | 3179 (51%) | 0.9% [0.4%, 1.9%] | 0.2% [0.1%, 0.3%] | 0 | — |

## Which identifiers the dated and leaking documents come from (all models, all events)

| identifier type | URLs | dated | leaking |
|---|---|---|---|
| arxiv | 4389 | 4389 | 15 |
| b/medrxiv | 797 | 797 | 0 |
| doi | 6731 | 6731 | 14 |
| nature | 5454 | 5454 | 0 |
| pii | 4029 | 4029 | 0 |
| elife | 278 | 278 | 0 |
| pubmed | 2140 | 2140 | 1 |
| pmc | 281 | 281 | 2 |
| undated | 19288 | — | 0 |
