# Run 1 — Claude Sonnet 5 and Claude Fable 5 on CUSP (Jan 2024 – Mar 2026)

Everything here is regenerable from the raw JSONL with `scripts/make_all_tables.sh`.
No table in this directory is hand-edited.

## What was run

| Model | Cutoff | Condition | Passes | Events |
|---|---|---|---|---|
| Claude Sonnet 5 | Jan 2026 | base (no tools) | 3 at effort=medium, 1 at effort=low | 4,760 each |
| Claude Sonnet 5 | Jan 2026 | WS+Cutoff, WS | 1 each | pinned 500 |
| Claude Fable 5 | Jan 2026 | base (no tools) | 1 at effort=medium | 4,760 |
| Claude Fable 5 | Jan 2026 | WS+Cutoff, WS | 1 each | pinned 500 |

Both models share a January 2026 cutoff, so they sit in an identical pre/post
partition. They are the only two current Claude models that yield a non-empty
post-cutoff partition on this corpus — Opus 5 (May 2026) and Fable 5.1 (Jun 2026)
would have none, because CUSP ends in March 2026.

## Layout

```
MANIFEST.json          Step-1 freeze: hashes, judge config, decoding params
RAW_HASHES.txt         sha256 of every raw artifact (raw files are gitignored)
pilot_ids.txt          402-event pilot: 150 stratified + all 252 Feb–Mar 2026
subset500_ids.txt      the pinned retrieval subset, selected by stored id
raw/                   predictions + judgements, one JSONL record per event
reports/               eval.py-schema reports, built by scripts/build_report.py
tables/                every table, .json and .txt
pilot/                 Step-2 pilot outputs and the FRQ token-cap probe
ab/                    Azure vs OpenAI judge-endpoint comparison
```

## Decisions that affect how the numbers read

**Refusals are excluded from denominators, not scored as wrong.** Both models
return `stop_reason="refusal"` on part of the corpus. These are deterministic —
the same item refuses on every retry — and category `bio` in essentially every
case. They are not answers, so counting them as wrong would measure safety
policy rather than foresight. Every report records the refusal count per task
and per research area; `build_report.py --score-refusals-as-wrong` quantifies
how much the choice moves each metric (for Sonnet 5 MCQ it is about 9 points).

| | overall | Biology | Medicine |
|---|---|---|---|
| Sonnet 5 (full corpus) | 4.3% | 8.3% | 12.0% |
| Fable 5 (60 matched biomedical MCQ) | — | 71.9% | 92.9% |

Fable 5's row therefore covers a materially different slice of CUSP than every
other row in the panel. Do not compare it naively.

**Two partition conventions coexist in the repository and both are reproduced.**
The main tables treat the cutoff month as post-cutoff; the gap and calibration
tables treat it as pre-cutoff. Each table is computed under the convention its
own generator used, so every new row is comparable with the six published rows
in that same table. With a Jan 2026 cutoff the choice moves the post-cutoff
partition between 455 and 252 events, so it is stated explicitly everywhere.

**FRQ is capped at 384 output tokens.** Not neutral, and chosen deliberately.
At 384 Sonnet 5 retains a mean of 1,019 characters, against Claude Sonnet 4.5's
1,036 and GPT-5.4's 1,089, so the judge sees the same amount of text from each.
The harness default of 250 (what Sonnet 4.5 ran with) would give Sonnet 5 only
~720 characters because of the newer tokenizer; 1024 would give it ~1,744 and
inflate its specificity score against the rest of the panel.

**Temperature cannot be matched.** Both models reject `temperature`, `top_p`
and `top_k` with HTTP 400. The six published models all ran at temperature 0.
The three repeated Sonnet 5 passes exist to bound the resulting stochasticity;
measured run-to-run sd is 0.0026 (merged binary), 0.0039 (MCQ), 0.0004 (date
score) — an order of magnitude below the confidence intervals.

**The judge was not changed.** Rubric hash `fc24e69d…` is byte-identical to the
rubric in the pre-release tree that produced the published numbers. The judge
runs on the same Azure `gpt-5.4-mini` deployment; an OpenAI-direct endpoint was
tested and rejected because leakage verdicts agreed only 75.5% of the time and
leakage scores correlated at r = 0.00 (see `ab/`). Web search fired on 100% of
FRQ judgements, matching the published runs.

## Validation

The analysis code reproduces the published paper exactly in four places, which
is the evidence that the new rows are computed the same way as the old ones:

- Table 1, all five metrics, all six models
- Table 6 pre/post block
- Table S13 binary extended metrics, all ten columns, plus the S2c instance counts
- Table S18, all thirty Δ_know / Δ_fore values

## Known gaps

- Δ_know / Δ_fore for the new models is underpowered by construction: 30
  post-cutoff ids survive in the shared retrieval set, so most cells fall below
  n=20 and are suppressed. This is what run 2 exists to fill.
- Sonnet 5's bio classifier also declines the search-query generation call, so
  28/500 and 29/500 rows in the two retrieval conditions ran with no context.
  They are flagged `retrieval_failed` and dropped from the decomposition.
- FRQ leakage `unclear` rate is 13.4% for Sonnet 5 against 1.9–2.9% for every
  published model. The fail rate, 0.20%, is inside the published band.
