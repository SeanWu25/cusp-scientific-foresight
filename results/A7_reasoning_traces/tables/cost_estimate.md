# A7 Step 2 cost estimate (before any coding call)

Coding sample: **11,849 traces** (`coding_sample.json`, seed 13), each coded by **two independent coder models**, 16 codes in one structured call per trace. Faithfulness judge (analysis D): **6,190 binary / perturbed / MCQ traces**, one call each.

Measured prompt sizes: system 1,279 tokens (identical every call, so it caches), user 239 tokens on average, output budgeted at 170 tokens. Faithfulness: system 170 + user 196, output 60.

| coder | endpoint | price in/out per MTok | calls | cost without caching | cost with prompt caching | price source |
|---|---|---|---|---|---|---|
| Claude Haiku 4.5 | claude-haiku-4-5 / anthropic | $1.0/$5.0 | 11849 | $28.06 | $14.42 | Anthropic list price for Claude Haiku 4.5, assumed; cache write 1.25x / read 0.1x |
| GPT-5.4-mini | gpt-5.4-mini / openai | $0.25/$2.0 | 11849 | $14.69 | $11.28 | scripts/run_cusp.py PRICING (gpt-5.4-mini), assumed; cached input 0.1x; reasoning_effort=minimal, but reasoning tokens bill as output so its output budget is raised to 430 |
| Faithfulness judge (Claude Haiku 4.5) | claude-haiku-4-5 / anthropic | $1.0/$5.0 | 6,190 | $4.13 | $4.13 | same |

**Total with prompt caching: $29.82** (without caching $46.87). Prices are assumed list prices, not verified against invoices. A 200-trace double-coded pilot (~$2) runs first to check the output format and the blinding asserts.

## Sample composition

| stratum | traces | purpose |
|---|---|---|
| MAIN — base condition, capped 80 per model x task x partition | 7,200 | analyses A, B, E, G |
| DATE — extra base date traces, to 300 per model | 1,560 | analysis C (priority) |
| PAIRED — 30 pinned-500 events per model x task, kept as base/WS+Cutoff/WS triples | 3,150 | analysis F |

By task: binary 2,065, binary_perturbed 2,067, mcq 2,058, date 3,599, frq 2,060

By condition: base 9,749, ws_cutoff 1,050, ws 1,050
