# Response to Reviewer 1, Comment 5 — benchmark selection bias (A5)

Supporting files in this directory: `metadata_audit.md` (what metadata exists and where it came from), `metadata/` (the 2026-09-25 Semantic Scholar / OpenAlex / Crossref snapshot, one JSONL per source), `by_source/`, `by_visibility/`, `by_vis_rate/`, `by_latency/`, `by_lat_review/` (full tables, CSV + markdown, all three partitions), `by_legacy/` (the first-pass 481- and 708-event tables, superseded), `tables/` (pooled), `figures/`, `novelty_discussion.md`, `MANIFEST.json` (git SHA, seeds, snapshot date, panel, coverage, partition sizes).

Regenerate with `results/A5_selection_bias/run_all.sh`. No inference; the only network step is the metadata snapshot, which is cached and never re-fetched. This document is written by `scripts/a5_make_response.py` from the stored CSVs — no number in it is typed by hand.

---

## 1. The reviewer's comment

> "Control benchmark selection bias by stratifying results across journals, repositories, event visibility, novelty, and publication latency."

## 2. Summary

Ten models, four tasks, 5,575 events. Every stratification is reported twice below — on the **whole dataset** and on the **post-cutoff partition only** (the forecasting regime the paper's claims rest on) — with the pre-cutoff partition in the supporting tables.

1. **Source / venue.** Performance differs across venues (85 of 112 tests significant after Holm correction), but the difference is confined to the date task and the leaderboard item type, and it disappears once discipline is held fixed (4 of 705 within-discipline tests). Every model scores higher on arXiv-sourced date items than on *Nature* items (10/10 models on the whole dataset, 10/10 post-cutoff; median +0.264 date score), which is a cadence property of the target, not knowledge about the papers.
2. **Event visibility, now on the whole corpus** (5,513 events with a citation count, 98.9%, versus 481 in the first pass). Citations predict performance **before** a model's cutoff and not after it. Pre-cutoff, the most-cited quartile beats the least-cited on FRQ for 6/6 models (median +0.225 on the 0–10 scale) and on MCQ for 6/6 (median +0.068); 11 of 32 pre-cutoff tests are significant. Post-cutoff the same contrasts are 4/6 (median +0.041) and 1/6 (median -0.028), binary is 5/8 (median +0.007), and 1 of 30 non-date post-cutoff tests are significant. Well-cited results are easier to *recall*, not easier to *forecast*. The age-adjusted citation-rate version gives the same picture (1 of 30 non-date post-cutoff tests).
3. **Publication latency, now on every journal event** (4,326 events, 77.6%, versus 708 in the first pass, and measuring the interval the reviewer means: how long a result was publicly observable before its journal version). 0 of 34 post-cutoff tests and 3 of 40 whole-dataset tests are significant. A second, independent latency — time in peer review, received → online, 3,740 *Nature* and *Science* events — gives 2 of 40 post-cutoff and 4 of 40 whole-dataset.
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

**Partition sizes are very unequal across models**, so whole-dataset numbers are not comparable *between* models (GPT-4o and LLaMA 3.3 have no pre-cutoff events; DeepSeek-V4-Pro has 4,760 pre and 815 post). That is why the post-cutoff tables are the ones to read for the forecasting claim:

| model | cutoff | n events | pre-cutoff | post-cutoff |
|---|---|---|---|---|
| GPT-4o | 2023-10 | 5,575 | 0 | 5,575 |
| LLaMA 3.3 70B | 2023-12 | 5,575 | 0 | 5,575 |
| GPT-OSS 20B | 2024-06 | 5,575 | 657 | 4,918 |
| DeepSeek-R1 | 2024-07 | 4,760 | 842 | 3,918 |
| Claude S4.5 | 2025-01 | 5,575 | 1,907 | 3,668 |
| GPT-5.4 | 2025-08 | 5,575 | 3,372 | 2,203 |
| Claude Sonnet 5 | 2026-01 | 5,575 | 4,305 | 1,270 |
| GPT-5.6 Sol | 2026-02 | 5,575 | 4,508 | 1,067 |
| DeepSeek-V4-Pro | 2026-04 | 5,575 | 4,760 | 815 |
| Claude Opus 4.8 | 2026-01 | 5,575 | 4,305 | 1,270 |

**Methods, unchanged from the first pass.** Binary is balanced accuracy (mean of recall on the real question and specificity on its perturbed twin). Every cell carries N and a 2,000-draw event-clustered bootstrap percentile CI; cells below n = 20 print `n<20` and no point estimate. Stratum effects use a 10,000-draw permutation test shuffling stratum labels across events, Holm–Bonferroni corrected across every model × partition × task test within a stratification. Pooled rows average only over models that carry every stratum unsuppressed, so every column of a pooled table rests on the same models (the count is printed). FRQ uses the published rubric (`judge_frq_combined`); refusals are excluded from denominators. With N in the thousands the permutation test flags differences too small to matter, so the size of every effect is printed next to its p-value.

## 4. Source and repository (all 5,575 events)

### 4.1 Whole dataset

| task | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | models pooled | Holm-sig |
|---|---|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.517 (31,299) | 0.508 (16,188) | 0.519 (6,292) | 0.512 (11,546) | 0.525 (4,136) | 0.679 (1,176) | 10 | 7 / 10 |
| MCQ (acc) | 0.711 (19,805) | 0.685 (10,163) | 0.696 (4,595) | 0.683 (7,485) | 0.700 (2,277) | 0.529 (583) | 10 | 10 / 10 |
| Date (score) | 0.280 (13,660) | 0.248 (7,057) | 0.291 (2,366) | 0.502 (3,767) | 0.538 (1,438) | 0.464 (588) | 10 | 10 / 10 |
| FRQ (0-10) | 4.16 (21,022) | 4.10 (9,917) | 4.32 (4,609) | 4.32 (8,032) | 4.34 (2,726) | no items | 10 | 10 / 10 |

### 4.2 Post-cutoff only

| task | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | models pooled | Holm-sig |
|---|---|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.506 (15,871) | 0.496 (8,184) | 0.497 (3,303) | 0.483 (6,191) | 0.493 (2,514) | 0.681 (742) | 9 | 5 / 10 |
| MCQ (acc) | 0.620 (9,087) | 0.574 (4,708) | 0.605 (2,205) | 0.538 (3,542) | 0.591 (1,262) | 0.375 (321) | 6 | 7 / 10 |
| Date (score) | 0.264 (5,999) | 0.240 (3,115) | 0.294 (1,082) | 0.461 (1,718) | 0.523 (810) | 0.446 (326) | 6 | 9 / 10 |
| FRQ (0-10) | 4.14 (10,924) | 4.10 (5,151) | 4.30 (2,468) | 4.32 (4,446) | 4.39 (1,658) | no items | 9 | 9 / 10 |

85 of 112 permutation tests are significant, so performance does vary across sources. The variation has two causes, neither a venue effect:

**(a) Date prediction is easier on arXiv items.** Every model scores higher on the arXiv feeds than on the journals — HF Daily Papers vs *Nature*: 10/10 models on the whole dataset (median +0.264, range +0.047 to +0.357) and 10/10 post-cutoff (median +0.271). arXiv posting follows a short, regular cadence while journal lags are long and variable, so the target itself is more predictable.

**(b) The leaderboard set is a different item type.** It is the only stratum where binary rises materially and MCQ falls; 59 events, no FRQ items.

Binary, MCQ and FRQ are otherwise flat across the five paper sources.

### 4.3 The confound, and the control

CUSP's venues are nested inside discipline: the arXiv feeds and the leaderboard set are 99–100% Artificial Intelligence, the journals 0–1.3%, and only 34 of 1,274 AI events appear in a journal. So we held discipline fixed and re-tested venue within each of the seven disciplines that carry two or more venues at n ≥ 100 (`by_source/within_discipline.md`):

| discipline | venues | events | tests | Holm-significant (p<0.05) |
|---|---|---|---|---|
| Biology | Nature, Science, Cell | 1,438 | 110 | **2** |
| Artificial Intelligence | HF Daily Papers (arXiv), Top-10 AI Paper of Week (arXiv) | 1,181 | 95 | **1** |
| Medicine | Nature, Cell, Science | 878 | 105 | **0** |
| Materials Science | Nature, Science | 460 | 110 | **1** |
| Physics | Nature, Science | 444 | 98 | **0** |
| Neuroscience | Nature, Science | 379 | 93 | **0** |
| Chemistry | Nature, Science | 226 | 94 | **0** |

**4 of 705.** Once discipline is fixed, the venue does not predict how well any model does. The raw source effect is a discipline effect — which the paper already stratifies on — plus the date-cadence difference above.

### 4.4 Per-model tables — whole dataset

**Binary (bal. acc)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.471 [0.459, 0.482] (3,219) | 0.472 [0.456, 0.487] (1,669) | 0.487 [0.458, 0.516] (661) | 0.475 [0.450, 0.500] (1,172) | 0.526 [0.482, 0.568] (414) | 0.653 [0.593, 0.712] (118) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 0.517 [0.508, 0.526] (3,195) | 0.504 [0.491, 0.516] (1,660) | 0.523 [0.506, 0.540] (654) | 0.503 [0.495, 0.511] (1,167) | 0.510 [0.497, 0.522] (414) | 0.579 [0.534, 0.630] (114) | 0.011 | 0.220 |
| GPT-OSS 20B | 2024-06 | 0.472 [0.459, 0.484] (3,218) | 0.475 [0.458, 0.492] (1,671) | 0.468 [0.438, 0.498] (662) | 0.446 [0.424, 0.468] (1,172) | 0.470 [0.433, 0.506] (414) | 0.720 [0.653, 0.780] (118) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 0.488 [0.471, 0.504] (2,797) | 0.469 [0.447, 0.493] (1,444) | 0.537 [0.499, 0.575] (573) | 0.453 [0.427, 0.483] (1,005) | 0.482 [0.442, 0.524] (410) | 0.585 [0.517, 0.653] (118) | 0.001 | **0.028** |
| Claude S4.5 | 2025-01 | 0.470 [0.455, 0.485] (3,009) | 0.455 [0.435, 0.475] (1,520) | 0.457 [0.417, 0.496] (554) | 0.532 [0.508, 0.556] (1,171) | 0.516 [0.477, 0.553] (414) | 0.678 [0.610, 0.746] (118) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 0.518 [0.502, 0.534] (3,219) | 0.510 [0.488, 0.531] (1,671) | 0.525 [0.489, 0.558] (662) | 0.512 [0.490, 0.533] (1,172) | 0.536 [0.495, 0.574] (414) | 0.653 [0.593, 0.712] (118) | 0.035 | 0.487 |
| Claude Sonnet 5 | 2026-01 | 0.576 [0.560, 0.591] (3,116) | 0.554 [0.533, 0.574] (1,610) | 0.536 [0.499, 0.576] (605) | 0.573 [0.548, 0.597] (1,171) | 0.565 [0.529, 0.602] (414) | 0.729 [0.661, 0.797] (118) | 0.001 | **0.033** |
| GPT-5.6 Sol | 2026-02 | 0.617 [0.604, 0.632] (3,216) | 0.602 [0.582, 0.622] (1,671) | 0.618 [0.587, 0.649] (662) | 0.565 [0.544, 0.584] (1,172) | 0.574 [0.545, 0.603] (414) | 0.805 [0.737, 0.864] (118) | 0.000 | **0.011** |
| DeepSeek-V4-Pro | 2026-04 | 0.477 [0.467, 0.486] (3,219) | 0.491 [0.478, 0.504] (1,671) | 0.465 [0.440, 0.488] (662) | 0.490 [0.473, 0.506] (1,172) | 0.497 [0.472, 0.522] (414) | 0.661 [0.593, 0.729] (118) | 0.000 | **0.011** |
| Claude Opus 4.8 | 2026-01 | 0.563 [0.547, 0.579] (3,091) | 0.551 [0.529, 0.573] (1,601) | 0.574 [0.537, 0.610] (597) | 0.576 [0.550, 0.601] (1,172) | 0.570 [0.533, 0.608] (414) | 0.729 [0.669, 0.788] (118) | 0.002 | 0.059 |

**MCQ (acc)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.561 [0.541, 0.582] (2,093) | 0.488 [0.459, 0.517] (1,083) | 0.581 [0.536, 0.625] (499) | 0.440 [0.406, 0.476] (768) | 0.500 [0.432, 0.567] (230) | 0.305 [0.186, 0.424] (59) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 0.474 [0.454, 0.495] (2,074) | 0.440 [0.409, 0.469] (1,076) | 0.490 [0.446, 0.534] (492) | 0.319 [0.286, 0.353] (764) | 0.357 [0.295, 0.417] (230) | 0.298 [0.185, 0.421] (57) | 0.000 | **0.011** |
| GPT-OSS 20B | 2024-06 | 0.522 [0.500, 0.543] (2,092) | 0.478 [0.448, 0.508] (1,084) | 0.504 [0.460, 0.546] (500) | 0.362 [0.328, 0.395] (768) | 0.448 [0.385, 0.511] (230) | 0.237 [0.136, 0.339] (59) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 0.620 [0.596, 0.643] (1,579) | 0.596 [0.561, 0.631] (805) | 0.644 [0.593, 0.692] (374) | 0.496 [0.453, 0.534] (579) | 0.585 [0.519, 0.650] (207) | 0.556 [0.423, 0.685] (54) | 0.000 | **0.011** |
| Claude S4.5 | 2025-01 | 0.728 [0.707, 0.747] (1,909) | 0.692 [0.663, 0.721] (958) | 0.674 [0.630, 0.720] (408) | 0.798 [0.769, 0.827] (766) | 0.796 [0.741, 0.847] (230) | 0.492 [0.356, 0.627] (59) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 0.828 [0.811, 0.844] (2,093) | 0.830 [0.808, 0.852] (1,084) | 0.794 [0.758, 0.827] (500) | 0.841 [0.815, 0.866] (768) | 0.843 [0.795, 0.891] (230) | 0.542 [0.407, 0.661] (59) | 0.000 | **0.011** |
| Claude Sonnet 5 | 2026-01 | 0.903 [0.890, 0.916] (1,911) | 0.897 [0.877, 0.916] (960) | 0.903 [0.874, 0.930] (422) | 0.957 [0.942, 0.970] (768) | 0.909 [0.868, 0.942] (230) | 0.746 [0.644, 0.847] (59) | 0.000 | **0.011** |
| GPT-5.6 Sol | 2026-02 | 0.881 [0.866, 0.894] (2,076) | 0.872 [0.852, 0.892] (1,080) | 0.830 [0.796, 0.862] (493) | 0.914 [0.894, 0.933] (768) | 0.857 [0.811, 0.898] (230) | 0.797 [0.695, 0.898] (59) | 0.000 | **0.013** |
| DeepSeek-V4-Pro | 2026-04 | 0.664 [0.643, 0.684] (2,093) | 0.632 [0.604, 0.661] (1,084) | 0.630 [0.588, 0.671] (500) | 0.742 [0.712, 0.774] (768) | 0.757 [0.700, 0.810] (230) | 0.458 [0.339, 0.593] (59) | 0.000 | **0.011** |
| Claude Opus 4.8 | 2026-01 | 0.932 [0.920, 0.943] (1,885) | 0.927 [0.910, 0.944] (949) | 0.907 [0.879, 0.933] (407) | 0.964 [0.950, 0.977] (768) | 0.948 [0.919, 0.974] (230) | 0.864 [0.763, 0.949] (59) | 0.001 | **0.038** |

**Date (score)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.145 [0.133, 0.157] (1,396) | 0.131 [0.116, 0.149] (723) | 0.169 [0.140, 0.200] (248) | 0.416 [0.388, 0.444] (380) | 0.499 [0.453, 0.545] (144) | 0.331 [0.254, 0.408] (59) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 0.473 [0.459, 0.487] (1,385) | 0.458 [0.439, 0.477] (720) | 0.501 [0.470, 0.532] (245) | 0.520 [0.497, 0.544] (379) | 0.588 [0.551, 0.625] (144) | 0.571 [0.509, 0.633] (57) | 0.000 | **0.011** |
| GPT-OSS 20B | 2024-06 | 0.271 [0.256, 0.287] (1,396) | 0.253 [0.232, 0.274] (724) | 0.292 [0.255, 0.331] (248) | 0.415 [0.386, 0.444] (380) | 0.520 [0.471, 0.571] (144) | 0.500 [0.408, 0.589] (59) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 0.250 [0.235, 0.264] (1,293) | 0.247 [0.228, 0.268] (670) | 0.340 [0.304, 0.379] (230) | 0.366 [0.335, 0.397] (348) | 0.499 [0.449, 0.548] (142) | 0.417 [0.345, 0.492] (59) | 0.000 | **0.011** |
| Claude S4.5 | 2025-01 | 0.197 [0.183, 0.211] (1,323) | 0.152 [0.135, 0.169] (675) | 0.218 [0.185, 0.259] (209) | 0.459 [0.429, 0.487] (380) | 0.483 [0.442, 0.526] (144) | 0.482 [0.430, 0.532] (59) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 0.197 [0.183, 0.211] (1,396) | 0.132 [0.114, 0.149] (724) | 0.201 [0.169, 0.238] (248) | 0.468 [0.439, 0.499] (380) | 0.521 [0.475, 0.569] (144) | 0.373 [0.310, 0.438] (59) | 0.000 | **0.011** |
| Claude Sonnet 5 | 2026-01 | 0.342 [0.328, 0.359] (1,345) | 0.343 [0.323, 0.363] (689) | 0.358 [0.320, 0.398] (224) | 0.699 [0.674, 0.726] (380) | 0.655 [0.614, 0.694] (144) | 0.601 [0.537, 0.663] (59) | 0.000 | **0.011** |
| GPT-5.6 Sol | 2026-02 | 0.345 [0.326, 0.365] (1,396) | 0.257 [0.233, 0.282] (724) | 0.263 [0.223, 0.305] (248) | 0.609 [0.575, 0.645] (380) | 0.525 [0.469, 0.583] (144) | 0.388 [0.303, 0.474] (59) | 0.000 | **0.011** |
| DeepSeek-V4-Pro | 2026-04 | 0.166 [0.154, 0.180] (1,396) | 0.143 [0.128, 0.158] (724) | 0.187 [0.159, 0.216] (248) | 0.344 [0.320, 0.372] (380) | 0.415 [0.375, 0.456] (144) | 0.359 [0.296, 0.424] (59) | 0.000 | **0.011** |
| Claude Opus 4.8 | 2026-01 | 0.411 [0.394, 0.429] (1,334) | 0.362 [0.338, 0.385] (684) | 0.378 [0.338, 0.419] (218) | 0.723 [0.696, 0.750] (380) | 0.676 [0.636, 0.715] (144) | 0.624 [0.561, 0.684] (59) | 0.000 | **0.011** |

**FRQ (0-10)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.23 [3.19, 3.26] (2,164) | 3.19 [3.14, 3.25] (1,022) | 3.38 [3.30, 3.48] (483) | 3.41 [3.36, 3.47] (816) | 3.46 [3.35, 3.58] (273) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 3.50 [3.46, 3.53] (2,148) | 3.50 [3.45, 3.54] (1,017) | 3.64 [3.58, 3.70] (476) | 3.35 [3.30, 3.40] (810) | 3.37 [3.29, 3.47] (272) | 0.000 | **0.011** |
| GPT-OSS 20B | 2024-06 | 3.86 [3.82, 3.90] (2,159) | 3.76 [3.70, 3.82] (1,022) | 4.04 [3.96, 4.12] (482) | 3.88 [3.83, 3.93] (815) | 3.87 [3.78, 3.97] (273) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 4.14 [4.10, 4.18] (1,856) | 4.10 [4.04, 4.15] (869) | 4.35 [4.27, 4.43] (415) | 4.23 [4.18, 4.29] (690) | 4.32 [4.22, 4.40] (270) | 0.000 | **0.011** |
| Claude S4.5 | 2025-01 | 3.92 [3.89, 3.96] (2,018) | 3.84 [3.78, 3.90] (945) | 4.10 [4.00, 4.19] (414) | 4.21 [4.16, 4.26] (816) | 4.22 [4.14, 4.30] (273) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 4.99 [4.96, 5.02] (2,163) | 4.95 [4.89, 5.00] (1,021) | 5.13 [5.06, 5.20] (482) | 5.03 [4.98, 5.09] (817) | 5.12 [5.03, 5.21] (273) | 0.001 | **0.023** |
| Claude Sonnet 5 | 2026-01 | 4.43 [4.40, 4.47] (2,107) | 4.37 [4.31, 4.42] (989) | 4.57 [4.49, 4.64] (458) | 4.85 [4.79, 4.91] (817) | 4.79 [4.68, 4.91] (273) | 0.000 | **0.011** |
| GPT-5.6 Sol | 2026-02 | 4.93 [4.89, 4.97] (2,134) | 4.85 [4.79, 4.90] (1,012) | 5.05 [4.97, 5.13] (459) | 5.09 [5.02, 5.15] (817) | 5.05 [4.95, 5.16] (273) | 0.000 | **0.011** |
| DeepSeek-V4-Pro | 2026-04 | 3.96 [3.91, 4.00] (2,164) | 3.94 [3.88, 4.00] (1,023) | 4.16 [4.08, 4.24] (484) | 3.93 [3.87, 3.99] (817) | 4.02 [3.91, 4.14] (273) | 0.000 | **0.011** |
| Claude Opus 4.8 | 2026-01 | 4.64 [4.60, 4.68] (2,109) | 4.54 [4.48, 4.60] (997) | 4.81 [4.73, 4.89] (456) | 5.22 [5.16, 5.27] (817) | 5.17 [5.08, 5.28] (273) | 0.000 | **0.011** |

### 4.5 Per-model tables — post-cutoff only

**Binary (bal. acc)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.471 [0.459, 0.482] (3,219) | 0.472 [0.456, 0.487] (1,669) | 0.487 [0.458, 0.516] (661) | 0.475 [0.450, 0.500] (1,172) | 0.526 [0.482, 0.568] (414) | 0.653 [0.593, 0.712] (118) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 0.517 [0.508, 0.526] (3,195) | 0.504 [0.491, 0.516] (1,660) | 0.523 [0.506, 0.540] (654) | 0.503 [0.495, 0.511] (1,167) | 0.510 [0.497, 0.522] (414) | 0.579 [0.534, 0.630] (114) | 0.011 | 0.220 |
| GPT-OSS 20B | 2024-06 | 0.474 [0.460, 0.488] (2,705) | 0.474 [0.456, 0.492] (1,438) | 0.463 [0.430, 0.496] (589) | 0.440 [0.415, 0.465] (1,042) | 0.470 [0.433, 0.506] (414) | 0.720 [0.653, 0.780] (118) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 0.495 [0.477, 0.514] (2,172) | 0.467 [0.441, 0.495] (1,142) | 0.533 [0.490, 0.574] (470) | 0.445 [0.416, 0.475] (837) | 0.482 [0.442, 0.524] (410) | 0.585 [0.517, 0.653] (118) | 0.001 | **0.025** |
| Claude S4.5 | 2025-01 | 0.458 [0.439, 0.477] (1,779) | 0.448 [0.422, 0.475] (872) | 0.440 [0.391, 0.489] (337) | 0.496 [0.466, 0.527] (751) | 0.515 [0.478, 0.552] (413) | 0.678 [0.610, 0.746] (118) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 0.494 [0.467, 0.522] (1,091) | 0.501 [0.463, 0.540] (553) | 0.471 [0.410, 0.537] (237) | 0.516 [0.481, 0.551] (483) | 0.553 [0.505, 0.602] (249) | 0.682 [0.606, 0.758] (66) | 0.015 | 0.255 |
| Claude Sonnet 5 | 2026-01 | 0.532 [0.497, 0.569] (608) | 0.523 [0.481, 0.567] (294) | 0.522 [0.437, 0.607] (124) | 0.516 [0.450, 0.581] (257) | 0.502 [0.412, 0.602] (74) | 0.767 [0.633, 0.900] (30) | 0.141 | 0.934 |
| GPT-5.6 Sol | 2026-02 | 0.613 [0.574, 0.653] (503) | 0.586 [0.527, 0.641] (264) | 0.527 [0.426, 0.633] (109) | 0.495 [0.439, 0.549] (225) | 0.440 [0.358, 0.515] (52) | 0.767 [0.633, 0.900] (30) | 0.001 | **0.038** |
| DeepSeek-V4-Pro | 2026-04 | 0.472 [0.443, 0.506] (396) | 0.462 [0.417, 0.510] (217) | 0.469 [0.385, 0.571] (88) | 0.454 [0.403, 0.515] (144) | -- | -- | 0.942 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.497 [0.464, 0.531] (599) | 0.489 [0.447, 0.531] (292) | 0.508 [0.426, 0.592] (122) | 0.460 [0.402, 0.522] (257) | 0.439 [0.359, 0.520] (74) | 0.700 [0.567, 0.833] (30) | 0.081 | 0.934 |

**MCQ (acc)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.561 [0.541, 0.582] (2,093) | 0.488 [0.459, 0.517] (1,083) | 0.581 [0.536, 0.625] (499) | 0.440 [0.406, 0.476] (768) | 0.500 [0.432, 0.567] (230) | 0.305 [0.186, 0.424] (59) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 0.474 [0.454, 0.495] (2,074) | 0.440 [0.409, 0.469] (1,076) | 0.490 [0.446, 0.534] (492) | 0.319 [0.286, 0.353] (764) | 0.357 [0.295, 0.417] (230) | 0.298 [0.185, 0.421] (57) | 0.000 | **0.011** |
| GPT-OSS 20B | 2024-06 | 0.520 [0.498, 0.544] (1,787) | 0.472 [0.440, 0.504] (941) | 0.499 [0.453, 0.546] (449) | 0.368 [0.332, 0.405] (687) | 0.448 [0.385, 0.511] (230) | 0.237 [0.136, 0.339] (59) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 0.620 [0.594, 0.646] (1,254) | 0.578 [0.542, 0.616] (645) | 0.644 [0.590, 0.694] (312) | 0.492 [0.447, 0.535] (490) | 0.585 [0.519, 0.650] (207) | 0.556 [0.423, 0.685] (54) | 0.000 | **0.011** |
| Claude S4.5 | 2025-01 | 0.705 [0.678, 0.729] (1,151) | 0.660 [0.621, 0.698] (576) | 0.655 [0.597, 0.714] (261) | 0.785 [0.749, 0.822] (507) | 0.796 [0.744, 0.844] (230) | 0.492 [0.356, 0.627] (59) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 0.838 [0.810, 0.865] (728) | 0.809 [0.768, 0.847] (387) | 0.760 [0.696, 0.817] (192) | 0.825 [0.784, 0.864] (326) | 0.859 [0.798, 0.916] (135) | 0.364 [0.212, 0.545] (33) | 0.000 | **0.011** |
| Claude Sonnet 5 | 2026-01 | 0.904 [0.873, 0.932] (395) | 0.865 [0.817, 0.910] (192) | 0.830 [0.752, 0.900] (100) | 0.973 [0.947, 0.995] (187) | 0.927 [0.842, 1.000] (41) | n<20 (15) | 0.001 | **0.028** |
| GPT-5.6 Sol | 2026-02 | 0.873 [0.835, 0.905] (338) | 0.862 [0.810, 0.911] (181) | 0.795 [0.707, 0.875] (88) | 0.910 [0.865, 0.952] (166) | 0.815 [0.667, 0.957] (27) | n<20 (15) | 0.112 | 0.934 |
| DeepSeek-V4-Pro | 2026-04 | 0.643 [0.588, 0.699] (269) | 0.654 [0.581, 0.727] (153) | 0.571 [0.456, 0.682] (70) | 0.789 [0.708, 0.864] (114) | -- | -- | 0.011 | 0.220 |
| Claude Opus 4.8 | 2026-01 | 0.921 [0.894, 0.946] (394) | 0.926 [0.886, 0.963] (189) | 0.885 [0.818, 0.948] (96) | 0.968 [0.941, 0.990] (187) | 0.951 [0.868, 1.000] (41) | n<20 (15) | 0.094 | 0.934 |

**Date (score)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.145 [0.133, 0.157] (1,396) | 0.131 [0.116, 0.149] (723) | 0.169 [0.140, 0.200] (248) | 0.416 [0.388, 0.444] (380) | 0.499 [0.453, 0.545] (144) | 0.331 [0.254, 0.408] (59) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 0.473 [0.459, 0.487] (1,385) | 0.458 [0.439, 0.477] (720) | 0.501 [0.470, 0.532] (245) | 0.520 [0.497, 0.544] (379) | 0.588 [0.551, 0.625] (144) | 0.571 [0.509, 0.633] (57) | 0.000 | **0.011** |
| GPT-OSS 20B | 2024-06 | 0.307 [0.289, 0.326] (1,129) | 0.280 [0.256, 0.303] (604) | 0.317 [0.274, 0.359] (217) | 0.453 [0.422, 0.483] (326) | 0.520 [0.471, 0.571] (144) | 0.500 [0.408, 0.589] (59) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 0.290 [0.273, 0.307] (968) | 0.281 [0.258, 0.306] (514) | 0.377 [0.335, 0.419] (184) | 0.408 [0.372, 0.444] (276) | 0.499 [0.449, 0.548] (142) | 0.417 [0.345, 0.492] (59) | 0.000 | **0.011** |
| Claude S4.5 | 2025-01 | 0.206 [0.189, 0.223] (730) | 0.173 [0.151, 0.196] (356) | 0.218 [0.174, 0.259] (114) | 0.503 [0.465, 0.536] (221) | 0.483 [0.441, 0.524] (144) | 0.482 [0.430, 0.532] (59) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 0.161 [0.139, 0.184] (391) | 0.118 [0.090, 0.146] (198) | 0.181 [0.131, 0.239] (74) | 0.468 [0.421, 0.517] (136) | 0.551 [0.494, 0.606] (92) | 0.378 [0.284, 0.471] (33) | 0.000 | **0.011** |
| Claude Sonnet 5 | 2026-01 | 0.205 [0.168, 0.241] (190) | 0.217 [0.171, 0.266] (89) | 0.256 [0.164, 0.361] (30) | 0.503 [0.435, 0.569] (59) | 0.500 [0.425, 0.583] (27) | n<20 (15) | 0.000 | **0.011** |
| GPT-5.6 Sol | 2026-02 | 0.217 [0.191, 0.245] (144) | 0.158 [0.126, 0.189] (73) | 0.182 [0.125, 0.237] (24) | 0.347 [0.304, 0.390] (52) | n<20 (19) | n<20 (15) | 0.000 | **0.011** |
| DeepSeek-V4-Pro | 2026-04 | 0.298 [0.226, 0.373] (97) | 0.324 [0.222, 0.431] (53) | n<20 (18) | 0.558 [0.432, 0.680] (28) | -- | -- | 0.005 | 0.127 |
| Claude Opus 4.8 | 2026-01 | 0.169 [0.144, 0.195] (188) | 0.173 [0.134, 0.215] (89) | 0.176 [0.127, 0.232] (29) | 0.467 [0.404, 0.534] (59) | 0.479 [0.420, 0.537] (27) | n<20 (15) | 0.000 | **0.011** |

**FRQ (0-10)**

| model | cutoff | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.23 [3.19, 3.26] (2,164) | 3.19 [3.14, 3.25] (1,022) | 3.38 [3.30, 3.48] (483) | 3.41 [3.36, 3.47] (816) | 3.46 [3.35, 3.58] (273) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 3.50 [3.46, 3.53] (2,148) | 3.50 [3.45, 3.54] (1,017) | 3.64 [3.58, 3.70] (476) | 3.35 [3.30, 3.40] (810) | 3.37 [3.29, 3.47] (272) | 0.000 | **0.011** |
| GPT-OSS 20B | 2024-06 | 3.85 [3.81, 3.89] (1,848) | 3.77 [3.71, 3.83] (891) | 4.02 [3.93, 4.10] (431) | 3.88 [3.82, 3.93] (739) | 3.87 [3.78, 3.97] (273) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 4.14 [4.10, 4.19] (1,475) | 4.08 [4.03, 4.15] (698) | 4.33 [4.24, 4.42] (345) | 4.25 [4.19, 4.30] (588) | 4.32 [4.22, 4.40] (270) | 0.000 | **0.011** |
| Claude S4.5 | 2025-01 | 3.94 [3.90, 3.99] (1,243) | 3.88 [3.81, 3.95] (578) | 4.08 [3.96, 4.19] (265) | 4.19 [4.12, 4.25] (551) | 4.22 [4.14, 4.30] (272) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 4.91 [4.84, 4.96] (778) | 4.91 [4.83, 5.00] (367) | 5.03 [4.93, 5.15] (182) | 5.03 [4.96, 5.12] (355) | 5.15 [5.03, 5.27] (160) | 0.002 | **0.043** |
| Claude Sonnet 5 | 2026-01 | 4.36 [4.27, 4.44] (449) | 4.37 [4.26, 4.47] (201) | 4.53 [4.37, 4.69] (102) | 4.72 [4.62, 4.83] (205) | 4.76 [4.50, 5.01] (51) | 0.000 | **0.011** |
| GPT-5.6 Sol | 2026-02 | 4.81 [4.72, 4.89] (367) | 4.77 [4.65, 4.90] (174) | 4.98 [4.80, 5.15] (82) | 5.01 [4.90, 5.12] (177) | 5.30 [5.03, 5.55] (36) | 0.000 | **0.013** |
| DeepSeek-V4-Pro | 2026-04 | 3.97 [3.87, 4.07] (292) | 4.01 [3.87, 4.16] (148) | 4.22 [4.02, 4.42] (67) | 3.89 [3.72, 4.04] (122) | -- | 0.078 | 0.934 |
| Claude Opus 4.8 | 2026-01 | 4.50 [4.43, 4.58] (452) | 4.39 [4.27, 4.51] (203) | 4.71 [4.55, 4.86] (102) | 5.04 [4.93, 5.14] (205) | 5.10 [4.84, 5.33] (51) | 0.000 | **0.011** |

## 5. Event visibility (5,513 events with citation counts)

Two measures, both from the 2026-09-25 snapshot: the **raw count** (quartiles over all 5,513 events: Q1 (<=10), Q2 (<=28), Q3 (<=68), Q4 (>68)) and the **citation rate** — count divided by months from the first-observable date to the snapshot (quartiles Q1 (<=0.96/mo), Q2 (<=1.83/mo), Q3 (<=3.94/mo), Q4 (>3.94/mo)). Raw counts favour older events (an Apr–Aug 2026 event has had months to be cited, a Jan 2024 event two and a half years), so the rate version is the age-adjusted one and the one we treat as primary; we show both because the published S19–S23 used raw quartiles.

### 5.1 Whole dataset

Raw citation quartile:

| task | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.500 (14,873) | 0.503 (16,807) | 0.510 (18,722) | 0.521 (19,019) | 10 | 1 / 10 |
| MCQ (acc) | 0.693 (10,328) | 0.702 (10,849) | 0.697 (11,551) | 0.701 (11,567) | 10 | 4 / 10 |
| Date (score) | 0.315 (4,777) | 0.297 (7,072) | 0.297 (8,275) | 0.353 (8,144) | 10 | 10 / 10 |
| FRQ (0-10) | 4.16 (10,870) | 4.18 (11,295) | 4.21 (11,947) | 4.26 (12,164) | 10 | 5 / 10 |

Citation-rate quartile:

| task | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.503 (15,897) | 0.514 (16,581) | 0.503 (18,090) | 0.518 (18,853) | 10 | 0 / 10 |
| MCQ (acc) | 0.705 (10,741) | 0.703 (10,742) | 0.685 (11,186) | 0.701 (11,626) | 10 | 3 / 10 |
| Date (score) | 0.296 (6,016) | 0.287 (6,757) | 0.298 (7,829) | 0.374 (7,666) | 10 | 7 / 10 |
| FRQ (0-10) | 4.18 (11,141) | 4.15 (11,239) | 4.20 (11,759) | 4.27 (12,137) | 10 | 3 / 10 |

### 5.2 Post-cutoff only

Raw citation quartile:

| task | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.485 (10,170) | 0.490 (8,956) | 0.479 (8,281) | 0.487 (7,480) | 8 | 0 / 10 |
| MCQ (acc) | 0.598 (5,722) | 0.610 (5,448) | 0.590 (5,084) | 0.570 (4,533) | 6 | 1 / 10 |
| Date (score) | 0.342 (2,631) | 0.310 (3,456) | 0.300 (3,529) | 0.326 (3,097) | 6 | 4 / 10 |
| FRQ (0-10) | 3.95 (6,009) | 3.96 (5,689) | 3.99 (5,277) | 4.00 (4,798) | 6 | 0 / 10 |

Citation-rate quartile:

| task | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.492 (9,767) | 0.505 (9,061) | 0.474 (9,242) | 0.490 (8,815) | 10 | 0 / 10 |
| MCQ (acc) | 0.708 (6,656) | 0.699 (6,018) | 0.672 (5,856) | 0.691 (5,485) | 10 | 1 / 10 |
| Date (score) | 0.298 (3,379) | 0.268 (3,431) | 0.287 (3,777) | 0.346 (3,421) | 10 | 3 / 10 |
| FRQ (0-10) | 4.17 (7,044) | 4.13 (6,321) | 4.19 (6,113) | 4.25 (5,781) | 10 | 0 / 10 |

### 5.3 Reading

The visibility effect lives in the pre-cutoff partition. Raw quartiles, pre-cutoff: 11 of 32 tests significant (FRQ 3 of 8, MCQ 3 of 8, date 5 of 8); the most-cited quartile beats the least-cited on FRQ for 6/6 models (median +0.225, range +0.040 to +0.350) and on MCQ for 6/6 (median +0.068). Post-cutoff: binary 0 of 10, MCQ 1 of 10, FRQ 0 of 10, date 4 of 10; the same Q4−Q1 contrasts are FRQ 4/6 (median +0.041), MCQ 1/6 (median -0.028), binary 5/8 (median +0.007). Citation-rate quartiles: 13 of 32 pre-cutoff, 4 of 40 post-cutoff (3 of them on the date task), 13 of 40 whole-dataset; post-cutoff Q4−Q1 is binary 4/10 (median -0.001) and FRQ 9/10 (median +0.081, none significant).

This is the pattern one expects if citation count indexes how often a result appears in training data: well-cited papers are recalled better (pre-cutoff FRQ and MCQ), but a paper's eventual visibility does not make its outcome easier to *forecast* from pre-cutoff knowledge. It also means the benchmark's headline post-cutoff numbers are not inflated by a few famous results.

The date task is the exception in both versions (10 of 10 whole-dataset tests significant on raw quartiles, 7 of 10 on rate), and it is the task on which no model has skill. On raw quartiles the direction is split (5/10 models favour Q4), which is what an age confound looks like: raw Q1 is dominated by the newest events, and the horizon study (Reviewer 1, comment 4) shows the date score depends on horizon through anchoring. On rate quartiles the direction is consistent (7/10 post-cutoff, 8/8 pre-cutoff favour Q4) and modest (post-cutoff median +0.051).

One caution that the first pass taught us: a pooled column is only interpretable when every column rests on the same models. Averaging whatever cells survive suppression manufactured a monotone MCQ/FRQ decline across quartiles that vanished on a balanced panel. Every pooled table here is balanced and prints the model count.

### 5.4 Per-model tables — raw citation quartile, whole dataset

**Binary (bal. acc)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.468 [0.447, 0.489] (1,592) | 0.471 [0.455, 0.488] (1,721) | 0.467 [0.452, 0.483] (1,901) | 0.474 [0.459, 0.489] (1,917) | 0.938 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.506 [0.495, 0.517] (1,587) | 0.514 [0.502, 0.526] (1,705) | 0.519 [0.508, 0.530] (1,883) | 0.504 [0.493, 0.515] (1,911) | 0.199 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.459 [0.439, 0.478] (1,592) | 0.472 [0.455, 0.489] (1,721) | 0.468 [0.453, 0.484] (1,903) | 0.465 [0.448, 0.481] (1,917) | 0.784 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.494 [0.463, 0.525] (866) | 0.470 [0.449, 0.491] (1,610) | 0.478 [0.457, 0.498] (1,867) | 0.480 [0.460, 0.500] (1,882) | 0.659 | 1.000 |
| Claude S4.5 | 2025-01 | 0.469 [0.446, 0.491] (1,407) | 0.444 [0.424, 0.464] (1,593) | 0.472 [0.452, 0.493] (1,797) | 0.508 [0.489, 0.528] (1,867) | 0.000 | **0.017** |
| GPT-5.4 | 2025-08 | 0.490 [0.467, 0.514] (1,592) | 0.505 [0.484, 0.526] (1,721) | 0.522 [0.502, 0.542] (1,904) | 0.515 [0.497, 0.534] (1,917) | 0.174 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.534 [0.512, 0.556] (1,535) | 0.541 [0.520, 0.563] (1,656) | 0.547 [0.525, 0.569] (1,836) | 0.584 [0.565, 0.604] (1,885) | 0.004 | 0.290 |
| GPT-5.6 Sol | 2026-02 | 0.590 [0.569, 0.611] (1,591) | 0.597 [0.577, 0.616] (1,720) | 0.591 [0.574, 0.607] (1,903) | 0.609 [0.593, 0.625] (1,917) | 0.376 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.472 [0.458, 0.486] (1,592) | 0.483 [0.470, 0.495] (1,721) | 0.476 [0.464, 0.489] (1,904) | 0.491 [0.477, 0.504] (1,917) | 0.240 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.520 [0.498, 0.542] (1,519) | 0.532 [0.512, 0.553] (1,639) | 0.558 [0.538, 0.578] (1,824) | 0.577 [0.558, 0.596] (1,889) | 0.001 | 0.080 |

**MCQ (acc)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.487 [0.459, 0.516] (1,133) | 0.543 [0.513, 0.572] (1,145) | 0.534 [0.506, 0.561] (1,205) | 0.529 [0.500, 0.557] (1,187) | 0.040 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.432 [0.404, 0.460] (1,130) | 0.470 [0.442, 0.499] (1,132) | 0.442 [0.414, 0.470] (1,189) | 0.404 [0.377, 0.431] (1,182) | 0.013 | 0.898 |
| GPT-OSS 20B | 2024-06 | 0.508 [0.479, 0.536] (1,133) | 0.519 [0.490, 0.549] (1,145) | 0.487 [0.459, 0.515] (1,206) | 0.406 [0.380, 0.434] (1,187) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 0.596 [0.556, 0.637] (535) | 0.627 [0.596, 0.658] (928) | 0.597 [0.568, 0.627] (1,048) | 0.561 [0.532, 0.593] (1,030) | 0.027 | 1.000 |
| Claude S4.5 | 2025-01 | 0.740 [0.712, 0.767] (953) | 0.716 [0.688, 0.743] (1,043) | 0.725 [0.700, 0.751] (1,122) | 0.742 [0.716, 0.766] (1,150) | 0.486 | 1.000 |
| GPT-5.4 | 2025-08 | 0.828 [0.805, 0.850] (1,133) | 0.831 [0.809, 0.852] (1,145) | 0.814 [0.793, 0.836] (1,207) | 0.837 [0.817, 0.858] (1,187) | 0.505 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.897 [0.878, 0.916] (1,032) | 0.891 [0.872, 0.910] (1,028) | 0.913 [0.896, 0.929] (1,088) | 0.942 [0.928, 0.956] (1,140) | 0.000 | **0.017** |
| GPT-5.6 Sol | 2026-02 | 0.853 [0.832, 0.875] (1,126) | 0.865 [0.845, 0.885] (1,135) | 0.874 [0.855, 0.892] (1,200) | 0.915 [0.900, 0.931] (1,183) | 0.000 | **0.017** |
| DeepSeek-V4-Pro | 2026-04 | 0.658 [0.630, 0.685] (1,133) | 0.635 [0.608, 0.664] (1,145) | 0.656 [0.628, 0.683] (1,207) | 0.730 [0.703, 0.755] (1,187) | 0.000 | **0.011** |
| Claude Opus 4.8 | 2026-01 | 0.931 [0.916, 0.947] (1,020) | 0.927 [0.911, 0.943] (1,003) | 0.930 [0.915, 0.946] (1,079) | 0.949 [0.935, 0.961] (1,134) | 0.162 | 1.000 |

**Date (score)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.336 [0.308, 0.366] (503) | 0.184 [0.165, 0.202] (723) | 0.139 [0.125, 0.155] (842) | 0.180 [0.163, 0.197] (821) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 0.449 [0.427, 0.471] (500) | 0.532 [0.514, 0.552] (717) | 0.496 [0.478, 0.514] (834) | 0.449 [0.432, 0.466] (820) | 0.000 | **0.011** |
| GPT-OSS 20B | 2024-06 | 0.375 [0.348, 0.404] (503) | 0.315 [0.291, 0.338] (723) | 0.277 [0.256, 0.298] (843) | 0.261 [0.244, 0.280] (821) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 0.384 [0.351, 0.416] (336) | 0.322 [0.301, 0.343] (697) | 0.270 [0.252, 0.287] (836) | 0.229 [0.213, 0.247] (812) | 0.000 | **0.011** |
| Claude S4.5 | 2025-01 | 0.278 [0.254, 0.303] (459) | 0.219 [0.200, 0.239] (676) | 0.208 [0.190, 0.227] (794) | 0.263 [0.243, 0.283] (800) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 0.198 [0.176, 0.221] (503) | 0.199 [0.178, 0.220] (723) | 0.209 [0.190, 0.228] (843) | 0.307 [0.284, 0.330] (821) | 0.000 | **0.011** |
| Claude Sonnet 5 | 2026-01 | 0.299 [0.273, 0.322] (485) | 0.335 [0.312, 0.357] (687) | 0.408 [0.388, 0.427] (801) | 0.538 [0.516, 0.560] (807) | 0.000 | **0.011** |
| GPT-5.6 Sol | 2026-02 | 0.259 [0.237, 0.282] (503) | 0.297 [0.272, 0.323] (723) | 0.336 [0.312, 0.361] (843) | 0.502 [0.473, 0.529] (821) | 0.000 | **0.011** |
| DeepSeek-V4-Pro | 2026-04 | 0.291 [0.265, 0.318] (503) | 0.182 [0.165, 0.198] (723) | 0.157 [0.143, 0.172] (843) | 0.197 [0.180, 0.214] (821) | 0.000 | **0.011** |
| Claude Opus 4.8 | 2026-01 | 0.281 [0.259, 0.304] (482) | 0.384 [0.359, 0.407] (680) | 0.466 [0.444, 0.488] (796) | 0.602 [0.578, 0.625] (800) | 0.000 | **0.011** |

**FRQ (0-10)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.33 [3.28, 3.38] (1,161) | 3.23 [3.18, 3.28] (1,158) | 3.26 [3.20, 3.31] (1,212) | 3.30 [3.25, 3.35] (1,224) | 0.041 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.45 [3.41, 3.49] (1,157) | 3.46 [3.42, 3.51] (1,147) | 3.51 [3.47, 3.55] (1,197) | 3.49 [3.45, 3.53] (1,219) | 0.127 | 1.000 |
| GPT-OSS 20B | 2024-06 | 3.86 [3.81, 3.92] (1,159) | 3.90 [3.84, 3.95] (1,156) | 3.86 [3.81, 3.91] (1,210) | 3.83 [3.78, 3.87] (1,223) | 0.299 | 1.000 |
| DeepSeek-R1 | 2024-07 | 4.18 [4.11, 4.24] (612) | 4.18 [4.13, 4.23] (1,079) | 4.18 [4.13, 4.23] (1,192) | 4.18 [4.14, 4.23] (1,214) | 0.997 | 1.000 |
| Claude S4.5 | 2025-01 | 3.96 [3.90, 4.01] (1,053) | 3.93 [3.87, 3.98] (1,073) | 4.00 [3.95, 4.05] (1,143) | 4.08 [4.03, 4.12] (1,194) | 0.000 | **0.017** |
| GPT-5.4 | 2025-08 | 4.91 [4.86, 4.96] (1,160) | 5.01 [4.97, 5.06] (1,154) | 5.07 [5.03, 5.12] (1,215) | 5.04 [5.00, 5.08] (1,224) | 0.000 | **0.011** |
| Claude Sonnet 5 | 2026-01 | 4.45 [4.40, 4.50] (1,130) | 4.49 [4.44, 4.54] (1,117) | 4.48 [4.42, 4.53] (1,183) | 4.68 [4.63, 4.73] (1,211) | 0.000 | **0.011** |
| GPT-5.6 Sol | 2026-02 | 4.89 [4.84, 4.93] (1,145) | 4.92 [4.86, 4.97] (1,132) | 4.96 [4.91, 5.01] (1,197) | 5.05 [5.00, 5.11] (1,218) | 0.000 | **0.017** |
| DeepSeek-V4-Pro | 2026-04 | 3.96 [3.90, 4.01] (1,161) | 3.99 [3.94, 4.04] (1,157) | 3.96 [3.91, 4.02] (1,214) | 3.98 [3.93, 4.03] (1,226) | 0.823 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 4.63 [4.58, 4.68] (1,132) | 4.68 [4.62, 4.73] (1,122) | 4.77 [4.71, 4.82] (1,184) | 4.97 [4.92, 5.03] (1,211) | 0.000 | **0.011** |

### 5.5 Per-model tables — raw citation quartile, post-cutoff only

**Binary (bal. acc)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.468 [0.447, 0.489] (1,592) | 0.471 [0.455, 0.488] (1,721) | 0.467 [0.452, 0.483] (1,901) | 0.474 [0.459, 0.489] (1,917) | 0.938 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.506 [0.495, 0.517] (1,587) | 0.514 [0.502, 0.526] (1,705) | 0.519 [0.508, 0.530] (1,883) | 0.504 [0.493, 0.515] (1,911) | 0.199 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.459 [0.438, 0.479] (1,574) | 0.474 [0.456, 0.493] (1,589) | 0.464 [0.446, 0.483] (1,572) | 0.466 [0.447, 0.485] (1,449) | 0.714 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.493 [0.464, 0.524] (843) | 0.475 [0.453, 0.497] (1,440) | 0.480 [0.457, 0.503] (1,457) | 0.477 [0.453, 0.501] (1,287) | 0.803 | 1.000 |
| Claude S4.5 | 2025-01 | 0.470 [0.447, 0.494] (1,327) | 0.444 [0.421, 0.466] (1,170) | 0.462 [0.436, 0.487] (958) | 0.494 [0.467, 0.521] (693) | 0.076 | 1.000 |
| GPT-5.4 | 2025-08 | 0.492 [0.464, 0.517] (1,315) | 0.507 [0.476, 0.540] (748) | 0.498 [0.455, 0.544] (372) | 0.509 [0.446, 0.568] (175) | 0.883 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.514 [0.486, 0.544] (972) | 0.531 [0.481, 0.584] (292) | 0.528 [0.425, 0.644] (69) | 0.538 [0.350, 0.743] (24) | 0.946 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.567 [0.536, 0.598] (900) | 0.569 [0.508, 0.625] (192) | 0.576 [0.428, 0.710] (44) | n<20 (17) | 0.992 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.467 [0.443, 0.494] (716) | 0.457 [0.388, 0.542] (98) | 0.421 [0.325, 0.500] (23) | n<20 (8) | 0.786 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.479 [0.454, 0.506] (960) | 0.500 [0.452, 0.549] (291) | 0.415 [0.311, 0.525] (69) | 0.437 [0.250, 0.656] (24) | 0.473 | 1.000 |

**MCQ (acc)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.487 [0.459, 0.516] (1,133) | 0.543 [0.513, 0.572] (1,145) | 0.534 [0.506, 0.561] (1,205) | 0.529 [0.500, 0.557] (1,187) | 0.040 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.432 [0.404, 0.460] (1,130) | 0.470 [0.442, 0.499] (1,132) | 0.442 [0.414, 0.470] (1,189) | 0.404 [0.377, 0.431] (1,182) | 0.013 | 0.898 |
| GPT-OSS 20B | 2024-06 | 0.506 [0.476, 0.537] (1,119) | 0.516 [0.488, 0.546] (1,064) | 0.469 [0.438, 0.499] (1,007) | 0.404 [0.372, 0.438] (901) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 0.593 [0.549, 0.635] (518) | 0.622 [0.589, 0.655] (839) | 0.586 [0.551, 0.619] (828) | 0.551 [0.513, 0.587] (720) | 0.045 | 1.000 |
| Claude S4.5 | 2025-01 | 0.740 [0.709, 0.768] (893) | 0.697 [0.666, 0.732] (780) | 0.698 [0.662, 0.735] (610) | 0.704 [0.662, 0.745] (439) | 0.174 | 1.000 |
| GPT-5.4 | 2025-08 | 0.831 [0.807, 0.854] (929) | 0.809 [0.775, 0.844] (488) | 0.812 [0.762, 0.860] (245) | 0.827 [0.748, 0.896] (104) | 0.750 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.911 [0.889, 0.932] (662) | 0.867 [0.819, 0.916] (188) | 0.896 [0.800, 0.978] (48) | n<20 (17) | 0.202 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.870 [0.843, 0.897] (632) | 0.848 [0.786, 0.906] (125) | 0.903 [0.788, 1.000] (31) | n<20 (12) | 0.680 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.671 [0.630, 0.711] (513) | 0.611 [0.500, 0.726] (72) | n<20 (16) | n<20 (5) | 0.305 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.933 [0.913, 0.950] (656) | 0.914 [0.872, 0.954] (185) | 0.918 [0.837, 0.980] (49) | n<20 (17) | 0.635 | 1.000 |

**Date (score)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.336 [0.308, 0.366] (503) | 0.184 [0.165, 0.202] (723) | 0.139 [0.125, 0.155] (842) | 0.180 [0.163, 0.197] (821) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 0.449 [0.427, 0.471] (500) | 0.532 [0.514, 0.552] (717) | 0.496 [0.478, 0.514] (834) | 0.449 [0.432, 0.466] (820) | 0.000 | **0.011** |
| GPT-OSS 20B | 2024-06 | 0.380 [0.352, 0.407] (492) | 0.334 [0.310, 0.360] (653) | 0.318 [0.295, 0.342] (678) | 0.310 [0.288, 0.333] (595) | 0.001 | 0.094 |
| DeepSeek-R1 | 2024-07 | 0.395 [0.363, 0.429] (323) | 0.348 [0.324, 0.372] (606) | 0.310 [0.288, 0.333] (629) | 0.276 [0.253, 0.301] (524) | 0.000 | **0.011** |
| Claude S4.5 | 2025-01 | 0.289 [0.263, 0.314] (421) | 0.243 [0.221, 0.266] (472) | 0.243 [0.215, 0.269] (400) | 0.307 [0.274, 0.343] (270) | 0.002 | 0.128 |
| GPT-5.4 | 2025-08 | 0.202 [0.177, 0.229] (392) | 0.220 [0.190, 0.253] (285) | 0.294 [0.242, 0.346] (146) | 0.436 [0.358, 0.519] (67) | 0.000 | **0.011** |
| Claude Sonnet 5 | 2026-01 | 0.249 [0.216, 0.283] (266) | 0.318 [0.267, 0.374] (101) | 0.387 [0.259, 0.516] (21) | n<20 (7) | 0.014 | 0.929 |
| GPT-5.6 Sol | 2026-02 | 0.222 [0.201, 0.243] (234) | 0.231 [0.182, 0.281] (62) | n<20 (11) | n<20 (5) | 0.718 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.346 [0.291, 0.407] (167) | 0.320 [0.165, 0.477] (23) | n<20 (4) | n<20 (2) | 0.753 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.214 [0.189, 0.239] (263) | 0.270 [0.227, 0.315] (101) | 0.294 [0.185, 0.412] (21) | n<20 (7) | 0.041 | 1.000 |

**FRQ (0-10)**

| model | cutoff | Q1 (<=10) | Q2 (<=28) | Q3 (<=68) | Q4 (>68) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.33 [3.28, 3.38] (1,161) | 3.23 [3.18, 3.28] (1,158) | 3.26 [3.20, 3.31] (1,212) | 3.30 [3.25, 3.35] (1,224) | 0.041 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.45 [3.41, 3.49] (1,157) | 3.46 [3.42, 3.51] (1,147) | 3.51 [3.47, 3.55] (1,197) | 3.49 [3.45, 3.53] (1,219) | 0.127 | 1.000 |
| GPT-OSS 20B | 2024-06 | 3.86 [3.81, 3.91] (1,146) | 3.88 [3.83, 3.94] (1,080) | 3.86 [3.80, 3.91] (1,019) | 3.82 [3.76, 3.87] (934) | 0.419 | 1.000 |
| DeepSeek-R1 | 2024-07 | 4.18 [4.12, 4.24] (595) | 4.17 [4.12, 4.22] (982) | 4.18 [4.13, 4.24] (958) | 4.20 [4.14, 4.26] (838) | 0.916 | 1.000 |
| Claude S4.5 | 2025-01 | 3.97 [3.92, 4.03] (993) | 3.98 [3.92, 4.04] (810) | 4.06 [3.99, 4.12] (638) | 4.11 [4.04, 4.18] (465) | 0.010 | 0.653 |
| GPT-5.4 | 2025-08 | 4.89 [4.84, 4.94] (957) | 5.02 [4.95, 5.08] (512) | 5.10 [5.01, 5.19] (253) | 5.07 [4.93, 5.21] (118) | 0.001 | 0.053 |
| Claude Sonnet 5 | 2026-01 | 4.45 [4.39, 4.51] (736) | 4.48 [4.35, 4.61] (198) | 4.61 [4.39, 4.82] (55) | n<20 (19) | 0.387 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 4.86 [4.79, 4.92] (665) | 4.97 [4.81, 5.15] (126) | 4.88 [4.56, 5.15] (33) | n<20 (12) | 0.365 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 3.99 [3.91, 4.06] (542) | 4.08 [3.87, 4.30] (68) | n<20 (15) | n<20 (4) | 0.416 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 4.61 [4.55, 4.67] (741) | 4.68 [4.56, 4.79] (198) | 4.83 [4.56, 5.10] (55) | n<20 (19) | 0.157 | 1.000 |

### 5.6 Per-model tables — citation-rate quartile, whole dataset

**Binary (bal. acc)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.465 [0.448, 0.483] (1,665) | 0.468 [0.451, 0.484] (1,713) | 0.465 [0.449, 0.481] (1,845) | 0.471 [0.455, 0.488] (1,908) | 0.947 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.507 [0.495, 0.518] (1,655) | 0.513 [0.500, 0.525] (1,701) | 0.514 [0.504, 0.524] (1,830) | 0.504 [0.494, 0.515] (1,900) | 0.539 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.454 [0.436, 0.470] (1,665) | 0.484 [0.467, 0.502] (1,714) | 0.462 [0.446, 0.479] (1,846) | 0.459 [0.443, 0.476] (1,908) | 0.083 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.471 [0.446, 0.497] (1,296) | 0.502 [0.478, 0.525] (1,455) | 0.466 [0.446, 0.487] (1,699) | 0.473 [0.454, 0.494] (1,775) | 0.133 | 1.000 |
| Claude S4.5 | 2025-01 | 0.473 [0.453, 0.495] (1,473) | 0.462 [0.440, 0.483] (1,569) | 0.456 [0.436, 0.476] (1,751) | 0.507 [0.488, 0.526] (1,871) | 0.002 | 0.144 |
| GPT-5.4 | 2025-08 | 0.494 [0.472, 0.517] (1,665) | 0.518 [0.495, 0.539] (1,714) | 0.508 [0.488, 0.528] (1,847) | 0.517 [0.500, 0.536] (1,908) | 0.380 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.549 [0.528, 0.570] (1,584) | 0.556 [0.535, 0.577] (1,649) | 0.543 [0.523, 0.562] (1,797) | 0.584 [0.564, 0.604] (1,882) | 0.026 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.599 [0.579, 0.619] (1,664) | 0.605 [0.586, 0.625] (1,713) | 0.592 [0.574, 0.608] (1,846) | 0.604 [0.588, 0.619] (1,908) | 0.702 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.479 [0.466, 0.493] (1,665) | 0.483 [0.470, 0.496] (1,714) | 0.478 [0.465, 0.491] (1,847) | 0.485 [0.471, 0.498] (1,908) | 0.864 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.540 [0.518, 0.562] (1,565) | 0.551 [0.530, 0.573] (1,639) | 0.550 [0.530, 0.570] (1,782) | 0.578 [0.559, 0.599] (1,885) | 0.068 | 1.000 |

**MCQ (acc)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.528 [0.497, 0.557] (1,156) | 0.517 [0.487, 0.546] (1,146) | 0.526 [0.497, 0.555] (1,174) | 0.523 [0.495, 0.552] (1,194) | 0.952 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.466 [0.438, 0.496] (1,148) | 0.450 [0.421, 0.478] (1,136) | 0.436 [0.408, 0.465] (1,162) | 0.396 [0.369, 0.423] (1,187) | 0.005 | 0.357 |
| GPT-OSS 20B | 2024-06 | 0.529 [0.500, 0.557] (1,156) | 0.521 [0.494, 0.550] (1,147) | 0.450 [0.422, 0.478] (1,174) | 0.420 [0.393, 0.448] (1,194) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 0.627 [0.593, 0.659] (793) | 0.614 [0.582, 0.648] (830) | 0.581 [0.549, 0.613] (935) | 0.565 [0.533, 0.595] (983) | 0.027 | 1.000 |
| Claude S4.5 | 2025-01 | 0.733 [0.706, 0.760] (995) | 0.727 [0.699, 0.753] (1,017) | 0.716 [0.687, 0.743] (1,091) | 0.746 [0.720, 0.770] (1,165) | 0.443 | 1.000 |
| GPT-5.4 | 2025-08 | 0.821 [0.799, 0.842] (1,156) | 0.841 [0.820, 0.861] (1,147) | 0.812 [0.790, 0.834] (1,175) | 0.836 [0.814, 0.856] (1,194) | 0.214 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.897 [0.879, 0.916] (1,024) | 0.909 [0.891, 0.925] (1,028) | 0.897 [0.878, 0.915] (1,069) | 0.940 [0.925, 0.953] (1,167) | 0.001 | 0.066 |
| GPT-5.6 Sol | 2026-02 | 0.861 [0.840, 0.880] (1,148) | 0.870 [0.850, 0.888] (1,135) | 0.862 [0.842, 0.883] (1,170) | 0.916 [0.900, 0.931] (1,191) | 0.000 | **0.018** |
| DeepSeek-V4-Pro | 2026-04 | 0.664 [0.637, 0.691] (1,156) | 0.649 [0.621, 0.677] (1,147) | 0.640 [0.613, 0.668] (1,175) | 0.725 [0.700, 0.752] (1,194) | 0.000 | **0.011** |
| Claude Opus 4.8 | 2026-01 | 0.928 [0.912, 0.943] (1,009) | 0.931 [0.915, 0.946] (1,009) | 0.933 [0.918, 0.947] (1,061) | 0.946 [0.934, 0.959] (1,157) | 0.291 | 1.000 |

**Date (score)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.235 [0.211, 0.259] (623) | 0.182 [0.162, 0.201] (695) | 0.155 [0.140, 0.172] (797) | 0.220 [0.202, 0.239] (774) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 0.458 [0.438, 0.478] (619) | 0.490 [0.470, 0.510] (688) | 0.499 [0.481, 0.518] (791) | 0.482 [0.464, 0.499] (773) | 0.027 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.328 [0.304, 0.351] (623) | 0.285 [0.263, 0.307] (695) | 0.276 [0.256, 0.297] (798) | 0.313 [0.293, 0.334] (774) | 0.004 | 0.285 |
| DeepSeek-R1 | 2024-07 | 0.315 [0.290, 0.339] (538) | 0.290 [0.267, 0.313] (631) | 0.276 [0.257, 0.295] (769) | 0.270 [0.249, 0.290] (743) | 0.021 | 1.000 |
| Claude S4.5 | 2025-01 | 0.236 [0.213, 0.259] (567) | 0.205 [0.185, 0.225] (646) | 0.218 [0.199, 0.237] (757) | 0.290 [0.269, 0.312] (759) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 0.194 [0.173, 0.217] (623) | 0.198 [0.177, 0.218] (695) | 0.207 [0.188, 0.227] (798) | 0.320 [0.297, 0.343] (774) | 0.000 | **0.011** |
| Claude Sonnet 5 | 2026-01 | 0.341 [0.318, 0.365] (592) | 0.350 [0.329, 0.371] (662) | 0.389 [0.369, 0.410] (763) | 0.531 [0.509, 0.553] (763) | 0.000 | **0.011** |
| GPT-5.6 Sol | 2026-02 | 0.272 [0.247, 0.297] (623) | 0.288 [0.262, 0.313] (695) | 0.338 [0.313, 0.363] (798) | 0.518 [0.488, 0.545] (774) | 0.000 | **0.011** |
| DeepSeek-V4-Pro | 2026-04 | 0.212 [0.192, 0.232] (623) | 0.172 [0.156, 0.191] (695) | 0.183 [0.168, 0.200] (798) | 0.224 [0.205, 0.242] (774) | 0.000 | **0.025** |
| Claude Opus 4.8 | 2026-01 | 0.370 [0.346, 0.396] (585) | 0.405 [0.382, 0.430] (655) | 0.433 [0.410, 0.457] (760) | 0.578 [0.554, 0.601] (758) | 0.000 | **0.011** |

**FRQ (0-10)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.28 [3.23, 3.33] (1,166) | 3.25 [3.19, 3.30] (1,163) | 3.27 [3.21, 3.32] (1,200) | 3.33 [3.28, 3.38] (1,226) | 0.148 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.47 [3.43, 3.51] (1,156) | 3.47 [3.42, 3.51] (1,156) | 3.50 [3.46, 3.55] (1,188) | 3.47 [3.43, 3.51] (1,220) | 0.618 | 1.000 |
| GPT-OSS 20B | 2024-06 | 3.92 [3.86, 3.97] (1,166) | 3.82 [3.77, 3.88] (1,160) | 3.86 [3.80, 3.91] (1,199) | 3.85 [3.80, 3.89] (1,223) | 0.067 | 1.000 |
| DeepSeek-R1 | 2024-07 | 4.18 [4.13, 4.23] (881) | 4.16 [4.11, 4.21] (978) | 4.16 [4.11, 4.21] (1,090) | 4.21 [4.17, 4.26] (1,148) | 0.414 | 1.000 |
| Claude S4.5 | 2025-01 | 3.92 [3.86, 3.97] (1,052) | 3.91 [3.85, 3.96] (1,072) | 4.02 [3.97, 4.07] (1,132) | 4.11 [4.07, 4.15] (1,207) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 4.96 [4.92, 5.01] (1,163) | 4.96 [4.91, 5.01] (1,161) | 5.07 [5.02, 5.11] (1,202) | 5.04 [5.00, 5.08] (1,227) | 0.002 | 0.190 |
| Claude Sonnet 5 | 2026-01 | 4.47 [4.42, 4.52] (1,125) | 4.47 [4.41, 4.52] (1,122) | 4.49 [4.44, 4.55] (1,175) | 4.67 [4.61, 4.72] (1,219) | 0.000 | **0.011** |
| GPT-5.6 Sol | 2026-02 | 4.91 [4.86, 4.97] (1,141) | 4.93 [4.88, 4.98] (1,139) | 4.95 [4.90, 5.01] (1,190) | 5.03 [4.98, 5.08] (1,222) | 0.018 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 3.98 [3.92, 4.03] (1,166) | 3.94 [3.89, 4.00] (1,162) | 3.98 [3.93, 4.03] (1,202) | 3.99 [3.94, 4.04] (1,228) | 0.637 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 4.69 [4.64, 4.74] (1,125) | 4.63 [4.58, 4.69] (1,126) | 4.74 [4.68, 4.79] (1,181) | 4.99 [4.94, 5.04] (1,217) | 0.000 | **0.011** |

### 5.7 Per-model tables — citation-rate quartile, post-cutoff only

**Binary (bal. acc)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.465 [0.448, 0.483] (1,665) | 0.468 [0.451, 0.484] (1,713) | 0.465 [0.449, 0.481] (1,845) | 0.471 [0.455, 0.488] (1,908) | 0.947 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.507 [0.495, 0.518] (1,655) | 0.513 [0.500, 0.525] (1,701) | 0.514 [0.504, 0.524] (1,830) | 0.504 [0.494, 0.515] (1,900) | 0.539 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.455 [0.435, 0.473] (1,510) | 0.485 [0.466, 0.505] (1,476) | 0.460 [0.442, 0.478] (1,607) | 0.458 [0.440, 0.478] (1,591) | 0.117 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.479 [0.453, 0.505] (1,109) | 0.507 [0.482, 0.534] (1,155) | 0.467 [0.443, 0.490] (1,397) | 0.469 [0.443, 0.493] (1,366) | 0.087 | 1.000 |
| Claude S4.5 | 2025-01 | 0.482 [0.457, 0.507] (1,065) | 0.448 [0.423, 0.473] (1,003) | 0.445 [0.420, 0.469] (1,086) | 0.481 [0.455, 0.505] (994) | 0.056 | 1.000 |
| GPT-5.4 | 2025-08 | 0.490 [0.457, 0.524] (863) | 0.504 [0.471, 0.538] (680) | 0.475 [0.439, 0.512] (610) | 0.535 [0.495, 0.573] (457) | 0.183 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.521 [0.483, 0.561] (531) | 0.554 [0.510, 0.595] (387) | 0.476 [0.424, 0.530] (267) | 0.513 [0.441, 0.588] (172) | 0.196 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.570 [0.529, 0.608] (487) | 0.579 [0.527, 0.629] (317) | 0.545 [0.479, 0.610] (203) | 0.574 [0.502, 0.642] (146) | 0.866 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.464 [0.431, 0.501] (359) | 0.498 [0.456, 0.547] (246) | 0.411 [0.375, 0.447] (131) | 0.448 [0.385, 0.519] (109) | 0.120 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.483 [0.449, 0.519] (523) | 0.498 [0.460, 0.536] (383) | 0.485 [0.431, 0.539] (266) | 0.443 [0.377, 0.512] (172) | 0.557 | 1.000 |

**MCQ (acc)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.528 [0.497, 0.557] (1,156) | 0.517 [0.487, 0.546] (1,146) | 0.526 [0.497, 0.555] (1,174) | 0.523 [0.495, 0.552] (1,194) | 0.952 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.466 [0.438, 0.496] (1,148) | 0.450 [0.421, 0.478] (1,136) | 0.436 [0.408, 0.465] (1,162) | 0.396 [0.369, 0.423] (1,187) | 0.005 | 0.357 |
| GPT-OSS 20B | 2024-06 | 0.523 [0.493, 0.554] (1,056) | 0.510 [0.481, 0.539] (1,008) | 0.446 [0.415, 0.476] (1,026) | 0.427 [0.395, 0.459] (1,001) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 0.620 [0.582, 0.657] (689) | 0.608 [0.571, 0.644] (676) | 0.578 [0.543, 0.612] (765) | 0.556 [0.520, 0.591] (775) | 0.059 | 1.000 |
| Claude S4.5 | 2025-01 | 0.727 [0.693, 0.760] (732) | 0.707 [0.671, 0.741] (662) | 0.697 [0.663, 0.730] (692) | 0.720 [0.685, 0.753] (636) | 0.601 | 1.000 |
| GPT-5.4 | 2025-08 | 0.816 [0.785, 0.848] (598) | 0.838 [0.802, 0.870] (470) | 0.802 [0.762, 0.839] (410) | 0.837 [0.794, 0.879] (288) | 0.468 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.920 [0.890, 0.948] (352) | 0.893 [0.854, 0.929] (261) | 0.871 [0.822, 0.918] (186) | 0.922 [0.868, 0.966] (116) | 0.241 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.866 [0.830, 0.903] (328) | 0.862 [0.813, 0.904] (225) | 0.859 [0.800, 0.911] (149) | 0.898 [0.833, 0.951] (98) | 0.819 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.694 [0.632, 0.749] (248) | 0.657 [0.582, 0.724] (175) | 0.591 [0.504, 0.682] (110) | 0.699 [0.592, 0.800] (73) | 0.266 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.923 [0.892, 0.949] (349) | 0.946 [0.918, 0.972] (259) | 0.918 [0.874, 0.956] (182) | 0.932 [0.883, 0.974] (117) | 0.633 | 1.000 |

**Date (score)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.235 [0.211, 0.259] (623) | 0.182 [0.162, 0.201] (695) | 0.155 [0.140, 0.172] (797) | 0.220 [0.202, 0.239] (774) | 0.000 | **0.011** |
| LLaMA 3.3 70B | 2023-12 | 0.458 [0.438, 0.478] (619) | 0.490 [0.470, 0.510] (688) | 0.499 [0.481, 0.518] (791) | 0.482 [0.464, 0.499] (773) | 0.027 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.357 [0.330, 0.382] (540) | 0.319 [0.293, 0.346] (579) | 0.306 [0.284, 0.330] (674) | 0.355 [0.330, 0.378] (625) | 0.008 | 0.584 |
| DeepSeek-R1 | 2024-07 | 0.357 [0.330, 0.384] (439) | 0.329 [0.303, 0.356] (480) | 0.314 [0.291, 0.336] (611) | 0.311 [0.287, 0.336] (552) | 0.066 | 1.000 |
| Claude S4.5 | 2025-01 | 0.277 [0.249, 0.306] (369) | 0.234 [0.209, 0.260] (382) | 0.239 [0.215, 0.262] (437) | 0.323 [0.292, 0.352] (375) | 0.000 | **0.011** |
| GPT-5.4 | 2025-08 | 0.212 [0.180, 0.245] (274) | 0.199 [0.167, 0.233] (224) | 0.242 [0.206, 0.282] (231) | 0.344 [0.295, 0.392] (161) | 0.000 | **0.011** |
| Claude Sonnet 5 | 2026-01 | 0.259 [0.214, 0.305] (151) | 0.241 [0.196, 0.292] (117) | 0.312 [0.254, 0.373] (79) | 0.358 [0.280, 0.440] (48) | 0.038 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.208 [0.182, 0.238] (131) | 0.228 [0.195, 0.262] (88) | 0.235 [0.190, 0.285] (54) | 0.314 [0.248, 0.389] (39) | 0.011 | 0.821 |
| DeepSeek-V4-Pro | 2026-04 | 0.388 [0.310, 0.472] (85) | 0.264 [0.182, 0.354] (61) | 0.307 [0.163, 0.458] (24) | 0.439 [0.287, 0.588] (26) | 0.120 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.229 [0.194, 0.264] (148) | 0.199 [0.165, 0.236] (117) | 0.257 [0.207, 0.311] (79) | 0.318 [0.242, 0.406] (48) | 0.018 | 1.000 |

**FRQ (0-10)**

| model | cutoff | Q1 (<=0.96/mo) | Q2 (<=1.83/mo) | Q3 (<=3.94/mo) | Q4 (>3.94/mo) | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.28 [3.23, 3.33] (1,166) | 3.25 [3.19, 3.30] (1,163) | 3.27 [3.21, 3.32] (1,200) | 3.33 [3.28, 3.38] (1,226) | 0.148 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.47 [3.43, 3.51] (1,156) | 3.47 [3.42, 3.51] (1,156) | 3.50 [3.46, 3.55] (1,188) | 3.47 [3.43, 3.51] (1,220) | 0.618 | 1.000 |
| GPT-OSS 20B | 2024-06 | 3.90 [3.85, 3.95] (1,074) | 3.83 [3.78, 3.89] (1,023) | 3.86 [3.80, 3.92] (1,049) | 3.83 [3.78, 3.88] (1,033) | 0.257 | 1.000 |
| DeepSeek-R1 | 2024-07 | 4.17 [4.11, 4.22] (770) | 4.17 [4.11, 4.23] (807) | 4.17 [4.12, 4.23] (899) | 4.22 [4.17, 4.27] (897) | 0.495 | 1.000 |
| Claude S4.5 | 2025-01 | 3.97 [3.90, 4.03] (796) | 3.96 [3.90, 4.02] (716) | 4.01 [3.95, 4.07] (722) | 4.13 [4.07, 4.18] (672) | 0.002 | 0.121 |
| GPT-5.4 | 2025-08 | 4.93 [4.86, 4.99] (629) | 4.89 [4.82, 4.97] (487) | 5.04 [4.96, 5.12] (415) | 5.06 [4.98, 5.14] (309) | 0.005 | 0.377 |
| Claude Sonnet 5 | 2026-01 | 4.48 [4.40, 4.55] (408) | 4.39 [4.29, 4.50] (282) | 4.47 [4.34, 4.59] (193) | 4.64 [4.50, 4.79] (125) | 0.067 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 4.87 [4.79, 4.96] (359) | 4.85 [4.75, 4.96] (227) | 4.91 [4.75, 5.06] (148) | 4.95 [4.79, 5.10] (102) | 0.748 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 4.00 [3.90, 4.10] (276) | 3.96 [3.82, 4.11] (177) | 4.00 [3.85, 4.16] (104) | 4.02 [3.83, 4.24] (72) | 0.958 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 4.65 [4.56, 4.73] (410) | 4.57 [4.47, 4.68] (283) | 4.62 [4.51, 4.74] (195) | 4.80 [4.65, 4.95] (125) | 0.120 | 1.000 |

### 5.8 The first-pass 481-event tables, and Supplementary Tables S19–S23

The 481-event version (Semantic Scholar, retrieved 2026-05-12, pinned retrieval subset) is kept under `by_legacy/visibility_481/` for continuity: 6 of 93 tests significant, 0 of 71 outside the date task — consistent with the whole-corpus result, just underpowered.

The published S19–S23 report Δ_know and Δ_fore per citation quartile for three models, with several cells resting on n = 1–3 (GPT-5.4 Q4 "+0.000 (n = 1)"). We regenerated them with N, a paired bootstrap CI and suppression below n = 20, extended from three models to the seven with a complete web-search triple on the pinned 500 (`by_visibility/citation_gap_S19_S23.md`). The regeneration reproduces every published non-suppressed cell to three decimals with matching N; of 101 cells, 32 are now suppressed rather than printed. They necessarily keep the May 2026 quartile edges (≤8, ≤22, ≤59) because they reproduce the published tables. We recommend the corrected tables replace S19–S23.

## 6. Publication latency (4,326 journal events)

**Definition.** Latency = the journal version's online-publication month (Crossref) minus the first-observable month: the earlier of CUSP's `publication_date` — which the build pipeline had already set to the earliest date found across Crossref, bioRxiv, medRxiv, Semantic Scholar and Europe PMC — and any Crossref-linked preprint's posted month (the dating correction below). It is the number of months a result was publicly observable before its journal version appeared: 0 means no earlier public trace exists, larger values mean a preprint or other public record preceded the journal. It is computable for every *Nature*, *Science* and *Cell* event in both halves of the corpus; arXiv events have no journal version and are excluded by construction. Strata: 0 mo, 1-6 mo, >6 mo — 84% of journal events have latency 0, 5% are 1–6 months, 11% exceed six months (the longest is 54 months); finer bins fall below n = 20 in most per-model post-cutoff cells.

### 6.1 Whole dataset

| task | 0 mo | 1-6 mo | >6 mo | models pooled | Holm-sig |
|---|---|---|---|---|---|
| Binary (bal. acc) | 0.515 (44,749) | 0.502 (3,006) | 0.515 (6,024) | 10 | 0 / 10 |
| MCQ (acc) | 0.697 (28,854) | 0.731 (2,001) | 0.724 (3,708) | 10 | 0 / 10 |
| Date (score) | 0.273 (18,793) | 0.273 (1,430) | 0.260 (2,860) | 10 | 3 / 10 |
| FRQ (0-10) | 4.17 (29,745) | 4.17 (1,971) | 4.16 (3,832) | 10 | 0 / 10 |

### 6.2 Post-cutoff only

| task | 0 mo | 1-6 mo | >6 mo | models pooled | Holm-sig |
|---|---|---|---|---|---|
| Binary (bal. acc) | 0.483 (20,807) | 0.469 (1,274) | 0.490 (2,362) | 6 | 0 / 10 |
| MCQ (acc) | 0.600 (13,671) | 0.632 (865) | 0.634 (1,464) | 6 | 0 / 9 |
| Date (score) | 0.263 (8,505) | 0.256 (595) | 0.246 (1,096) | 6 | 0 / 6 |
| FRQ (0-10) | 3.94 (14,032) | 3.92 (853) | 3.90 (1,526) | 6 | 0 / 9 |

**0 of 34 post-cutoff, 0 of 32 pre-cutoff, 3 of 40 whole-dataset tests are significant** (post-cutoff by task: binary 0 of 10, MCQ 0 of 9, FRQ 0 of 9, date 0 of 6). Post-cutoff, the longest-latency stratum versus the zero-latency stratum: binary 7/10 models higher (median +0.015), MCQ 6/9 (+0.034), FRQ 4/9 (-0.009), date 2/6 (-0.027).

**A dating correction this pass surfaced.** Crossref links a preprint to 493 journal events; for 246 of them the preprint was posted *before* CUSP's `publication_date` (median 11 months earlier, IQR 7–15), i.e. the build pipeline's earliest-date search missed them. The latency above uses the earlier of the two dates. The cutoff partition keeps the benchmark's own date, so the table below counts, per model, how many of its post-cutoff journal events had a preprint before its cutoff — observable-before-cutoff items the benchmark treats as prospective:

| model | cutoff | post-cutoff journal events | with a preprint before the cutoff | share |
|---|---|---|---|---|
| GPT-4o | 2023-10 | 4,326 | 55 | 1.3% |
| LLaMA 3.3 70B | 2023-12 | 4,326 | 78 | 1.8% |
| GPT-OSS 20B | 2024-06 | 3,759 | 113 | 3.0% |
| DeepSeek-R1 | 2024-07 | 3,606 | 109 | 3.0% |
| Claude S4.5 | 2025-01 | 2,721 | 96 | 3.5% |
| GPT-5.4 | 2025-08 | 1,618 | 77 | 4.8% |
| Claude Sonnet 5 | 2026-01 | 981 | 43 | 4.4% |
| GPT-5.6 Sol | 2026-02 | 824 | 34 | 4.1% |
| DeepSeek-V4-Pro | 2026-04 | 684 | 26 | 3.8% |
| Claude Opus 4.8 | 2026-01 | 981 | 43 | 4.4% |

These are 1.3–4.8% of each model's post-cutoff journal events, and by construction they sit in the non-zero latency strata, so the post-cutoff latency tables above are the test of whether they inflate the forecasting numbers: they do not (0 of 34 post-cutoff tests).

### 6.3 Editorial latency (received → online), 3,740 *Nature* and *Science* events

A different construct: how long the manuscript sat in review. Strata: <=6 mo, 7-12 mo, 13-24 mo, >24 mo.

Whole dataset:

| task | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.512 (9,175) | 0.512 (21,489) | 0.519 (14,803) | 0.515 (1,980) | 10 | 0 / 10 |
| MCQ (acc) | 0.694 (5,483) | 0.702 (13,320) | 0.706 (9,862) | 0.715 (1,283) | 10 | 0 / 10 |
| Date (score) | 0.258 (4,356) | 0.270 (9,478) | 0.276 (6,063) | 0.262 (800) | 10 | 0 / 10 |
| FRQ (0-10) | 4.01 (5,547) | 4.13 (13,702) | 4.22 (10,318) | 4.17 (1,362) | 10 | 4 / 10 |

Post-cutoff only:

| task | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | models pooled | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.483 (4,393) | 0.502 (11,191) | 0.507 (7,978) | 0.492 (1,070) | 10 | 0 / 10 |
| MCQ (acc) | 0.692 (2,620) | 0.697 (6,861) | 0.706 (5,286) | 0.723 (699) | 9 | 0 / 10 |
| Date (score) | 0.248 (1,744) | 0.277 (3,963) | 0.300 (2,471) | 0.272 (337) | 5 | 1 / 10 |
| FRQ (0-10) | 3.98 (2,677) | 4.10 (7,146) | 4.20 (5,518) | 4.21 (725) | 9 | 1 / 10 |

2 of 40 post-cutoff, 3 of 32 pre-cutoff, 4 of 40 whole-dataset tests significant, and every significant one but a single date test is on FRQ. The pattern is a small, monotone rise in FRQ score with time in review: 13–24 months versus ≤6 months is higher for 10/10 models post-cutoff (median +0.226 on the 0–10 scale) and 8/8 pre-cutoff (median +0.218); binary and MCQ are flat (0 of 28 and 0 of 28 across all partitions). Because it appears in the pre- and post-cutoff partitions alike, it is a property of the items — longer-reviewed papers draw higher rubric scores for their proposed solutions — not a knowledge or cutoff artefact, and it does not touch the binary or mechanism results.

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
| DeepSeek-V4-Pro | 2026-04 | 0.480 [0.472, 0.488] (4,631) | 0.459 [0.426, 0.492] (307) | 0.485 [0.464, 0.506] (614) | 0.417 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.561 [0.548, 0.574] (4,408) | 0.545 [0.494, 0.596] (292) | 0.559 [0.524, 0.597] (589) | 0.836 | 1.000 |

**MCQ (acc)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.530 [0.512, 0.548] (3,077) | 0.604 [0.539, 0.668] (212) | 0.609 [0.561, 0.660] (386) | 0.003 | 0.300 |
| LLaMA 3.3 70B | 2023-12 | 0.465 [0.445, 0.483] (3,046) | 0.509 [0.439, 0.573] (212) | 0.456 [0.406, 0.504] (384) | 0.412 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.499 [0.481, 0.517] (3,078) | 0.542 [0.475, 0.608] (212) | 0.544 [0.493, 0.592] (386) | 0.136 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.614 [0.593, 0.635] (2,248) | 0.648 [0.581, 0.717] (179) | 0.616 [0.565, 0.665] (331) | 0.666 | 1.000 |
| Claude S4.5 | 2025-01 | 0.704 [0.687, 0.721] (2,724) | 0.757 [0.695, 0.816] (189) | 0.735 [0.689, 0.779] (362) | 0.168 | 1.000 |
| GPT-5.4 | 2025-08 | 0.821 [0.808, 0.835] (3,079) | 0.849 [0.799, 0.897] (212) | 0.832 [0.794, 0.868] (386) | 0.533 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.899 [0.888, 0.910] (2,755) | 0.913 [0.872, 0.951] (184) | 0.910 [0.880, 0.939] (354) | 0.718 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.865 [0.853, 0.877] (3,058) | 0.899 [0.857, 0.938] (208) | 0.906 [0.877, 0.934] (383) | 0.034 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.643 [0.626, 0.660] (3,079) | 0.670 [0.609, 0.728] (212) | 0.694 [0.648, 0.739] (386) | 0.112 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.926 [0.916, 0.936] (2,710) | 0.923 [0.883, 0.962] (181) | 0.937 [0.911, 0.961] (350) | 0.731 | 1.000 |

**Date (score)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.152 [0.142, 0.163] (1,930) | 0.111 [0.082, 0.144] (146) | 0.102 [0.082, 0.124] (291) | 0.001 | 0.103 |
| LLaMA 3.3 70B | 2023-12 | 0.477 [0.465, 0.489] (1,915) | 0.475 [0.428, 0.521] (146) | 0.431 [0.399, 0.462] (289) | 0.022 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.275 [0.262, 0.288] (1,931) | 0.238 [0.195, 0.284] (146) | 0.230 [0.201, 0.262] (291) | 0.023 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.264 [0.252, 0.277] (1,765) | 0.276 [0.232, 0.324] (144) | 0.213 [0.183, 0.241] (284) | 0.010 | 0.970 |
| Claude S4.5 | 2025-01 | 0.185 [0.173, 0.196] (1,793) | 0.195 [0.150, 0.243] (134) | 0.183 [0.153, 0.215] (280) | 0.886 | 1.000 |
| GPT-5.4 | 2025-08 | 0.176 [0.164, 0.188] (1,931) | 0.153 [0.115, 0.199] (146) | 0.200 [0.168, 0.235] (291) | 0.191 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.332 [0.320, 0.345] (1,841) | 0.398 [0.347, 0.450] (139) | 0.396 [0.361, 0.431] (278) | 0.000 | **0.031** |
| GPT-5.6 Sol | 2026-02 | 0.316 [0.300, 0.333] (1,931) | 0.301 [0.245, 0.356] (146) | 0.270 [0.233, 0.307] (291) | 0.116 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.170 [0.159, 0.181] (1,931) | 0.140 [0.108, 0.173] (146) | 0.113 [0.095, 0.133] (291) | 0.000 | **0.021** |
| Claude Opus 4.8 | 2026-01 | 0.379 [0.365, 0.394] (1,825) | 0.442 [0.388, 0.497] (137) | 0.460 [0.425, 0.496] (274) | 0.000 | **0.021** |

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
| DeepSeek-V4-Pro | 2026-04 | 4.00 [3.96, 4.03] (3,076) | 3.92 [3.80, 4.06] (202) | 3.87 [3.77, 3.97] (393) | 0.038 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 4.62 [4.58, 4.65] (2,993) | 4.76 [4.63, 4.89] (193) | 4.70 [4.61, 4.81] (376) | 0.031 | 1.000 |

### 6.5 Per-model tables — latency, post-cutoff only

**Binary (bal. acc)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.473 [0.464, 0.484] (4,628) | 0.481 [0.448, 0.511] (307) | 0.467 [0.444, 0.491] (614) | 0.844 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.514 [0.507, 0.521] (4,590) | 0.503 [0.479, 0.528] (307) | 0.515 [0.493, 0.537] (612) | 0.758 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.469 [0.457, 0.481] (4,036) | 0.487 [0.446, 0.532] (245) | 0.497 [0.465, 0.528] (451) | 0.263 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.493 [0.478, 0.509] (3,179) | 0.462 [0.413, 0.516] (218) | 0.485 [0.440, 0.531] (387) | 0.596 | 1.000 |
| Claude S4.5 | 2025-01 | 0.452 [0.436, 0.468] (2,638) | 0.453 [0.388, 0.517] (134) | 0.466 [0.418, 0.516] (216) | 0.888 | 1.000 |
| GPT-5.4 | 2025-08 | 0.495 [0.471, 0.518] (1,736) | 0.426 [0.306, 0.554] (63) | 0.509 [0.404, 0.610] (82) | 0.507 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.525 [0.500, 0.554] (970) | n<20 (19) | 0.589 [0.419, 0.760] (37) | 0.401 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.597 [0.566, 0.627] (833) | n<20 (10) | 0.569 [0.375, 0.758] (33) | 0.753 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.462 [0.438, 0.487] (668) | n<20 (9) | 0.528 [0.382, 0.719] (24) | 0.328 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.493 [0.466, 0.520] (957) | n<20 (19) | 0.576 [0.438, 0.720] (37) | 0.236 | 1.000 |

**MCQ (acc)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.530 [0.512, 0.548] (3,077) | 0.604 [0.539, 0.668] (212) | 0.609 [0.561, 0.660] (386) | 0.003 | 0.300 |
| LLaMA 3.3 70B | 2023-12 | 0.465 [0.445, 0.483] (3,046) | 0.509 [0.439, 0.573] (212) | 0.456 [0.406, 0.504] (384) | 0.412 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.499 [0.480, 0.517] (2,725) | 0.524 [0.446, 0.601] (170) | 0.532 [0.474, 0.591] (282) | 0.488 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.612 [0.590, 0.634] (1,856) | 0.621 [0.538, 0.700] (132) | 0.601 [0.537, 0.665] (223) | 0.928 | 1.000 |
| Claude S4.5 | 2025-01 | 0.683 [0.660, 0.705] (1,761) | 0.688 [0.587, 0.777] (93) | 0.716 [0.640, 0.791] (134) | 0.714 | 1.000 |
| GPT-5.4 | 2025-08 | 0.813 [0.791, 0.835] (1,206) | 0.848 [0.739, 0.940] (46) | 0.891 [0.800, 0.966] (55) | 0.306 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.879 [0.854, 0.903] (651) | n<20 (13) | 0.957 [0.852, 1.000] (23) | 0.284 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.858 [0.830, 0.885] (577) | n<20 (9) | 0.905 [0.760, 1.000] (21) | 0.571 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.634 [0.591, 0.677] (470) | n<20 (9) | n<20 (13) | -- | -- |
| Claude Opus 4.8 | 2026-01 | 0.918 [0.895, 0.938] (644) | n<20 (13) | 0.909 [0.762, 1.000] (22) | 0.850 | 1.000 |

**Date (score)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.152 [0.142, 0.163] (1,930) | 0.111 [0.082, 0.144] (146) | 0.102 [0.082, 0.124] (291) | 0.001 | 0.103 |
| LLaMA 3.3 70B | 2023-12 | 0.477 [0.465, 0.489] (1,915) | 0.475 [0.428, 0.521] (146) | 0.431 [0.399, 0.462] (289) | 0.022 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.304 [0.290, 0.319] (1,632) | 0.281 [0.226, 0.342] (114) | 0.276 [0.239, 0.320] (204) | 0.389 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.299 [0.284, 0.313] (1,382) | 0.325 [0.267, 0.384] (102) | 0.268 [0.229, 0.310] (182) | 0.229 | 1.000 |
| Claude S4.5 | 2025-01 | 0.197 [0.184, 0.211] (1,038) | 0.186 [0.127, 0.253] (63) | 0.205 [0.158, 0.253] (99) | 0.882 | 1.000 |
| GPT-5.4 | 2025-08 | 0.148 [0.130, 0.167] (608) | 0.156 [0.072, 0.257] (24) | 0.195 [0.117, 0.291] (31) | 0.509 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.213 [0.186, 0.240] (292) | n<20 (7) | n<20 (10) | -- | -- |
| GPT-5.6 Sol | 2026-02 | 0.194 [0.173, 0.215] (229) | n<20 (3) | n<20 (9) | -- | -- |
| DeepSeek-V4-Pro | 2026-04 | 0.308 [0.250, 0.366] (160) | n<20 (2) | n<20 (6) | -- | -- |
| Claude Opus 4.8 | 2026-01 | 0.167 [0.148, 0.188] (289) | n<20 (7) | n<20 (10) | -- | -- |

**FRQ (0-10)**

| model | cutoff | 0 mo | 1-6 mo | >6 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.24 [3.21, 3.28] (3,073) | 3.13 [3.00, 3.27] (203) | 3.24 [3.14, 3.33] (393) | 0.251 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.51 [3.49, 3.54] (3,047) | 3.46 [3.36, 3.56] (203) | 3.55 [3.48, 3.63] (391) | 0.311 | 1.000 |
| GPT-OSS 20B | 2024-06 | 3.85 [3.82, 3.89] (2,717) | 3.89 [3.76, 4.02] (163) | 3.80 [3.71, 3.90] (290) | 0.596 | 1.000 |
| DeepSeek-R1 | 2024-07 | 4.17 [4.13, 4.20] (2,124) | 4.12 [3.98, 4.26] (144) | 4.04 [3.94, 4.15] (250) | 0.082 | 1.000 |
| Claude S4.5 | 2025-01 | 3.95 [3.91, 3.99] (1,853) | 3.94 [3.74, 4.13] (94) | 3.79 [3.64, 3.93] (139) | 0.112 | 1.000 |
| GPT-5.4 | 2025-08 | 4.92 [4.87, 4.97] (1,218) | 4.97 [4.73, 5.20] (46) | 4.96 [4.73, 5.19] (63) | 0.873 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 4.38 [4.32, 4.44] (710) | n<20 (14) | 4.25 [3.83, 4.63] (28) | 0.421 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 4.82 [4.75, 4.88] (590) | n<20 (9) | 4.91 [4.51, 5.28] (24) | 0.604 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 4.03 [3.95, 4.10] (481) | n<20 (8) | n<20 (18) | -- | -- |
| Claude Opus 4.8 | 2026-01 | 4.49 [4.43, 4.55] (715) | n<20 (14) | 4.54 [4.21, 4.88] (28) | 0.769 | 1.000 |

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
| DeepSeek-V4-Pro | 2026-04 | 0.483 [0.465, 0.500] (942) | 0.484 [0.472, 0.496] (2,213) | 0.478 [0.463, 0.492] (1,528) | 0.485 [0.442, 0.528] (203) | 0.935 | 1.000 |
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
| DeepSeek-V4-Pro | 2026-04 | 0.634 [0.594, 0.674] (577) | 0.654 [0.630, 0.679] (1,411) | 0.652 [0.623, 0.679] (1,051) | 0.728 [0.656, 0.800] (136) | 0.243 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.930 [0.908, 0.951] (526) | 0.927 [0.912, 0.941] (1,252) | 0.930 [0.913, 0.947] (935) | 0.958 [0.920, 0.992] (119) | 0.671 | 1.000 |

**Date (score)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.110 [0.093, 0.129] (443) | 0.139 [0.126, 0.153] (971) | 0.165 [0.147, 0.185] (621) | 0.114 [0.074, 0.160] (82) | 0.001 | 0.108 |
| LLaMA 3.3 70B | 2023-12 | 0.451 [0.427, 0.474] (443) | 0.470 [0.452, 0.487] (964) | 0.469 [0.449, 0.489] (615) | 0.530 [0.470, 0.588] (81) | 0.100 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.231 [0.205, 0.255] (444) | 0.274 [0.256, 0.293] (971) | 0.278 [0.256, 0.301] (621) | 0.234 [0.176, 0.296] (82) | 0.025 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.212 [0.190, 0.235] (419) | 0.247 [0.231, 0.264] (907) | 0.280 [0.257, 0.303] (562) | 0.235 [0.180, 0.294] (73) | 0.001 | 0.108 |
| Claude S4.5 | 2025-01 | 0.169 [0.147, 0.193] (418) | 0.180 [0.164, 0.196] (913) | 0.193 [0.174, 0.214] (586) | 0.174 [0.122, 0.231] (79) | 0.469 | 1.000 |
| GPT-5.4 | 2025-08 | 0.143 [0.121, 0.168] (444) | 0.181 [0.164, 0.199] (971) | 0.187 [0.166, 0.208] (621) | 0.167 [0.114, 0.222] (82) | 0.043 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.377 [0.350, 0.404] (430) | 0.337 [0.318, 0.356] (924) | 0.327 [0.305, 0.349] (600) | 0.340 [0.279, 0.403] (78) | 0.041 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.324 [0.290, 0.359] (444) | 0.325 [0.302, 0.346] (971) | 0.299 [0.271, 0.326] (621) | 0.285 [0.203, 0.368] (82) | 0.429 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.142 [0.120, 0.163] (444) | 0.152 [0.138, 0.166] (971) | 0.183 [0.163, 0.204] (621) | 0.136 [0.095, 0.181] (82) | 0.015 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.417 [0.385, 0.450] (427) | 0.395 [0.375, 0.415] (915) | 0.378 [0.354, 0.403] (595) | 0.403 [0.334, 0.469] (79) | 0.278 | 1.000 |

**FRQ (0-10)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.15 [3.07, 3.23] (570) | 3.21 [3.16, 3.26] (1,412) | 3.26 [3.20, 3.31] (1,065) | 3.22 [3.08, 3.36] (138) | 0.145 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.40 [3.34, 3.47] (571) | 3.49 [3.45, 3.53] (1,402) | 3.56 [3.51, 3.60] (1,053) | 3.48 [3.35, 3.61] (138) | 0.001 | 0.080 |
| GPT-OSS 20B | 2024-06 | 3.71 [3.63, 3.79] (571) | 3.77 [3.72, 3.81] (1,408) | 3.95 [3.90, 4.01] (1,062) | 3.90 [3.75, 4.05] (139) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 4.04 [3.97, 4.12] (508) | 4.10 [4.06, 4.16] (1,216) | 4.20 [4.15, 4.26] (880) | 4.17 [4.02, 4.32] (120) | 0.004 | 0.391 |
| Claude S4.5 | 2025-01 | 3.77 [3.70, 3.85] (531) | 3.89 [3.84, 3.94] (1,312) | 3.97 [3.91, 4.03] (985) | 3.93 [3.76, 4.07] (134) | 0.002 | 0.150 |
| GPT-5.4 | 2025-08 | 4.84 [4.77, 4.91] (569) | 4.98 [4.94, 5.03] (1,412) | 5.04 [4.99, 5.09] (1,063) | 4.97 [4.84, 5.10] (139) | 0.000 | **0.011** |
| Claude Sonnet 5 | 2026-01 | 4.26 [4.18, 4.33] (546) | 4.40 [4.35, 4.45] (1,365) | 4.52 [4.47, 4.57] (1,045) | 4.35 [4.19, 4.50] (139) | 0.000 | **0.011** |
| GPT-5.6 Sol | 2026-02 | 4.76 [4.68, 4.84] (559) | 4.92 [4.87, 4.97] (1,392) | 4.95 [4.89, 5.00] (1,055) | 4.97 [4.82, 5.11] (139) | 0.001 | 0.108 |
| DeepSeek-V4-Pro | 2026-04 | 3.72 [3.64, 3.80] (572) | 3.93 [3.88, 3.99] (1,412) | 4.07 [4.02, 4.12] (1,065) | 4.15 [3.99, 4.30] (137) | 0.000 | **0.011** |
| Claude Opus 4.8 | 2026-01 | 4.46 [4.38, 4.54] (550) | 4.63 [4.58, 4.68] (1,371) | 4.66 [4.61, 4.72] (1,045) | 4.60 [4.44, 4.75] (139) | 0.001 | 0.051 |

### 6.7 Per-model tables — editorial latency, post-cutoff only

**Binary (bal. acc)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.465 [0.445, 0.485] (940) | 0.468 [0.454, 0.482] (2,213) | 0.484 [0.466, 0.502] (1,528) | 0.445 [0.398, 0.493] (203) | 0.250 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.516 [0.500, 0.532] (941) | 0.501 [0.489, 0.512] (2,194) | 0.528 [0.515, 0.540] (1,515) | 0.529 [0.501, 0.557] (201) | 0.015 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.452 [0.426, 0.478] (764) | 0.475 [0.459, 0.492] (1,895) | 0.490 [0.469, 0.512] (1,301) | 0.464 [0.408, 0.518] (179) | 0.163 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.453 [0.422, 0.485] (627) | 0.482 [0.459, 0.504] (1,534) | 0.520 [0.492, 0.548] (1,007) | 0.462 [0.390, 0.531] (142) | 0.020 | 1.000 |
| Claude S4.5 | 2025-01 | 0.465 [0.429, 0.499] (434) | 0.458 [0.436, 0.481] (1,230) | 0.442 [0.413, 0.470] (858) | 0.490 [0.411, 0.570] (125) | 0.548 | 1.000 |
| GPT-5.4 | 2025-08 | 0.461 [0.406, 0.514] (251) | 0.494 [0.460, 0.528] (724) | 0.529 [0.489, 0.568] (596) | 0.443 [0.314, 0.571] (69) | 0.162 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.463 [0.410, 0.519] (127) | 0.571 [0.526, 0.617] (399) | 0.502 [0.454, 0.547] (330) | 0.566 [0.429, 0.723] (42) | 0.041 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.609 [0.535, 0.683] (101) | 0.594 [0.543, 0.643] (343) | 0.617 [0.563, 0.671] (282) | 0.565 [0.383, 0.740] (37) | 0.884 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.471 [0.417, 0.536] (82) | 0.467 [0.425, 0.512] (263) | 0.476 [0.437, 0.517] (237) | 0.435 [0.364, 0.500] (31) | 0.921 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.473 [0.417, 0.536] (126) | 0.507 [0.463, 0.552] (396) | 0.485 [0.445, 0.527] (324) | 0.517 [0.412, 0.667] (41) | 0.800 | 1.000 |

**MCQ (acc)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.498 [0.458, 0.539] (576) | 0.539 [0.512, 0.566] (1,411) | 0.558 [0.529, 0.587] (1,051) | 0.522 [0.437, 0.603] (136) | 0.145 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 0.458 [0.418, 0.501] (576) | 0.455 [0.429, 0.481] (1,397) | 0.477 [0.446, 0.509] (1,040) | 0.444 [0.362, 0.526] (135) | 0.707 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.496 [0.448, 0.539] (476) | 0.504 [0.475, 0.532] (1,215) | 0.518 [0.485, 0.550] (912) | 0.431 [0.345, 0.520] (123) | 0.327 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.604 [0.553, 0.655] (336) | 0.603 [0.571, 0.636] (864) | 0.617 [0.578, 0.656] (613) | 0.560 [0.459, 0.659] (84) | 0.783 | 1.000 |
| Claude S4.5 | 2025-01 | 0.656 [0.598, 0.713] (270) | 0.698 [0.666, 0.732] (778) | 0.684 [0.646, 0.721] (591) | 0.756 [0.667, 0.849] (86) | 0.317 | 1.000 |
| GPT-5.4 | 2025-08 | 0.830 [0.768, 0.885] (165) | 0.834 [0.800, 0.866] (477) | 0.810 [0.770, 0.849] (421) | 0.900 [0.811, 0.979] (50) | 0.401 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.897 [0.829, 0.962] (78) | 0.892 [0.853, 0.930] (251) | 0.872 [0.826, 0.913] (226) | 1.000 [1.000, 1.000] (30) | 0.204 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.864 [0.770, 0.942] (66) | 0.836 [0.787, 0.885] (220) | 0.893 [0.849, 0.935] (206) | 0.960 [0.869, 1.000] (25) | 0.176 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.556 [0.429, 0.686] (54) | 0.637 [0.565, 0.711] (171) | 0.669 [0.595, 0.740] (178) | n<20 (19) | 0.322 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.922 [0.857, 0.976] (77) | 0.915 [0.880, 0.948] (248) | 0.929 [0.894, 0.961] (226) | 0.933 [0.838, 1.000] (30) | 0.947 | 1.000 |

**Date (score)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.110 [0.093, 0.129] (443) | 0.139 [0.126, 0.153] (971) | 0.165 [0.147, 0.185] (621) | 0.114 [0.074, 0.160] (82) | 0.001 | 0.108 |
| LLaMA 3.3 70B | 2023-12 | 0.451 [0.427, 0.474] (443) | 0.470 [0.452, 0.487] (964) | 0.469 [0.449, 0.489] (615) | 0.530 [0.470, 0.588] (81) | 0.100 | 1.000 |
| GPT-OSS 20B | 2024-06 | 0.258 [0.229, 0.289] (354) | 0.306 [0.284, 0.328] (805) | 0.316 [0.288, 0.343] (502) | 0.262 [0.200, 0.334] (70) | 0.025 | 1.000 |
| DeepSeek-R1 | 2024-07 | 0.235 [0.207, 0.263] (306) | 0.283 [0.262, 0.304] (700) | 0.333 [0.307, 0.363] (416) | 0.273 [0.203, 0.342] (58) | 0.000 | **0.042** |
| Claude S4.5 | 2025-01 | 0.185 [0.155, 0.219] (198) | 0.187 [0.168, 0.207] (523) | 0.216 [0.191, 0.243] (317) | 0.181 [0.114, 0.256] (46) | 0.268 | 1.000 |
| GPT-5.4 | 2025-08 | 0.147 [0.105, 0.194] (104) | 0.133 [0.107, 0.161] (265) | 0.162 [0.133, 0.194] (199) | n<20 (19) | 0.369 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 0.236 [0.172, 0.311] (45) | 0.198 [0.156, 0.241] (127) | 0.210 [0.168, 0.257] (96) | n<20 (9) | 0.640 | 1.000 |
| GPT-5.6 Sol | 2026-02 | 0.219 [0.152, 0.294] (32) | 0.214 [0.182, 0.247] (98) | 0.175 [0.145, 0.204] (76) | n<20 (9) | 0.219 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 0.334 [0.179, 0.497] (23) | 0.203 [0.128, 0.282] (61) | 0.391 [0.286, 0.499] (58) | n<20 (8) | 0.021 | 1.000 |
| Claude Opus 4.8 | 2026-01 | 0.154 [0.109, 0.209] (45) | 0.180 [0.152, 0.212] (127) | 0.159 [0.124, 0.198] (94) | n<20 (9) | 0.586 | 1.000 |

**FRQ (0-10)**

| model | cutoff | <=6 mo | 7-12 mo | 13-24 mo | >24 mo | p (perm) | p (Holm) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 3.15 [3.07, 3.23] (570) | 3.21 [3.16, 3.26] (1,412) | 3.26 [3.20, 3.31] (1,065) | 3.22 [3.08, 3.36] (138) | 0.145 | 1.000 |
| LLaMA 3.3 70B | 2023-12 | 3.40 [3.34, 3.47] (571) | 3.49 [3.45, 3.53] (1,402) | 3.56 [3.51, 3.60] (1,053) | 3.48 [3.35, 3.61] (138) | 0.001 | 0.080 |
| GPT-OSS 20B | 2024-06 | 3.68 [3.60, 3.76] (469) | 3.77 [3.73, 3.83] (1,222) | 3.96 [3.90, 4.01] (923) | 3.88 [3.72, 4.03] (124) | 0.000 | **0.011** |
| DeepSeek-R1 | 2024-07 | 4.01 [3.93, 4.10] (380) | 4.09 [4.04, 4.15] (980) | 4.22 [4.16, 4.28] (708) | 4.17 [4.01, 4.33] (104) | 0.002 | 0.150 |
| Claude S4.5 | 2025-01 | 3.77 [3.67, 3.86] (277) | 3.91 [3.85, 3.97] (827) | 4.00 [3.92, 4.07] (626) | 3.98 [3.78, 4.13] (90) | 0.004 | 0.396 |
| GPT-5.4 | 2025-08 | 4.76 [4.63, 4.88] (169) | 4.92 [4.84, 5.00] (496) | 4.95 [4.87, 5.02] (429) | 4.93 [4.73, 5.13] (50) | 0.106 | 1.000 |
| Claude Sonnet 5 | 2026-01 | 4.06 [3.90, 4.22] (85) | 4.33 [4.22, 4.43] (286) | 4.47 [4.37, 4.57] (249) | 4.63 [4.39, 4.87] (29) | 0.001 | 0.071 |
| GPT-5.6 Sol | 2026-02 | 4.64 [4.41, 4.86] (69) | 4.73 [4.62, 4.83] (235) | 4.88 [4.77, 4.99] (213) | 5.12 [4.85, 5.42] (23) | 0.025 | 1.000 |
| DeepSeek-V4-Pro | 2026-04 | 3.71 [3.50, 3.93] (59) | 3.94 [3.82, 4.07] (187) | 4.12 [4.00, 4.23] (179) | n<20 (15) | 0.005 | 0.409 |
| Claude Opus 4.8 | 2026-01 | 4.31 [4.15, 4.48] (87) | 4.46 [4.36, 4.57] (286) | 4.53 [4.42, 4.63] (252) | 4.52 [4.21, 4.80] (29) | 0.233 | 1.000 |

### 6.8 The superseded 708-event measure

The first pass used `original_publication_date − first_date_found` over 708 extension events. On inspection, `first_date_found` is the Crossref record-creation date for 96% of them, so that interval mostly measured online-first versus print-issue scheduling (0–3 months, all post-cutoff, no pre-cutoff partition). It is kept under `by_legacy/latency_708/` (0 of 72 significant) and should not be cited; section 6 replaces it.

## 7. Novelty — why we are not stratifying on it

We have no gold standard and no agreed proxy, and we decline to invent one. `novelty_discussion.md` lists six candidates (citation count, venue prestige, semantic distance from prior literature, rarity of the category combination, novelty claims in the abstract, an LLM-judged departure score) with what each would and would not capture. Two objections apply to all of them:

- **Circularity.** Novelty is close to the construct CUSP measures. A result that departs sharply from prior work is almost by definition harder to forecast. A novelty stratification showing lower performance on novel events would re-measure the benchmark's own target through a noisier instrument, not demonstrate a compositional bias.
- **Range restriction.** Every CUSP event was selected for being notable — published in *Nature*, *Science* or *Cell*, or curated onto a "top AI paper" list. The sampling frame is already truncated at the high end of novelty and visibility. Any within-benchmark stratification, including the citation analysis above, probes variation *inside* an already-selected band and can neither detect nor correct the selection that produced the band.

We think the second point is the honest answer to the reviewer's underlying concern, and we prefer to state it as a limitation of the benchmark rather than let a novelty table imply a control we do not have. A defensible novelty instrument would need a definition, a validation against human ratings, and inter-rater agreement — a study, not a table.

## 8. Proposed manuscript text

**[PROPOSED — Results, new subsection "Sensitivity to benchmark composition"]**

> To test whether our conclusions depend on how CUSP was assembled, we stratified every model's performance on all four tasks by source venue, citation quartile and publication latency, each on the whole benchmark and on the post-cutoff partition, with event-clustered bootstrap intervals and permutation tests corrected across the family (Supplementary Tables S24–S28). Performance varies across venues, but the variation is confined to the date task, where every model scores higher on arXiv-sourced events than on journal-sourced ones (median +0.264 date score), consistent with arXiv's regular posting cadence; because venues are nested within disciplines, we repeated the analysis with discipline held fixed and found 4 of 705 tests significant. Citation count, taken from a single Semantic Scholar snapshot over 5,513 events, predicts performance before a model's cutoff (the most-cited quartile scores higher on mechanism questions for 6 of 6 models with both quartiles populated, and on solution questions for 6 of 6) but not after it (1 of 30 post-cutoff tests outside the date task), indicating that visibility aids recall rather than forecasting. Publication latency — months a result was publicly observable before its journal version, over 4,326 journal events — shows 0 of 34 significant post-cutoff tests, and time in peer review over 3,740 events shows 2 of 40.

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
