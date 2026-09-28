# A8 cost estimate (before running)

Calls per model: 500 events x 2 variants x 5 values of X = 5,000. Token counts are the per-call means of each model's stored base run (binary tasks) plus ~22 tokens for the injected sentence. Prices are assumed list prices, not verified against invoices.

| model | endpoint | in tok/call | out tok/call | price in/out per MTok | est. cost (5,000 calls) | est. wall time | price source |
|---|---|---|---|---|---|---|---|
| GPT-4o | gpt-4o via azure | 144 | 73 | $2.5/$10.0 | $5.45 | 0.2 h @ conc 8 | Azure OpenAI gpt-4o-2024-11-20 list price (calibration_study/prices.json), assumed |
| LLaMA 3.3 70B | Llama-3.3-70B-Instruct via azure | 169 | 76 | $0.71/$0.71 | $0.87 | 0.3 h @ conc 8 | Azure AI Foundry serverless list price (calibration_study/prices.json), assumed |
| GPT-OSS 20B | gpt-oss-20b via local | 204 | 328 | $0.0/$0.0 | $0.00 | 0.2 h @ conc 16 | served locally with vLLM on the lab GPUs (Azure deployment returns 404), no API cost |
| DeepSeek-R1 | not runnable |  |  |  |  |  | n/a — Azure deployment retired (HTTP 410 / 400 'dependent service'); cannot be run |
| Claude S4.5 | claude-sonnet-4-5 via anthropic | 155 | 116 | $3.0/$15.0 | $11.03 | 0.4 h @ conc 12 | Anthropic list price for Claude Sonnet 4.5, assumed |
| GPT-5.4 | gpt-5.4 via openai | 143 | 666 | $1.25/$10.0 | $34.18 | 1.0 h @ conc 10 | scripts/run_cusp.py PRICING, assumed; reasoning tokens bill as output |
| Claude Sonnet 5 | claude-sonnet-5 via anthropic | 211 | 124 | $2.0/$10.0 | $8.31 | 0.2 h @ conc 14 | scripts/run_cusp.py PRICING, assumed |
| GPT-5.6 Sol | gpt-5.6-sol via openai | 145 | 496 | $4.0/$20.0 | $52.47 | 1.7 h @ conc 10 | scripts/run_cusp.py PRICING, assumed; reasoning tokens bill as output |
| DeepSeek-V4-Pro | DeepSeek-V4-Pro via azure | 141 | 74 | $1.74/$3.48 | $2.51 | 0.5 h @ conc 8 | Azure AI Foundry price as listed by a third-party calculator (futureagi.com, verified Aug 2026), assumed |
| Claude Opus 4.8 | claude-opus-4-8 via anthropic | 211 | 105 | $5.0/$25.0 | $18.35 | 0.5 h @ conc 8 | platform.claude.com Opus 4.8 overview ($5/$25), assumed |

**Total (runnable models): $133.17** plus ~$0.02 already spent on ten one-line endpoint probes.
