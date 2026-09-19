# Token and cost accounting (actual, from raw JSONL usage fields)

Arms A and C reused stored outputs: zero new inference. Arm F is derived: zero inference.

| run | records | calls | input tokens | output tokens | USD (list price) |
|---|---|---|---|---|---|
| gpt4o_B1 | 1125 | 1125 | 199,770 | 94,827 | $1.45 |
| gpt4o_B2 | 1125 | 1125 | 202,020 | 98,374 | $1.49 |
| gpt4o_D | 1125 | 5625 | 847,875 | 343,888 | $5.56 |
| gpt4o_E | 1125 | 1125 | 206,805 | 113,555 | $1.65 |
| gpt54_B1 | 1125 | 1125 | 198,645 | 120,318 | $2.30 |
| gpt54_B2 | 1125 | 1125 | 200,895 | 119,047 | $2.29 |
| gpt54_D | 1125 | 5625 | 842,250 | 496,373 | $9.55 |
| gpt54_E | 1125 | 1125 | 205,680 | 120,758 | $2.33 |
| llama33_B1 | 1125 | 1125 | 227,354 | 91,570 | $0.23 |
| llama33_B2 | 1125 | 1125 | 230,729 | 90,204 | $0.23 |
| llama33_D | 1125 | 11250 | 1,981,929 | 785,547 | $1.96 |
| llama33_E | 1125 | 1125 | 234,824 | 89,857 | $0.23 |
