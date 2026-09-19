# Token and cost accounting (actual, from raw JSONL usage fields)

Arms A and C reused stored outputs: zero new inference. Arm F is derived: zero inference.

| run | records | calls | input tokens | output tokens | USD (list price) |
|---|---|---|---|---|---|
| gpt4o_B1 | 1125 | 1125 | 199,770 | 94,827 | $1.45 |
| gpt4o_B2 | 595 | 595 | 105,651 | 52,573 | $0.79 |
| gpt54_B1 | 1125 | 1125 | 198,645 | 120,318 | $2.30 |
| gpt54_B2 | 277 | 277 | 49,032 | 29,484 | $0.56 |
| llama33_B1 | 1125 | 1125 | 227,354 | 91,570 | $0.23 |
| llama33_B2 | 1125 | 1125 | 230,729 | 90,204 | $0.23 |
| llama33_D | 3 | 30 | 4,950 | 2,099 | $0.01 |
| llama33_E | 282 | 282 | 58,246 | 22,253 | $0.06 |
