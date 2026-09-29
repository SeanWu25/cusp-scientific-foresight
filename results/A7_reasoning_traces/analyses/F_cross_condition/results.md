# Analysis F — the same item under base, WS+Cutoff and unrestricted WS

Matched triples: the same model, task and event coded under all three conditions. **1,050 complete triples** (414 distinct events, 7 models).

## Is the retrieved evidence actually referred to in the trace?

Detected by an explicit reference to the supplied material ("Source 2", "the search results", "according to the context"). This is a lower bound: a trace can use retrieved content without naming it.

| condition | traces | explicitly reference retrieved material | carry EVIDENCE_CITED |
|---|---|---|---|
| base | 1,050 | 2.1% | 12.6% |
| ws_cutoff | 1,050 | 32.4% | 50.4% |
| ws | 1,050 | 35.2% | 59.5% |

## Does the conclusion change, and does it change more when the evidence is referenced?

| condition vs base | retrieved material referenced | answer changed | n |
|---|---|---|---|
| ws_cutoff | yes | 59.3% | 307 |
| ws_cutoff | no | 59.7% | 524 |
| ws | yes | 63.2% | 315 |
| ws | no | 61.0% | 510 |

## Code prevalence shift across conditions, on the matched triples

| code | base | WS+Cutoff | WS | WS+Cutoff minus base [95% CI] | p (Holm) |
|---|---|---|---|---|---|
| EVIDENCE_CITED | 12.6% | 50.4% | 59.5% | +37.8 pts [+34.3, +41.4] | 0.014 |
| KNOWLEDGE_GAP_ADMITTED | 1.0% | 0.1% | 0.6% | -0.9 pts [-1.5, -0.3] | 0.014 |
| ABSENCE_AS_EVIDENCE | 3.7% | 5.3% | 6.1% | +1.6 pts [-0.2, +3.4] | 0.096 |
| RATE_OF_PROGRESS | 7.7% | 5.3% | 2.7% | -2.4 pts [-4.0, -0.9] | 0.018 |
| ROUND_ANCHOR | 3.7% | 2.3% | 1.6% | -1.4 pts [-2.6, -0.3] | 0.028 |
| PROVENANCE_INFERRED | 9.1% | 23.7% | 36.6% | +14.6 pts [+11.9, +17.1] | 0.014 |
| FIELD_MOMENTUM | 15.6% | 8.3% | 2.5% | -7.3 pts [-9.6, -5.0] | 0.014 |
