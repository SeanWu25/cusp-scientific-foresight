# Changelog

## CUSP v2 — 29 October 2026

This release adds the April–August 2026 extension of CUSP, results for nine models, the model-inference entry point and all analysis code of the CUSP v2 study. It adds 701 files (about 274 MB) and changes 2 existing files (`README.md`, `docs/INFERENCE.md`). No manuscript or review material is included.

### Data
- **`data/CUSP_v2_full.jsonl`** — 5,575 events (January 2024 – August 2026) and 19,706 validated questions: 2,951 Binary, 4,305 perturbed Binary, 4,734 MCQ, 4,765 FRQ and 2,951 Date. The first 4,760 events are identical to `CUSP_final.jsonl` on Hugging Face.
- **`data/CUSP_v2_extension_apr_aug_2026.jsonl`** — the 815 new events (Nature 382, Science 210, Hugging Face daily papers 131, Cell 92), same fields as the Hugging Face release.
- **`data/README.md`** — format, provenance and how to split events by knowledge cutoff.

### Model inference (added 28 October 2026)
- **`docs/INFERENCE.md`** — the protocol to run a model on CUSP and score it: setup, inference per provider (OpenAI, Azure, Anthropic, local open-weight models through vLLM), retrieval conditions, prompt locations, output fields, FRQ judging and scoring, and which parts need a proprietary API.
- **`configs/model_settings.json`** — identifier, knowledge cutoff, provider and decoding flags of the nine models.
- **`scripts/run_cusp.py`** (concurrent inference with full per-call logging), **`scripts/judge_frq.py`** (two-stage FRQ judge), **`scripts/build_report.py`** and **`scripts/scoring_v1.py`** (scoring with a byte-identity check of the graders); `scripts/test_LLM.py` and `scripts/web_search.py` updated to the versions used for the CUSP v2 runs (prompts and parser unchanged).
- Correction (29 October): the FRQ judge is **GPT-5.4-mini** on Azure OpenAI (README and `docs/INFERENCE.md` previously said GPT-5).

### Results
- Scored per-event reports for all nine models:
  - original corpus: `run_evaluation/frq_results/` (GPT-4o, LLaMA 3.3 70B, GPT-OSS 20B, DeepSeek R1, Claude Sonnet 4.5, GPT-5.4), `results_sonnet5_run1/`, `results_opus48_run1/`, `results_sol_run1/` (Claude Sonnet 5, Claude Opus 4.8, GPT-5.6 Sol, including repeated runs and the WS+Cutoff / WS runs on the pinned 500-event subset);
  - April–August 2026 extension: `results_extension_run2/` (every model except DeepSeek R1, whose deployment was retired);
  - LLaMA 3.3 retrieval runs: `results_llama33_run1/`.
- Each run folder has a `MANIFEST.json` and `RAW_HASHES.txt` (SHA-256, date and settings of every raw file).

### Analyses (see `docs/REVISION_ANALYSES.md`)
- `horizon_study/` — forecast-horizon mixed-effects models, within-model slopes, anchoring null and curvature tests.
- `results/A4_retrieval/` — ground truth in retrieved evidence, document-level leakage, fixed evidence packets on 1,000 events.
- `calibration_study/` — prompting, self-consistency, probability elicitation, ensembles and cutoff-restricted retrieval.
- `results/A8_base_rate/` — stated-prior sweep (10–90%) for eight models.
- `results/A2_binary_validity/` — negatives realized elsewhere, detectability of perturbations.
- `results/A1_2_task_correlation/` — model-level and event-level task correlations.
- `results/A5_selection_bias_cmpre/` (+ `results/A5_selection_bias/metadata/`) — source, citation visibility, publication and editorial latency.
- `results/A7_reasoning_traces/` — coded stated justifications of the models.
- `run_evaluation/` — 27 new scripts for the main tables, figures and supplementary tables.

### Conventions
- An event in a model's knowledge-cutoff month counts as pre-cutoff in every analysis.
- DeepSeek R1 is evaluated on the original corpus only.

### Not included
Raw API transcripts, pilot runs and run logs (their hashes are in `RAW_HASHES.txt`); raw human annotation files; shell launch scripts with machine-specific paths; results of models outside the nine-model panel. Local paths, endpoint names and contact addresses were replaced by placeholders.
