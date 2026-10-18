# A4.3 extension — 500 more events for the fixed-evidence-packet experiment (total 1,000)

**Why.** In the first 500 events (`results_sonnet5_run1/subset500_ids.txt`, published Jan 2024 – Mar 2026) only
31 events are post-cutoff for Claude Sonnet 5 (cutoff 2026-01) and 4 for GPT-5.6 Sol (cutoff 2026-02). Their
post-cutoff cells in Figure 3a were suppressed (fewer than 20 events).

**Sample** (`scripts/a43_ext_sample.py`, seed 20261018). Pool: every CUSP event (original corpus + Apr–Aug 2026
extension) that is not in the first 500, was published after 2026-02, and has a stored base record for all six
evaluated models (852 events). 500 drawn without replacement, stratified by publication month (proportional).
Every added event is post-cutoff for every evaluated model. Counts: `sample.json`.

**Method.** Identical to the first 500, with `--set ext500`:
fixed queries by Claude Opus 4.8 with the same combined-query prompt (same prompt hash), gpt-5.4-mini for the
events Opus 4.8 refuses; one You.com call per event and freshness bound, filtered by the unmodified
`scripts/web_search.py`; each model run through `scripts/run_cusp.py process_row` with its original decoding
parameters; FRQ graded with the same stage-2 rubric and Azure judge; scored with `scripts/build_report.py`.
The DeepSeek R1 bound (2024-07-01) is not retrieved, because R1 has no fixed-packet run.

**Differences from the first 500 to state in the paper.** (1) Evidence was retrieved on 2026-10-18; the first 500
were retrieved on 2026-09-21. The web index differs by about four weeks. (2) The original self-query retrieval runs exist only
for the first 500, so the fixed − original comparison (Tables 20/21, `a43_gaps.py`, `a43_pre_post_correlation.py`)
stays on the first 500. The fixed-packet gaps of Figure 3a use base + fixed runs only and are computed on all
1,000 events by `scripts/a43_gaps_1000.py`.

Files: `queries.jsonl`, `evidence/<bound>.jsonl`, `model_outputs.jsonl`, `benchmark_ext500.jsonl` (the 500
benchmark rows, both corpus files), `reports/`, `judgements_rubric/`, `judgements_merged/`, `logs/`.
