### Independent second pass over every flagged item (GPT-5.5 + OpenAI web search)

| quantity | outcome | value |
|---|---|---|
| negatives: ACHIEVED re-decided independently | ACHIEVED | 23 |
| negatives: ACHIEVED re-decided independently | NOT_ACHIEVED | 1 |
| negatives: second pass relied on the SAME evidence as the first | 19/24 | 0.792 |
| negatives: mislabelling rate, BOTH passes agree | 23/200 | 0.115 [0.078, 0.167] |
| negatives: mislabelling rate, first pass only | 24/199 | 0.121 [0.082, 0.173] |
| negatives: weighted, BOTH passes agree |  | 0.117 [0.075, 0.163] |
| negatives: sampled item replaced (no verifier could decide it) | 1 | 3d9e3543 -> 01418ea8 (Medicine|numeric) |
| positives: NOT_CONFIRMED re-searched | FOUND | 31 |
| positives: NOT_CONFIRMED re-searched | NOT_FOUND | 6 |
| positives: confirmation rate after second search | 193/200 | 0.965 [0.930, 0.983] |
| positives: first-pass refusals decided by the second provider | 4 of 4 | FOUND, FOUND, FOUND, NOT_FOUND |
