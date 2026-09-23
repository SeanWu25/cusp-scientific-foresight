# A5 Step 0 — what source metadata actually exists per event

Reviewer 1, comment 5 asks us to stratify by **journal, repository, event
visibility, novelty, and publication latency**. This file reports what the
corpus can and cannot support, *before* any performance numbers are computed.

Corpus: 5,575 events = 4,760 original (`archive/data/canonical/merged_validated_cusp_fixed.jsonl`,
Jan 2024–Mar 2026) + 815 extension (`benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl`,
Apr–Aug 2026). Event ids are disjoint.

## 1. Field coverage

| field | original (n=4,760) | extension (n=815) | pooled | usable for |
|---|---|---|---|---|
| `id`, `row_index` | 100% | 100% | 100% | join key |
| `publication_date` | 100% | 100% | 100% | cutoff partition |
| `source` | 100% | 100% | 100% | **source / journal** |
| `main_area` (8 disciplines + Other) | 100% | 100% | 100% | discipline (already in paper) |
| `sub_categories` | 100% | 100% | 100% | — |
| `paper_link` | 98.8% | 100% | 99.0% | venue confirmation |
| `source_abstract` | 98.8% | 100% | 99.0% | novelty proxies (§5) |
| `first_date_found` | **0%** | 86.9% | 12.7% | latency (extension only) |
| `first_date_source` | **0%** | 86.9% | 12.7% | latency provenance |
| `original_publication_date` | **0%** | 86.9% | 12.7% | **latency** |
| `citation_count` | 10.1% (481/4,760) | **0%** | **8.6%** | **visibility** |
| `benchmark_label`, `best_score_*` | 1.2% (59) | 0% | 1.1% | leaderboard stratum only |

**No field records journal impact factor, altmetrics, download counts, author
count, institution, or funding.** Nothing in the corpus supports a novelty
measure (§5).

## 2. Journal / repository — FEASIBLE as specified, full coverage

`source` has six values and is **one-to-one with the venue**: every DOI under a
given `source` resolves to a single journal, and both AI feeds are entirely
arXiv. We verified this rather than assuming it — the DOI prefix/token for all
5,516 linked events:

| `source` | venue | DOI / host | n | share |
|---|---|---|---|---|
| `nature` | *Nature* | `10.1038/s41586` (all 2,493) | 2,493 | 44.7% |
| `science` | *Science* | `10.1126/science` (all 1,249) | 1,249 | 22.4% |
| `cell` | *Cell* | `10.1016/j.cell` (all 584) | 584 | 10.5% |
| `hugging_face_top_ai_papers` | HF Daily Papers | arXiv (all 894) | 894 | 16.0% |
| `top_ai_papers` | Top-10 AI Paper of the Week | arXiv (all 296) | 296 | 5.3% |
| `leaderboard_questions` | leaderboards | no paper link | 59 | 1.1% |

Two consequences worth stating plainly:

- **The per-journal stratification and the repository stratification are the
  same stratification.** There are no sibling journals to separate (no *Nature
  Medicine*, no *Cell Reports*): the scrape targeted the three flagship
  journals only. Reporting "per journal" and "per repository" as two analyses
  would be reporting one analysis twice.
- **No stratum is a singleton**, so the "other" bucket the reviewer anticipates
  is not needed. The smallest, `leaderboard_questions` (n=59), is kept as its
  own stratum because it is a genuinely different item type — but it carries
  **no FRQ items at all** (0/59), so it is absent from every FRQ table, and its
  per-model pre/post splits frequently fall below n=20 and are suppressed.

Per-stratum task availability (events offering each task):

| source | events | binary | binary pert. | MCQ | FRQ | date |
|---|---|---|---|---|---|---|
| Nature | 2,493 | 1,396 | 1,823 | 2,093 | 2,167 | 1,396 |
| Science | 1,249 | 724 | 947 | 1,084 | 1,024 | 724 |
| HF Daily Papers | 894 | 380 | 792 | 768 | 817 | 380 |
| Cell | 584 | 248 | 414 | 500 | 484 | 248 |
| Top-10 AI Paper | 296 | 144 | 270 | 230 | 273 | 144 |
| Leaderboards | 59 | 59 | 59 | 59 | **0** | 59 |

## 3. Event visibility (citations) — FEASIBLE ONLY ON 8.6% OF THE CORPUS

`citation_count` was never collected for the benchmark. It exists **only** for
the pinned 500-event retrieval subset, in a file outside this repository:

- file: `/home/seanwu/FutureScience_backup_20260508_013823/benchmark_data/CUSP/sample_500_stratified_with_citations.jsonl`
- **481 of 500** events carry a count (19 failed: 10 "link format not
  recognised", 9 "not found in S2 or OpenAlex")
- source: **Semantic Scholar** batch API, OpenAlex fallback (`add_citations.py`)
- **retrieval date: 2026-05-12** (file mtime; the script fetches live counts).
  Counts move over time and this is one snapshot — it is now ~4 months stale.
- range 0–1,161, median 22
- all 481 are in the **original** half, publication dates 2024-01 → 2026-03

So the visibility stratification covers **481/5,575 = 8.6% of the benchmark**,
and **0% of the extension**. It cannot be computed "on the full dataset" as the
prompt asks. We did not fetch new counts: doing so would mix two retrieval
dates in one analysis, and re-fetching all 5,575 would produce counts measured
2026-09 against outcomes resolved by 2026-08, a different (and for the recent
half, near-zero-by-construction) quantity.

Quartile edges over those 481 events are **Q1 ≤ 8, Q2 ≤ 22, Q3 ≤ 59, Q4 > 59** —
recomputed here and identical to the edges used in published Supplementary
Tables S19–S23, confirming those tables used this same file.

A further structural limit: because the subset spans 2024-01 to 2026-03, a model
with an early cutoff has *every* citation-bearing event post-cutoff, and a model
with a late cutoff has *every* one pre-cutoff. For most models one of the two
partitions does not exist at all — by construction, not by suppression.

## 4. Publication latency — FEASIBLE ONLY ON THE EXTENSION (12.7%), AND CENSORED

The original half has **no preprint or first-seen date field whatsoever**, so it
contributes nothing. The extension has three date fields on 708/815 events.

One trap we checked before using them: `first_date_found` is **identical to
`publication_date` for all 708 events** (verified, 708/708), because
`publication_date` was *derived* from it during month-normalisation. Computing
latency as `publication_date − first_date_found` therefore returns exactly 0 for
every event — a spurious null. The real interval is:

> **latency = `original_publication_date` − `first_date_found`**

| latency | n | share |
|---|---|---|
| 0 months | 442 | 62.4% |
| 1 month | 156 | 22.0% |
| 2 months | 101 | 14.3% |
| 3 months | 9 | 1.3% |

Bins used: **0 mo / 1 mo / 2–3 mo** (the 3-month cell has n=9 and is pooled
upward rather than printed). Excluded for lack of a preprint date: **107
extension events + all 4,760 original events = 4,867 of 5,575 (87.3%)**.

`first_date_source` for the 708: Crossref `created` 677, arXiv 24, bioRxiv
preprint 4, Semantic Scholar 2, OpenAlex 1. Crossref `created` is a DOI-record
date, not a true preprint posting date, so for 96% of these events the measured
quantity is "first indexed → issue publication", not "preprint → publication".

The range is **right-censored by the extension window** (Apr–Aug 2026): a paper
first seen in August cannot exhibit a 4-month latency inside the corpus, so the
upper tail is missing rather than empty.

Finally, the extension is **post-cutoff for every model in the panel** (it
postdates the latest cutoff, 2026-04). This stratification therefore has **no
pre-cutoff partition for any model**, and its OVERALL column equals its
POST-CUTOFF column. The pre/post contrast the prompt asks for cannot be formed
here.

## 5. Novelty — NOT COMPUTED

No gold standard, no agreed proxy, and nothing in the metadata that measures it.
Per instruction we do not invent one. Candidate proxies and what each would and
would not capture are in `novelty_discussion.md`, flagged as an open team
decision.

## 6. Pre/post partition sizes per model

Partition rule "main": an event published in the cutoff month counts as POST.
**These are wildly unequal across models, so pooled OVERALL numbers are not
comparable between models** — a headline "overall" difference between GPT-4o and
DeepSeek-V4-Pro is mostly a difference in what fraction of the corpus each one
had already seen.

| model | cutoff | n events | pre-cutoff | post-cutoff |
|---|---|---|---|---|
| GPT-4o | 2023-10 | 5,575 | **0** | 5,575 |
| LLaMA 3.3 70B | 2023-12 | 5,575 | **0** | 5,575 |
| GPT-OSS 20B | 2024-06 | 5,575 | 657 | 4,918 |
| DeepSeek-R1 | 2024-07 | 4,760 | 842 | 3,918 |
| Claude S4.5 | 2025-01 | 5,575 | 1,907 | 3,668 |
| GPT-5.4 | 2025-08 | 5,575 | 3,372 | 2,203 |
| Claude Sonnet 5 | 2026-01 | 5,575 | 4,305 | 1,270 |
| Claude Opus 4.8 | 2026-01 | 5,575 | 4,305 | 1,270 |
| GPT-5.6 Sol | 2026-02 | 5,575 | 4,508 | 1,067 |
| DeepSeek-V4-Pro | 2026-04 | 5,575 | 4,760 | **815** |

GPT-4o and LLaMA 3.3 have **no pre-cutoff partition at all** — every event
postdates their cutoffs — so their PRE columns are empty everywhere below.
DeepSeek-V4-Pro's post-cutoff partition is exactly the 815-event extension.
DeepSeek-R1 covers the original half only (4,760).

## 7. Verdict on feasibility

| stratification | verdict | coverage | partitions available |
|---|---|---|---|
| **Journal** | feasible; **identical to repository** | 100% | pre / post / overall |
| **Repository / source** | feasible as specified | 100% | pre / post / overall |
| **Event visibility (citations)** | **feasible on 8.6% only** | 481 events, original half, pinned-500 | one partition per model, by construction |
| **Publication latency** | **feasible on 12.7% only**, censored, and the interval is "first indexed → published" not "preprint → published" for 96% of it | 708 events, extension only | **post only** |
| **Novelty** | not computed by instruction | — | — |

## 8. What we used for FRQ

The **published rubric** (`judge_frq_combined`, rubric sha256 `fc24e69d…`),
stage-2 grading now complete for all ten models on both halves. These are *not*
the archived legacy-rubric scores. Refusals are excluded from denominators, as
in the published tables. Two Claude models' FRQ responses are truncated at their
token caps; the direction of that effect on scores is not established.
