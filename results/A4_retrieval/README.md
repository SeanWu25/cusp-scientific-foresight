# A4 — retrieval experiments and knowledge access (Reviewer 2, concern C4)

Regenerate from stored JSONL (no inference):

    python results/A4_retrieval/scripts/a42_summarize.py          # A4.2 tables + figure from verdicts.jsonl
    python results/A4_retrieval/scripts/a43_gaps.py               # A4.3 reports, gaps.csv, results.md, figure
    python results/A4_retrieval/scripts/a43_inclusion_summary.py  # A4.3 inclusion table (appends to results.md)
    python results/A4_retrieval/scripts/a4_manifest.py            # MANIFEST.json

Inference steps (already run; all checkpointed per item and resumable):

    a42_build_sample.py   -> A4_2_groundtruth_inclusion/sample.json (seed 20260921)
    a42_judge.py          -> A4_2_groundtruth_inclusion/verdicts.jsonl   (You.com re-query + Claude Sonnet 5 judge)
    a43_queries.py        -> A4_3_fixed_queries/queries.jsonl           (Claude Opus 4.8; gpt-5.4-mini for refused items)
    a43_evidence.py       -> A4_3_fixed_queries/evidence/<bound>.jsonl  (You.com, one call per event x bound)
    a43_run.py            -> A4_3_fixed_queries/model_outputs.jsonl     (run_cusp.py process_row, unmodified)
    a43_inclusion.py      -> A4_3_fixed_queries/inclusion_verdicts.jsonl

`A4_1_pipeline/pipeline_description.md` is the code-verified description; `response_A4.md` the reviewer response.
Raw retrieval runs used as inputs are listed in `scripts/a42_common.py` (`RUNS`); two of them (DeepSeek R1, Claude
Sonnet 4.5) live only in the pre-release backup tree `~/FutureScience_backup_20260508_013823/benchmark_logs/`.
