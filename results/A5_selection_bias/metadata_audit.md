# A5 Step 0 — what source metadata actually exists per event (updated 2026-09-25)

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

## 3. Event visibility (citations) — NOW FEASIBLE ON THE WHOLE CORPUS

*First pass (2026-09-23).* `citation_count` had never been collected for the
benchmark; it existed only for the pinned 500-event retrieval subset, in a file
outside this repository (`/home/seanwu/FutureScience_backup_20260508_013823/benchmark_data/CUSP/sample_500_stratified_with_citations.jsonl`,
481 of 500 events, Semantic Scholar with OpenAlex fallback, retrieved
2026-05-12, quartile edges ≤8 / ≤22 / ≤59 — the edges of published S19–S23).
That covered 8.6% of the benchmark and 0% of the extension.

*Second pass (2026-09-25).* The limit was a limit of the corpus files, not of
the events, so `scripts/a5_fetch_metadata.py` and `scripts/a5_fetch_s2.py`
took one snapshot over every event with a paper link:

| source | role | requests | resolved |
|---|---|---|---|
| Semantic Scholar `/graph/v1/paper/batch` (`ARXIV:<id>` / `DOI:<doi>`, 500 per call) | primary | 11 | 5,443 |
| OpenAlex `/works?filter=doi:` (50 per call) | fallback | 110 | +70 |
| leaderboard items | no paper | — | 59 excluded |

**5,513 of 5,575 events (98.9%) carry a citation count**; 3 linked events
resolved at neither service. Snapshot date is in `metadata/SNAPSHOT.json`; the
raw records are `metadata/s2_citations.jsonl` and `metadata/openalex_citations.jsonl`,
cached so a rerun never re-fetches.

Two things learned on the way:

- **OpenAlex is unusable for arXiv items.** It credits most arXiv citations to
  the later journal version and returned a median of 0 citations for the HF
  Daily Papers feed (and no record at all for 229 of 1,190 arXiv events).
  Semantic Scholar gives the same feed a median of 61. Hence S2 primary.
- **The two snapshots agree.** On the 481 first-pass events, May-2026 S2 counts
  versus September-2026 counts have Spearman ρ = 0.965. The earlier tables
  were narrow, not wrong.

Quartile edges over all 5,513 events are Q1 ≤ 10, Q2 ≤ 28, Q3 ≤ 68. Because
raw counts favour older events (the extension has had at most five months to be
cited), the analysis also uses a **citation rate** — count divided by months
from the first-observable month to the snapshot — with edges 0.96 / 1.83 /
3.94 citations per month. The S19–S23 fold-in keeps the May-2026 file and
edges, because its job is to reproduce the published tables.

## 4. Publication latency — NOW FEASIBLE ON EVERY JOURNAL EVENT

*First pass.* The only latency-like fields were the extension's
`first_date_found` / `original_publication_date` (708 events). On inspection,
`first_date_found` is the Crossref record-creation date for 96% of them, so
`original_publication_date − first_date_found` mostly measured online-first
versus print-issue scheduling (0–3 months), with no pre-cutoff partition. It is
kept under `by_legacy/latency_708/` and is superseded.

*Second pass.* Two facts make a whole-corpus latency computable:

1. **CUSP's `publication_date` is already the first-observable date.** The build
   pipeline set it to the earliest date found across Crossref, bioRxiv, medRxiv,
   Semantic Scholar and Europe PMC (verified in the horizon study: the cached
   lookup equals `publication_date` for all 3,642 original DOI events).
2. **Crossref returns the journal version's own dates for every journal DOI.**
   `scripts/a5_fetch_metadata.py` fetched all 4,326 (Nature 2,493, Science
   1,249, Cell 584; both halves): `created`, `published-online`,
   `published-print`, `issued`; the `received` / `accepted` / `first_online`
   assertions; and `has-preprint` relations, then the posted date of each of
   the 503 linked preprints. Raw records: `metadata/crossref_dates.jsonl`,
   `metadata/crossref_preprints.jsonl`.

Definitions used:

> **latency** = online month of the journal version − first-observable month,
> where first-observable = the earlier of CUSP's `publication_date` and any
> Crossref-linked preprint's posted month. **4,326 events (77.6%)**, both
> halves, all three partitions.
>
> **editorial latency** = online month − manuscript-received month. Nature and
> Science deposit received dates; Cell (Elsevier) does not. **3,740 events
> (67.1%)**.

Distribution of latency: 0 months for 84.1% of journal events (no earlier
public record found by either the build pipeline or Crossref), 1–6 months for
5.4%, more than six months for 10.5% (maximum 54). Bins are therefore
0 / 1–6 / >6 months; finer bins fall below n = 20 in most per-model
post-cutoff cells. Editorial latency quartiles are 7 / 11 / 15 months; bins
≤6 / 7–12 / 13–24 / >24.

**A dating correction this surfaced.** For 246 of the 493 journal events with a
Crossref-linked preprint, the preprint was posted before CUSP's
`publication_date` — median 11 months earlier (IQR 7–15) — so the build
pipeline's earliest-date search missed them. The latency uses the corrected
date; the cutoff partition keeps the benchmark's own date, and the response
reports per model how many post-cutoff journal events had a preprint before
the cutoff (1.3–4.8%).

arXiv events (1,190) have no journal version and no latency by construction;
leaderboard items (59) have no paper.

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

## 7. Verdict on feasibility (second pass)

| stratification | verdict | coverage | partitions available |
|---|---|---|---|
| **Journal** | feasible; **identical to repository** | 100% (5,575) | pre / post / overall |
| **Repository / source** | feasible as specified | 100% (5,575) | pre / post / overall |
| **Event visibility (citations)** | feasible on the whole corpus, single snapshot 2026-09-25; raw and age-adjusted quartiles | 5,513 events (98.9%) | pre / post / overall |
| **Publication latency** | feasible on every journal event; arXiv items have no journal version | 4,326 events (77.6%) | pre / post / overall |
| **Editorial latency** | feasible for Nature and Science | 3,740 events (67.1%) | pre / post / overall |
| **Novelty** | not computed by instruction | — | — |

## 8. What we used for FRQ

The **published rubric** (`judge_frq_combined`, rubric sha256 `fc24e69d…`),
stage-2 grading now complete for all ten models on both halves. These are *not*
the archived legacy-rubric scores. Refusals are excluded from denominators, as
in the published tables. Two Claude models' FRQ responses are truncated at their
token caps; the direction of that effect on scores is not established.
