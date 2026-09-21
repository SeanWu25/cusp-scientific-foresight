# A4 — horizon-dependent forecasting error (Reviewer 1, comment 4)

Everything in `tables/` and `figures/` is regenerated from stored, already-scored
reports by two commands; nothing here runs a model, a judge, or the scoring code:

    python horizon_study/run_all.py     # all tables (~40 min; --stage <name> for one)
    python horizon_study/figures.py     # all figures

## Layout

    data.py      loader: events (first-observable and DOI dates), model registry with
                 verified cutoffs, item-level post-cutoff table with the h >= 1 assertion
    stats.py     event-level bootstrap, binned tables, within-model trend tests,
                 conditional-logit (event FE) models, spline / broken-stick fits,
                 anchoring nulls
    glmm.py      crossed random-intercept GLMM/LMM (event, model) by sparse PIRLS +
                 Laplace — the lme4 nAGQ=1 estimator; validated on simulated data
    run_all.py   stages: counts, dates, binned, trends, pooled, continuous, ws, null,
                 sensitivity
    figures.py   horizon_{orig,ext,merged}, horizon_ws, date_null_*, continuous_*
    RESULTS.md   answer to the reviewer

## Definitions

* **Horizon** h = months(first-observable date) − months(model cutoff). Post-cutoff =
  h ≥ 1; the cutoff month itself is excluded (month resolution; Sol's cutoff is the
  16th). `data.load_items` asserts this and a sensitivity run includes h = 0.
* **First-observable date**: the stored `publication_date` of the original corpus
  already is the earliest date the build pipeline found (Crossref creation,
  bioRxiv/medRxiv, Semantic Scholar, Europe PMC — verified against the cached
  lookups for all 3,642 DOI events); arXiv events use the earlier of the stored
  month and the arXiv-id month. Extension events carry `first_date_found`.
* **DOI/journal date** (sensitivity only): recovered from the build-stage CSVs for
  3,150 DOI events; `original_publication_date` on the extension.
* **Datasets**: 1 original corpus, 2 extension, 3 WS+Cutoff on the pinned 500
  subset (paired with base on the same items), 4 merged 1+2 (contract-checked as
  poolable in `results_merged_sonnet5/MERGED_MANIFEST.json`; the date task is kept
  but read only against the anchoring null because the extension's five-month
  window inflates constant-guess scores).
* **Bins**: 1–3, 4–6, 7–12, 13–24, 25+ (primary); 2-month and 6-month robustness.
  Cells with n < 20 items are suppressed. Every mean carries N and a 95%
  event-level bootstrap CI (10k resamples; 2k for the robustness schemes).
* **Trend tests**: within-model OLS slope per 12 months of horizon with bootstrap
  CI and two-sided bootstrap p, Holm-corrected across the entire family.
* **Pooled models**: logistic (binary/MCQ) or Gaussian (date metrics) with crossed
  random intercepts for event and model, horizon in years; variants with calendar
  month, a quadratic, and a random horizon slope by model; plus conditional logit
  stratified by event with model fixed effects for curvature and bin contrasts.
  See the identification note in `tables/pooled.md`.
