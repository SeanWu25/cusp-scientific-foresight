# Analyses added for CUSP v2

Every folder below holds the code that produced one analysis, its result tables and figures, and a README with the regeneration commands. The analyses read stored, already-scored model outputs; none of them calls a model. Raw API transcripts are not in this repository; the `RAW_HASHES.txt` and `MANIFEST.json` files record the SHA-256 hash, date and settings of every raw file used.

| Analysis | Folder | Entry point | Main outputs |
|---|---|---|---|
| Model runs on CUSP v2 (Claude Sonnet 5, Claude Opus 4.8, GPT-5.6 Sol on the original corpus; all panel models on the April–August 2026 extension; LLaMA 3.3 retrieval runs) | [`results_sonnet5_run1/`](../results_sonnet5_run1), [`results_opus48_run1/`](../results_opus48_run1), [`results_sol_run1/`](../results_sol_run1), [`results_extension_run2/`](../results_extension_run2), [`results_llama33_run1/`](../results_llama33_run1) | `scripts/run_cusp.py`, `scripts/judge_frq.py`, `scripts/build_report.py` | `reports/*.json` (scored per-event results, the input of every table), `tables/` |
| Main tables and figures (Table 1, Fig. 3, Fig. 4, Extended Data, supplementary tables) | [`run_evaluation/`](../run_evaluation) | `make_table1_overleaf.py`, `make_fig3_overleaf.py`, `make_fig4_overleaf.py`, `make_ed_anchor.py`, `make_si_*.py`, `prepost_table.py` | figures and LaTeX/Markdown tables |
| Forecast-horizon analysis (mixed-effects models, within-model slopes, anchoring null, curvature) | [`horizon_study/`](../horizon_study) | `run_no_v4pro.py main`, `curvature_continuous.py` | `tables_no_v4pro/`, `figures_no_v4pro/` |
| Information access and retrieval audit (ground truth in retrieved evidence, document-level leakage, fixed evidence packets on 1,000 events) | [`results/A4_retrieval/`](../results/A4_retrieval) | `scripts/a42_*.py`, `scripts/a43_*.py` | `tables/`, `A4_2_groundtruth_inclusion/`, `A4_3_fixed_queries/` |
| Calibration and elicitation interventions (prompting, self-consistency, probability elicitation, ensembles, cutoff-restricted retrieval) | [`calibration_study/`](../calibration_study) | `run_arm.py`, `analyze.py` | `tables_cmpre/`, `figures_cmpre/` |
| Base-rate injection sweep (stated prior 10–90%, eight models) | [`results/A8_base_rate/`](../results/A8_base_rate) | `scripts/a8_*.py` | `tables_cmpre/`, `figures_cmpre/` |
| Binary task validity (negatives realized elsewhere, detectability of perturbations) | [`results/A2_binary_validity/`](../results/A2_binary_validity) | `scripts/` | `tables/`, `figures/`, `SUMMARY.md` |
| Task correlations (model level and event level) | [`results/A1_2_task_correlation/`](../results/A1_2_task_correlation) | `compute_task_correlation.py` | `task_correlation_table1panel.md` |
| Benchmark composition (source, citation visibility, publication and editorial latency) | [`results/A5_selection_bias_cmpre/`](../results/A5_selection_bias_cmpre) | `scripts/a5_*.py` | `tables/`, `by_*/` |
| Stated reasoning of the models (coded justifications) | [`results/A7_reasoning_traces/`](../results/A7_reasoning_traces) | `scripts/a7_*.py` | `tables/`, `analyses/` |

**Conventions.** All analyses count an event in a model's cutoff month as pre-cutoff (folders and files marked `_cmpre`). DeepSeek R1 is evaluated on the original corpus only, because its deployment was retired before the extension was collected. The nine-model panel and the cutoff of each model are in [`configs/model_settings.json`](../configs/model_settings.json).

**Paths.** The scripts are run from the repository root. They read the benchmark from `archive/data/canonical/merged_validated_cusp_fixed.jsonl` (original corpus) and `benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl` (extension); the public equivalents are [`data/CUSP_v2_full.jsonl`](../data/CUSP_v2_full.jsonl) and [`data/CUSP_v2_extension_apr_aug_2026.jsonl`](../data/CUSP_v2_extension_apr_aug_2026.jsonl) (same events and questions). The scored reports of the six models of the first CUSP release are read from `run_evaluation/frq_results/`.

The revision analysis code was run with Python 3.13; it also parses on Python 3.10.
