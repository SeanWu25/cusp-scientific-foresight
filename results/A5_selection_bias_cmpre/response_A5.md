# Response to Reviewer 1, Comment 5 — benchmark selection bias (A5)

Supporting files in this directory: `metadata_audit.md` (what metadata exists and where it came from), `metadata/` (the 2026-09-25 Semantic Scholar / OpenAlex / Crossref snapshot, one JSONL per source), `by_source/`, `by_visibility/`, `by_vis_rate/`, `by_latency/`, `by_lat_review/` (full tables, CSV + markdown, all three partitions), `by_legacy/` (the first-pass 481- and 708-event tables, superseded), `tables/` (pooled), `figures/`, `novelty_discussion.md`, `MANIFEST.json` (git SHA, seeds, snapshot date, panel, coverage, partition sizes).

Regenerate with `results/A5_selection_bias/run_all.sh`. No inference; the only network step is the metadata snapshot, which is cached and never re-fetched. This document is written by `scripts/a5_make_response.py` from the stored CSVs — no number in it is typed by hand.

---

## 1. The reviewer's comment

> "Control benchmark selection bias by stratifying results across journals, repositories, event visibility, novelty, and publication latency."

## 2. Summary

Ten models, four tasks, 5,575 events. Every stratification is reported twice below — on the **whole dataset** and on the **post-cutoff partition only** (the forecasting regime the paper's claims rest on) — with the pre-cutoff partition in the supporting tables.

1. **Source / venue.** Performance differs across venues (77 of 100 tests significant after Holm correction), but the difference is confined to the date task and the leaderboard item type, and it disappears once discipline is held fixed (4 of 632 within-discipline tests). Every model scores higher on arXiv-sourced date items than on *Nature* items (9/9 models on the whole dataset, 9/9 post-cutoff; median +0.264 date score), which is a cadence property of the target, not knowledge about the papers.
2. **Event visibility, now on the whole corpus** (5,513 events with a citation count, 98.9%, versus 481 in the first pass). Citations predict performance **before** a model's cutoff and not after it. Pre-cutoff, the most-cited quartile beats the least-cited on FRQ for 5/6 models (median +0.224 on the 0–10 scale) and on MCQ for 5/6 (median +0.049); 11 of 28 pre-cutoff tests are significant. Post-cutoff the same contrasts are 4/6 (median +0.041) and 2/6 (median -0.028), binary is 3/6 (median +0.001), and 1 of 27 non-date post-cutoff tests are significant. Well-cited results are easier to *recall*, not easier to *forecast*. The age-adjusted citation-rate version gives the same picture (2 of 27 non-date post-cutoff tests).
3. **Publication latency, now on every journal event** (4,326 events, 77.6%, versus 708 in the first pass, and measuring the interval the reviewer means: how long a result was publicly observable before its journal version). 0 of 29 post-cutoff tests and 2 of 36 whole-dataset tests are significant. A second, independent latency — time in peer review, received → online, 3,740 *Nature* and *Science* events — gives 2 of 36 post-cutoff and 4 of 36 whole-dataset.
4. **Novelty** is not stratified; section 8 says why, and we prefer stating the limitation to inventing a proxy.

The paper's headline claims — near-chance binary forecasting, a large retrospective/prospective gap, no model beating a constant-month date baseline — hold within every paper venue (the 59 leaderboard items are a different item type, section 4), every citation quartile and every latency stratum of the post-cutoff partition.

## 3. What changed since the first pass, and what the metadata now supports

The first pass could stratify visibility on 481 events and latency on 708, because those were the only events carrying the fields. Both limits were limits of the *corpus files*, not of the events, so we took a single metadata snapshot on **2026-09-25** over the whole benchmark:

- **Citations**: Semantic Scholar batch API for every linked event (primary), OpenAlex as fallback for the 70 it did not resolve; 5,513 of the 5,516 linked events resolved (3 did not; the 59 leaderboard items have no paper). One snapshot, one date, both halves of the corpus. Against the May 2026 counts for the 481 first-pass events the new counts have Spearman ρ = 0.965, so the two snapshots agree on ordering and the earlier tables were not wrong, only narrow. Semantic Scholar is primary because OpenAlex credits most arXiv citations to the later journal version and returns near-zero counts for arXiv records.
- **Publication dates**: Crossref for every journal DOI (4,326 of 4,326 resolved), giving the journal version's online date, and — for *Nature* and *Science*, which deposit them — the manuscript received and accepted dates. Cell (Elsevier) deposits neither.


| stratification | events | share of 5,575 | scope | partitions |
|---|---|---|---|---|
| Journal / repository (`source`) | 5,575 | 100% | both halves | pre / post / overall |
| Event visibility -- citation quartile | 5,513 | 98.9% | both halves | pre / post / overall |
| Event visibility -- citation-rate quartile | 5,513 | 98.9% | both halves | pre / post / overall |
| Publication latency (observable before journal version) | 4,326 | 77.6% | all journal events, both halves | pre / post / overall |
| Editorial latency (received -> online) | 3,740 | 67.1% | Nature + Science, both halves | pre / post / overall |
| Novelty | 0 | -- | not computed (section 8) | -- |

**Journal and repository are one stratification.** Every `nature` DOI is `10.1038/s41586`, every `science` is `10.1126/science`, every `cell` is `10.1016/j.cell`, and both AI feeds are entirely arXiv — verified from the DOIs, not assumed. There are no sibling journals to separate and no singleton strata, so no "other" bucket is needed.

**Partition sizes are very unequal across models**, so whole-dataset numbers are not comparable *between* models (GPT-4o and LLaMA 3.3 have no pre-cutoff events; Claude Sonnet 5, Claude Opus 4.8 and GPT-5.6 Sol have few post-cutoff events). That is why the post-cutoff tables are the ones to read for the forecasting claim:

| model | cutoff | n events | pre-cutoff | post-cutoff |
|---|---|---|---|---|
| GPT-4o | 2023-10 | 5,575 | 0 | 5,575 |
| LLaMA 3.3 70B | 2023-12 | 5,575 | 0 | 5,575 |
| GPT-OSS 20B | 2024-06 | 5,575 | 842 | 4,733 |
| DeepSeek-R1 | 2024-07 | 4,760 | 1,028 | 3,732 |
| Claude S4.5 | 2025-01 | 5,575 | 2,124 | 3,451 |
| GPT-5.4 | 2025-08 | 5,575 | 3,587 | 1,988 |
| Claude Sonnet 5 | 2026-01 | 5,575 | 4,508 | 1,067 |
| GPT-5.6 Sol | 2026-02 | 5,575 | 4,719 | 856 |
| Claude Opus 4.8 | 2026-01 | 5,575 | 4,508 | 1,067 |

**Methods, unchanged from the first pass.** Binary is balanced accuracy (mean of recall on the real question and specificity on its perturbed twin). Every cell carries N and a 2,000-draw event-clustered bootstrap percentile CI; cells below n = 20 print `n<20` and no point estimate. Stratum effects use a 10,000-draw permutation test shuffling stratum labels across events, Holm–Bonferroni corrected across every model × partition × task test within a stratification. Pooled rows average only over models that carry every stratum unsuppressed, so every column of a pooled table rests on the same models (the count is printed). FRQ uses the published rubric (`judge_frq_combined`); refusals are excluded from denominators. With N in the thousands the permutation test flags differences too small to matter, so the size of every effect is printed next to its p-value.

## 4. Source and repository (all 5,575 events)

### 4.1 Whole dataset

| task | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | models pooled | Holm-sig |
|---|---|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.521 (28,080) | 0.510 (14,517) | 0.525 (5,630) | 0.515 (10,374) | 0.528 (3,722) | 0.681 (1,058) | 9 | 6 / 9 |
| MCQ (acc) | 0.716 (17,712) | 0.691 (9,079) | 0.703 (4,095) | 0.677 (6,717) | 0.693 (2,047) | 0.537 (524) | 9 | 9 / 9 |
| Date (score) | 0.292 (12,264) | 0.260 (6,333) | 0.302 (2,118) | 0.519 (3,387) | 0.552 (1,294) | 0.476 (529) | 9 | 9 / 9 |
| FRQ (0-10) | 4.18 (18,858) | 4.12 (8,894) | 4.34 (4,125) | 4.36 (7,215) | 4.38 (2,453) | no items | 9 | 9 / 9 |

### 4.2 Post-cutoff only

| task | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | models pooled | Holm-sig |
|---|---|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.493 (14,670) | 0.485 (7,561) | 0.489 (3,033) | 0.483 (5,731) | 0.489 (2,366) | 0.669 (682) | 8 | 4 / 9 |
| MCQ (acc) | 0.622 (8,804) | 0.575 (4,542) | 0.606 (2,129) | 0.541 (3,446) | 0.591 (1,230) | 0.369 (306) | 6 | 6 / 9 |
| Date (score) | 0.267 (5,784) | 0.244 (2,982) | 0.295 (1,035) | 0.460 (1,656) | 0.520 (791) | 0.455 (311) | 6 | 9 / 9 |
| FRQ (0-10) | 4.05 (10,091) | 4.02 (4,762) | 4.23 (2,275) | 4.23 (4,105) | 4.28 (1,558) | no items | 8 | 9 / 9 |

77 of 100 permutation tests are significant, so performance does vary across sources. The variation has two causes, neither a venue effect:

**(a) Date prediction is easier on arXiv items.** Every model scores higher on the arXiv feeds than on the journals — HF Daily Papers vs *Nature*: 9/9 models on the whole dataset (median +0.264, range +0.047 to +0.357) and 9/9 post-cutoff (median +0.271). arXiv posting follows a short, regular cadence while journal lags are long and variable, so the target itself is more predictable.

**(b) The leaderboard set is a different item type.** It is the only stratum where binary rises materially and MCQ falls; 59 events, no FRQ items.

Binary, MCQ and FRQ are otherwise flat across the five paper sources.

### 4.3 The confound, and the control

CUSP's venues are nested inside discipline: the arXiv feeds and the leaderboard set are 99–100% Artificial Intelligence, the journals 0–1.3%, and only 34 of 1,274 AI events appear in a journal. So we held discipline fixed and re-tested venue within each of the seven disciplines that carry two or more venues at n ≥ 100 (`by_source/within_discipline.md`):

| discipline | venues | events | tests | Holm-significant (p<0.05) |
|---|---|---|---|---|
| Biology | Nature, Science, Cell | 1,438 | 97 | **2** |
| Artificial Intelligence | HF Daily Papers (arXiv), Top-10 AI Paper of Week (arXiv) | 1,181 | 82 | **1** |
| Medicine | Nature, Cell, Science | 878 | 97 | **0** |
| Materials Science | Nature, Science | 460 | 97 | **1** |
| Physics | Nature, Science | 444 | 89 | **0** |
| Neuroscience | Nature, Science | 379 | 87 | **0** |
| Chemistry | Nature, Science | 226 | 83 | **0** |

**4 of 632.** Once discipline is fixed, the venue does not predict how well any model does. The raw source effect is a discipline effect — which the paper already stratifies on — plus the date-cadence difference above.

### 4.4 Per-model tables — whole dataset

**Binary (bal. acc)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.471 [0.459, 0.482] (3,219) | 0.472 [0.456, 0.487] (1,669) | 0.487 [0.458, 0.516] (661) | 0.475 [0.450, 0.500] (1,172) | 0.526 [0.482, 0.568] (414) | 0.653 [0.593, 0.712] (118) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 0.517 [0.508, 0.526] (3,195) | 0.504 [0.491, 0.516] (1,660) | 0.523 [0.506, 0.540] (654) | 0.503 [0.495, 0.511] (1,167) | 0.510 [0.497, 0.522] (414) | 0.579 [0.534, 0.630] (114) | 0.011 | 0.176 |
| GPT-OSS 20B | 2024-06 | 0.472 [0.459, 0.484] (3,218) | 0.475 [0.458, 0.492] (1,671) | 0.468 [0.438, 0.498] (662) | 0.446 [0.424, 0.468] (1,172) | 0.470 [0.433, 0.506] (414) | 0.720 [0.653, 0.780] (118) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 0.488 [0.471, 0.504] (2,797) | 0.469 [0.447, 0.493] (1,444) | 0.537 [0.499, 0.575] (573) | 0.453 [0.427, 0.483] (1,005) | 0.482 [0.442, 0.524] (410) | 0.585 [0.517, 0.653] (118) | 0.001 | **0.023** |
| Claude S4.5 | 2025-01 | 0.470 [0.455, 0.485] (3,009) | 0.455 [0.435, 0.475] (1,520) | 0.457 [0.417, 0.496] (554) | 0.532 [0.508, 0.556] (1,171) | 0.516 [0.477, 0.553] (414) | 0.678 [0.610, 0.746] (118) | 0.000 | **0.010** |
| GPT-5.4 | 2025-08 | 0.518 [0.502, 0.534] (3,219) | 0.510 [0.488, 0.531] (1,671) | 0.525 [0.489, 0.558] (662) | 0.512 [0.490, 0.533] (1,172) | 0.536 [0.495, 0.574] (414) | 0.653 [0.593, 0.712] (118) | 0.035 | 0.383 |
| Claude Sonnet 5 | 2026-01 | 0.576 [0.560, 0.591] (3,116) | 0.554 [0.533, 0.574] (1,610) | 0.536 [0.499, 0.576] (605) | 0.573 [0.548, 0.597] (1,171) | 0.565 [0.529, 0.602] (414) | 0.729 [0.661, 0.797] (118) | 0.001 | **0.027** |
| GPT-5.6 Sol | 2026-02 | 0.617 [0.604, 0.632] (3,216) | 0.602 [0.582, 0.622] (1,671) | 0.618 [0.587, 0.649] (662) | 0.565 [0.544, 0.584] (1,172) | 0.574 [0.545, 0.603] (414) | 0.805 [0.737, 0.864] (118) | 0.000 | **0.010** |
| Claude Opus 4.8 | 2026-01 | 0.563 [0.547, 0.579] (3,091) | 0.551 [0.529, 0.573] (1,601) | 0.574 [0.537, 0.610] (597) | 0.576 [0.550, 0.601] (1,172) | 0.570 [0.533, 0.608] (414) | 0.729 [0.669, 0.788] (118) | 0.002 | 0.051 |

**MCQ (acc)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.561 [0.541, 0.582] (2,093) | 0.488 [0.459, 0.517] (1,083) | 0.581 [0.536, 0.625] (499) | 0.440 [0.406, 0.476] (768) | 0.500 [0.432, 0.567] (230) | 0.305 [0.186, 0.424] (59) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 0.474 [0.454, 0.495] (2,074) | 0.440 [0.409, 0.469] (1,076) | 0.490 [0.446, 0.534] (492) | 0.319 [0.286, 0.353] (764) | 0.357 [0.295, 0.417] (230) | 0.298 [0.185, 0.421] (57) | 0.000 | **0.010** |
| GPT-OSS 20B | 2024-06 | 0.522 [0.500, 0.543] (2,092) | 0.478 [0.448, 0.508] (1,084) | 0.504 [0.460, 0.546] (500) | 0.362 [0.328, 0.395] (768) | 0.448 [0.385, 0.511] (230) | 0.237 [0.136, 0.339] (59) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 0.620 [0.596, 0.643] (1,579) | 0.596 [0.561, 0.631] (805) | 0.644 [0.593, 0.692] (374) | 0.496 [0.453, 0.534] (579) | 0.585 [0.519, 0.650] (207) | 0.556 [0.423, 0.685] (54) | 0.000 | **0.010** |
| Claude S4.5 | 2025-01 | 0.728 [0.707, 0.747] (1,909) | 0.692 [0.663, 0.721] (958) | 0.674 [0.630, 0.720] (408) | 0.798 [0.769, 0.827] (766) | 0.796 [0.741, 0.847] (230) | 0.492 [0.356, 0.627] (59) | 0.000 | **0.010** |
| GPT-5.4 | 2025-08 | 0.828 [0.811, 0.844] (2,093) | 0.830 [0.808, 0.852] (1,084) | 0.794 [0.758, 0.827] (500) | 0.841 [0.815, 0.866] (768) | 0.843 [0.795, 0.891] (230) | 0.542 [0.407, 0.661] (59) | 0.000 | **0.010** |
| Claude Sonnet 5 | 2026-01 | 0.903 [0.890, 0.916] (1,911) | 0.897 [0.877, 0.916] (960) | 0.903 [0.874, 0.930] (422) | 0.957 [0.942, 0.970] (768) | 0.909 [0.868, 0.942] (230) | 0.746 [0.644, 0.847] (59) | 0.000 | **0.010** |
| GPT-5.6 Sol | 2026-02 | 0.881 [0.866, 0.894] (2,076) | 0.872 [0.852, 0.892] (1,080) | 0.830 [0.796, 0.862] (493) | 0.914 [0.894, 0.933] (768) | 0.857 [0.811, 0.898] (230) | 0.797 [0.695, 0.898] (59) | 0.000 | **0.010** |
| Claude Opus 4.8 | 2026-01 | 0.932 [0.920, 0.943] (1,885) | 0.927 [0.910, 0.944] (949) | 0.907 [0.879, 0.933] (407) | 0.964 [0.950, 0.977] (768) | 0.948 [0.919, 0.974] (230) | 0.864 [0.763, 0.949] (59) | 0.001 | **0.031** |

**Date (score)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.145 [0.133, 0.157] (1,396) | 0.131 [0.116, 0.149] (723) | 0.169 [0.140, 0.200] (248) | 0.416 [0.388, 0.444] (380) | 0.499 [0.453, 0.545] (144) | 0.331 [0.254, 0.408] (59) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 0.473 [0.459, 0.487] (1,385) | 0.458 [0.439, 0.477] (720) | 0.501 [0.470, 0.532] (245) | 0.520 [0.497, 0.544] (379) | 0.588 [0.551, 0.625] (144) | 0.571 [0.509, 0.633] (57) | 0.000 | **0.010** |
| GPT-OSS 20B | 2024-06 | 0.271 [0.256, 0.287] (1,396) | 0.253 [0.232, 0.274] (724) | 0.292 [0.255, 0.331] (248) | 0.415 [0.386, 0.444] (380) | 0.520 [0.471, 0.571] (144) | 0.500 [0.408, 0.589] (59) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 0.250 [0.235, 0.264] (1,293) | 0.247 [0.228, 0.268] (670) | 0.340 [0.304, 0.379] (230) | 0.366 [0.335, 0.397] (348) | 0.499 [0.449, 0.548] (142) | 0.417 [0.345, 0.492] (59) | 0.000 | **0.010** |
| Claude S4.5 | 2025-01 | 0.197 [0.183, 0.211] (1,323) | 0.152 [0.135, 0.169] (675) | 0.218 [0.185, 0.259] (209) | 0.459 [0.429, 0.487] (380) | 0.483 [0.442, 0.526] (144) | 0.482 [0.430, 0.532] (59) | 0.000 | **0.010** |
| GPT-5.4 | 2025-08 | 0.197 [0.183, 0.211] (1,396) | 0.132 [0.114, 0.149] (724) | 0.201 [0.169, 0.238] (248) | 0.468 [0.439, 0.499] (380) | 0.521 [0.475, 0.569] (144) | 0.373 [0.310, 0.438] (59) | 0.000 | **0.010** |
| Claude Sonnet 5 | 2026-01 | 0.342 [0.328, 0.359] (1,345) | 0.343 [0.323, 0.363] (689) | 0.358 [0.320, 0.398] (224) | 0.699 [0.674, 0.726] (380) | 0.655 [0.614, 0.694] (144) | 0.601 [0.537, 0.663] (59) | 0.000 | **0.010** |
| GPT-5.6 Sol | 2026-02 | 0.345 [0.326, 0.365] (1,396) | 0.257 [0.233, 0.282] (724) | 0.263 [0.223, 0.305] (248) | 0.609 [0.575, 0.645] (380) | 0.525 [0.469, 0.583] (144) | 0.388 [0.303, 0.474] (59) | 0.000 | **0.010** |
| Claude Opus 4.8 | 2026-01 | 0.411 [0.394, 0.429] (1,334) | 0.362 [0.338, 0.385] (684) | 0.378 [0.338, 0.419] (218) | 0.723 [0.696, 0.750] (380) | 0.676 [0.636, 0.715] (144) | 0.624 [0.561, 0.684] (59) | 0.000 | **0.010** |

**FRQ (0-10)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.23 [3.19, 3.26] (2,164) | 3.19 [3.14, 3.25] (1,022) | 3.38 [3.30, 3.48] (483) | 3.41 [3.36, 3.47] (816) | 3.46 [3.35, 3.58] (273) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 3.50 [3.46, 3.53] (2,148) | 3.50 [3.45, 3.54] (1,017) | 3.64 [3.58, 3.70] (476) | 3.35 [3.30, 3.40] (810) | 3.37 [3.29, 3.47] (272) | 0.000 | **0.010** |
| GPT-OSS 20B | 2024-06 | 3.86 [3.82, 3.90] (2,159) | 3.76 [3.70, 3.82] (1,022) | 4.04 [3.96, 4.12] (482) | 3.88 [3.83, 3.93] (815) | 3.87 [3.78, 3.97] (273) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 4.14 [4.10, 4.18] (1,856) | 4.10 [4.04, 4.15] (869) | 4.35 [4.27, 4.43] (415) | 4.23 [4.18, 4.29] (690) | 4.32 [4.22, 4.40] (270) | 0.000 | **0.010** |
| Claude S4.5 | 2025-01 | 3.92 [3.89, 3.96] (2,018) | 3.84 [3.78, 3.90] (945) | 4.10 [4.00, 4.19] (414) | 4.21 [4.16, 4.26] (816) | 4.22 [4.14, 4.30] (273) | 0.000 | **0.010** |
| GPT-5.4 | 2025-08 | 4.99 [4.96, 5.02] (2,163) | 4.95 [4.89, 5.00] (1,021) | 5.13 [5.06, 5.20] (482) | 5.03 [4.98, 5.09] (817) | 5.12 [5.03, 5.21] (273) | 0.001 | **0.019** |
| Claude Sonnet 5 | 2026-01 | 4.43 [4.40, 4.47] (2,107) | 4.37 [4.31, 4.42] (989) | 4.57 [4.49, 4.64] (458) | 4.85 [4.79, 4.91] (817) | 4.79 [4.68, 4.91] (273) | 0.000 | **0.010** |
| GPT-5.6 Sol | 2026-02 | 4.93 [4.89, 4.97] (2,134) | 4.85 [4.79, 4.90] (1,012) | 5.05 [4.97, 5.13] (459) | 5.09 [5.02, 5.15] (817) | 5.05 [4.95, 5.16] (273) | 0.000 | **0.010** |
| Claude Opus 4.8 | 2026-01 | 4.64 [4.60, 4.68] (2,109) | 4.54 [4.48, 4.60] (997) | 4.81 [4.73, 4.89] (456) | 5.22 [5.16, 5.27] (817) | 5.17 [5.08, 5.28] (273) | 0.000 | **0.010** |

### 4.5 Per-model tables — post-cutoff only

**Binary (bal. acc)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.471 [0.459, 0.482] (3,219) | 0.472 [0.456, 0.487] (1,669) | 0.487 [0.458, 0.516] (661) | 0.475 [0.450, 0.500] (1,172) | 0.526 [0.482, 0.568] (414) | 0.653 [0.593, 0.712] (118) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 0.517 [0.508, 0.526] (3,195) | 0.504 [0.491, 0.516] (1,660) | 0.523 [0.506, 0.540] (654) | 0.503 [0.495, 0.511] (1,167) | 0.510 [0.497, 0.522] (414) | 0.579 [0.534, 0.630] (114) | 0.011 | 0.176 |
| GPT-OSS 20B | 2024-06 | 0.474 [0.460, 0.488] (2,586) | 0.473 [0.456, 0.493] (1,365) | 0.463 [0.428, 0.498] (559) | 0.439 [0.413, 0.465] (996) | 0.470 [0.433, 0.506] (414) | 0.720 [0.653, 0.780] (118) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 0.496 [0.477, 0.516] (2,040) | 0.465 [0.437, 0.492] (1,072) | 0.532 [0.489, 0.575] (448) | 0.445 [0.414, 0.477] (798) | 0.482 [0.442, 0.524] (410) | 0.585 [0.517, 0.653] (118) | 0.002 | **0.036** |
| Claude S4.5 | 2025-01 | 0.452 [0.433, 0.473] (1,657) | 0.450 [0.422, 0.478] (795) | 0.445 [0.393, 0.498] (316) | 0.495 [0.465, 0.527] (713) | 0.514 [0.476, 0.552] (411) | 0.670 [0.591, 0.750] (88) | 0.000 | **0.010** |
| GPT-5.4 | 2025-08 | 0.496 [0.468, 0.524] (996) | 0.497 [0.453, 0.540] (496) | 0.459 [0.393, 0.529] (202) | 0.510 [0.471, 0.547] (435) | 0.542 [0.482, 0.597] (199) | 0.682 [0.606, 0.758] (66) | 0.020 | 0.235 |
| Claude Sonnet 5 | 2026-01 | 0.536 [0.496, 0.579] (491) | 0.530 [0.484, 0.580] (253) | 0.524 [0.423, 0.633] (97) | 0.514 [0.442, 0.586] (225) | 0.439 [0.324, 0.563] (52) | 0.767 [0.633, 0.900] (30) | 0.096 | 0.766 |
| GPT-5.6 Sol | 2026-02 | 0.607 [0.557, 0.653] (396) | 0.588 [0.515, 0.650] (217) | 0.492 [0.359, 0.621] (88) | 0.469 [0.400, 0.532] (187) | n<20 (15) | -- | 0.007 | 0.119 |
| Claude Opus 4.8 | 2026-01 | 0.505 [0.468, 0.544] (486) | 0.490 [0.446, 0.539] (251) | 0.475 [0.386, 0.568] (96) | 0.479 [0.411, 0.546] (225) | 0.431 [0.344, 0.516] (52) | 0.700 [0.567, 0.833] (30) | 0.151 | 1.000 |

**MCQ (acc)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.561 [0.541, 0.582] (2,093) | 0.488 [0.459, 0.517] (1,083) | 0.581 [0.536, 0.625] (499) | 0.440 [0.406, 0.476] (768) | 0.500 [0.432, 0.567] (230) | 0.305 [0.186, 0.424] (59) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 0.474 [0.454, 0.495] (2,074) | 0.440 [0.409, 0.469] (1,076) | 0.490 [0.446, 0.534] (492) | 0.319 [0.286, 0.353] (764) | 0.357 [0.295, 0.417] (230) | 0.298 [0.185, 0.421] (57) | 0.000 | **0.010** |
| GPT-OSS 20B | 2024-06 | 0.525 [0.502, 0.550] (1,713) | 0.475 [0.443, 0.508] (897) | 0.492 [0.446, 0.540] (429) | 0.373 [0.336, 0.409] (660) | 0.448 [0.385, 0.511] (230) | 0.237 [0.136, 0.339] (59) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 0.615 [0.587, 0.643] (1,183) | 0.577 [0.537, 0.617] (607) | 0.649 [0.593, 0.703] (296) | 0.493 [0.449, 0.542] (471) | 0.585 [0.519, 0.650] (207) | 0.556 [0.423, 0.685] (54) | 0.000 | **0.010** |
| Claude S4.5 | 2025-01 | 0.711 [0.684, 0.737] (1,075) | 0.665 [0.623, 0.707] (529) | 0.668 [0.609, 0.728] (247) | 0.782 [0.744, 0.817] (481) | 0.799 [0.746, 0.849] (229) | 0.455 [0.318, 0.591] (44) | 0.000 | **0.010** |
| GPT-5.4 | 2025-08 | 0.845 [0.818, 0.873] (666) | 0.803 [0.757, 0.846] (350) | 0.759 [0.689, 0.822] (166) | 0.838 [0.797, 0.877] (302) | 0.856 [0.787, 0.920] (104) | 0.364 [0.212, 0.545] (33) | 0.000 | **0.010** |
| Claude Sonnet 5 | 2026-01 | 0.903 [0.870, 0.933] (318) | 0.883 [0.832, 0.929] (163) | 0.846 [0.763, 0.921] (78) | 0.970 [0.940, 0.994] (166) | 0.926 [0.810, 1.000] (27) | n<20 (15) | 0.016 | 0.211 |
| GPT-5.6 Sol | 2026-02 | 0.865 [0.822, 0.904] (267) | 0.862 [0.808, 0.915] (152) | 0.812 [0.718, 0.900] (69) | 0.906 [0.856, 0.951] (139) | n<20 (8) | -- | 0.287 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.916 [0.883, 0.946] (320) | 0.945 [0.909, 0.976] (163) | 0.868 [0.793, 0.940] (76) | 0.964 [0.935, 0.988] (166) | 0.963 [0.875, 1.000] (27) | n<20 (15) | 0.056 | 0.559 |

**Date (score)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.145 [0.133, 0.157] (1,396) | 0.131 [0.116, 0.149] (723) | 0.169 [0.140, 0.200] (248) | 0.416 [0.388, 0.444] (380) | 0.499 [0.453, 0.545] (144) | 0.331 [0.254, 0.408] (59) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 0.473 [0.459, 0.487] (1,385) | 0.458 [0.439, 0.477] (720) | 0.501 [0.470, 0.532] (245) | 0.520 [0.497, 0.544] (379) | 0.588 [0.551, 0.625] (144) | 0.571 [0.509, 0.633] (57) | 0.000 | **0.010** |
| GPT-OSS 20B | 2024-06 | 0.313 [0.294, 0.332] (1,069) | 0.287 [0.263, 0.312] (568) | 0.333 [0.290, 0.376] (202) | 0.464 [0.433, 0.496] (307) | 0.520 [0.471, 0.571] (144) | 0.500 [0.408, 0.589] (59) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 0.299 [0.280, 0.317] (904) | 0.285 [0.260, 0.313] (478) | 0.387 [0.346, 0.430] (175) | 0.415 [0.377, 0.452] (260) | 0.499 [0.449, 0.548] (142) | 0.417 [0.345, 0.492] (59) | 0.000 | **0.010** |
| Claude S4.5 | 2025-01 | 0.209 [0.192, 0.227] (676) | 0.179 [0.156, 0.204] (322) | 0.220 [0.179, 0.267] (106) | 0.507 [0.469, 0.544] (211) | 0.483 [0.440, 0.526] (144) | 0.534 [0.477, 0.587] (44) | 0.000 | **0.010** |
| GPT-5.4 | 2025-08 | 0.166 [0.143, 0.190] (354) | 0.122 [0.093, 0.153] (171) | 0.159 [0.109, 0.214] (59) | 0.438 [0.385, 0.494] (119) | 0.529 [0.462, 0.595] (73) | 0.378 [0.284, 0.471] (33) | 0.000 | **0.010** |
| Claude Sonnet 5 | 2026-01 | 0.178 [0.144, 0.218] (140) | 0.211 [0.159, 0.267] (70) | 0.227 [0.118, 0.370] (21) | 0.479 [0.411, 0.552] (52) | n<20 (19) | n<20 (15) | 0.000 | **0.010** |
| GPT-5.6 Sol | 2026-02 | 0.227 [0.198, 0.259] (97) | 0.168 [0.133, 0.206] (53) | n<20 (18) | 0.349 [0.297, 0.402] (41) | n<20 (6) | -- | 0.000 | **0.010** |
| Claude Opus 4.8 | 2026-01 | 0.163 [0.134, 0.194] (139) | 0.162 [0.117, 0.210] (70) | 0.154 [0.104, 0.211] (21) | 0.448 [0.380, 0.517] (52) | n<20 (19) | n<20 (15) | 0.000 | **0.010** |

**FRQ (0-10)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.23 [3.19, 3.26] (2,164) | 3.19 [3.14, 3.25] (1,022) | 3.38 [3.30, 3.48] (483) | 3.41 [3.36, 3.47] (816) | 3.46 [3.35, 3.58] (273) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 3.50 [3.46, 3.53] (2,148) | 3.50 [3.45, 3.54] (1,017) | 3.64 [3.58, 3.70] (476) | 3.35 [3.30, 3.40] (810) | 3.37 [3.29, 3.47] (272) | 0.000 | **0.010** |
| GPT-OSS 20B | 2024-06 | 3.85 [3.81, 3.90] (1,775) | 3.76 [3.70, 3.82] (849) | 4.04 [3.96, 4.13] (411) | 3.88 [3.83, 3.94] (712) | 3.87 [3.78, 3.97] (273) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 4.14 [4.10, 4.19] (1,397) | 4.11 [4.04, 4.17] (664) | 4.33 [4.23, 4.41] (334) | 4.26 [4.20, 4.31] (566) | 4.32 [4.22, 4.40] (270) | 0.000 | **0.010** |
| Claude S4.5 | 2025-01 | 3.94 [3.89, 3.99] (1,167) | 3.87 [3.80, 3.95] (531) | 4.10 [3.97, 4.21] (251) | 4.18 [4.12, 4.25] (524) | 4.22 [4.14, 4.30] (270) | 0.000 | **0.010** |
| GPT-5.4 | 2025-08 | 4.89 [4.83, 4.96] (709) | 4.92 [4.83, 5.01] (333) | 5.05 [4.93, 5.16] (156) | 5.04 [4.96, 5.13] (323) | 5.18 [5.04, 5.31] (128) | 0.001 | **0.031** |
| Claude Sonnet 5 | 2026-01 | 4.35 [4.26, 4.44] (364) | 4.40 [4.29, 4.52] (172) | 4.52 [4.34, 4.70] (82) | 4.71 [4.60, 4.82] (177) | 4.75 [4.43, 5.04] (36) | 0.000 | **0.010** |
| GPT-5.6 Sol | 2026-02 | 4.79 [4.70, 4.89] (289) | 4.72 [4.59, 4.86] (148) | 5.00 [4.81, 5.19] (64) | 5.05 [4.92, 5.16] (149) | n<20 (10) | 0.001 | **0.025** |
| Claude Opus 4.8 | 2026-01 | 4.47 [4.38, 4.56] (367) | 4.42 [4.29, 4.55] (174) | 4.74 [4.57, 4.91] (82) | 5.00 [4.89, 5.11] (177) | 5.11 [4.81, 5.40] (36) | 0.000 | **0.010** |

## 5. Event visibility (5,513 events with citation counts)

Two measures, both from the 2026-09-25 snapshot: the **raw count** (quartiles over all 5,513 events: Q1 (<=10), Q2 (<=28), Q3 (<=68), Q4 (>68)) and the **citation rate** — count divided by months from the first-observable date to the snapshot (quartiles Q1 (<=0.96/mo), Q2 (<=1.83/mo), Q3 (<=3.94/mo), Q4 (>3.94/mo)). Raw counts favour older events (an Apr–Aug 2026 event has had months to be cited, a Jan 2024 event two and a half years), so the rate version is the age-adjusted one and the one we treat as primary; we show both because the published S19–S23 used raw quartiles.

### 5.1 Whole dataset

Raw citation quartile:

| task | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.503 (13,281) | 0.505 (15,086) | 0.514 (16,818) | 0.524 (17,102) | 9 | 1 / 9 |
| MCQ (acc) | 0.697 (9,195) | 0.710 (9,704) | 0.702 (10,344) | 0.698 (10,380) | 9 | 3 / 9 |
| Date (score) | 0.318 (4,274) | 0.310 (6,349) | 0.312 (7,432) | 0.370 (7,323) | 9 | 9 / 9 |
| FRQ (0-10) | 4.18 (9,709) | 4.20 (10,138) | 4.23 (10,733) | 4.29 (10,938) | 9 | 5 / 9 |

Citation-rate quartile:

| task | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.506 (14,232) | 0.518 (14,867) | 0.506 (16,243) | 0.522 (16,945) | 9 | 0 / 9 |
| MCQ (acc) | 0.710 (9,585) | 0.709 (9,595) | 0.690 (10,011) | 0.699 (10,432) | 9 | 2 / 9 |
| Date (score) | 0.305 (5,393) | 0.299 (6,062) | 0.310 (7,031) | 0.391 (6,892) | 9 | 6 / 9 |
| FRQ (0-10) | 4.20 (9,975) | 4.18 (10,077) | 4.23 (10,557) | 4.30 (10,909) | 9 | 3 / 9 |

### 5.2 Post-cutoff only

Raw citation quartile:

| task | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.482 (8,166) | 0.479 (8,135) | 0.480 (7,807) | 0.482 (7,004) | 6 | 0 / 9 |
| MCQ (acc) | 0.599 (5,664) | 0.610 (5,292) | 0.593 (4,885) | 0.572 (4,294) | 6 | 1 / 9 |
| Date (score) | 0.342 (2,604) | 0.314 (3,353) | 0.303 (3,371) | 0.321 (2,910) | 6 | 4 / 9 |
| FRQ (0-10) | 3.95 (5,953) | 3.96 (5,534) | 4.00 (5,076) | 4.01 (4,545) | 6 | 0 / 9 |

Citation-rate quartile:

| task | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.497 (9,012) | 0.501 (8,348) | 0.479 (8,622) | 0.495 (8,261) | 9 | 0 / 9 |
| MCQ (acc) | 0.711 (6,136) | 0.707 (5,532) | 0.682 (5,460) | 0.690 (5,146) | 9 | 1 / 9 |
| Date (score) | 0.287 (3,141) | 0.273 (3,165) | 0.283 (3,533) | 0.328 (3,217) | 9 | 2 / 9 |
| FRQ (0-10) | 4.19 (6,484) | 4.14 (5,825) | 4.21 (5,699) | 4.27 (5,427) | 9 | 1 / 9 |

### 5.3 Reading

The visibility effect lives in the pre-cutoff partition. Raw quartiles, pre-cutoff: 11 of 28 tests significant (FRQ 3 of 7, MCQ 3 of 7, date 5 of 7); the most-cited quartile beats the least-cited on FRQ for 5/6 models (median +0.224, range -0.069 to +0.347) and on MCQ for 5/6 (median +0.049). Post-cutoff: binary 0 of 9, MCQ 1 of 9, FRQ 0 of 9, date 4 of 9; the same Q4−Q1 contrasts are FRQ 4/6 (median +0.041), MCQ 2/6 (median -0.028), binary 3/6 (median +0.001). Citation-rate quartiles: 11 of 28 pre-cutoff, 4 of 36 post-cutoff (2 of them on the date task), 11 of 36 whole-dataset; post-cutoff Q4−Q1 is binary 3/9 (median -0.002) and FRQ 8/9 (median +0.059, none significant).

This is the pattern one expects if citation count indexes how often a result appears in training data: well-cited papers are recalled better (pre-cutoff FRQ and MCQ), but a paper's eventual visibility does not make its outcome easier to *forecast* from pre-cutoff knowledge. It also means the benchmark's headline post-cutoff numbers are not inflated by a few famous results.

The date task is the exception in both versions (9 of 9 whole-dataset tests significant on raw quartiles, 6 of 9 on rate), and it is the task on which no model has skill. On raw quartiles the direction is split (5/9 models favour Q4), which is what an age confound looks like: raw Q1 is dominated by the newest events, and the horizon study (Reviewer 1, comment 4) shows the date score depends on horizon through anchoring. On rate quartiles the direction is consistent (7/9 post-cutoff, 7/7 pre-cutoff favour Q4) and modest (post-cutoff median +0.051).

One caution that the first pass taught us: a pooled column is only interpretable when every column rests on the same models. Averaging whatever cells survive suppression manufactured a monotone MCQ/FRQ decline across quartiles that vanished on a balanced panel. Every pooled table here is balanced and prints the model count.

### 5.4 Per-model tables — raw citation quartile, whole dataset

**Binary (bal. acc)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.468 [0.447, 0.489] (1,592) | 0.471 [0.455, 0.488] (1,721) | 0.467 [0.452, 0.483] (1,901) | 0.474 [0.459, 0.489] (1,917) | 0.938 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.506 [0.495, 0.517] (1,587) | 0.514 [0.502, 0.526] (1,705) | 0.519 [0.508, 0.530] (1,883) | 0.504 [0.493, 0.515] (1,911) | 0.199 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.459 [0.439, 0.478] (1,592) | 0.472 [0.455, 0.489] (1,721) | 0.468 [0.453, 0.484] (1,903) | 0.465 [0.448, 0.481] (1,917) | 0.784 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.494 [0.463, 0.525] (866) | 0.470 [0.449, 0.491] (1,610) | 0.478 [0.457, 0.498] (1,867) | 0.480 [0.460, 0.500] (1,882) | 0.659 | 1.000 |
| Claude S4.5 | 2025-01 | 0.469 [0.446, 0.491] (1,407) | 0.444 [0.424, 0.464] (1,593) | 0.472 [0.452, 0.493] (1,797) | 0.508 [0.489, 0.528] (1,867) | 0.000 | **0.015** |
| GPT-5.4 | 2025-08 | 0.490 [0.467, 0.514] (1,592) | 0.505 [0.484, 0.526] (1,721) | 0.522 [0.502, 0.542] (1,904) | 0.515 [0.497, 0.534] (1,917) | 0.174 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.534 [0.512, 0.556] (1,535) | 0.541 [0.520, 0.563] (1,656) | 0.547 [0.525, 0.569] (1,836) | 0.584 [0.565, 0.604] (1,885) | 0.004 | 0.256 |
| GPT-5.6 Sol | 2026-02 | 0.590 [0.569, 0.611] (1,591) | 0.597 [0.577, 0.616] (1,720) | 0.591 [0.574, 0.607] (1,903) | 0.609 [0.593, 0.625] (1,917) | 0.376 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.520 [0.498, 0.542] (1,519) | 0.532 [0.512, 0.553] (1,639) | 0.558 [0.538, 0.578] (1,824) | 0.577 [0.558, 0.596] (1,889) | 0.001 | 0.071 |

**MCQ (acc)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.487 [0.459, 0.516] (1,133) | 0.543 [0.513, 0.572] (1,145) | 0.534 [0.506, 0.561] (1,205) | 0.529 [0.500, 0.557] (1,187) | 0.040 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.432 [0.404, 0.460] (1,130) | 0.470 [0.442, 0.499] (1,132) | 0.442 [0.414, 0.470] (1,189) | 0.404 [0.377, 0.431] (1,182) | 0.013 | 0.791 |
| GPT-OSS 20B | 2024-06 | 0.508 [0.479, 0.536] (1,133) | 0.519 [0.490, 0.549] (1,145) | 0.487 [0.459, 0.515] (1,206) | 0.406 [0.380, 0.434] (1,187) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 0.596 [0.556, 0.637] (535) | 0.627 [0.596, 0.658] (928) | 0.597 [0.568, 0.627] (1,048) | 0.561 [0.532, 0.593] (1,030) | 0.027 | 1.000 |
| Claude S4.5 | 2025-01 | 0.740 [0.712, 0.767] (953) | 0.716 [0.688, 0.743] (1,043) | 0.725 [0.700, 0.751] (1,122) | 0.742 [0.716, 0.766] (1,150) | 0.486 | 1.000 |
| GPT-5.4 | 2025-08 | 0.828 [0.805, 0.850] (1,133) | 0.831 [0.809, 0.852] (1,145) | 0.814 [0.793, 0.836] (1,207) | 0.837 [0.817, 0.858] (1,187) | 0.505 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.897 [0.878, 0.916] (1,032) | 0.891 [0.872, 0.910] (1,028) | 0.913 [0.896, 0.929] (1,088) | 0.942 [0.928, 0.956] (1,140) | 0.000 | **0.015** |
| GPT-5.6 Sol | 2026-02 | 0.853 [0.832, 0.875] (1,126) | 0.865 [0.845, 0.885] (1,135) | 0.874 [0.855, 0.892] (1,200) | 0.915 [0.900, 0.931] (1,183) | 0.000 | **0.015** |
| Claude Opus 4.8 | 2026-01 | 0.931 [0.916, 0.947] (1,020) | 0.927 [0.911, 0.943] (1,003) | 0.930 [0.915, 0.946] (1,079) | 0.949 [0.935, 0.961] (1,134) | 0.162 | 1.000 |

**Date (score)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.336 [0.308, 0.366] (503) | 0.184 [0.165, 0.202] (723) | 0.139 [0.125, 0.155] (842) | 0.180 [0.163, 0.197] (821) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 0.449 [0.427, 0.471] (500) | 0.532 [0.514, 0.552] (717) | 0.496 [0.478, 0.514] (834) | 0.449 [0.432, 0.466] (820) | 0.000 | **0.010** |
| GPT-OSS 20B | 2024-06 | 0.375 [0.348, 0.404] (503) | 0.315 [0.291, 0.338] (723) | 0.277 [0.256, 0.298] (843) | 0.261 [0.244, 0.280] (821) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 0.384 [0.351, 0.416] (336) | 0.322 [0.301, 0.343] (697) | 0.270 [0.252, 0.287] (836) | 0.229 [0.213, 0.247] (812) | 0.000 | **0.010** |
| Claude S4.5 | 2025-01 | 0.278 [0.254, 0.303] (459) | 0.219 [0.200, 0.239] (676) | 0.208 [0.190, 0.227] (794) | 0.263 [0.243, 0.283] (800) | 0.000 | **0.010** |
| GPT-5.4 | 2025-08 | 0.198 [0.176, 0.221] (503) | 0.199 [0.178, 0.220] (723) | 0.209 [0.190, 0.228] (843) | 0.307 [0.284, 0.330] (821) | 0.000 | **0.010** |
| Claude Sonnet 5 | 2026-01 | 0.299 [0.273, 0.322] (485) | 0.335 [0.312, 0.357] (687) | 0.408 [0.388, 0.427] (801) | 0.538 [0.516, 0.560] (807) | 0.000 | **0.010** |
| GPT-5.6 Sol | 2026-02 | 0.259 [0.237, 0.282] (503) | 0.297 [0.272, 0.323] (723) | 0.336 [0.312, 0.361] (843) | 0.502 [0.473, 0.529] (821) | 0.000 | **0.010** |
| Claude Opus 4.8 | 2026-01 | 0.281 [0.259, 0.304] (482) | 0.384 [0.359, 0.407] (680) | 0.466 [0.444, 0.488] (796) | 0.602 [0.578, 0.625] (800) | 0.000 | **0.010** |

**FRQ (0-10)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.33 [3.28, 3.38] (1,161) | 3.23 [3.18, 3.28] (1,158) | 3.26 [3.20, 3.31] (1,212) | 3.30 [3.25, 3.35] (1,224) | 0.041 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.45 [3.41, 3.49] (1,157) | 3.46 [3.42, 3.51] (1,147) | 3.51 [3.47, 3.55] (1,197) | 3.49 [3.45, 3.53] (1,219) | 0.127 | 1.000 |
| GPT-OSS 20B | 2024-06 | 3.86 [3.81, 3.92] (1,159) | 3.90 [3.84, 3.95] (1,156) | 3.86 [3.81, 3.91] (1,210) | 3.83 [3.78, 3.87] (1,223) | 0.299 | 1.000 |
| DeepSeek-R1 | 2024-07 | 4.18 [4.11, 4.24] (612) | 4.18 [4.13, 4.23] (1,079) | 4.18 [4.13, 4.23] (1,192) | 4.18 [4.14, 4.23] (1,214) | 0.997 | 1.000 |
| Claude S4.5 | 2025-01 | 3.96 [3.90, 4.01] (1,053) | 3.93 [3.87, 3.98] (1,073) | 4.00 [3.95, 4.05] (1,143) | 4.08 [4.03, 4.12] (1,194) | 0.000 | **0.015** |
| GPT-5.4 | 2025-08 | 4.91 [4.86, 4.96] (1,160) | 5.01 [4.97, 5.06] (1,154) | 5.07 [5.03, 5.12] (1,215) | 5.04 [5.00, 5.08] (1,224) | 0.000 | **0.010** |
| Claude Sonnet 5 | 2026-01 | 4.45 [4.40, 4.50] (1,130) | 4.49 [4.44, 4.54] (1,117) | 4.48 [4.42, 4.53] (1,183) | 4.68 [4.63, 4.73] (1,211) | 0.000 | **0.010** |
| GPT-5.6 Sol | 2026-02 | 4.89 [4.84, 4.93] (1,145) | 4.92 [4.86, 4.97] (1,132) | 4.96 [4.91, 5.01] (1,197) | 5.05 [5.00, 5.11] (1,218) | 0.000 | **0.015** |
| Claude Opus 4.8 | 2026-01 | 4.63 [4.58, 4.68] (1,132) | 4.68 [4.62, 4.73] (1,122) | 4.77 [4.71, 4.82] (1,184) | 4.97 [4.92, 5.03] (1,211) | 0.000 | **0.010** |

### 5.5 Per-model tables — raw citation quartile, post-cutoff only

**Binary (bal. acc)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.468 [0.447, 0.489] (1,592) | 0.471 [0.455, 0.488] (1,721) | 0.467 [0.452, 0.483] (1,901) | 0.474 [0.459, 0.489] (1,917) | 0.938 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.506 [0.495, 0.517] (1,587) | 0.514 [0.502, 0.526] (1,705) | 0.519 [0.508, 0.530] (1,883) | 0.504 [0.493, 0.515] (1,911) | 0.199 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.459 [0.439, 0.480] (1,569) | 0.474 [0.455, 0.493] (1,550) | 0.467 [0.449, 0.486] (1,488) | 0.460 [0.439, 0.480] (1,309) | 0.693 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.493 [0.462, 0.523] (838) | 0.475 [0.451, 0.499] (1,392) | 0.476 [0.453, 0.500] (1,372) | 0.479 [0.454, 0.504] (1,162) | 0.823 | 1.000 |
| Claude S4.5 | 2025-01 | 0.471 [0.448, 0.494] (1,317) | 0.443 [0.419, 0.465] (1,116) | 0.456 [0.429, 0.483] (861) | 0.499 [0.468, 0.528] (594) | 0.043 | 1.000 |
| GPT-5.4 | 2025-08 | 0.494 [0.467, 0.522] (1,263) | 0.499 [0.465, 0.533] (651) | 0.493 [0.440, 0.542] (302) | 0.477 [0.397, 0.552] (111) | 0.977 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.517 [0.487, 0.549] (869) | 0.526 [0.460, 0.594] (188) | 0.561 [0.404, 0.723] (44) | n<20 (17) | 0.838 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.557 [0.522, 0.593] (757) | 0.579 [0.494, 0.657] (111) | 0.607 [0.407, 0.773] (27) | n<20 (8) | 0.809 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.482 [0.453, 0.509] (862) | 0.509 [0.444, 0.576] (187) | 0.439 [0.306, 0.599] (44) | n<20 (17) | 0.584 | 1.000 |

**MCQ (acc)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.487 [0.459, 0.516] (1,133) | 0.543 [0.513, 0.572] (1,145) | 0.534 [0.506, 0.561] (1,205) | 0.529 [0.500, 0.557] (1,187) | 0.040 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.432 [0.404, 0.460] (1,130) | 0.470 [0.442, 0.499] (1,132) | 0.442 [0.414, 0.470] (1,189) | 0.404 [0.377, 0.431] (1,182) | 0.013 | 0.791 |
| GPT-OSS 20B | 2024-06 | 0.505 [0.478, 0.534] (1,114) | 0.519 [0.489, 0.549] (1,041) | 0.469 [0.438, 0.499] (954) | 0.408 [0.374, 0.442] (817) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 0.595 [0.551, 0.637] (513) | 0.621 [0.588, 0.654] (808) | 0.583 [0.549, 0.618] (785) | 0.540 [0.502, 0.578] (655) | 0.021 | 1.000 |
| Claude S4.5 | 2025-01 | 0.742 [0.712, 0.771] (884) | 0.697 [0.664, 0.730] (742) | 0.717 [0.681, 0.753] (551) | 0.706 [0.660, 0.751] (381) | 0.221 | 1.000 |
| GPT-5.4 | 2025-08 | 0.835 [0.811, 0.859] (890) | 0.809 [0.772, 0.846] (424) | 0.816 [0.761, 0.869] (201) | 0.847 [0.757, 0.923] (72) | 0.633 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.914 [0.891, 0.935] (591) | 0.882 [0.820, 0.935] (119) | 0.867 [0.735, 0.968] (30) | n<20 (12) | 0.413 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.872 [0.843, 0.902] (533) | 0.823 [0.731, 0.903] (79) | n<20 (18) | n<20 (5) | 0.235 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.929 [0.908, 0.949] (591) | 0.915 [0.862, 0.965] (118) | 0.968 [0.900, 1.000] (31) | n<20 (12) | 0.585 | 1.000 |

**Date (score)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.336 [0.308, 0.366] (503) | 0.184 [0.165, 0.202] (723) | 0.139 [0.125, 0.155] (842) | 0.180 [0.163, 0.197] (821) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 0.449 [0.427, 0.471] (500) | 0.532 [0.514, 0.552] (717) | 0.496 [0.478, 0.514] (834) | 0.449 [0.432, 0.466] (820) | 0.000 | **0.010** |
| GPT-OSS 20B | 2024-06 | 0.380 [0.352, 0.406] (490) | 0.341 [0.314, 0.367] (632) | 0.329 [0.303, 0.354] (636) | 0.322 [0.298, 0.347] (530) | 0.018 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.396 [0.362, 0.430] (320) | 0.353 [0.328, 0.377] (586) | 0.317 [0.293, 0.341] (587) | 0.287 [0.262, 0.312] (464) | 0.000 | **0.010** |
| Claude S4.5 | 2025-01 | 0.290 [0.263, 0.316] (419) | 0.249 [0.225, 0.273] (449) | 0.253 [0.224, 0.281] (356) | 0.321 [0.283, 0.358] (233) | 0.002 | 0.128 |
| GPT-5.4 | 2025-08 | 0.204 [0.179, 0.231] (372) | 0.225 [0.190, 0.262] (246) | 0.286 [0.229, 0.346] (116) | 0.368 [0.273, 0.468] (42) | 0.001 | **0.040** |
| Claude Sonnet 5 | 2026-01 | 0.238 [0.205, 0.276] (228) | 0.324 [0.257, 0.391] (58) | n<20 (11) | n<20 (5) | 0.027 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.223 [0.202, 0.246] (179) | 0.260 [0.186, 0.343] (28) | n<20 (6) | n<20 (2) | 0.267 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.208 [0.181, 0.235] (227) | 0.291 [0.228, 0.358] (58) | n<20 (11) | n<20 (5) | 0.010 | 0.624 |

**FRQ (0-10)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.33 [3.28, 3.38] (1,161) | 3.23 [3.18, 3.28] (1,158) | 3.26 [3.20, 3.31] (1,212) | 3.30 [3.25, 3.35] (1,224) | 0.041 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.45 [3.41, 3.49] (1,157) | 3.46 [3.42, 3.51] (1,147) | 3.51 [3.47, 3.55] (1,197) | 3.49 [3.45, 3.53] (1,219) | 0.127 | 1.000 |
| GPT-OSS 20B | 2024-06 | 3.86 [3.81, 3.91] (1,141) | 3.89 [3.84, 3.94] (1,057) | 3.86 [3.81, 3.92] (975) | 3.82 [3.76, 3.88] (844) | 0.462 | 1.000 |
| DeepSeek-R1 | 2024-07 | 4.18 [4.11, 4.24] (589) | 4.18 [4.13, 4.23] (956) | 4.19 [4.13, 4.24] (908) | 4.22 [4.16, 4.28] (775) | 0.738 | 1.000 |
| Claude S4.5 | 2025-01 | 3.97 [3.92, 4.03] (985) | 3.97 [3.91, 4.03] (774) | 4.07 [4.00, 4.13] (575) | 4.12 [4.04, 4.19] (406) | 0.004 | 0.223 |
| GPT-5.4 | 2025-08 | 4.90 [4.84, 4.95] (920) | 5.02 [4.94, 5.09] (442) | 5.10 [5.00, 5.20] (209) | 5.13 [4.95, 5.29] (77) | 0.001 | 0.066 |
| Claude Sonnet 5 | 2026-01 | 4.45 [4.39, 4.51] (661) | 4.50 [4.33, 4.66] (125) | 4.58 [4.32, 4.86] (33) | n<20 (12) | 0.599 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 4.85 [4.78, 4.91] (562) | 5.00 [4.81, 5.19] (77) | n<20 (17) | n<20 (4) | 0.127 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 4.61 [4.55, 4.68] (666) | 4.62 [4.48, 4.76] (125) | 4.83 [4.47, 5.17] (33) | n<20 (12) | 0.395 | 1.000 |

### 5.6 Per-model tables — citation-rate quartile, whole dataset

**Binary (bal. acc)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.465 [0.448, 0.483] (1,665) | 0.468 [0.451, 0.484] (1,713) | 0.465 [0.449, 0.481] (1,845) | 0.471 [0.455, 0.488] (1,908) | 0.947 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.507 [0.495, 0.518] (1,655) | 0.513 [0.500, 0.525] (1,701) | 0.514 [0.504, 0.524] (1,830) | 0.504 [0.494, 0.515] (1,900) | 0.539 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.454 [0.436, 0.470] (1,665) | 0.484 [0.467, 0.502] (1,714) | 0.462 [0.446, 0.479] (1,846) | 0.459 [0.443, 0.476] (1,908) | 0.083 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.471 [0.446, 0.497] (1,296) | 0.502 [0.478, 0.525] (1,455) | 0.466 [0.446, 0.487] (1,699) | 0.473 [0.454, 0.494] (1,775) | 0.133 | 1.000 |
| Claude S4.5 | 2025-01 | 0.473 [0.453, 0.495] (1,473) | 0.462 [0.440, 0.483] (1,569) | 0.456 [0.436, 0.476] (1,751) | 0.507 [0.488, 0.526] (1,871) | 0.002 | 0.131 |
| GPT-5.4 | 2025-08 | 0.494 [0.472, 0.517] (1,665) | 0.518 [0.495, 0.539] (1,714) | 0.508 [0.488, 0.528] (1,847) | 0.517 [0.500, 0.536] (1,908) | 0.380 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.549 [0.528, 0.570] (1,584) | 0.556 [0.535, 0.577] (1,649) | 0.543 [0.523, 0.562] (1,797) | 0.584 [0.564, 0.604] (1,882) | 0.026 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.599 [0.579, 0.619] (1,664) | 0.605 [0.586, 0.625] (1,713) | 0.592 [0.574, 0.608] (1,846) | 0.604 [0.588, 0.619] (1,908) | 0.702 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.540 [0.518, 0.562] (1,565) | 0.551 [0.530, 0.573] (1,639) | 0.550 [0.530, 0.570] (1,782) | 0.578 [0.559, 0.599] (1,885) | 0.068 | 1.000 |

**MCQ (acc)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.528 [0.497, 0.557] (1,156) | 0.517 [0.487, 0.546] (1,146) | 0.526 [0.497, 0.555] (1,174) | 0.523 [0.495, 0.552] (1,194) | 0.952 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.466 [0.438, 0.496] (1,148) | 0.450 [0.421, 0.478] (1,136) | 0.436 [0.408, 0.465] (1,162) | 0.396 [0.369, 0.423] (1,187) | 0.005 | 0.324 |
| GPT-OSS 20B | 2024-06 | 0.529 [0.500, 0.557] (1,156) | 0.521 [0.494, 0.550] (1,147) | 0.450 [0.422, 0.478] (1,174) | 0.420 [0.393, 0.448] (1,194) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 0.627 [0.593, 0.659] (793) | 0.614 [0.582, 0.648] (830) | 0.581 [0.549, 0.613] (935) | 0.565 [0.533, 0.595] (983) | 0.027 | 1.000 |
| Claude S4.5 | 2025-01 | 0.733 [0.706, 0.760] (995) | 0.727 [0.699, 0.753] (1,017) | 0.716 [0.687, 0.743] (1,091) | 0.746 [0.720, 0.770] (1,165) | 0.443 | 1.000 |
| GPT-5.4 | 2025-08 | 0.821 [0.799, 0.842] (1,156) | 0.841 [0.820, 0.861] (1,147) | 0.812 [0.790, 0.834] (1,175) | 0.836 [0.814, 0.856] (1,194) | 0.214 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.897 [0.879, 0.916] (1,024) | 0.909 [0.891, 0.925] (1,028) | 0.897 [0.878, 0.915] (1,069) | 0.940 [0.925, 0.953] (1,167) | 0.001 | 0.059 |
| GPT-5.6 Sol | 2026-02 | 0.861 [0.840, 0.880] (1,148) | 0.870 [0.850, 0.888] (1,135) | 0.862 [0.842, 0.883] (1,170) | 0.916 [0.900, 0.931] (1,191) | 0.000 | **0.016** |
| Claude Opus 4.8 | 2026-01 | 0.928 [0.912, 0.943] (1,009) | 0.931 [0.915, 0.946] (1,009) | 0.933 [0.918, 0.947] (1,061) | 0.946 [0.934, 0.959] (1,157) | 0.291 | 1.000 |

**Date (score)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.235 [0.211, 0.259] (623) | 0.182 [0.162, 0.201] (695) | 0.155 [0.140, 0.172] (797) | 0.220 [0.202, 0.239] (774) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 0.458 [0.438, 0.478] (619) | 0.490 [0.470, 0.510] (688) | 0.499 [0.481, 0.518] (791) | 0.482 [0.464, 0.499] (773) | 0.027 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.328 [0.304, 0.351] (623) | 0.285 [0.263, 0.307] (695) | 0.276 [0.256, 0.297] (798) | 0.313 [0.293, 0.334] (774) | 0.004 | 0.259 |
| DeepSeek-R1 | 2024-07 | 0.315 [0.290, 0.339] (538) | 0.290 [0.267, 0.313] (631) | 0.276 [0.257, 0.295] (769) | 0.270 [0.249, 0.290] (743) | 0.021 | 1.000 |
| Claude S4.5 | 2025-01 | 0.236 [0.213, 0.259] (567) | 0.205 [0.185, 0.225] (646) | 0.218 [0.199, 0.237] (757) | 0.290 [0.269, 0.312] (759) | 0.000 | **0.010** |
| GPT-5.4 | 2025-08 | 0.194 [0.173, 0.217] (623) | 0.198 [0.177, 0.218] (695) | 0.207 [0.188, 0.227] (798) | 0.320 [0.297, 0.343] (774) | 0.000 | **0.010** |
| Claude Sonnet 5 | 2026-01 | 0.341 [0.318, 0.365] (592) | 0.350 [0.329, 0.371] (662) | 0.389 [0.369, 0.410] (763) | 0.531 [0.509, 0.553] (763) | 0.000 | **0.010** |
| GPT-5.6 Sol | 2026-02 | 0.272 [0.247, 0.297] (623) | 0.288 [0.262, 0.313] (695) | 0.338 [0.313, 0.363] (798) | 0.518 [0.488, 0.545] (774) | 0.000 | **0.010** |
| Claude Opus 4.8 | 2026-01 | 0.370 [0.346, 0.396] (585) | 0.405 [0.382, 0.430] (655) | 0.433 [0.410, 0.457] (760) | 0.578 [0.554, 0.601] (758) | 0.000 | **0.010** |

**FRQ (0-10)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.28 [3.23, 3.33] (1,166) | 3.25 [3.19, 3.30] (1,163) | 3.27 [3.21, 3.32] (1,200) | 3.33 [3.28, 3.38] (1,226) | 0.148 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.47 [3.43, 3.51] (1,156) | 3.47 [3.42, 3.51] (1,156) | 3.50 [3.46, 3.55] (1,188) | 3.47 [3.43, 3.51] (1,220) | 0.618 | 1.000 |
| GPT-OSS 20B | 2024-06 | 3.92 [3.86, 3.97] (1,166) | 3.82 [3.77, 3.88] (1,160) | 3.86 [3.80, 3.91] (1,199) | 3.85 [3.80, 3.89] (1,223) | 0.067 | 1.000 |
| DeepSeek-R1 | 2024-07 | 4.18 [4.13, 4.23] (881) | 4.16 [4.11, 4.21] (978) | 4.16 [4.11, 4.21] (1,090) | 4.21 [4.17, 4.26] (1,148) | 0.414 | 1.000 |
| Claude S4.5 | 2025-01 | 3.92 [3.86, 3.97] (1,052) | 3.91 [3.85, 3.96] (1,072) | 4.02 [3.97, 4.07] (1,132) | 4.11 [4.07, 4.15] (1,207) | 0.000 | **0.010** |
| GPT-5.4 | 2025-08 | 4.96 [4.92, 5.01] (1,163) | 4.96 [4.91, 5.01] (1,161) | 5.07 [5.02, 5.11] (1,202) | 5.04 [5.00, 5.08] (1,227) | 0.002 | 0.173 |
| Claude Sonnet 5 | 2026-01 | 4.47 [4.42, 4.52] (1,125) | 4.47 [4.41, 4.52] (1,122) | 4.49 [4.44, 4.55] (1,175) | 4.67 [4.61, 4.72] (1,219) | 0.000 | **0.010** |
| GPT-5.6 Sol | 2026-02 | 4.91 [4.86, 4.97] (1,141) | 4.93 [4.88, 4.98] (1,139) | 4.95 [4.90, 5.01] (1,190) | 5.03 [4.98, 5.08] (1,222) | 0.018 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 4.69 [4.64, 4.74] (1,125) | 4.63 [4.58, 4.69] (1,126) | 4.74 [4.68, 4.79] (1,181) | 4.99 [4.94, 5.04] (1,217) | 0.000 | **0.010** |

### 5.7 Per-model tables — citation-rate quartile, post-cutoff only

**Binary (bal. acc)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.465 [0.448, 0.483] (1,665) | 0.468 [0.451, 0.484] (1,713) | 0.465 [0.449, 0.481] (1,845) | 0.471 [0.455, 0.488] (1,908) | 0.947 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.507 [0.495, 0.518] (1,655) | 0.513 [0.500, 0.525] (1,701) | 0.514 [0.504, 0.524] (1,830) | 0.504 [0.494, 0.515] (1,900) | 0.539 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.455 [0.435, 0.475] (1,477) | 0.487 [0.467, 0.507] (1,410) | 0.459 [0.440, 0.477] (1,539) | 0.455 [0.435, 0.474] (1,490) | 0.070 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.479 [0.452, 0.507] (1,061) | 0.507 [0.481, 0.533] (1,102) | 0.463 [0.439, 0.487] (1,322) | 0.472 [0.447, 0.496] (1,279) | 0.092 | 1.000 |
| Claude S4.5 | 2025-01 | 0.484 [0.460, 0.511] (1,032) | 0.442 [0.415, 0.468] (938) | 0.443 [0.418, 0.468] (1,015) | 0.481 [0.454, 0.506] (903) | 0.021 | 1.000 |
| GPT-5.4 | 2025-08 | 0.494 [0.459, 0.527] (800) | 0.498 [0.460, 0.534] (615) | 0.466 [0.428, 0.505] (540) | 0.531 [0.487, 0.576] (372) | 0.241 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.530 [0.486, 0.573] (467) | 0.537 [0.489, 0.584] (308) | 0.492 [0.422, 0.566] (197) | 0.506 [0.420, 0.590] (146) | 0.725 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.565 [0.517, 0.613] (392) | 0.570 [0.509, 0.630] (256) | 0.504 [0.400, 0.606] (138) | 0.572 [0.487, 0.650] (117) | 0.581 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.493 [0.454, 0.534] (463) | 0.486 [0.444, 0.529] (305) | 0.503 [0.433, 0.571] (196) | 0.461 [0.387, 0.539] (146) | 0.832 | 1.000 |

**MCQ (acc)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.528 [0.497, 0.557] (1,156) | 0.517 [0.487, 0.546] (1,146) | 0.526 [0.497, 0.555] (1,174) | 0.523 [0.495, 0.552] (1,194) | 0.952 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.466 [0.438, 0.496] (1,148) | 0.450 [0.421, 0.478] (1,136) | 0.436 [0.408, 0.465] (1,162) | 0.396 [0.369, 0.423] (1,187) | 0.005 | 0.324 |
| GPT-OSS 20B | 2024-06 | 0.526 [0.496, 0.556] (1,034) | 0.509 [0.477, 0.540] (967) | 0.450 [0.418, 0.481] (983) | 0.430 [0.400, 0.463] (942) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 0.621 [0.585, 0.658] (659) | 0.610 [0.572, 0.648] (644) | 0.571 [0.536, 0.610] (730) | 0.549 [0.513, 0.586] (728) | 0.026 | 1.000 |
| Claude S4.5 | 2025-01 | 0.732 [0.701, 0.762] (709) | 0.709 [0.673, 0.746] (615) | 0.709 [0.673, 0.746] (653) | 0.721 [0.684, 0.757] (581) | 0.746 | 1.000 |
| GPT-5.4 | 2025-08 | 0.823 [0.790, 0.854] (548) | 0.840 [0.805, 0.873] (432) | 0.799 [0.758, 0.840] (364) | 0.848 [0.798, 0.890] (243) | 0.358 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.919 [0.887, 0.949] (309) | 0.912 [0.873, 0.948] (204) | 0.880 [0.821, 0.930] (142) | 0.907 [0.846, 0.962] (97) | 0.618 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.871 [0.828, 0.909] (264) | 0.868 [0.817, 0.915] (182) | 0.832 [0.759, 0.897] (113) | 0.895 [0.819, 0.961] (76) | 0.628 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.913 [0.879, 0.943] (309) | 0.947 [0.912, 0.975] (206) | 0.935 [0.892, 0.977] (139) | 0.939 [0.888, 0.981] (98) | 0.486 | 1.000 |

**Date (score)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.235 [0.211, 0.259] (623) | 0.182 [0.162, 0.201] (695) | 0.155 [0.140, 0.172] (797) | 0.220 [0.202, 0.239] (774) | 0.000 | **0.010** |
| LLaMA 3.3 70B | 2023-12 | 0.458 [0.438, 0.478] (619) | 0.490 [0.470, 0.510] (688) | 0.499 [0.481, 0.518] (791) | 0.482 [0.464, 0.499] (773) | 0.027 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.362 [0.336, 0.391] (524) | 0.331 [0.303, 0.359] (544) | 0.312 [0.288, 0.335] (639) | 0.365 [0.339, 0.390] (581) | 0.011 | 0.689 |
| DeepSeek-R1 | 2024-07 | 0.363 [0.335, 0.390] (418) | 0.336 [0.308, 0.364] (454) | 0.321 [0.298, 0.345] (575) | 0.321 [0.295, 0.348] (510) | 0.109 | 1.000 |
| Claude S4.5 | 2025-01 | 0.280 [0.250, 0.310] (358) | 0.241 [0.215, 0.268] (352) | 0.245 [0.220, 0.271] (405) | 0.332 [0.301, 0.363] (342) | 0.000 | **0.016** |
| GPT-5.4 | 2025-08 | 0.219 [0.186, 0.256] (250) | 0.196 [0.164, 0.231] (200) | 0.235 [0.196, 0.275] (197) | 0.306 [0.254, 0.361] (129) | 0.005 | 0.328 |
| Claude Sonnet 5 | 2026-01 | 0.242 [0.194, 0.291] (128) | 0.237 [0.185, 0.292] (84) | 0.294 [0.222, 0.373] (51) | 0.334 [0.251, 0.430] (39) | 0.180 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.208 [0.177, 0.241] (94) | 0.241 [0.202, 0.279] (64) | 0.227 [0.168, 0.293] (27) | 0.302 [0.223, 0.382] (30) | 0.056 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.216 [0.178, 0.253] (127) | 0.202 [0.162, 0.244] (84) | 0.261 [0.194, 0.327] (51) | 0.294 [0.211, 0.386] (39) | 0.120 | 1.000 |

**FRQ (0-10)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.28 [3.23, 3.33] (1,166) | 3.25 [3.19, 3.30] (1,163) | 3.27 [3.21, 3.32] (1,200) | 3.33 [3.28, 3.38] (1,226) | 0.148 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.47 [3.43, 3.51] (1,156) | 3.47 [3.42, 3.51] (1,156) | 3.50 [3.46, 3.55] (1,188) | 3.47 [3.43, 3.51] (1,220) | 0.618 | 1.000 |
| GPT-OSS 20B | 2024-06 | 3.90 [3.85, 3.95] (1,052) | 3.84 [3.78, 3.89] (988) | 3.86 [3.80, 3.92] (1,006) | 3.84 [3.79, 3.89] (971) | 0.301 | 1.000 |
| DeepSeek-R1 | 2024-07 | 4.17 [4.11, 4.23] (743) | 4.17 [4.11, 4.23] (774) | 4.18 [4.13, 4.24] (854) | 4.23 [4.18, 4.28] (857) | 0.399 | 1.000 |
| Claude S4.5 | 2025-01 | 3.98 [3.91, 4.04] (775) | 3.94 [3.87, 4.01] (669) | 4.01 [3.95, 4.08] (677) | 4.14 [4.08, 4.19] (619) | 0.000 | **0.016** |
| GPT-5.4 | 2025-08 | 4.93 [4.86, 4.99] (579) | 4.89 [4.81, 4.97] (443) | 5.04 [4.96, 5.12] (372) | 5.08 [4.99, 5.17] (254) | 0.007 | 0.436 |
| Claude Sonnet 5 | 2026-01 | 4.47 [4.39, 4.56] (360) | 4.37 [4.26, 4.49] (223) | 4.47 [4.33, 4.60] (146) | 4.69 [4.52, 4.85] (102) | 0.020 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 4.85 [4.76, 4.94] (291) | 4.82 [4.70, 4.93] (184) | 4.93 [4.77, 5.10] (109) | 4.89 [4.70, 5.07] (76) | 0.716 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 4.65 [4.56, 4.73] (362) | 4.54 [4.43, 4.66] (225) | 4.58 [4.45, 4.71] (147) | 4.81 [4.64, 4.97] (102) | 0.067 | 1.000 |

### 5.8 The first-pass 481-event tables, and Supplementary Tables S19–S23

The 481-event version (Semantic Scholar, retrieved 2026-05-12, pinned retrieval subset) is kept under `by_legacy/visibility_481/` for continuity: 7 of 87 tests significant, 0 of 66 outside the date task — consistent with the whole-corpus result, just underpowered.

The published S19–S23 report Δ_know and Δ_fore per citation quartile for three models, with several cells resting on n = 1–3 (GPT-5.4 Q4 "+0.000 (n = 1)"). We regenerated them with N, a paired bootstrap CI and suppression below n = 20, extended from three models to the seven with a complete web-search triple on the pinned 500 (`by_visibility/citation_gap_S19_S23.md`). The regeneration reproduces every published non-suppressed cell to three decimals with matching N; of 101 cells, 32 are now suppressed rather than printed. They necessarily keep the May 2026 quartile edges (≤8, ≤22, ≤59) because they reproduce the published tables. We recommend the corrected tables replace S19–S23.

## 6. Publication latency (4,326 journal events)

**Definition.** Latency = the journal version's online-publication month (Crossref) minus the first-observable month: the earlier of CUSP's `publication_date` — which the build pipeline had already set to the earliest date found across Crossref, bioRxiv, medRxiv, Semantic Scholar and Europe PMC — and any Crossref-linked preprint's posted month (the dating correction below). It is the number of months a result was publicly observable before its journal version appeared: 0 means no earlier public trace exists, larger values mean a preprint or other public record preceded the journal. It is computable for every *Nature*, *Science* and *Cell* event in both halves of the corpus; arXiv events have no journal version and are excluded by construction. Strata: 0 mo, 1-6 mo, >6 mo — 84% of journal events have latency 0, 5% are 1–6 months, 11% exceed six months (the longest is 54 months); finer bins fall below n = 20 in most per-model post-cutoff cells.

### 6.1 Whole dataset

| task | 0 mo | 1-6 mo | >6 mo | models pooled | Holm-sig |
|---|---|---|---|---|---|
| Binary (bal. acc) | 0.519 (40,118) | 0.507 (2,699) | 0.519 (5,410) | 9 | 0 / 9 |
| MCQ (acc) | 0.703 (25,775) | 0.738 (1,789) | 0.727 (3,322) | 9 | 0 / 9 |
| Date (score) | 0.284 (16,862) | 0.288 (1,284) | 0.276 (2,569) | 9 | 2 / 9 |
| FRQ (0-10) | 4.18 (26,669) | 4.20 (1,769) | 4.19 (3,439) | 9 | 0 / 9 |

### 6.2 Post-cutoff only

| task | 0 mo | 1-6 mo | >6 mo | models pooled | Holm-sig |
|---|---|---|---|---|---|
| Binary (bal. acc) | 0.482 (20,122) | 0.456 (1,212) | 0.489 (2,256) | 6 | 0 / 9 |
| MCQ (acc) | 0.601 (13,247) | 0.644 (827) | 0.641 (1,401) | 6 | 0 / 6 |
| Date (score) | 0.289 (7,649) | 0.281 (549) | 0.265 (1,019) | 5 | 0 / 6 |
| FRQ (0-10) | 3.94 (13,614) | 3.93 (815) | 3.89 (1,458) | 6 | 0 / 8 |

**0 of 29 post-cutoff, 0 of 28 pre-cutoff, 2 of 36 whole-dataset tests are significant** (post-cutoff by task: binary 0 of 9, MCQ 0 of 6, FRQ 0 of 8, date 0 of 6). Post-cutoff, the longest-latency stratum versus the zero-latency stratum: binary 6/9 models higher (median +0.009), MCQ 4/6 (+0.064), FRQ 3/8 (-0.009), date 2/6 (-0.017).

**A dating correction this pass surfaced.** Crossref links a preprint to 493 journal events; for 246 of them the preprint was posted *before* CUSP's `publication_date` (median 11 months earlier, IQR 7–15), i.e. the build pipeline's earliest-date search missed them. The latency above uses the earlier of the two dates. The cutoff partition keeps the benchmark's own date, so the table below counts, per model, how many of its post-cutoff journal events had a preprint before its cutoff — observable-before-cutoff items the benchmark treats as prospective:

| model | cutoff | post-cutoff journal events | with a preprint before the cutoff | share |
|---|---|---|---|---|
| GPT-4o | 2023-10 | 4,326 | 69 | 1.6% |
| LLaMA 3.3 70B | 2023-12 | 4,326 | 83 | 1.9% |
| GPT-OSS 20B | 2024-06 | 3,606 | 109 | 3.0% |
| DeepSeek-R1 | 2024-07 | 3,445 | 104 | 3.0% |
| Claude S4.5 | 2025-01 | 2,550 | 92 | 3.6% |
| GPT-5.4 | 2025-08 | 1,469 | 71 | 4.8% |
| Claude Sonnet 5 | 2026-01 | 824 | 34 | 4.1% |
| GPT-5.6 Sol | 2026-02 | 684 | 25 | 3.7% |
| Claude Opus 4.8 | 2026-01 | 824 | 34 | 4.1% |

These are 1.6–4.8% of each model's post-cutoff journal events, and by construction they sit in the non-zero latency strata, so the post-cutoff latency tables above are the test of whether they inflate the forecasting numbers: they do not (0 of 29 post-cutoff tests).

### 6.3 Editorial latency (received → online), 3,740 *Nature* and *Science* events

A different construct: how long the manuscript sat in review. Strata: <=6 mo, 7-12 mo, 13-24 mo, >24 mo.

Whole dataset:

| task | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.516 (8,233) | 0.515 (19,276) | 0.523 (13,275) | 0.519 (1,777) | 9 | 0 / 9 |
| MCQ (acc) | 0.701 (4,906) | 0.707 (11,909) | 0.712 (8,811) | 0.713 (1,147) | 9 | 0 / 9 |
| Date (score) | 0.270 (3,912) | 0.283 (8,507) | 0.286 (5,442) | 0.276 (718) | 9 | 0 / 9 |
| FRQ (0-10) | 4.04 (4,975) | 4.15 (12,290) | 4.23 (9,253) | 4.18 (1,225) | 9 | 4 / 9 |

Post-cutoff only:

| task | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.488 (4,080) | 0.503 (10,373) | 0.514 (7,376) | 0.486 (983) | 9 | 0 / 9 |
| MCQ (acc) | 0.671 (2,437) | 0.682 (6,338) | 0.686 (4,876) | 0.696 (643) | 8 | 0 / 9 |
| Date (score) | 0.251 (1,680) | 0.280 (3,832) | 0.304 (2,397) | 0.281 (322) | 5 | 1 / 9 |
| FRQ (0-10) | 3.89 (2,487) | 4.02 (6,602) | 4.11 (5,091) | 4.11 (665) | 8 | 1 / 9 |

2 of 36 post-cutoff, 2 of 28 pre-cutoff, 4 of 36 whole-dataset tests significant, and every significant one but a single date test is on FRQ. The pattern is a small, monotone rise in FRQ score with time in review: 13–24 months versus ≤6 months is higher for 9/9 models post-cutoff (median +0.205 on the 0–10 scale) and 7/7 pre-cutoff (median +0.187); binary and MCQ are flat (0 of 25 and 0 of 25 across all partitions). Because it appears in the pre- and post-cutoff partitions alike, it is a property of the items — longer-reviewed papers draw higher rubric scores for their proposed solutions — not a knowledge or cutoff artefact, and it does not touch the binary or mechanism results.

### 6.4 Per-model tables — latency, whole dataset

**Binary (bal. acc)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.473 [0.464, 0.484] (4,628) | 0.481 [0.448, 0.511] (307) | 0.467 [0.444, 0.491] (614) | 0.844 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.514 [0.507, 0.521] (4,590) | 0.503 [0.479, 0.528] (307) | 0.515 [0.493, 0.537] (612) | 0.758 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.469 [0.458, 0.480] (4,630) | 0.479 [0.441, 0.518] (307) | 0.487 [0.462, 0.513] (614) | 0.484 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.489 [0.474, 0.503] (3,935) | 0.472 [0.423, 0.521] (298) | 0.480 [0.441, 0.517] (581) | 0.763 | 1.000 |
| Claude S4.5 | 2025-01 | 0.461 [0.448, 0.474] (4,218) | 0.464 [0.417, 0.514] (282) | 0.479 [0.444, 0.514] (583) | 0.621 | 1.000 |
| GPT-5.4 | 2025-08 | 0.519 [0.506, 0.532] (4,631) | 0.466 [0.414, 0.520] (307) | 0.513 [0.480, 0.547] (614) | 0.135 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.565 [0.551, 0.578] (4,449) | 0.549 [0.498, 0.600] (292) | 0.563 [0.528, 0.600] (590) | 0.826 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.615 [0.604, 0.626] (4,629) | 0.602 [0.556, 0.646] (307) | 0.606 [0.574, 0.638] (613) | 0.745 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.561 [0.548, 0.574] (4,408) | 0.545 [0.494, 0.596] (292) | 0.559 [0.524, 0.597] (589) | 0.836 | 1.000 |

**MCQ (acc)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.530 [0.512, 0.548] (3,077) | 0.604 [0.539, 0.668] (212) | 0.609 [0.561, 0.660] (386) | 0.003 | 0.267 |
| LLaMA 3.3 70B | 2023-12 | 0.465 [0.445, 0.483] (3,046) | 0.509 [0.439, 0.573] (212) | 0.456 [0.406, 0.504] (384) | 0.412 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.499 [0.481, 0.517] (3,078) | 0.542 [0.475, 0.608] (212) | 0.544 [0.493, 0.592] (386) | 0.136 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.614 [0.593, 0.635] (2,248) | 0.648 [0.581, 0.717] (179) | 0.616 [0.565, 0.665] (331) | 0.666 | 1.000 |
| Claude S4.5 | 2025-01 | 0.704 [0.687, 0.721] (2,724) | 0.757 [0.695, 0.816] (189) | 0.735 [0.689, 0.779] (362) | 0.168 | 1.000 |
| GPT-5.4 | 2025-08 | 0.821 [0.808, 0.835] (3,079) | 0.849 [0.799, 0.897] (212) | 0.832 [0.794, 0.868] (386) | 0.533 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.899 [0.888, 0.910] (2,755) | 0.913 [0.872, 0.951] (184) | 0.910 [0.880, 0.939] (354) | 0.718 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.865 [0.853, 0.877] (3,058) | 0.899 [0.857, 0.938] (208) | 0.906 [0.877, 0.934] (383) | 0.034 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.926 [0.916, 0.936] (2,710) | 0.923 [0.883, 0.962] (181) | 0.937 [0.911, 0.961] (350) | 0.731 | 1.000 |

**Date (score)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.152 [0.142, 0.163] (1,930) | 0.111 [0.082, 0.144] (146) | 0.102 [0.082, 0.124] (291) | 0.001 | 0.091 |
| LLaMA 3.3 70B | 2023-12 | 0.477 [0.465, 0.489] (1,915) | 0.475 [0.428, 0.521] (146) | 0.431 [0.399, 0.462] (289) | 0.022 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.275 [0.262, 0.288] (1,931) | 0.238 [0.195, 0.284] (146) | 0.230 [0.201, 0.262] (291) | 0.023 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.264 [0.252, 0.277] (1,765) | 0.276 [0.232, 0.324] (144) | 0.213 [0.183, 0.241] (284) | 0.010 | 0.851 |
| Claude S4.5 | 2025-01 | 0.185 [0.173, 0.196] (1,793) | 0.195 [0.150, 0.243] (134) | 0.183 [0.153, 0.215] (280) | 0.886 | 1.000 |
| GPT-5.4 | 2025-08 | 0.176 [0.164, 0.188] (1,931) | 0.153 [0.115, 0.199] (146) | 0.200 [0.168, 0.235] (291) | 0.191 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.332 [0.320, 0.345] (1,841) | 0.398 [0.347, 0.450] (139) | 0.396 [0.361, 0.431] (278) | 0.000 | **0.028** |
| GPT-5.6 Sol | 2026-02 | 0.316 [0.300, 0.333] (1,931) | 0.301 [0.245, 0.356] (146) | 0.270 [0.233, 0.307] (291) | 0.116 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.379 [0.365, 0.394] (1,825) | 0.442 [0.388, 0.497] (137) | 0.460 [0.425, 0.496] (274) | 0.000 | **0.019** |

**FRQ (0-10)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.24 [3.21, 3.28] (3,073) | 3.13 [3.00, 3.27] (203) | 3.24 [3.14, 3.33] (393) | 0.251 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.51 [3.49, 3.54] (3,047) | 3.46 [3.36, 3.56] (203) | 3.55 [3.48, 3.63] (391) | 0.311 | 1.000 |
| GPT-OSS 20B | 2024-06 | 3.85 [3.82, 3.89] (3,068) | 3.88 [3.75, 4.01] (203) | 3.84 [3.75, 3.93] (392) | 0.894 | 1.000 |
| DeepSeek-R1 | 2024-07 | 4.16 [4.13, 4.19] (2,576) | 4.15 [4.03, 4.27] (193) | 4.11 [4.03, 4.20] (371) | 0.590 | 1.000 |
| Claude S4.5 | 2025-01 | 3.94 [3.90, 3.97] (2,823) | 3.90 [3.76, 4.04] (187) | 3.84 [3.74, 3.93] (367) | 0.159 | 1.000 |
| GPT-5.4 | 2025-08 | 4.99 [4.96, 5.02] (3,071) | 5.05 [4.93, 5.16] (203) | 5.03 [4.95, 5.12] (392) | 0.395 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 4.43 [4.40, 4.47] (2,990) | 4.53 [4.40, 4.66] (190) | 4.38 [4.28, 4.48] (374) | 0.166 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 4.91 [4.88, 4.95] (3,028) | 4.92 [4.79, 5.05] (194) | 4.99 [4.89, 5.09] (383) | 0.347 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 4.62 [4.58, 4.65] (2,993) | 4.76 [4.63, 4.89] (193) | 4.70 [4.61, 4.81] (376) | 0.031 | 1.000 |

### 6.5 Per-model tables — latency, post-cutoff only

**Binary (bal. acc)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.473 [0.464, 0.484] (4,628) | 0.481 [0.448, 0.511] (307) | 0.467 [0.444, 0.491] (614) | 0.844 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.514 [0.507, 0.521] (4,590) | 0.503 [0.479, 0.528] (307) | 0.515 [0.493, 0.537] (612) | 0.758 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.468 [0.456, 0.480] (3,866) | 0.496 [0.454, 0.542] (227) | 0.496 [0.464, 0.531] (417) | 0.210 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.493 [0.477, 0.510] (3,004) | 0.460 [0.409, 0.511] (206) | 0.484 [0.438, 0.534] (350) | 0.574 | 1.000 |
| Claude S4.5 | 2025-01 | 0.449 [0.433, 0.465] (2,459) | 0.458 [0.388, 0.531] (117) | 0.469 [0.417, 0.522] (192) | 0.795 | 1.000 |
| GPT-5.4 | 2025-08 | 0.496 [0.472, 0.519] (1,575) | 0.339 [0.223, 0.459] (48) | 0.505 [0.398, 0.610] (71) | 0.084 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.529 [0.499, 0.561] (800) | n<20 (10) | 0.557 [0.363, 0.757] (31) | 0.750 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.592 [0.556, 0.627] (668) | n<20 (9) | 0.556 [0.300, 0.816] (24) | 0.747 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.494 [0.466, 0.525] (792) | n<20 (10) | 0.538 [0.400, 0.688] (31) | 0.584 | 1.000 |

**MCQ (acc)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.530 [0.512, 0.548] (3,077) | 0.604 [0.539, 0.668] (212) | 0.609 [0.561, 0.660] (386) | 0.003 | 0.267 |
| LLaMA 3.3 70B | 2023-12 | 0.465 [0.445, 0.483] (3,046) | 0.509 [0.439, 0.573] (212) | 0.456 [0.406, 0.504] (384) | 0.412 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.501 [0.481, 0.519] (2,620) | 0.541 [0.457, 0.619] (159) | 0.535 [0.475, 0.593] (260) | 0.391 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.609 [0.586, 0.631] (1,760) | 0.624 [0.537, 0.710] (125) | 0.597 [0.531, 0.665] (201) | 0.884 | 1.000 |
| Claude S4.5 | 2025-01 | 0.686 [0.664, 0.707] (1,648) | 0.723 [0.624, 0.814] (83) | 0.750 [0.670, 0.826] (120) | 0.286 | 1.000 |
| GPT-5.4 | 2025-08 | 0.816 [0.793, 0.838] (1,096) | 0.861 [0.735, 0.971] (36) | 0.900 [0.808, 0.979] (50) | 0.262 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.887 [0.859, 0.915] (533) | n<20 (8) | n<20 (18) | -- | -- |
| GPT-5.6 Sol | 2026-02 | 0.858 [0.827, 0.889] (466) | n<20 (9) | n<20 (13) | -- | -- |
| Claude Opus 4.8 | 2026-01 | 0.919 [0.896, 0.942] (534) | n<20 (8) | n<20 (17) | -- | -- |

**Date (score)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.152 [0.142, 0.163] (1,930) | 0.111 [0.082, 0.144] (146) | 0.102 [0.082, 0.124] (291) | 0.001 | 0.091 |
| LLaMA 3.3 70B | 2023-12 | 0.477 [0.465, 0.489] (1,915) | 0.475 [0.428, 0.521] (146) | 0.431 [0.399, 0.462] (289) | 0.022 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.311 [0.297, 0.328] (1,547) | 0.290 [0.231, 0.346] (104) | 0.285 [0.242, 0.327] (188) | 0.464 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.304 [0.288, 0.319] (1,298) | 0.333 [0.273, 0.393] (97) | 0.287 [0.245, 0.332] (162) | 0.474 | 1.000 |
| Claude S4.5 | 2025-01 | 0.200 [0.186, 0.214] (959) | 0.194 [0.129, 0.265] (56) | 0.219 [0.167, 0.275] (89) | 0.748 | 1.000 |
| GPT-5.4 | 2025-08 | 0.149 [0.131, 0.168] (539) | n<20 (18) | 0.219 [0.130, 0.326] (27) | 0.103 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.197 [0.165, 0.229] (220) | n<20 (3) | n<20 (8) | -- | -- |
| GPT-5.6 Sol | 2026-02 | 0.200 [0.176, 0.223] (160) | n<20 (2) | n<20 (6) | -- | -- |
| Claude Opus 4.8 | 2026-01 | 0.162 [0.138, 0.188] (219) | n<20 (3) | n<20 (8) | -- | -- |

**FRQ (0-10)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.24 [3.21, 3.28] (3,073) | 3.13 [3.00, 3.27] (203) | 3.24 [3.14, 3.33] (393) | 0.251 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.51 [3.49, 3.54] (3,047) | 3.46 [3.36, 3.56] (203) | 3.55 [3.48, 3.63] (391) | 0.311 | 1.000 |
| GPT-OSS 20B | 2024-06 | 3.86 [3.82, 3.89] (2,613) | 3.88 [3.74, 4.02] (154) | 3.80 [3.69, 3.91] (268) | 0.569 | 1.000 |
| DeepSeek-R1 | 2024-07 | 4.17 [4.14, 4.21] (2,032) | 4.14 [3.99, 4.28] (136) | 4.03 [3.92, 4.14] (227) | 0.051 | 1.000 |
| Claude S4.5 | 2025-01 | 3.95 [3.91, 3.99] (1,740) | 3.95 [3.73, 4.14] (84) | 3.80 [3.64, 3.94] (125) | 0.181 | 1.000 |
| GPT-5.4 | 2025-08 | 4.92 [4.87, 4.97] (1,109) | 5.04 [4.77, 5.33] (35) | 4.94 [4.70, 5.18] (54) | 0.667 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 4.39 [4.32, 4.45] (586) | n<20 (9) | 4.23 [3.82, 4.61] (23) | 0.383 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 4.79 [4.72, 4.87] (475) | n<20 (8) | n<20 (18) | -- | -- |
| Claude Opus 4.8 | 2026-01 | 4.48 [4.42, 4.55] (591) | n<20 (9) | 4.59 [4.21, 4.98] (23) | 0.551 | 1.000 |

### 6.6 Per-model tables — editorial latency, whole dataset

**Binary (bal. acc)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.465 [0.445, 0.485] (940) | 0.468 [0.454, 0.482] (2,213) | 0.484 [0.466, 0.502] (1,528) | 0.445 [0.398, 0.493] (203) | 0.250 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.516 [0.500, 0.532] (941) | 0.501 [0.489, 0.512] (2,194) | 0.528 [0.515, 0.540] (1,515) | 0.529 [0.501, 0.557] (201) | 0.015 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.457 [0.434, 0.479] (942) | 0.473 [0.457, 0.488] (2,213) | 0.486 [0.468, 0.503] (1,527) | 0.460 [0.408, 0.511] (203) | 0.265 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.459 [0.429, 0.487] (847) | 0.477 [0.456, 0.496] (1,935) | 0.507 [0.483, 0.533] (1,285) | 0.480 [0.417, 0.543] (170) | 0.080 | 1.000 |
| Claude S4.5 | 2025-01 | 0.478 [0.453, 0.503] (874) | 0.466 [0.447, 0.484] (2,042) | 0.455 [0.433, 0.478] (1,417) | 0.494 [0.430, 0.555] (192) | 0.491 | 1.000 |
| GPT-5.4 | 2025-08 | 0.515 [0.486, 0.544] (942) | 0.509 [0.490, 0.527] (2,213) | 0.527 [0.503, 0.550] (1,528) | 0.516 [0.446, 0.578] (203) | 0.723 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.566 [0.539, 0.593] (904) | 0.570 [0.551, 0.587] (2,136) | 0.565 [0.541, 0.587] (1,480) | 0.600 [0.536, 0.664] (202) | 0.755 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.611 [0.588, 0.633] (941) | 0.613 [0.595, 0.630] (2,212) | 0.612 [0.592, 0.633] (1,527) | 0.596 [0.534, 0.655] (203) | 0.957 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.573 [0.545, 0.600] (902) | 0.564 [0.544, 0.583] (2,118) | 0.546 [0.522, 0.568] (1,468) | 0.548 [0.488, 0.604] (200) | 0.458 | 1.000 |

**MCQ (acc)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.498 [0.458, 0.539] (576) | 0.539 [0.512, 0.566] (1,411) | 0.558 [0.529, 0.587] (1,051) | 0.522 [0.437, 0.603] (136) | 0.145 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.458 [0.418, 0.501] (576) | 0.455 [0.429, 0.481] (1,397) | 0.477 [0.446, 0.509] (1,040) | 0.444 [0.362, 0.526] (135) | 0.707 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.494 [0.452, 0.536] (577) | 0.511 [0.484, 0.536] (1,411) | 0.518 [0.489, 0.549] (1,050) | 0.426 [0.345, 0.507] (136) | 0.207 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.602 [0.556, 0.648] (447) | 0.612 [0.582, 0.641] (1,079) | 0.625 [0.588, 0.658] (759) | 0.557 [0.462, 0.653] (97) | 0.586 | 1.000 |
| Claude S4.5 | 2025-01 | 0.700 [0.660, 0.740] (527) | 0.726 [0.702, 0.751] (1,273) | 0.704 [0.675, 0.732] (937) | 0.758 [0.685, 0.831] (128) | 0.400 | 1.000 |
| GPT-5.4 | 2025-08 | 0.835 [0.804, 0.865] (577) | 0.826 [0.806, 0.847] (1,411) | 0.821 [0.797, 0.844] (1,051) | 0.875 [0.818, 0.929] (136) | 0.446 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.912 [0.888, 0.934] (532) | 0.902 [0.885, 0.918] (1,270) | 0.887 [0.866, 0.906] (943) | 0.960 [0.924, 0.992] (124) | 0.051 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.879 [0.852, 0.904] (568) | 0.868 [0.850, 0.886] (1,405) | 0.884 [0.865, 0.902] (1,045) | 0.919 [0.871, 0.962] (136) | 0.295 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.930 [0.908, 0.951] (526) | 0.927 [0.912, 0.941] (1,252) | 0.930 [0.913, 0.947] (935) | 0.958 [0.920, 0.992] (119) | 0.671 | 1.000 |

**Date (score)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.110 [0.093, 0.129] (443) | 0.139 [0.126, 0.153] (971) | 0.165 [0.147, 0.185] (621) | 0.114 [0.074, 0.160] (82) | 0.001 | 0.098 |
| LLaMA 3.3 70B | 2023-12 | 0.451 [0.427, 0.474] (443) | 0.470 [0.452, 0.487] (964) | 0.469 [0.449, 0.489] (615) | 0.530 [0.470, 0.588] (81) | 0.100 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.231 [0.205, 0.255] (444) | 0.274 [0.256, 0.293] (971) | 0.278 [0.256, 0.301] (621) | 0.234 [0.176, 0.296] (82) | 0.025 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.212 [0.190, 0.235] (419) | 0.247 [0.231, 0.264] (907) | 0.280 [0.257, 0.303] (562) | 0.235 [0.180, 0.294] (73) | 0.001 | 0.098 |
| Claude S4.5 | 2025-01 | 0.169 [0.147, 0.193] (418) | 0.180 [0.164, 0.196] (913) | 0.193 [0.174, 0.214] (586) | 0.174 [0.122, 0.231] (79) | 0.469 | 1.000 |
| GPT-5.4 | 2025-08 | 0.143 [0.121, 0.168] (444) | 0.181 [0.164, 0.199] (971) | 0.187 [0.166, 0.208] (621) | 0.167 [0.114, 0.222] (82) | 0.043 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.377 [0.350, 0.404] (430) | 0.337 [0.318, 0.356] (924) | 0.327 [0.305, 0.349] (600) | 0.340 [0.279, 0.403] (78) | 0.041 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.324 [0.290, 0.359] (444) | 0.325 [0.302, 0.346] (971) | 0.299 [0.271, 0.326] (621) | 0.285 [0.203, 0.368] (82) | 0.429 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.417 [0.385, 0.450] (427) | 0.395 [0.375, 0.415] (915) | 0.378 [0.354, 0.403] (595) | 0.403 [0.334, 0.469] (79) | 0.278 | 1.000 |

**FRQ (0-10)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.15 [3.07, 3.23] (570) | 3.21 [3.16, 3.26] (1,412) | 3.26 [3.20, 3.31] (1,065) | 3.22 [3.08, 3.36] (138) | 0.145 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.40 [3.34, 3.47] (571) | 3.49 [3.45, 3.53] (1,402) | 3.56 [3.51, 3.60] (1,053) | 3.48 [3.35, 3.61] (138) | 0.001 | 0.073 |
| GPT-OSS 20B | 2024-06 | 3.71 [3.63, 3.79] (571) | 3.77 [3.72, 3.81] (1,408) | 3.95 [3.90, 4.01] (1,062) | 3.90 [3.75, 4.05] (139) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 4.04 [3.97, 4.12] (508) | 4.10 [4.06, 4.16] (1,216) | 4.20 [4.15, 4.26] (880) | 4.17 [4.02, 4.32] (120) | 0.004 | 0.353 |
| Claude S4.5 | 2025-01 | 3.77 [3.70, 3.85] (531) | 3.89 [3.84, 3.94] (1,312) | 3.97 [3.91, 4.03] (985) | 3.93 [3.76, 4.07] (134) | 0.002 | 0.136 |
| GPT-5.4 | 2025-08 | 4.84 [4.77, 4.91] (569) | 4.98 [4.94, 5.03] (1,412) | 5.04 [4.99, 5.09] (1,063) | 4.97 [4.84, 5.10] (139) | 0.000 | **0.010** |
| Claude Sonnet 5 | 2026-01 | 4.26 [4.18, 4.33] (546) | 4.40 [4.35, 4.45] (1,365) | 4.52 [4.47, 4.57] (1,045) | 4.35 [4.19, 4.50] (139) | 0.000 | **0.010** |
| GPT-5.6 Sol | 2026-02 | 4.76 [4.68, 4.84] (559) | 4.92 [4.87, 4.97] (1,392) | 4.95 [4.89, 5.00] (1,055) | 4.97 [4.82, 5.11] (139) | 0.001 | 0.098 |
| Claude Opus 4.8 | 2026-01 | 4.46 [4.38, 4.54] (550) | 4.63 [4.58, 4.68] (1,371) | 4.66 [4.61, 4.72] (1,045) | 4.60 [4.44, 4.75] (139) | 0.001 | **0.046** |

### 6.7 Per-model tables — editorial latency, post-cutoff only

**Binary (bal. acc)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.465 [0.445, 0.485] (940) | 0.468 [0.454, 0.482] (2,213) | 0.484 [0.466, 0.502] (1,528) | 0.445 [0.398, 0.493] (203) | 0.250 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.516 [0.500, 0.532] (941) | 0.501 [0.489, 0.512] (2,194) | 0.528 [0.515, 0.540] (1,515) | 0.529 [0.501, 0.557] (201) | 0.015 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.457 [0.433, 0.483] (717) | 0.472 [0.455, 0.490] (1,808) | 0.487 [0.465, 0.509] (1,247) | 0.466 [0.407, 0.526] (175) | 0.367 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.455 [0.422, 0.491] (576) | 0.483 [0.459, 0.505] (1,457) | 0.519 [0.490, 0.548] (947) | 0.451 [0.373, 0.527] (128) | 0.032 | 1.000 |
| Claude S4.5 | 2025-01 | 0.462 [0.428, 0.498] (403) | 0.455 [0.431, 0.479] (1,121) | 0.440 [0.410, 0.468] (812) | 0.478 [0.408, 0.558] (112) | 0.664 | 1.000 |
| GPT-5.4 | 2025-08 | 0.468 [0.410, 0.524] (226) | 0.497 [0.458, 0.535] (655) | 0.525 [0.484, 0.564] (547) | 0.389 [0.256, 0.528] (60) | 0.128 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.466 [0.406, 0.533] (98) | 0.571 [0.521, 0.624] (332) | 0.514 [0.461, 0.567] (273) | 0.558 [0.417, 0.722] (37) | 0.186 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.625 [0.544, 0.702] (82) | 0.571 [0.505, 0.633] (263) | 0.628 [0.569, 0.686] (237) | 0.552 [0.351, 0.760] (31) | 0.538 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.474 [0.406, 0.549] (97) | 0.510 [0.463, 0.560] (330) | 0.497 [0.450, 0.548] (270) | 0.509 [0.393, 0.661] (36) | 0.905 | 1.000 |

**MCQ (acc)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.498 [0.458, 0.539] (576) | 0.539 [0.512, 0.566] (1,411) | 0.558 [0.529, 0.587] (1,051) | 0.522 [0.437, 0.603] (136) | 0.145 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.458 [0.418, 0.501] (576) | 0.455 [0.429, 0.481] (1,397) | 0.477 [0.446, 0.509] (1,040) | 0.444 [0.362, 0.526] (135) | 0.707 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.492 [0.446, 0.538] (447) | 0.509 [0.481, 0.538] (1,161) | 0.524 [0.493, 0.558] (879) | 0.438 [0.352, 0.523] (121) | 0.284 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.596 [0.543, 0.656] (312) | 0.596 [0.562, 0.629] (820) | 0.617 [0.577, 0.655] (579) | 0.558 [0.449, 0.671] (77) | 0.740 | 1.000 |
| Claude S4.5 | 2025-01 | 0.657 [0.598, 0.714] (254) | 0.706 [0.672, 0.739] (708) | 0.687 [0.647, 0.723] (559) | 0.778 [0.684, 0.867] (81) | 0.175 | 1.000 |
| GPT-5.4 | 2025-08 | 0.833 [0.770, 0.890] (150) | 0.845 [0.810, 0.877] (432) | 0.805 [0.766, 0.844] (389) | 0.907 [0.810, 0.978] (43) | 0.233 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.902 [0.820, 0.969] (61) | 0.897 [0.849, 0.936] (204) | 0.878 [0.830, 0.922] (189) | 1.000 [1.000, 1.000] (25) | 0.316 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.870 [0.776, 0.949] (54) | 0.828 [0.772, 0.884] (169) | 0.887 [0.838, 0.931] (177) | n<20 (19) | 0.279 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.934 [0.867, 0.985] (61) | 0.907 [0.866, 0.944] (205) | 0.942 [0.908, 0.973] (190) | 0.920 [0.807, 1.000] (25) | 0.626 | 1.000 |

**Date (score)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.110 [0.093, 0.129] (443) | 0.139 [0.126, 0.153] (971) | 0.165 [0.147, 0.185] (621) | 0.114 [0.074, 0.160] (82) | 0.001 | 0.098 |
| LLaMA 3.3 70B | 2023-12 | 0.451 [0.427, 0.474] (443) | 0.470 [0.452, 0.487] (964) | 0.469 [0.449, 0.489] (615) | 0.530 [0.470, 0.588] (81) | 0.100 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.262 [0.230, 0.292] (331) | 0.315 [0.293, 0.337] (763) | 0.321 [0.293, 0.350] (474) | 0.270 [0.203, 0.342] (67) | 0.030 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.238 [0.207, 0.268] (280) | 0.287 [0.266, 0.308] (661) | 0.344 [0.314, 0.376] (387) | 0.298 [0.226, 0.377] (52) | 0.000 | **0.019** |
| Claude S4.5 | 2025-01 | 0.195 [0.163, 0.230] (183) | 0.187 [0.168, 0.208] (473) | 0.221 [0.194, 0.248] (300) | 0.194 [0.117, 0.277] (40) | 0.258 | 1.000 |
| GPT-5.4 | 2025-08 | 0.151 [0.108, 0.199] (91) | 0.141 [0.113, 0.167] (237) | 0.162 [0.131, 0.197] (179) | n<20 (16) | 0.641 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.198 [0.121, 0.281] (31) | 0.183 [0.135, 0.231] (95) | 0.191 [0.143, 0.247] (73) | n<20 (9) | 0.940 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.229 [0.158, 0.305] (23) | 0.221 [0.185, 0.259] (61) | 0.189 [0.156, 0.225] (58) | n<20 (8) | 0.432 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.121 [0.076, 0.175] (31) | 0.177 [0.141, 0.217] (95) | 0.153 [0.113, 0.196] (72) | n<20 (9) | 0.283 | 1.000 |

**FRQ (0-10)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.15 [3.07, 3.23] (570) | 3.21 [3.16, 3.26] (1,412) | 3.26 [3.20, 3.31] (1,065) | 3.22 [3.08, 3.36] (138) | 0.145 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.40 [3.34, 3.47] (571) | 3.49 [3.45, 3.53] (1,402) | 3.56 [3.51, 3.60] (1,053) | 3.48 [3.35, 3.61] (138) | 0.001 | 0.073 |
| GPT-OSS 20B | 2024-06 | 3.66 [3.57, 3.74] (443) | 3.78 [3.73, 3.83] (1,170) | 3.95 [3.90, 4.01] (888) | 3.89 [3.74, 4.04] (122) | 0.000 | **0.010** |
| DeepSeek-R1 | 2024-07 | 4.02 [3.93, 4.10] (357) | 4.11 [4.05, 4.16] (936) | 4.21 [4.15, 4.27] (671) | 4.20 [4.04, 4.36] (96) | 0.004 | 0.356 |
| Claude S4.5 | 2025-01 | 3.78 [3.69, 3.89] (258) | 3.89 [3.84, 3.95] (762) | 3.99 [3.91, 4.06] (594) | 4.01 [3.83, 4.19] (83) | 0.009 | 0.744 |
| GPT-5.4 | 2025-08 | 4.76 [4.64, 4.88] (154) | 4.90 [4.82, 4.99] (449) | 4.94 [4.87, 5.02] (396) | 4.99 [4.78, 5.21] (42) | 0.144 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 4.08 [3.90, 4.26] (66) | 4.31 [4.19, 4.43] (235) | 4.49 [4.39, 4.60] (211) | 4.57 [4.31, 4.83] (23) | 0.003 | 0.235 |
| GPT-5.6 Sol | 2026-02 | 4.63 [4.42, 4.84] (58) | 4.70 [4.58, 4.82] (186) | 4.86 [4.74, 4.99] (177) | n<20 (16) | 0.075 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 4.30 [4.11, 4.48] (68) | 4.45 [4.33, 4.56] (236) | 4.51 [4.40, 4.61] (213) | 4.52 [4.19, 4.87] (23) | 0.339 | 1.000 |

### 6.8 The superseded 708-event measure

The first pass used `original_publication_date − first_date_found` over 708 extension events. On inspection, `first_date_found` is the Crossref record-creation date for 96% of them, so that interval mostly measured online-first versus print-issue scheduling (0–3 months, all post-cutoff, no pre-cutoff partition). It is kept under `by_legacy/latency_708/` (0 of 64 significant) and should not be cited; section 6 replaces it.

## 7. Novelty — why we are not stratifying on it

We have no gold standard and no agreed proxy, and we decline to invent one. `novelty_discussion.md` lists six candidates (citation count, venue prestige, semantic distance from prior literature, rarity of the category combination, novelty claims in the abstract, an LLM-judged departure score) with what each would and would not capture. Two objections apply to all of them:

- **Circularity.** Novelty is close to the construct CUSP measures. A result that departs sharply from prior work is almost by definition harder to forecast. A novelty stratification showing lower performance on novel events would re-measure the benchmark's own target through a noisier instrument, not demonstrate a compositional bias.
- **Range restriction.** Every CUSP event was selected for being notable — published in *Nature*, *Science* or *Cell*, or curated onto a "top AI paper" list. The sampling frame is already truncated at the high end of novelty and visibility. Any within-benchmark stratification, including the citation analysis above, probes variation *inside* an already-selected band and can neither detect nor correct the selection that produced the band.

We think the second point is the honest answer to the reviewer's underlying concern, and we prefer to state it as a limitation of the benchmark rather than let a novelty table imply a control we do not have. A defensible novelty instrument would need a definition, a validation against human ratings, and inter-rater agreement — a study, not a table.

## 8. Proposed manuscript text

**[PROPOSED — Results, new subsection "Sensitivity to benchmark composition"]**

> To test whether our conclusions depend on how CUSP was assembled, we stratified every model's performance on all four tasks by source venue, citation quartile and publication latency, each on the whole benchmark and on the post-cutoff partition, with event-clustered bootstrap intervals and permutation tests corrected across the family (Supplementary Tables S24–S28). Performance varies across venues, but the variation is confined to the date task, where every model scores higher on arXiv-sourced events than on journal-sourced ones (median +0.264 date score), consistent with arXiv's regular posting cadence; because venues are nested within disciplines, we repeated the analysis with discipline held fixed and found 4 of 632 tests significant. Citation count, taken from a single Semantic Scholar snapshot over 5,513 events, predicts performance before a model's cutoff (the most-cited quartile scores higher on mechanism questions for 5 of 6 models with both quartiles populated, and on solution questions for 5 of 6) but not after it (1 of 27 post-cutoff tests outside the date task), indicating that visibility aids recall rather than forecasting. Publication latency — months a result was publicly observable before its journal version, over 4,326 journal events — shows 0 of 29 significant post-cutoff tests, and time in peer review over 3,740 events shows 2 of 36.

**[PROPOSED — Limitations]**

> Two limits of this benchmark's construction bound what the stratification above can establish. First, every CUSP event was selected for being notable — published in *Nature*, *Science* or *Cell*, or curated onto a widely-read preprint list — so the corpus is truncated at the high end of both visibility and novelty, and no within-benchmark stratification can detect the selection that produced that truncation. Second, source venue and scientific discipline are nearly collinear in CUSP: only 34 of 1,274 artificial-intelligence events appear in a journal, so an arXiv-versus-journal contrast cannot be fully separated from an AI-versus-other-discipline contrast. We report the discipline-controlled analysis for this reason and do not interpret the raw venue contrast causally.

**[PROPOSED — Limitations, novelty]**

> We do not stratify by novelty. We have no validated measure of it, and the available proxies are either confounded with venue and discipline or circular with the construct the benchmark measures: an event that departs sharply from prior work is, by construction, harder to forecast from pre-cutoff knowledge. Establishing a novelty measure — with a definition, validation against human judgement, and inter-rater agreement — is future work.

**[PROPOSED — replacement caption for Supplementary Tables S19–S23]**

> Knowledge gap (Δ_know) and foresight gap (Δ_fore) on post-cutoff instances, stratified by citation-count quartile, for the seven models with a complete web-search triple on the 500-event retrieval subset. Citation counts were retrieved from Semantic Scholar on 2026-05-12 over the 481 subset events for which a count resolved; quartile edges are ≤8, ≤22, ≤59, >59. Cells are the mean difference with a 95% paired bootstrap interval and N; cells with fewer than 20 paired observations are suppressed rather than reported as point estimates. These tables supersede the previously submitted S19–S23, which reported point estimates at N as low as 1.

**[PROPOSED — new Supplementary Table captions S24–S28]**

> **S24.** Performance by source venue, per model and task, on the whole benchmark and on the pre- and post-cutoff partitions. Binary is balanced accuracy. Cells give the value, a 95% event-clustered bootstrap interval and N; cells below N = 20 are suppressed. p-values are permutation tests across strata, Holm-corrected.
> **S25.** The same analysis with scientific discipline held fixed, for the seven disciplines carrying two or more venues at N ≥ 100.
> **S26.** Performance by citation quartile over the 5,513 events with a citation count (Semantic Scholar, OpenAlex fallback, snapshot 2026-09-25), raw count and count per month since first observable.
> **S27.** Performance by publication latency — months between the first public record of a result and its journal version (Crossref, snapshot 2026-09-25) — over the 4,326 journal events.
> **S28.** Performance by editorial latency (manuscript received to online publication) over the 3,740 *Nature* and *Science* events that deposit a received date.

## 9. Limitations of this analysis

- Citation counts are one snapshot (2026-09-25); the extension half has had at most five months to accrue citations, which is why the age-adjusted rate version is shown alongside the raw one.
- Latency 0 means "no earlier public record found by the build pipeline or by Crossref", not "no preprint existed": a preprint the pipeline missed makes the true latency longer, so the zero-latency stratum is contaminated toward longer latencies, which biases a latency effect toward zero, not away from it.
- Editorial latency is available only for *Nature* and *Science*; Cell does not deposit received dates.
- Venue and discipline are nearly collinear; the discipline-controlled analysis narrows but does not eliminate the confound, and it cannot compare arXiv against journals within AI.
- Pre/post partition sizes differ by orders of magnitude across models; two models have no pre-cutoff partition at all.
- The leaderboard stratum (59 events) carries no FRQ items and is frequently suppressed in per-model splits.
- Two Claude models' FRQ responses are truncated at their token caps; the direction of that effect on scores is not established.
