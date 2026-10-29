# LLaMA 3.3 70B — WS+Cutoff (2026-09-20) and unrestricted WS (2026-10-05) on the pinned 500-event subset

Generated 2026-09-20 to fill the one retrieval cell the published runs lacked
(LLaMA 3.3 had no stored WS+Cutoff run). Used by `calibration_study/` (arm C)
and `horizon_study/` (dataset 3).

| item | value |
|---|---|
| model | `Llama-3.3-70B-Instruct` on the Azure AI Foundry OpenAI-compatible endpoint (the published base run's `model` field is `Llama-3.3-70B`; same weights, serving stack not recorded for the original) |
| harness | `scripts/run_cusp.py --condition ws_cutoff --ws-cutoff 2023-12 --temperature 0 --max-tokens 2048 --frq-max-tokens 2048 --concurrency 6`, frozen prompts, JSON mode |
| retrieval | You.com, documents restricted to ≤ 2023-12 (the model's knowledge cutoff); query generation by the same model via `scripts/web_search.py` |
| items | `results_sonnet5_run1/subset500_ids.txt` (500 events; all post-cutoff for this model) |
| outputs | `raw/ws_cutoff_500.jsonl` and `raw/ws_500.jsonl` (gitignored, sha256 in `RAW_HASHES.txt`), `reports/ws_cutoff_500.json` and `reports/ws_500.json` built by `scripts/build_report.py` (scoring_v1) |
| unrestricted WS | `raw/ws_500.jsonl`, generated 2026-10-05 with `--condition ws` and otherwise identical flags, for the A4.3 forecasting-gap rows (`postrun_ws.sh`); 500 rows, 0 errors, 2 retrieval failures |
| FRQ | generated and archived verbatim; stage-2 rubric scored 2026-10-04 (legacy rubric, `judgements_rubric/`, merged in `judgements_merged/`; report rebuilt with `--frq-scores include`, all other task fields unchanged) for the A4.3 FRQ gap rows |
