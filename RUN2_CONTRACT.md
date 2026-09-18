# RUN2_CONTRACT.md — what run 2 must hold identical to be poolable with run 1

Run 1 covers the existing CUSP corpus, **Jan 2024 – Mar 2026**, 4,760 events.
Run 2 will cover the **Apr – Aug 2026** extension. The two are only poolable if
everything below matches. Every value here is machine-checked against
`results_sonnet5_run1/MANIFEST.json`; do not transcribe them by hand.

## 1. Frozen identities

| Item | Where it is pinned | Check |
|---|---|---|
| Prompt templates | `MANIFEST.prompt_templates` — sha256 of each system prompt by AST literal value | must match exactly |
| Judge rubrics | `MANIFEST.judge_rubrics` — `judge_frq_combined` = `fc24e69d…` (2,697 chars) | must match exactly |
| Scoring code | `MANIFEST.code_sha256["scripts/eval.py"]` | must match, or the diff must be shown to be non-behavioural |
| Judge model | `gpt-5.4-mini` | same id **and** same serving stack |
| Model under test | `claude-sonnet-5` (dateless ids are pinned snapshots, not aliases) | `response.model` must echo this |
| Event-ID scheme | UUIDv4 in the `id` field, carried unchanged from the benchmark JSONL | run-2 ids must not collide with run-1 ids |
| Partition rule | `MANIFEST.partition_rule` | see §3 |

Hashes are taken from the *parsed literal value*, not the source text, so
reformatting the file cannot break a match and cannot hide a real edit either.

## 2. Decoding parameters

Sonnet 5 rejects every sampling parameter. Run 2 must send the same set, which
is none:

- `temperature` — **not sent.** `400 temperature is deprecated for this model`
- `top_p`, `top_k` — **not sent.** Same 400.
- `output_config.effort` — must equal run 1's value (`MANIFEST.decoding.effort`)
- `max_tokens` — 2048 for binary / perturbed / MCQ / date
- FRQ `max_tokens` — must equal run 1's value; see the note in
  `MANIFEST.unmatchable_parameters`, this cap is not neutral across models
- thinking — adaptive, always on, not configurable off
- retries — 2, backoff `2**attempt` seconds

Because temperature cannot be pinned to 0, Sonnet 5 is stochastic. Run 1 is
executed three times end to end; **run 2 must also be executed three times**, or
the run-to-run variance terms cannot be pooled.

## 3. Partition rule

The repository contains two cutoff conventions that differ by one month, and
both appear in the published tables:

- **main tables** (`make_latex_tables.py`, `compare_models.py`): `pre` if
  `pub_month < cutoff_month`, so the cutoff month counts as **post**
- **gap and calibration tables** (`filter_ids_by_cutoff`): `post` if
  `pub_month > cutoff_month`, so the cutoff month counts as **pre**

Run 1 reproduces each table under the convention its own generator used, so each
Sonnet 5 row is comparable with the six published rows in that same table. Run 2
must do the same. With a Jan 2026 cutoff every run-2 event is post-cutoff under
both conventions, so the choice does not affect run-2 rows — but it does affect
the pooled pre/post split, so it must not be changed.

## 4. Refusals

Sonnet 5 declines a material share of biomedical items with
`stop_reason="refusal"`, category `bio`. These are **deterministic** — the same
item refuses on every retry — and they are **not answers**. Run 2 must:

1. record `stop_reason`, `stop_details.category` and `stop_details.explanation`
   on every refusal;
2. exclude refused instances from scoring denominators rather than score them
   as wrong;
3. report the refusal rate per task and per research area alongside every score.

## 5. Per-instance logging

One JSONL record per event, keyed by `id`, appended and never overwritten, with
at minimum: raw verbatim response per task, parse outcome, condition label, run
index, start and end timestamps, retry count, refusal flag and category, stop
reason, token usage, latency, and the realised MCQ choice permutation
(`mcq_shuffled_choices`, `mcq_shuffled_answer_key`).

## 6. MCQ permutations

Drawn from `random.Random(42)` in benchmark file order, before any concurrency.
Run 2 draws its own permutations over its own file — it must not attempt to
continue run 1's stream. This matches the published work, where all six models
drew different permutations from each other.

## 7. Merge procedure

`scripts/merge_runs.py` concatenates run-1 and run-2 JSONL, verifies the
contract, and recomputes every table over the union. Nothing is re-run in April.

```bash
python scripts/merge_runs.py \
    --run1-manifest results_sonnet5_run1/MANIFEST.json \
    --run2-manifest results_sonnet5_run2/MANIFEST.json \
    --run1 'results_sonnet5_run1/raw/*.jsonl' \
    --run2 'results_sonnet5_run2/raw/*.jsonl' \
    --out  results_sonnet5_merged/
```

The merge **aborts** on any contract violation. Override only with
`--allow-mismatch <field>`, which stamps the violation into the merged
manifest so it cannot be lost.
