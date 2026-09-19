# Token and cost accounting (actual, from raw JSONL usage fields)

Arms A and C reused stored outputs: zero new inference. Arm F is derived: zero inference.

| run | records | calls | input tokens | output tokens | USD (list price) |
|---|---|---|---|---|---|
| gpt4o_B1 | 834 | 834 | 147,596 | 70,190 | $1.07 |
| gpt54_B1 | 677 | 677 | 118,294 | 73,040 | $1.39 |
| llama33_B1 | 1125 | 1125 | 227,354 | 91,570 | $0.23 |
| llama33_B2 | 103 | 103 | 21,293 | 8,081 | $0.02 |
| llama33_D | 3 | 30 | 4,950 | 2,099 | $0.01 |
| llama33_E | 3 | 3 | 591 | 266 | $0.00 |
