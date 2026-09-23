# Response to Reviewer 1, Comment 5 — benchmark selection bias (A5)

Supporting files in this directory: `metadata_audit.md` (what metadata exists,
read this first), `by_source/`, `by_visibility/`, `by_latency/` (full tables,
CSV + markdown), `tables/` (manuscript-ready), `figures/`,
`novelty_discussion.md`, `MANIFEST.json` (git SHA, seeds, citation retrieval
date, panel, partition sizes).

Regenerate with, in order:

```
python results/A5_selection_bias/scripts/a5_analysis.py
python results/A5_selection_bias/scripts/a5_within_discipline.py
python results/A5_selection_bias/scripts/a5_citation_gap.py
python results/A5_selection_bias/scripts/a5_figures.py
python results/A5_selection_bias/scripts/a5_tables.py
```

No inference; stored outputs only.

---

## 1. The reviewer's comment

> "Control benchmark selection bias by stratifying results across journals,
> repositories, event visibility, novelty, and publication latency."

## 2. Summary of what we found

Across ten models and four tasks, on the entire 5,575-event corpus:

1. **Source composition matters for exactly one task — date prediction — and
   the effect is large.** Every one of the ten models scores higher on arXiv-
   sourced items than on journal-sourced ones (10/10, median +0.27 date score,
   range +0.07 to +0.34). Binary, MCQ and FRQ show no consistent direction
   (6/10, 6/10 and 8/10 models, median differences +0.003, +0.024 and +0.13,
   overall partition).
2. **That source effect is a discipline effect, not a venue effect.** With
   discipline held fixed, only **4 of 705** model × task × partition tests
   survive Holm correction — noise level, and scattered with no pattern.
3. **Event visibility does not bias our results.** Only 6 of 93 tests are
   significant, *all* of them on the date task; binary, MCQ and FRQ give 0 of 71.
   Performance is flat across citation quartiles.
4. **Publication latency does not bias our results.** **0 of 72** tests are
   significant, on any task, for any model.
5. **We do not stratify on novelty**, and we give our reasons rather than
   substituting a proxy.

The headline claims of the paper — near-chance binary forecasting, a large
retrospective/prospective gap, no model beating a constant-month date baseline —
do not depend on which venues, how visible, or how quickly-published the events
are. The one composition effect we did find is confined to the task on which no
model has skill anyway.

## 3. What the metadata can and cannot support

This must be stated before the results, because three of the five requested
stratifications are not available at full coverage. Details in
`metadata_audit.md`.

| stratification | verdict | coverage |
|---|---|---|
| Journal | feasible — but **identical to** repository | 100% (5,575) |
| Repository / source | feasible as specified | 100% (5,575) |
| Event visibility | **8.6% of the corpus only** | 481 events, original half |
| Publication latency | **12.7% only**, post-cutoff only, censored | 708 events, extension half |
| Novelty | no proxy exists; not computed | — |

Three points we want to be explicit about:

- **Journal and repository are one stratification, not two.** We verified the
  DOIs rather than assuming: every `nature` event is `10.1038/s41586`
  (*Nature* itself), every `science` is `10.1126/science`, every `cell` is
  `10.1016/j.cell`, and both AI feeds are entirely arXiv. The scrape targeted
  three flagship journals, so there are no sibling journals to separate. No
  stratum is a singleton, so the "other" bucket the reviewer anticipates is not
  needed.
- **Citation counts exist for 481 events (8.6%), retrieved once on 2026-05-12**
  from Semantic Scholar (OpenAlex fallback), all inside the pinned 500-event
  retrieval subset, none in the extension. We did not re-fetch: mixing two
  retrieval dates in one analysis would be worse, and fresh counts for the
  recent half would be near-zero by construction. Recomputed quartile edges
  (≤8, ≤22, ≤59) are identical to those in published Supplementary Tables
  S19–S23.
- **Latency is "first indexed → published", not "preprint → published", for 96%
  of the events that have it**, its observed range is 0–3 months, and it is
  right-censored by the Apr–Aug 2026 extension window. The original half carries
  no preprint date at all. Because the extension postdates every model cutoff,
  this stratification has **no pre-cutoff partition for any model**, so its
  OVERALL column equals its POST column.

**Partition sizes are very unequal across models** and OVERALL numbers are
therefore not comparable between models: GPT-4o and LLaMA 3.3 have **zero**
pre-cutoff events, while DeepSeek-V4-Pro has 4,760 pre and 815 post. Per-model
pre/post N is in `tables/A5_partition_sizes.csv` and reprinted beside every
table.

**Methods used throughout.** Binary is balanced accuracy (mean of recall on the
real question and specificity on its perturbed twin), because raw merged
accuracy is dominated by class balance interacting with response bias. Every
cell carries N and a 2,000-draw event-clustered bootstrap percentile CI; cells
below n = 20 print `n<20` and no point estimate. Stratum effects are tested with
a 10,000-draw permutation test that shuffles stratum labels across *events*
(preserving event clustering), Holm–Bonferroni corrected across every
model × partition × task test within each stratification. FRQ uses the published
rubric (`judge_frq_combined`, sha256 `fc24e69d…`), now graded for all ten models
on both halves; refusals are excluded from denominators.

## 4. Source and repository

Full tables: `by_source/source_tables.md`; figures `figures/A5_source_*.png`.
Mean across the ten models, OVERALL, each column pooled over models carrying
every stratum (N = observations):

| task | Nature | Science | Cell | HF Daily Papers | Top-10 AI Paper | Leaderboards |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.517 | 0.508 | 0.519 | 0.512 | 0.525 | **0.679** |
| MCQ (acc) | 0.711 | 0.685 | 0.696 | 0.683 | 0.700 | **0.529** |
| Date (score) | 0.280 | 0.248 | 0.291 | **0.502** | **0.538** | 0.464 |
| FRQ (0–10) | 4.16 | 4.10 | 4.32 | 4.32 | 4.34 | no items |

85 of 112 permutation tests are significant after Holm correction, so
**performance does vary across sources**. But the variation has exactly two
sources, and neither is a venue effect:

**(a) The date task is much easier on arXiv items.** Every one of the ten models
scores higher on arXiv than on journal items — 10/10 in both the post-cutoff and
overall partitions, median +0.27, range +0.07 (LLaMA 3.3) to +0.34 (Claude
Sonnet 5). This is visible as a step in every panel of
`figures/A5_source_overall.png`. The natural reading is that arXiv posting dates
follow a short, regular cadence while journal publication lags are long and
variable, so the target is intrinsically more predictable — not that models know
more about arXiv papers.

**(b) The leaderboard set behaves differently because it is a different item
type.** It is the only stratum where binary accuracy rises materially (0.679 vs
≈0.52) and the only one where MCQ falls materially (0.529 vs ≈0.69). It is 59
events, 1.1% of the corpus, and carries **no FRQ items at all**.

Binary, MCQ and FRQ are otherwise flat across the five paper sources — spreads
of 0.017, 0.028 and 0.24 points respectively across venues that differ by a
factor of eight in size.

### 4b. The confound, and the control (new analysis)

CUSP's source strata are **nested inside discipline by construction**: the two
arXiv feeds and the leaderboard set are 99–100% Artificial Intelligence, while
*Nature*, *Science* and *Cell* are 0–1.3%. Only **34 of 1,274 AI events (2.7%)
appear in a journal**. An arXiv-vs-journal contrast therefore cannot be
separated from an AI-vs-other-discipline contrast in this benchmark, and we do
not claim otherwise.

What we *can* do is hold discipline fixed and ask whether the venue still
matters. Seven disciplines carry two or more venues at n ≥ 100 (Biology and
Medicine with all three journals; Materials Science, Physics, Neuroscience and
Chemistry with *Nature* vs *Science*; AI with the two arXiv feeds) — 1,777
cells, 705 tests (`by_source/within_discipline.md`):

| discipline | venues | events | tests | Holm-significant |
|---|---|---|---|---|
| Biology | Nature, Science, Cell | 1,438 | 110 | 2 |
| Artificial Intelligence | HF Daily Papers, Top-10 AI Paper | 1,181 | 95 | 1 |
| Medicine | Nature, Cell, Science | 878 | 105 | 0 |
| Materials Science | Nature, Science | 460 | 110 | 1 |
| Physics | Nature, Science | 444 | 98 | 0 |
| Neuroscience | Nature, Science | 379 | 93 | 0 |
| Chemistry | Nature, Science | 226 | 94 | 0 |

**4 of 705.** The four are scattered across four different model × discipline ×
partition combinations with no pattern. **Once discipline is fixed, the venue an
event was published in does not predict how well any model does on it.** The
large raw source effect is a discipline effect — which the paper already
stratifies on — plus the date-task cadence difference described above.

## 5. Event visibility (citations)

Full tables: `by_visibility/visibility_tables.md`; figures
`figures/A5_visibility_*.png`. 481 events, original half, retrieved 2026-05-12.
Mean across the ten models, OVERALL:

| task | Q1 (≤8) | Q2 (≤22) | Q3 (≤59) | Q4 (>59) | Holm-significant |
|---|---|---|---|---|---|
| Binary (bal. acc) | 0.528 | 0.509 | 0.517 | 0.521 | 0 / 10 |
| MCQ (acc) | 0.693 | 0.712 | 0.703 | 0.740 | 0 / 10 |
| Date (score) | 0.319 | 0.346 | 0.298 | 0.338 | 4 / 10 |
| FRQ (0–10) | 4.26 | 4.20 | 4.27 | 4.18 | 0 / 10 |

**6 of 93 tests across all three partitions are significant, and every one of
them is on the date task.** Binary, MCQ and FRQ give 0 of 71. We take this as
evidence that how visible an event is does not bias our headline results.

One caution about how these columns must be read, because we got it wrong
ourselves on a first pass: a column average is only interpretable if every
column rests on the *same* models. Averaging whatever cells survive suppression
produces a clean monotone decline in MCQ and FRQ across quartiles that vanishes
once the panel is balanced — it was an artefact of different models dropping out
of different columns. All pooled columns reported here are balanced, and the
summariser enforces it.

### 5b. Supplementary Tables S19–S23, corrected and extended

The published citation-quartile tables report Δ_know and Δ_fore per quartile for
three models, and several of their cells rest on n = 1–3 — e.g. GPT-5.4 Q4
"+0.000 (n = 1)". We regenerated them with N, a paired bootstrap CI, and
suppression below n = 20, and extended the panel from three models to the seven
that have a complete web-search triple on the pinned 500
(`by_visibility/citation_gap_S19_S23.md`).

The regeneration **reproduces every published non-suppressed cell exactly** —
DeepSeek-R1 and Claude S4.5 at all four quartiles, GPT-5.4 at Q1, all to three
decimals with matching N — which validates the pipeline. Of 101 cells, **32 are
now suppressed** rather than printed, including all four unreadable ones. We
recommend the corrected tables replace S19–S23.

## 6. Publication latency

Full tables: `by_latency/latency_tables.md`. 708 extension events; no pre-cutoff
partition exists, so OVERALL = POST.

| task | 0 mo | 1 mo | 2–3 mo | Holm-significant |
|---|---|---|---|---|
| Binary (bal. acc) | 0.499 | 0.510 | 0.519 | 0 / 9 |
| MCQ (acc) | 0.722 | 0.658 | 0.732 | 0 / 9 |
| Date (score) | 0.277 | 0.267 | 0.274 | 0 / 9 |
| FRQ (0–10) | 4.12 | 4.11 | 4.27 | 0 / 9 |

**0 of 72 tests significant.** This is a clean null, but a weak one: the range
is only 0–3 months, it is right-censored, and for 96% of these events the
interval measured is "first indexed → published" rather than "preprint →
published". We report it as no evidence of a latency effect within a narrow
latency range, not as evidence that latency never matters.

## 7. Novelty — why we are not stratifying on it

We have no gold standard and no agreed proxy, and we decline to invent one.
`novelty_discussion.md` lists six candidates (citation count, venue prestige,
semantic distance from prior literature, rarity of the category combination,
novelty claims in the abstract, an LLM-judged departure score) with what each
would and would not capture. Two objections apply to all of them:

- **Circularity.** Novelty is close to the construct CUSP measures. A result
  that departs sharply from prior work is almost by definition harder to
  forecast. A novelty stratification showing lower performance on novel events
  would re-measure the benchmark's own target through a noisier instrument, not
  demonstrate a compositional bias.
- **Range restriction.** Every CUSP event was selected for being notable —
  published in *Nature*, *Science* or *Cell*, or curated onto a "top AI paper"
  list. The sampling frame is already truncated at the high end of novelty and
  visibility. Any within-benchmark stratification, including the citation
  analysis above, probes variation *inside* an already-selected band and can
  neither detect nor correct the selection that produced the band.

We think the second point is the honest answer to the reviewer's underlying
concern, and we prefer to state it as a limitation of the benchmark rather than
let a novelty table imply a control we do not have. A defensible novelty
instrument would need a definition, a validation against human ratings, and
inter-rater agreement — a study, not a table.

## 8. Proposed manuscript text

The manuscript source is not in this repository; these are standalone passages
to be placed as indicated, marked as proposed.

**[PROPOSED — Results, new subsection "Sensitivity to benchmark composition"]**

> To test whether our conclusions depend on how CUSP was assembled, we
> stratified every model's performance on all four tasks by source venue,
> citation quartile and publication latency, each reported pre-cutoff,
> post-cutoff and overall, with event-clustered bootstrap intervals and
> permutation tests corrected across the family (Supplementary Tables S24–S27).
> Performance varies significantly across source venues, but the variation is
> confined to the date task, where every model scores higher on arXiv-sourced
> events than on journal-sourced ones (10/10 models, median +0.27 date score) —
> consistent with arXiv's short and regular posting cadence making the target
> more predictable. Because CUSP's venues are nested within disciplines (the
> arXiv feeds are 99–100% artificial intelligence, the journals 0–1.3%), we
> repeated the analysis with discipline held fixed: of 705 model × task ×
> partition tests within the seven disciplines carrying two or more venues, four
> survive correction. Venue therefore does not predict performance once
> discipline is controlled. Citation quartile shows no effect on binary,
> mechanism or solution performance (0 of 71 tests), and publication latency
> shows no effect on any task (0 of 72 tests).

**[PROPOSED — Limitations]**

> Two limits of this benchmark's construction bound what the stratification
> above can establish. First, every CUSP event was selected for being notable —
> published in *Nature*, *Science* or *Cell*, or curated onto a widely-read
> preprint list — so the corpus is truncated at the high end of both visibility
> and novelty, and no within-benchmark stratification can detect the selection
> that produced that truncation. Second, source venue and scientific discipline
> are nearly collinear in CUSP: only 34 of 1,274 artificial-intelligence events
> appear in a journal, so an arXiv-versus-journal contrast cannot be fully
> separated from an AI-versus-other-discipline contrast. We report the
> discipline-controlled analysis for this reason and do not interpret the raw
> venue contrast causally.

**[PROPOSED — Limitations, novelty]**

> We do not stratify by novelty. We have no validated measure of it, and the
> available proxies are either confounded with venue and discipline or
> circular with the construct the benchmark measures: an event that departs
> sharply from prior work is, by construction, harder to forecast from
> pre-cutoff knowledge. Establishing a novelty measure — with a definition,
> validation against human judgement, and inter-rater agreement — is future
> work.

**[PROPOSED — replacement caption for Supplementary Tables S19–S23]**

> Knowledge gap (Δ_know) and foresight gap (Δ_fore) on post-cutoff instances,
> stratified by citation-count quartile, for the seven models with a complete
> web-search triple on the 500-event retrieval subset. Citation counts were
> retrieved from Semantic Scholar on 2026-05-12 over the 481 subset events for
> which a count resolved; quartile edges are ≤8, ≤22, ≤59, >59. Cells are the
> mean difference with a 95% paired bootstrap interval and N; cells with fewer
> than 20 paired observations are suppressed rather than reported as point
> estimates. These tables supersede the previously submitted S19–S23, which
> reported point estimates at N as low as 1.

**[PROPOSED — new Supplementary Table captions S24–S27]**

> **S24.** Performance by source venue, per model and task, pre-cutoff,
> post-cutoff and overall. Binary is balanced accuracy. Cells give the value, a
> 95% event-clustered bootstrap interval and N; cells below N = 20 are
> suppressed. p-values are permutation tests across strata, Holm-corrected.
> **S25.** The same analysis with scientific discipline held fixed, for the seven
> disciplines carrying two or more venues at N ≥ 100.
> **S26.** Performance by citation quartile, over the 481 events with citation
> counts (retrieved 2026-05-12).
> **S27.** Performance by publication latency, over the 708 extension events
> carrying both a first-indexed and a publication date. Latency range 0–3 months,
> right-censored by the extension window; this stratification has no pre-cutoff
> partition because the extension postdates every model cutoff.

## 9. Honest limitations of this analysis

- Visibility rests on **8.6%** of the corpus and a single citation snapshot that
  is now four months stale; latency on **12.7%**, post-cutoff only, over a
  0–3 month censored range.
- Venue and discipline are nearly collinear; the discipline-controlled analysis
  narrows but does not eliminate the confound, and it cannot compare arXiv
  against journals within AI (only 34 such journal events exist).
- Pre/post partition sizes differ by orders of magnitude across models; two
  models have no pre-cutoff partition at all.
- The leaderboard stratum (59 events) carries no FRQ items and is frequently
  suppressed in per-model splits.
- The permutation test detects *any* difference across strata; with N in the
  thousands it will flag differences too small to matter, which is why we report
  the magnitude of every range alongside its p-value.
- Two Claude models' FRQ responses are truncated at their token caps; the
  direction of that effect on scores is not established.
