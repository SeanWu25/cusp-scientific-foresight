# Reviewer 1, comment 6 — calibration interventions

> "Deepen discussion of calibration by comparing prompting, retrieval,
> self-consistency, ensembles, and explicit probabilistic forecasting
> interventions."

**Status: analysis complete; ready for PI review.** Regenerates from stored
outputs with `python calibration_study/analyze.py` (~40 min). Full write-up:
`calibration_study/RESULTS.md`; tables in `calibration_study/tables/*.md`;
figures in `calibration_study/figures/`; raw per-item outputs in
`calibration_study/raw/` with prompt hashes in the manifests.

## 1. What we did

* **Question.** Is near-chance binary forecasting a limit on forecasting ability
  or an artefact of single-shot yes/no elicitation? The decisive quantity is the
  Murphy decomposition of the Brier score: an intervention that improves
  reliability but not resolution has made the model better calibrated but no
  better at forecasting.
* **Models** chosen to span response bias (Table S13): LLaMA 3.3 70B (+0.84,
  strong Yes), GPT-5.4 (+0.24, mild Yes), GPT-4o (−0.58, strong No). DeepSeek R1
  (the intended balanced model) could not be re-run: its deployment was retired
  before the study (see §5).
* **Items.** The pinned 500-event retrieval subset (296 binary, 394 perturbed,
  435 MCQ); every arm paired on identical items; post-cutoff throughout (GPT-5.4
  also has a pre/post split).
* **Arms.** A base (stored); B1 asymmetric and B2 symmetric debiasing prompts
  (confidence elicitation byte-identical to base, asserted); C retrieval
  restricted to pre-cutoff documents (stored for GPT-4o and GPT-5.4; generated
  for LLaMA); D self-consistency, n = 10/5/5 samples at T = 1.0 with the
  confidence request removed, probability = vote share (Laplace-smoothed log
  loss also reported); E direct probability elicitation (P(Yes); per-option
  probabilities for MCQ, sum-to-one audited); F ensembles derived from A (mean
  probability, mean logit, majority vote; three-model and all-model).
* **Metrics.** Accuracy and bias index; Brier, log loss, ECE/MCE (10 equal-width
  bins; equal-mass ECE as robustness), Murphy reliability/resolution/
  uncertainty, AUROC, Brier skill vs the base-rate forecast; reliability diagrams
  and confidence histograms per model × arm; 10k paired event bootstraps with
  Holm correction across arms.

## 2. What we found

1. **No intervention gives any model forecasting skill.** Brier skill against
   the constant base-rate forecast is negative in every model × arm cell;
   resolution never leaves the 0.00–0.02 band (uncertainty 0.245); AUROC never
   moves with a CI excluding zero except under retrieval (below).
2. **Direct probability elicitation (E) is the only intervention that improves
   calibration for all three models** — Brier −0.028 [−0.039, −0.016] (LLaMA),
   −0.010 [−0.032, +0.011] (GPT-5.4), −0.019 [−0.028, −0.008] (GPT-4o) — and the
   gain is entirely reliability; resolution changes are 0.000, +0.001, −0.002.
3. **Prompting changes nothing** (|ΔBrier| ≤ 0.008, all CIs span zero); the
   asymmetric prompt lowers MCQ accuracy for the two weaker models.
   **Self-consistency is the worst calibration arm everywhere** (Brier +0.11 to
   +0.20) because sampling is near-degenerate: 70–77% of items are unanimous
   at T = 1.0.
4. **Retrieval is the one arm that improves discrimination** (binary AUROC
   +0.04 to +0.10; LLaMA MCQ AUROC +0.11) while leaving calibration worse or
   unchanged; on GPT-5.4's pre-cutoff items the same arm reaches AUROC 0.81,
   the recall signature.
5. **Ensembling models with opposite biases gives the best Brier in the study**
   (all-model mean probability 0.267, bias +0.05) with AUROC 0.503, exactly
   chance.
6. **Effect direction does not depend on the model's baseline bias for
   calibration**, only for accuracy: each intervention shifts bias in a fixed
   direction for all models (prompts → No, retrieval → Yes, probabilities → the
   middle), so it helps the model whose bias it opposes and not the other,
   while the reliability gain from E appears in all three.

## 3. Suggested text for the response letter

We thank the reviewer and have added a dedicated calibration-intervention study
(new Supplementary Section S-C, Tables S-C1–S-C4, Figures S-C1–S-C3). On the
pinned 500-event subset and three models chosen to span response bias, we
compare six conditions paired on identical items — base, two debiasing prompts,
retrieval restricted to pre-cutoff documents, self-consistency sampling, direct
probability elicitation, and three ensembling rules — and decompose the Brier
score into reliability and resolution so that better-behaved probabilities can be
distinguished from more informative ones.

The interventions can move reliability substantially: eliciting a probability
instead of a label lowers the Brier score for every model, and averaging models
with opposite biases gives the best-calibrated forecasts in the study. None of
them moves resolution or discrimination: resolution stays within 0.00–0.02 for
every model and condition, no condition reaches the Brier score of a constant
base-rate forecast, and the only condition that raises AUROC (retrieval) does so
while worsening calibration. Prompting has no effect and self-consistency
sampling degrades calibration because the models' samples are nearly unanimous.
We therefore keep our claim, now stated more precisely: elicitation determines
how badly miscalibrated the forecasts are, but not whether they contain
information about which events occur.

## 4. Manuscript changes proposed

* New supplementary section: design table; master table (model × arm × task ×
  pre/post with all metrics and CIs); delta-vs-base table with corrected
  p-values; reliability diagrams and confidence histograms faceted model × arm;
  ensemble table; cost table.
* Main text: one paragraph in Results replacing the current calibration
  paragraph, and the precise claim above in Discussion.

## 5. Panel composition (DeepSeek R1 → GPT-5.4)

The design called for DeepSeek R1 as the balanced model. Its Azure Foundry
deployment was retired before the study ran (HTTP 410 `model_deprecated`; no
other endpoint serves the original weights, and the R1-0528 / MAI-DS-R1
checkpoints are neither deployed nor the same model), so paired intervention
arms could not be generated for it. GPT-5.4 (bias +0.238, the next-closest to
neutral with a live deployment and a stored WS+Cutoff run) takes the middle
position, so the panel still spans strong-Yes, mild-Yes and strong-No bias. R1
stays in the tables for the two arms that need no new inference (base and
stored retrieval), and its retrieval arm tells the same story as the panel:
post-cutoff Brier +0.013 [−0.004, +0.031], resolution unchanged, AUROC +0.038
[−0.018, +0.095]; pre-cutoff AUROC +0.164 [+0.050, +0.281] and accuracy
+0.156, i.e. recall rather than foresight. The stored R1 base outputs are
untouched. Cost of the new inference: about $33 (arms B, D, E for three
models, plus the LLaMA retrieval arm) at list prices.
