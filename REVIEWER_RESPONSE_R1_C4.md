# Reviewer 1, comment 4 — horizon-dependent forecasting error

> "Analyze horizon dependent forecasting errors to separate short term
> extrapolation failures from genuinely long range scientific prediction
> limitations."

**Status: analysis complete; ready for PI review.** Everything below regenerates
from stored model outputs (no new inference for the six published models):
`python horizon_study/run_all.py` (tables, ~40 min) and
`python horizon_study/figures.py`. Full write-up with every table referenced:
`horizon_study/RESULTS.md`; tables in `horizon_study/tables/*.md`; figures in
`horizon_study/figures/`.

## 1. What we did

* **Horizon** = months from each model's knowledge cutoff to the event's
  first-observable month. Post-cutoff only (h ≥ 1), asserted in code; the cutoff
  month itself is excluded because dates are month-resolved (Sol's cutoff is the
  16th). The stored event dates are already first-observable dates (verified for
  all 3,642 DOI events against the build pipeline's cached lookups); a journal-date
  sensitivity is reported.
* **Cutoffs** verified against vendor pages on 2026-09-20 for GPT-4o, LLaMA 3.3,
  GPT-OSS-20B, GPT-5.4, Claude Sonnet 5 and GPT-5.6 Sol; Claude Sonnet 4.5 has two
  published dates (reliable Jan 2025 used, training-data Jul 2025 as sensitivity);
  DeepSeek-V4-Pro April 2026 confirmed by the authors; DeepSeek R1 (2024-07) is
  the one unverifiable cutoff (sensitivity at its self-reported Dec 2023).
* **Datasets**: (1) original corpus, (2) Apr–Aug 2026 extension (100% post-cutoff),
  (3) retrieval-constrained WS+Cutoff condition on the pinned 500 subset, paired
  with base on the same items, (4) merged 1+2 (passed the run-2 poolability
  contract; the date task is not comparable across corpora and is read only
  against a null).
* **Two analyses, as the design point requires.** Descriptive: per-model binned
  means (1–3, 4–6, 7–12, 13–24, 25+ months; 2- and 6-month robustness), N and
  10k event-bootstrap CI in every cell, cells with n < 20 suppressed.
  Inferential: pooled across nine models with crossed random intercepts for
  event and model (the same event sits at a different horizon for each model,
  cutoffs Oct 2023–Apr 2026), plus variants with calendar month, a quadratic, a
  random slope per model, and a conditional logit stratified by event for shape.
  Continuous spline and broken-stick fits locate any bend. A constructed
  anchoring null for the date task. Trend tests Holm-corrected across the whole
  family (149 tests).

## 2. What we found

1. **MCQ, the only task with headroom, degrades gradually with horizon.** Pooled:
   −0.26 log-odds per year of horizon (95% CI −0.41 to −0.11, Holm p = 0.009),
   about 5 accuracy points over 27 months at a 60% baseline. All six models with
   a usable range have negative within-model slopes (−1.4 to −4.1 points per
   12 months; GPT-5.4 −17 over its 7-month range); none reverses.
2. **No threshold.** Quadratic term −0.02 [−0.15, +0.10]; event-stratified
   curvature p = 0.36; broken-stick breakpoint CI spans the whole 4–26 month
   range and the stick gains 4.4 deviance for one parameter. Extension events
   at 28–34 months (the two oldest models) lie on the extrapolated line.
3. **Binary is a floor effect, not horizon-independence.** Accuracy 0.41–0.57
   and AUROC 0.46–0.55 in every bin; the visible binary slopes are response-bias
   drift acting on a 43%-Yes item mix and have opposite signs for the Yes- and
   No-biased models. The text says this rather than claiming flatness.
4. **The date task's apparent improvement with horizon is an artefact.** Models
   predict 10–44 months past their cutoff; a constant predictor at each model's
   own median offset reproduces 107–147% of every model's absolute-error slope,
   and signed error falls by exactly one month per month of horizon as
   arithmetic requires.
5. **Two distinct horizon effects, separated by the retrieval condition.**
   Retrieval restricted to pre-cutoff documents does not change the accuracy
   horizon slope (condition × horizon within event × model strata, five models:
   binary −0.01 [−0.28, +0.27], MCQ +0.19 [−0.15, +0.52]), so the slow MCQ decline
   is a reasoning-side limit. Its benefit on date error, 6.4 months on average,
   shrinks by 7.9 months per year of horizon (CI 4.5 to 11.2, p = 4e-6): a
   knowledge-access effect confined to near-cutoff events.
6. **Robust to the conventions.** Journal (DOI) dates: 70/75 within-model slopes
   keep their sign, pooled MCQ −0.18 [−0.33, −0.03]. Alternative cutoffs,
   inclusion of the cutoff month, and 2-/6-month bins change no conclusion
   (direction agrees across bin schemes in 78/95 cells; the disagreements are
   flat cells whose CI includes zero).

## 3. Suggested text for the response letter

We thank the reviewer for this suggestion. We now measure horizon as the number
of months from each model's verified knowledge cutoff to the event's
first-observable date and analyse post-cutoff items only, on the original
corpus, the April–August 2026 extension, their union, and the
retrieval-constrained condition (new Supplementary Section S-H, Tables S-H1–S-H6,
Figures S-H1–S-H4). Because our panel's cutoffs span October 2023 to April 2026,
the same event sits at a different horizon for each model; we exploit this with
a mixed-effects model with crossed random intercepts for event and model, which
separates horizon from item difficulty and model level, and with
event-stratified tests of the curve's shape.

For mechanistic MCQ, the one task with headroom, accuracy declines gradually with
horizon (−0.26 log-odds per year, 95% CI −0.41 to −0.11) with no evidence of a
threshold: the quadratic term is null, the breakpoint of a broken-stick fit is
unidentified, and events 28–34 months past cutoff lie on the extrapolated line.
Binary feasibility sits at floor at every horizon, so its flatness is
uninformative, and we say so. For the temporal task we construct an explicit
anchoring null (a constant prediction at the model's typical offset from its
cutoff) that reproduces the observed error-versus-horizon profile in full, so we
draw no horizon conclusion from that task. Finally, the retrieval-constrained
condition lets us separate two mechanisms: restricting retrieval to pre-cutoff
documents leaves the MCQ decline unchanged, whereas its benefit on date error
disappears by roughly two years of horizon. We interpret the former as a
reasoning-side limit and the latter as a knowledge-access effect, which is the
distinction the reviewer asked us to draw.

We note one limitation explicitly in the new section: with a single cutoff per
model, horizon equals calendar month minus cutoff, so a purely linear horizon
effect cannot be separated from calendar drift except through the random-effects
assumption and the agreement of eight models whose cutoffs are two years apart;
the shape conclusions (gradual, no threshold) are identified within events.

## 4. Manuscript changes proposed

* New supplementary section with: the definitions above; the post-cutoff-N table
  per model × dataset; binned tables for the four datasets; the pooled
  mixed-effects table with and without calendar control; the continuous-fit
  figure with bend points; the date-task figure with the null overlaid; the
  base-vs-retrieval figure; the sensitivity table.
* Main text: two sentences in Results (gradual MCQ decline, no threshold, floor
  on binary, date artefact) and one in Discussion (reasoning-side vs
  knowledge-access horizon effects).

## 5. Data correction made while doing this (GPT-5.6 Sol retrieval runs)

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
the cutoff month), so no coefficient here changes; the correction matters for
the knowledge-access decomposition elsewhere in the paper. Sonnet 5's retrieval
runs were checked and are unaffected. A LLaMA 3.3 WS+Cutoff run, which never
existed, was generated for dataset 3 (`results_llama33_run1/`).
