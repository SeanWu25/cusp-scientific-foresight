# Reviewer 1, comment 6 — calibration interventions

Regenerable from stored model outputs with `python calibration_study/analyze.py`. Full write-up, tables and figures: `calibration_study/RESULTS.md`, `calibration_study/tables/`, `calibration_study/figures/`.

**Design.** Three models spanning response bias (LLaMA 3.3 +0.84, GPT-5.4
+0.24, GPT-4o −0.58) on the pinned 500 subset; five arms paired on identical
items: base, two debiasing prompts, pre-cutoff retrieval, self-consistency
(n = 10/5/5 at T = 1), direct probability elicitation, plus three derived
ensembles. Brier, log loss, ECE/MCE, Murphy reliability/resolution, AUROC, all
with 10k paired event bootstraps and Holm correction; post-cutoff throughout.

**Findings for the response letter.**

1. No intervention gives any model forecasting skill: the Brier skill score
   against the constant base-rate forecast is negative in every model × arm
   cell, and resolution never leaves the 0.00–0.02 band (uncertainty 0.245).
2. Direct probability elicitation is the only arm that improves calibration for
   all three models (Brier −0.028, −0.010, −0.019), and the gain is entirely
   reliability; resolution and AUROC do not move. Ensembling models with
   opposite biases gives the best Brier in the study with AUROC at exactly
   chance.
3. Prompting changes nothing (|ΔBrier| ≤ 0.008, CIs span zero). Self-consistency
   is the worst calibration arm everywhere because sampling is near-degenerate
   (70–77% unanimous votes). Retrieval is the one arm that raises AUROC
   (+0.04 to +0.10 binary, +0.11 MCQ for LLaMA) and it does so while leaving
   calibration worse or unchanged; LLaMA's retrieval arm was generated for this
   study since none was stored.
4. Every intervention shifts bias in a fixed direction for all models (prompts
   → No, retrieval → Yes, probabilities → the middle), so accuracy changes depend
   on whether the shift opposes the model's baseline bias while the reliability
   gain does not. Suggested phrasing: elicitation determines how badly
   miscalibrated the forecasts are; it does not determine whether they contain
   information about which events occur.

## Panel composition (DeepSeek R1 → GPT-5.4)

The design called for DeepSeek R1 as the balanced model (bias index −0.025).
Its Azure Foundry deployment was retired before the study ran (HTTP 410,
`model_deprecated`; no other endpoint serves the original weights, and the
R1-0528 / MAI-DS-R1 checkpoints are neither deployed nor the same model), so
paired intervention arms could not be generated for it. GPT-5.4 (bias +0.238,
the next-closest to neutral with a live deployment and a stored WS+Cutoff run)
takes the middle position, so the panel still spans strong-Yes, mild-Yes and
strong-No bias. R1 remains in the tables for the two arms that need no new
inference (base and stored retrieval), and its retrieval arm tells the same
story as the panel: post-cutoff, Brier +0.013 [−0.004, +0.031], resolution
unchanged, AUROC +0.038 [−0.018, +0.095]; pre-cutoff, AUROC +0.164
[+0.050, +0.281] and accuracy +0.156, i.e. recall rather than foresight. The
stored R1 base outputs are untouched.
