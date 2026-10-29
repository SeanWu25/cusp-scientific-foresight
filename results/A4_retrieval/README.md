# A4 — retrieval experiments and knowledge access

Regenerate from stored JSONL (no inference):

    python results/A4_retrieval/scripts/a42_summarize.py          # A4.2 tables + figure from verdicts.jsonl
    python results/A4_retrieval/scripts/a43_gaps.py               # A4.3 reports, gaps.csv, results.md, figure
    python results/A4_retrieval/scripts/a43_inclusion_summary.py  # A4.3 inclusion table (appends to results.md)
    python results/A4_retrieval/scripts/a43_pre_post_correlation.py  # A4.3 pre/post gap table + original-vs-fixed agreement
    python results/A4_retrieval/scripts/make_table17.py             # manuscript Table 17, full version (tables/table17_gaps_full.tex)
    python results/A4_retrieval/scripts/make_table19_frq.py         # FRQ-only agreement table, 0-10 units (tables/table19_agreement_frq.tex)
    python results/A4_retrieval/scripts/a4_manifest.py            # MANIFEST.json

Inference steps (already run; all checkpointed per item and resumable):

    a42_build_sample.py   -> A4_2_groundtruth_inclusion/sample.json (seed 20260921)
    a42_judge.py          -> A4_2_groundtruth_inclusion/verdicts.jsonl   (You.com re-query + Claude Sonnet 5 judge)
    a43_queries.py        -> A4_3_fixed_queries/queries.jsonl           (Claude Opus 4.8; gpt-5.4-mini for refused items)
    a43_evidence.py       -> A4_3_fixed_queries/evidence/<bound>.jsonl  (You.com, one call per event x bound)
    a43_run.py            -> A4_3_fixed_queries/model_outputs.jsonl     (run_cusp.py process_row, unmodified)
    a43_inclusion.py      -> A4_3_fixed_queries/inclusion_verdicts.jsonl
    a43_judge_frq.sh      -> A4_3_fixed_queries/judgements_rubric/   (stage-2 FRQ rubric, legacy, Azure judge, 2026-10-04)
    a43_finalize_frq.sh   -> sweep + merge judgements, then reruns every regenerate step above

A4.3 extension to 1,000 events (added 2026-10-18; see `A4_3_fixed_queries/ext500/README.md`):

    a43_ext_sample.py     -> A4_3_fixed_queries/ext500/subset_ext500_ids.txt + sample.json (seed 20261018)
    a43_ext_pipeline.sh   -> ext500/ queries, evidence, model_outputs, FRQ judgements, reports (all steps above, --set ext500)
    a43_gaps_1000.py      -> tables/A4_3_gaps_fixed1000.json, A4_3_fixed_queries/gaps_fixed1000.md (no inference)
    python run_evaluation/make_fig3_overleaf.py --packets 1000   # Figure 3 with panel a on 1,000 events (forecasting_gap_rev_1000.png)

`A4_1_pipeline/pipeline_description.md` is the code-verified description; `response_A4.md` the reviewer response.
Raw retrieval runs used as inputs are listed in `scripts/a42_common.py` (`RUNS`); two of them (DeepSeek R1, Claude
Sonnet 4.5) live only in the pre-release backup tree `~/FutureScience_backup_20260508_013823/benchmark_logs/`.
