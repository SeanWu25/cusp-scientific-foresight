# Reviewer 1, comment 4 — horizon-dependent forecasting error

> "Analyze horizon dependent forecasting errors to separate short term
> extrapolation failures from genuinely long range scientific prediction
> limitations."

**Status: analysis complete; ready for PI review.** Everything below regenerates
from stored model outputs (no new inference for the published models):
`python horizon_study/run_all.py` (tables, ~21 min) and
`python horizon_study/figures.py`. Full write-up with every table referenced:
`horizon_study/RESULTS.md`; tables in `horizon_study/tables/*.md`; figures in
`horizon_study/figures/`.

**Updated 2026-09-25**: Claude Opus 4.8 added (panel now **ten** models), and the
**FRQ task added** to the horizon analysis, which previously covered three of the
four tasks. Both changes moved numbers — the Holm family grew from 149 to 203
tests — and §6 records exactly what changed.

## 1. What we did

* **Horizon** = months from each model's knowledge cutoff to the event's
  first-observable month. Post-cutoff only (h ≥ 1), asserted in code; the cutoff
  month itself is excluded because dates are month-resolved (Sol's cutoff is the
  16th). The stored event dates are already first-observable dates (verified for
  all 3,642 DOI events against the build pipeline's cached lookups); a journal-date
  sensitivity is reported.
* **Cutoffs** verified against vendor pages on 2026-09-20 (Opus 4.8 on 2026-09-22)
  for GPT-4o, LLaMA 3.3, GPT-OSS-20B, GPT-5.4, Claude Sonnet 5, Claude Opus 4.8
  and GPT-5.6 Sol; Claude Sonnet 4.5 has two published dates (reliable Jan 2025
  used, training-data Jul 2025 as sensitivity); DeepSeek-V4-Pro April 2026
  confirmed by the authors; DeepSeek R1 (2024-07) is the one unverifiable cutoff
  (sensitivity at its self-reported Dec 2023).
* **Datasets**: (1) original corpus, (2) Apr–Aug 2026 extension (100% post-cutoff),
  (3) retrieval-constrained WS+Cutoff condition on the pinned 500 subset, paired
  with base on the same items, (4) merged 1+2.
* **Tasks**: binary (merged real + perturbed), MCQ, date, and **FRQ** (published
  rubric, 0–10; a continuous outcome, so fitted with the Gaussian crossed model
  used for the date metrics).
* **Two analyses.** Descriptive: per-model binned means (1–3, 4–6, 7–12, 13–24,
  25+ months; 2- and 6-month robustness), N and 10k event-bootstrap CI in every
  cell, cells with n < 20 suppressed. Inferential: pooled across ten models with
  crossed random intercepts for event and model (the same event sits at a
  different horizon for each model, cutoffs Oct 2023–Apr 2026), plus variants with
  calendar month, a quadratic, a random slope per model, and a conditional logit
  stratified by event for shape. Continuous spline and broken-stick fits locate
  any bend. A constructed anchoring null for the date task. Trend tests
  Holm-corrected across the whole family (**203** tests).

## 2. Is the new CUSP corpus in the analysis? Yes — and why Sol's horizon is still short

**Asked directly: does the horizon analysis use the new (April–August 2026) CUSP
corpus?** Yes — verified, and it is what makes the recent models analysable at
all. `horizon_study/data.py` loads both halves and the merged dataset is the
primary one. The check below contrasts what each model would have on the original
corpus alone against what it has with the extension pooled in (post-cutoff binary
events; `tables/n_post_cutoff.md`):

| model | cutoff | original corpus alone | **merged (what we report)** |
|---|---|---|---|
| GPT-4o | 2023-10 | 4,285 ev, h 3–29 | 4,965 ev, h 3–34 |
| LLaMA 3.3 70B | 2023-12 | 4,250 ev, h 1–27 | 4,930 ev, h 1–32 |
| GPT-OSS 20B | 2024-06 | 3,500 ev, h 1–21 | 4,180 ev, h 1–26 |
| DeepSeek R1 | 2024-07 | 3,310 ev, h 1–20 | 3,310 ev, h 1–20 (no extension run) |
| Claude S4.5 | 2025-01 | 2,206 ev, h 1–14 | 2,779 ev, h 1–19 |
| GPT-5.4 | 2025-08 | 1,048 ev, h 1–7 | 1,728 ev, h 1–12 |
| Claude Sonnet 5 | 2026-01 | 209 ev, h 1–2 | 868 ev, h 1–7 |
| Claude Opus 4.8 | 2026-01 | 209 ev, h 1–2 | 862 ev, h 1–7 |
| **GPT-5.6 Sol** | 2026-02 | **12 ev, h 1–1** | **692 ev, h 1–6** |
| DeepSeek-V4-Pro | 2026-04 | **0 ev** | 532 ev, h 1–4 |

For GPT-5.6 Sol specifically — the model that prompted the question — the
extension multiplies its usable post-cutoff evidence by 58× and turns a single
horizon into a six-month range. DeepSeek-V4-Pro has **no** post-cutoff events at
all without it.

**Why Sol's horizon is nevertheless short: it is arithmetic, not coverage.**
Maximum horizon = (corpus end, Aug 2026) − (model cutoff). Sol's cutoff is
February 2026, so six months is the largest horizon that can exist for it in this
corpus; Sonnet 5 and Opus 4.8 cap at seven, DeepSeek-V4-Pro at four, while GPT-4o
reaches 34. No amount of additional data inside the current window changes this —
only extending the corpus past August 2026 would.

The consequence we state in the paper: **the four models released since January
2026 constrain only the short end of every horizon curve**, and every
long-horizon statement in this response rests on GPT-4o, LLaMA 3.3 and GPT-OSS,
whose horizons reach 26–34 months.

## 3. What we found

1. **MCQ, the only closed-form task with headroom, degrades gradually with
   horizon on the original corpus.** Pooled: −0.256 log-odds per year (95% CI
   −0.406 to −0.106, Holm p = 0.014), about 5 accuracy points over 27 months at a
   60% baseline. All six models with a usable range have negative within-model
   slopes (−1.4 to −4.1 points per 12 months; GPT-5.4 −17.4 over its 7-month
   range); none reverses. **Pooling the extension attenuates this to −0.171
   [−0.288, −0.054], Holm p = 0.058** — same sign and overlapping CI, but no
   longer significant after correction, and only 3 of 10 within-model slopes stay
   negative. We attribute the attenuation to corpus composition rather than to
   horizon (study A5 shows the two halves differ systematically by source), and we
   report both rather than the more favourable one.
2. **No threshold.** Quadratic term −0.019 [−0.142, +0.105]; event-stratified
   curvature p = 0.36; broken-stick breakpoint CI spans the whole 4–26 month
   range. Extension events at 28–34 months (the two oldest models) lie on the
   extrapolated line.
3. **Binary is a floor effect, not horizon-independence.** Accuracy 0.41–0.57 and
   AUROC 0.46–0.55 in every bin of the original corpus; the visible binary slopes
   are response-bias drift acting on a 43%-Yes item mix and have opposite signs
   for the Yes- and No-biased models. The bias-immune MCC, in 2-month bins for all
   ten models, shows no horizon structure: **no model's 1–6 month MCC differs from
   its > 6 month MCC** (every paired CI spans zero, merged corpus). Claude Sonnet 5
   is the only model with a short-horizon MCC distinguishable from zero
   (+0.067 [+0.006, +0.128], p = 0.030). Notably **Claude Opus 4.8, which shares
   Sonnet 5's January 2026 cutoff and run configuration, does not** (+0.007
   [−0.052, +0.065]) — so the one positive short-horizon signal in the panel is not
   reproduced by a sibling model at the same cutoff, and we do not claim a "binary
   foresight half-life" from this panel.
4. **FRQ shows no horizon effect at all**, and its variance structure says
   something about why. Full treatment in §4.
5. **The date task's apparent improvement with horizon is an artefact.** For the
   six models with more than seven months of horizon range, a constant predictor
   at each model's own median offset reproduces **107–147%** of the model's
   absolute-error slope, and signed error falls by exactly one month per month of
   horizon as arithmetic requires. (For Sonnet 5 and Opus 4.8 the ratio is
   negative and uninterpretable: their original-corpus horizon range is 1–2 months,
   so the denominator is noise. We therefore draw the conclusion only from the six
   models where it is measurable.)
6. **Two distinct horizon effects, separated by the retrieval condition.**
   Retrieval restricted to pre-cutoff documents does not change the accuracy
   horizon slope (condition × horizon within event × model strata, five models:
   binary +0.03 [−0.24, +0.30], p = 0.82; MCQ +0.21 [−0.12, +0.55], p = 0.21), so
   the MCQ decline is a reasoning-side limit. Its benefit on date error, 6.4 months
   on average, shrinks by 7.9 months per year of horizon (CI 4.5 to 11.2,
   p = 4 × 10⁻⁶): a knowledge-access effect confined to near-cutoff events. FRQ
   behaves like the accuracy tasks — the base-vs-retrieval difference in FRQ
   horizon slope has a CI spanning zero for all four models with enough paired
   items.
7. **Robust to the conventions.** Journal (DOI) dates: 89/96 within-model slopes
   keep their sign, pooled MCQ −0.182 [−0.334, −0.031]. Alternative cutoffs,
   inclusion of the cutoff month, and 2-/6-month bins change no conclusion
   (direction agrees across bin schemes in 100/126 cells; the disagreements are
   flat cells whose CI includes zero).

## 4. FRQ by horizon, per model

FRQ was not previously part of this analysis. It is the published rubric mean
(0–10, `judge_frq_combined`), entered as a continuous outcome and fitted with the
Gaussian crossed model used for the date metrics. Merged corpus, post-cutoff,
h ≥ 1. Slopes are per 12 months with a 10k event bootstrap; Holm across the
203-test family.

| model | horizon | n items | FRQ slope /yr [95% CI] | p | Holm |
|---|---|---|---|---|---|
| GPT-4o | 3–34 | 4,758 | +0.063 [+0.027, +0.099] | 0.001 | 0.163 |
| LLaMA 3.3 70B | 1–32 | 4,723 | −0.041 [−0.071, −0.011] | 0.006 | 0.973 |
| GPT-OSS 20B | 1–26 | 4,018 | +0.028 [−0.018, +0.073] | 0.24 | 1 |
| DeepSeek R1 | 1–20 | 3,231 | +0.060 [−0.003, +0.124] | 0.065 | 1 |
| Claude S4.5 | 1–19 | 2,739 | +0.030 [−0.043, +0.101] | 0.425 | 1 |
| GPT-5.4 | 1–12 | 1,647 | −0.303 [−0.442, −0.165] | 0.0002 | **0.041*** |
| Claude Sonnet 5 | 1–7 | 822 | −0.223 [−0.570, +0.118] | 0.21 | 1 |
| Claude Opus 4.8 | 1–7 | 827 | −0.282 [−0.622, +0.064] | 0.11 | 1 |
| GPT-5.6 Sol | 1–6 | 633 | +0.060 [−0.478, +0.591] | 0.819 | 1 |
| DeepSeek-V4-Pro | 1–4 | 497 | +0.028 [−0.755, +0.821] | 0.947 | 1 |

**Pooled, FRQ is the flattest of the four tasks.** Crossed event × model GLMM over
23,895 items / 4,765 events / ten models / 1–34 months: **+0.014 points per year
[−0.012, +0.039]**, Holm p = 1. Over the full 34 months the point estimate moves
FRQ by 0.04 points on a 0–10 scale. Compare date score +0.136 (Holm 0), MCQ
−0.171 (0.058), binary −0.057 (0.086).

### Model-specific findings

1. **GPT-5.4's significant decline is an artefact, and it is instructive.** It is
   the only Holm-significant FRQ trend in the panel (−0.303/yr). Split by corpus
   the slope is **+0.242/yr within the original half** and **−0.298/yr within the
   extension**, neither significant; what the merged fit reads as a slope is the
   **−0.220 level difference between halves** (orig mean 5.049, n = 1,019; ext
   mean 4.829, n = 628). GPT-5.4's August 2025 cutoff places the original corpus
   at horizons 1–7 and the extension at 8–12, so a level step between corpora
   becomes a downward line. Study A5 supplies the mechanism: FRQ runs ≈ 0.2 points
   lower on journal-sourced events, and the extension is the more journal-heavy
   half (84% vs 77%). **No model shows a within-corpus FRQ decline with horizon.**
2. **The same trap, smaller, for the two Claude models.** Sonnet 5 (−0.223) and
   Opus 4.8 (−0.282) have the next most negative slopes and the same structure —
   level shifts of −0.125 and −0.174 between halves. Neither is significant, and
   neither should be read as horizon decay.
3. **Opus 4.8's original-corpus slope is not reportable.** With a 1–2 month
   post-cutoff window on that half (n = 205), the per-year extrapolation is
   +5.3 points, which is arithmetic rather than a finding. We report only its
   merged slope, and only with its CI.
4. **GPT-4o is the one model whose FRQ rises with horizon** at conventional
   significance (+0.063 [+0.027, +0.099], p = 0.001; Holm 0.163 across 203 tests).
   Its binned profile is shallowly U-shaped — 3.45 at 1–3 months, 3.18 at 4–6,
   3.36 at 25+ — so this is drift in a weak model at the bottom of the range, not
   improving foresight.
5. **LLaMA 3.3 has the tightest interval in the panel and it is still null in
   practice**: −0.041 [−0.071, −0.011] per year, i.e. 0.04 points on a 0–10 scale,
   over a 32-month range. This is the strongest available evidence that FRQ does
   not decay with horizon.
6. **The two newest models cannot answer the question.** Sol (+0.060
   [−0.478, +0.591], h 1–6) and DeepSeek-V4-Pro (+0.028 [−0.755, +0.821], h 1–4)
   have intervals of ±0.5 and ±0.8 points per year. Neither can distinguish a real
   decline from none; this is the horizon-ceiling limitation of §2 in its sharpest
   form.
7. **The model ordering is completely stable across horizon.** Between bin 1–3 and
   bin 7–12 the eight models present in both keep an **identical ranking** — GPT-5.4,
   Opus 4.8, Sonnet 5, DeepSeek R1, Claude S4.5, GPT-OSS, LLaMA 3.3, GPT-4o — and
   the spread between best and worst is unchanged (1.569 → 1.555 points). Models
   neither converge nor diverge as the forecast gets harder.
8. **Retrieval does not change the FRQ horizon slope.** On the pinned 500 subset,
   base vs WS+Cutoff on identical items: −0.123 [−0.303, +0.049] for GPT-4o,
   −0.127 [−0.383, +0.127] for DeepSeek R1, +0.058 [−0.424, +0.543] for Claude
   S4.5, +0.799 [−0.340, +2.013] for GPT-5.4 — every CI spanning zero. Sonnet 5,
   Opus 4.8 and Sol have 24, 24 and 1 paired post-cutoff items and are not fitted.

### What this means for the benchmark

In the same pooled fit, **event SD is 0.472 and model SD is 1.393** — the reverse
of MCQ (2.407 vs 1.517). Which *paper* is asked drives mechanistic accuracy; for
FRQ, model identity explains roughly three times what paper identity does. Taken
with the flat horizon slope and the ≈ 1.0 retrospective ceiling reported
elsewhere in the revision, an FRQ score behaves as a stable property of the model
— nearly independent of which paper is asked and of how far ahead it is being
asked to see. We state this in the paper as a limitation of the task rather than a
result about forecasting.

## 5. Suggested text for the response letter

We thank the reviewer for this suggestion. We now measure horizon as the number
of months from each model's verified knowledge cutoff to the event's
first-observable date and analyse post-cutoff items only, across all four tasks,
on the original corpus, the April–August 2026 extension, their union, and the
retrieval-constrained condition (new Supplementary Section S-H, Tables S-H1–S-H7,
Figures S-H1–S-H4). Because our panel's cutoffs span October 2023 to April 2026,
the same event sits at a different horizon for each model; we exploit this with a
mixed-effects model with crossed random intercepts for event and model, which
separates horizon from item difficulty and model level, and with event-stratified
tests of the curve's shape.

For mechanistic MCQ, the one closed-form task with headroom, accuracy declines
gradually with horizon on the original corpus (−0.26 log-odds per year, 95% CI
−0.41 to −0.11) with no evidence of a threshold: the quadratic term is null, the
breakpoint of a broken-stick fit is unidentified, and events 28–34 months past
cutoff lie on the extrapolated line. The decline attenuates and loses significance
when the April–August 2026 extension is pooled in (−0.17, 95% CI −0.29 to −0.05),
which we attribute to the two corpus halves differing in composition rather than
to horizon; we report both estimates. Binary feasibility sits at floor at every
horizon, so its flatness is uninformative, and we say so. Free-response solution
quality is flat with horizon (+0.01 points per year on a 0–10 scale, 95% CI −0.01
to +0.04); in the same model, variation in FRQ score attributable to the model
exceeds that attributable to the paper by roughly threefold, the reverse of the
mechanistic task, indicating that this task measures a stable property of the
model rather than event-specific foresight. For the temporal task we construct an
explicit anchoring null (a constant prediction at the model's typical offset from
its cutoff) that reproduces the observed error-versus-horizon profile in full, so
we draw no horizon conclusion from that task. Finally, the retrieval-constrained
condition lets us separate two mechanisms: restricting retrieval to pre-cutoff
documents leaves the MCQ decline unchanged, whereas its benefit on date error
disappears by roughly two years of horizon. We interpret the former as a
reasoning-side limit and the latter as a knowledge-access effect, which is the
distinction the reviewer asked us to draw.

We note two limitations explicitly in the new section. First, with a single cutoff
per model, horizon equals calendar month minus cutoff, so a purely linear horizon
effect cannot be separated from calendar drift except through the random-effects
assumption and the agreement of models whose cutoffs are two years apart; the
shape conclusions (gradual, no threshold) are identified within events. Second,
the maximum horizon available to a model is the distance from its cutoff to the
end of the corpus, so the four models released since January 2026 contribute only
horizons of one to seven months and every long-horizon statement rests on the
three oldest models.

## 6. Manuscript changes proposed

* New supplementary section with: the definitions above; the horizon-range table
  from §2; the post-cutoff-N table per model × dataset; binned tables for the four
  datasets and all four tasks; the pooled mixed-effects table with and without
  calendar control; the continuous-fit figure with bend points; the date-task
  figure with the null overlaid; the base-vs-retrieval figure; the sensitivity
  table.
* Main text: three sentences in Results (gradual MCQ decline on the original
  corpus with no threshold, floor on binary, flat FRQ with its variance split,
  date artefact) and one in Discussion (reasoning-side vs knowledge-access horizon
  effects).

## 7. What changed on 2026-09-25, and why

Claude Opus 4.8 joined the benchmark panel on 2026-09-22, one day after this study
was first built, and was never registered in it; the FRQ task had never been part
of the horizon analysis at all. Both are now included (`horizon_study/data.py`,
commit `f9c3d77`). Consequences for the numbers previously circulated:

| quantity | before | now | conclusion |
|---|---|---|---|
| panel | 9 models | **10 models** | — |
| Holm family | 149 tests | **203 tests** | corrections are stricter |
| Pooled MCQ, original corpus | −0.26, Holm 0.009 | −0.256, **Holm 0.014** | unchanged |
| Pooled MCQ, merged corpus | not reported | −0.171, **Holm 0.058** | newly reported; not significant |
| DOI-date sign agreement | 70/75 | **89/96** | unchanged |
| Bin-scheme agreement | 78/95 | **100/126** | unchanged |
| WS × horizon, binary | −0.01 [−0.28, +0.27] | **+0.03 [−0.24, +0.30]** | unchanged (null) |
| WS × horizon, MCQ | +0.19 [−0.15, +0.52] | **+0.21 [−0.12, +0.55]** | unchanged (null) |
| Date-null share reproduced | "107–147%, every model" | **107–147% for the six models with > 7 months of range**; negative and uninterpretable for the two with a 1–2 month range | scope narrowed |
| Positive short-horizon MCC | "Sol +0.21, Sonnet 5 +0.07" | **Sonnet 5 +0.067 only**; Opus 4.8, at the same cutoff, is +0.007 (n.s.) | weakened |
| FRQ horizon | not analysed | **+0.014/yr [−0.012, +0.039], Holm 1** | new |

No conclusion in the previous version is reversed. Two are weakened and now
stated more narrowly (the date-null scope and the short-horizon MCC), one is
newly qualified (the pooled MCQ decline does not survive pooling the extension),
and FRQ is new.

## 8. Data correction made while doing this (GPT-5.6 Sol retrieval runs)

Both stored GPT-5.6 Sol retrieval runs (WS+Cutoff and unrestricted WS on the
pinned subset) had run with no retrieval context: the query-generation helper in
`scripts/web_search.py` sent `temperature=0`, which the model rejects, and the
harness answered every row without context. Fixed (the helper now drops the
parameter for a model that rejects it; no other model is affected; prompts and
scoring code untouched) and both runs regenerated on 2026-09-20 (500/500 rows
with context, ≈ $49). Reports, FRQ leakage verdicts and panel tables were rebuilt
with the repo's own scripts; the failed artefacts are kept as
`*.FAILED_no_context.*`. With real retrieval Sol behaves like the rest of the
panel (WS+Cutoff vs base: perturbed-binary +0.17, MCQ +0.06, date score +0.42,
all p < 0.001, almost entirely on pre-cutoff events). For this comment Sol still
contributes one post-cutoff event to dataset 3 (its February 2026 events fall in
the ambiguous cutoff month), so no coefficient here changes; the correction
matters for the knowledge-access decomposition elsewhere in the paper. Sonnet 5's
retrieval runs were checked and are unaffected. A LLaMA 3.3 WS+Cutoff run, which
never existed, was generated for dataset 3 (`results_llama33_run1/`).
