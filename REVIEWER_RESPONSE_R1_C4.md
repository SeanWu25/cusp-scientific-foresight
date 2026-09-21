# Reviewer 1, comment 4 — horizon-dependent forecasting error

Regenerable from stored model outputs with `python horizon_study/run_all.py` and `python horizon_study/figures.py`. Full write-up, tables and figures: `horizon_study/RESULTS.md`, `horizon_study/tables/`, `horizon_study/figures/`.

**Design.** Horizon = months from each model's verified knowledge cutoff to the
event's first-observable month (the stored dates already are first-observable; a
DOI-date sensitivity is reported). Post-cutoff only, asserted in code. Nine
models with cutoffs from Oct 2023 to Apr 2026, so the same event sits at a
different horizon for each model; that is what lets a crossed random-effects
model (event + model intercepts) separate horizon from item difficulty and
model level. Four datasets: the original corpus, the Apr–Aug 2026 extension,
the retrieval-constrained condition on the pinned 500 subset, and the merged
corpus.

**Findings for the response letter.**

1. MCQ, the only task with headroom, degrades gradually with horizon: −0.26
   log-odds per year pooled (95% CI −0.41 to −0.11, Holm p = 0.009; about 5
   accuracy points over 27 months). All six models with a usable range have
   negative within-model slopes; none reverses.
2. There is no threshold. The quadratic term is zero (−0.02 [−0.15, +0.10]),
   the event-stratified curvature test is null (p = 0.36), and the broken-stick
   breakpoint's bootstrap CI spans the whole 4–26 month range. Extension events
   at 28–34 months lie on the extrapolated line, not below it.
3. Binary accuracy is flat because it is at floor (0.41–0.57, AUROC 0.46–0.55
   in every bin); its apparent slopes are response-bias drift with opposite
   signs for Yes- and No-biased models. We say so rather than claim
   horizon-independence.
4. The date task's "improvement" with horizon is an artefact: models predict 10–44
   months past their cutoff, and a constant predictor at each model's own median
   offset reproduces 107–147% of the observed absolute-error slope. Signed error
   falls by exactly one month per month of horizon, as arithmetic requires.
5. Retrieval restricted to pre-cutoff documents does not change the accuracy
   horizon slope (condition × horizon interaction within event × model strata,
   five models: binary −0.01 [−0.28, +0.27], MCQ +0.19 [−0.15, +0.52]), but its
   benefit on date error shrinks by 7.9 months per year of horizon
   (CI 4.5 to 11.2, p = 4e-6). So there are two
   distinct horizon effects: a slow reasoning-side MCQ decline that retrieval does
   not touch, and a knowledge-access effect on dates confined to near-cutoff events.
6. Identification caveat, stated in the write-up: with one cutoff per model,
   horizon = calendar − cutoff, so the linear decline cannot be separated from
   calendar drift except through the random-effects assumption and the agreement
   of eight models with cutoffs two years apart. The shape claims (gradual, no
   threshold) are identified within events. Conclusions survive DOI dates,
   alternative cutoffs, inclusion of the cutoff month, and 2-/6-month bins.

## Data correction made for this comment (GPT-5.6 Sol retrieval runs)

While assembling dataset 3 we found that both stored GPT-5.6 Sol retrieval runs
(WS+Cutoff and unrestricted WS, pinned 500 subset) had run with no retrieval
context: the query-generation helper in `scripts/web_search.py` sent
`temperature=0`, which the model rejects with HTTP 400, and the harness
recorded `web_search_error` on all 500 rows and answered every task without
context. The stored report was also truncated to 63 rows. Fix: the helper now
drops the temperature parameter for a model the moment that model rejects it
(no change for any other model; prompts and scoring code untouched). Both runs
were regenerated on 2026-09-20: 500/500 rows with retrieval context (mean 8.9k
characters from 8 sources), zero web-search errors, refusal counts as in the
base run, ≈ $49 at list price. The failed artefacts are kept as
`*.FAILED_no_context.*`; reports and panel tables were rebuilt with the repo's
own scripts. With real retrieval Sol behaves like the rest of the panel
(`results_sol_run1/tables/web_search_block.txt`: WS+Cutoff vs base on the
pinned subset, perturbed-binary +0.17, MCQ +0.06, date score +0.42, all
p < 0.001, almost entirely on the 452 pre-cutoff events). For the horizon
analysis Sol still contributes a single post-cutoff event to dataset 3 because
its February 2026 events fall in the cutoff month, so no coefficient in this
comment changes; the correction matters for the knowledge-access decomposition
(Δ_know / Δ_fore) elsewhere in the paper. Sonnet 5's retrieval runs were checked
and do not have this failure (94–97% of rows carry context; the rest are
scattered transient errors already flagged `retrieval_failed`). Sol's manifest
hashes are being re-frozen by the run owner once its FRQ leakage verdicts finish.
