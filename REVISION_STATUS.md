# CUSP revision status — index for picking up work

Nature Machine Intelligence revision of "Forecasting Scientific Progress with Artificial
Intelligence". This file is the map: what has been answered, where it lives, what is still open.
Last updated 2026-09-29.

**Read this first, then the relevant `response_*.md`.** Every study regenerates from stored JSONL
with one command and does no new benchmark inference. Several sessions share this repo and this
working tree, so check `git status` and `ps` before assuming an untracked file is abandoned.

## Reviewer responses

| reviewer point | study | response file | regenerate with | status |
|---|---|---|---|---|
| R1 C4 — horizon / time-to-event | `horizon_study/` | `REVIEWER_RESPONSE_R1_C4.md` | `python horizon_study/run_all.py` then `figures.py` | complete. §9 adds the reviewer's own mixed model with horizon as 1- and 3-month bin dummies, base and retrieval, four tasks |
| R1 C5 — benchmark selection bias | `results/A5_selection_bias/` | `response_A5.md` | `bash results/A5_selection_bias/run_all.sh` | complete. Whole-corpus citation and latency snapshot (2026-09-25); source, visibility, latency, novelty, all split pre/post cutoff |
| R1 C6 — calibration / elicitation | `calibration_study/` | `REVIEWER_RESPONSE_R1_C6.md` | `python calibration_study/analyze.py` | complete. Arms A–F; B1/B2/D/E were run on three models |
| R2 C2 — validity of the binary task | `results/A2_binary_validity/` | `REVIEWER_RESPONSE_R2_C2.md`, `REVIEWER_RESPONSE_R2_NEGATIVES_STRICT.md`, `DATASET_CHECK_BINARY.md` | see that study's README | **owned by another session; untracked at time of writing** |
| R2 C4 — retrieval and knowledge access | `results/A4_retrieval/` | `REVIEWER_RESPONSE_R2_C4.md`, `results/A4_retrieval/response_A4.md` | `bash results/A4_retrieval/run_all.sh` | complete, but see open decision 1 |
| R2 C5 — why failures occur, controlled | `results/A8_base_rate/` | `response_A8.md` | `bash results/A8_base_rate/run_all.sh` | complete. Base-rate injection swept over 10/30/50/70/90% on 9 panel models, 500 events, both binary variants |
| R2 C5 — why failures occur, observational | `results/A7_reasoning_traces/` | `response_A7.md` | `bash results/A7_reasoning_traces/run_all.sh` | complete, but see open decision 2 |
| MCQ / FRQ validity | `results/A3_mcq_frq_validity/` | `response_A3.md` | see that study's README | **owned by another session** |
| task correlation | `results/A1_2_task_correlation/` | — | `compute_task_correlation.py` | **owned by another session** |
| FRQ human study | `results/frq_human_study/` | — | see that study's scripts | **owned by another session**; exports committed 2026-09-29 |

## Open decisions that need the PI

1. **Opus 4.8 joined the panel and broke two "out-of-panel" claims.** It wrote the fixed queries for
   A4.3 and was the judge in A2 Study 2, and it is now an evaluated model. Options put to Sean
   earlier: regenerate the queries with Opus 5 or Haiku 4.5 (about $4 plus a roughly $200 rerun),
   reword to "outside the panel at the time", or drop Opus 4.8 from the retrieval-study rows. No
   decision recorded. Four lines of prose in the A2 study also need editing either way.
2. **A7's human validation is built but not run.** `results/A7_reasoning_traces/human_validation.csv`
   holds 2,149 rows over 300 passages for three annotators, with a 429-row block annotated by all
   three for inter-rater reliability. Reviewer 2 already criticised the FRQ judge for weak human
   agreement (r = 0.34), and A7's coding is currently model-against-model only. Recommendation on
   record: run it before submission, otherwise the same criticism lands again.
3. **`calibration_study/prices.json` holds assumed list prices**, never checked against an invoice.
   Every cost figure in A5, A6, A7 and A8 inherits that assumption and says so.

## Conventions and traps that cost real time to find

* **Merged binary, always.** Ground truth is Yes for every original binary item and No for every
  perturbed twin. Any statistic computed on one variant alone measures response bias, not skill.
  Pool both variants of the same event. A7 was rewritten mid-analysis over exactly this.
* **Two partition rules both appear in the published tables**, differing by one month. Main tables:
  pre if `pub_month < cutoff_month`. Gap and calibration tables: post if `pub_month > cutoff_month`.
  Reproduce each table under the rule its own generator used.
* **No provider-native thinking text exists anywhere in this corpus.** Only the in-answer 1–2
  sentence `reasoning` field. Any future chain-of-thought work needs a fresh run with capture on.
* **DeepSeek-R1's deployment is retired** and GPT-OSS 20B has no Azure deployment. GPT-OSS runs
  locally with `bash results/A8_base_rate/scripts/serve_gptoss.sh` (vLLM, port 8077).
* **Claude Sonnet 4.5 now refuses about 13% of binary items**, against 1% in its April 2026 base run.
  Provider classifier drift, not an experimental effect.
* Peer sessions share this repo and the judge endpoints. Check `ListAgents` and `ps` before killing
  anything that looks stray.

## Where the detail lives

Durable notes are in the session memory directory, indexed by `MEMORY.md`: one file per study
(`horizon-study-a4`, `calibration-study-a6`, `cusp-event-metadata-limits`, `base-rate-study-a8`,
`reasoning-trace-study-a7`), plus model facts (`opus-4-8-model-facts`,
`deepseek-r1-deployment-gone`) and environment traps (`azure-judge-throughput-knee`,
`pkill-self-match-trap`, `peer-sessions-share-repo-and-judge`).

Each study directory has its own `README.md` explaining its layout, and a `MANIFEST.json` recording
models, API-reported snapshots, seeds, prompt hashes, costs and the git SHA at the time of the run.
