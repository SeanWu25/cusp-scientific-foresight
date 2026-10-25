# Coverage: items with a parsed answer / a confidence, per condition (1,000 items = 500 events x 2 variants)

| model | condition | parsed answer | with confidence | statuses |
|---|---|---|---|---|
| GPT-4o | base | 1000 | 1000 | graded 1000 |
| GPT-4o | 10 | 1000 | 1000 | ok 1000 |
| GPT-4o | 30 | 1000 | 1000 | ok 1000 |
| GPT-4o | 50 | 1000 | 1000 | ok 1000 |
| GPT-4o | 70 | 1000 | 1000 | ok 1000 |
| GPT-4o | 90 | 1000 | 1000 | ok 1000 |
| GPT-4o | **common set** | — | — | 500 events with both variants valid under every condition |
| LLaMA 3.3 70B | base | 994 | 949 | absent 6, graded 994 |
| LLaMA 3.3 70B | 10 | 1000 | 1000 | ok 1000 |
| LLaMA 3.3 70B | 30 | 1000 | 1000 | ok 1000 |
| LLaMA 3.3 70B | 50 | 1000 | 1000 | ok 1000 |
| LLaMA 3.3 70B | 70 | 1000 | 1000 | ok 1000 |
| LLaMA 3.3 70B | 90 | 1000 | 1000 | ok 1000 |
| LLaMA 3.3 70B | **common set** | — | — | 455 events with both variants valid under every condition |
| GPT-OSS 20B | base | 998 | 995 | graded 1000 |
| GPT-OSS 20B | 10 | 999 | 999 | ok 999, truncated 1 |
| GPT-OSS 20B | 30 | 998 | 998 | ok 998, truncated 2 |
| GPT-OSS 20B | 50 | 996 | 996 | ok 996, truncated 4 |
| GPT-OSS 20B | 70 | 996 | 994 | ok 996, truncated 4 |
| GPT-OSS 20B | 90 | 986 | 985 | ok 986, truncated 14 |
| GPT-OSS 20B | **common set** | — | — | 474 events with both variants valid under every condition |
| Claude S4.5 | base | 931 | 868 | absent 44, graded 944, skipped:API refusal 12 |
| Claude S4.5 | 10 | 857 | 848 | ok 857, refusal 137, unparseable 6 |
| Claude S4.5 | 30 | 865 | 860 | ok 865, refusal 134, unparseable 1 |
| Claude S4.5 | 50 | 864 | 862 | ok 864, refusal 134, unparseable 2 |
| Claude S4.5 | 70 | 865 | 859 | ok 865, refusal 132, unparseable 3 |
| Claude S4.5 | 90 | 862 | 856 | ok 862, refusal 136, unparseable 2 |
| Claude S4.5 | **common set** | — | — | 341 events with both variants valid under every condition |
| GPT-5.4 | base | 999 | 999 | graded 1000 |
| GPT-5.4 | 10 | 978 | 978 | ok 978, truncated 22 |
| GPT-5.4 | 30 | 986 | 986 | ok 986, truncated 14 |
| GPT-5.4 | 50 | 976 | 976 | ok 976, truncated 24 |
| GPT-5.4 | 70 | 988 | 988 | ok 988, truncated 12 |
| GPT-5.4 | 90 | 995 | 995 | ok 995, truncated 5 |
| GPT-5.4 | **common set** | — | — | 449 events with both variants valid under every condition |
| Claude Sonnet 5 | base | 973 | 966 | graded 973, skipped:API refusal 27 |
| Claude Sonnet 5 | 10 | 970 | 963 | ok 970, refusal 30 |
| Claude Sonnet 5 | 30 | 971 | 966 | ok 971, refusal 29 |
| Claude Sonnet 5 | 50 | 971 | 971 | ok 971, refusal 29 |
| Claude Sonnet 5 | 70 | 971 | 971 | ok 971, refusal 29 |
| Claude Sonnet 5 | 90 | 971 | 971 | ok 971, refusal 29 |
| Claude Sonnet 5 | **common set** | — | — | 461 events with both variants valid under every condition |
| GPT-5.6 Sol | base | 995 | 995 | graded 999, skipped:API refusal 1 |
| GPT-5.6 Sol | 10 | 1000 | 1000 | ok 1000 |
| GPT-5.6 Sol | 30 | 999 | 999 | ok 999, truncated 1 |
| GPT-5.6 Sol | 50 | 998 | 998 | ok 998, refusal 1, truncated 1 |
| GPT-5.6 Sol | 70 | 998 | 998 | ok 998, truncated 2 |
| GPT-5.6 Sol | 90 | 999 | 999 | ok 999, truncated 1 |
| GPT-5.6 Sol | **common set** | — | — | 493 events with both variants valid under every condition |
| DeepSeek-V4-Pro | base | 1000 | 1000 | graded 1000 |
| DeepSeek-V4-Pro | 10 | 1000 | 1000 | ok 1000 |
| DeepSeek-V4-Pro | 30 | 1000 | 1000 | ok 1000 |
| DeepSeek-V4-Pro | 50 | 1000 | 1000 | ok 1000 |
| DeepSeek-V4-Pro | 70 | 1000 | 1000 | ok 1000 |
| DeepSeek-V4-Pro | 90 | 1000 | 1000 | ok 1000 |
| DeepSeek-V4-Pro | **common set** | — | — | 500 events with both variants valid under every condition |
| Claude Opus 4.8 | base | 966 | 966 | graded 966, skipped:API refusal 34 |
| Claude Opus 4.8 | 10 | 969 | 969 | ok 969, refusal 31 |
| Claude Opus 4.8 | 30 | 971 | 971 | ok 971, refusal 29 |
| Claude Opus 4.8 | 50 | 968 | 968 | ok 968, refusal 32 |
| Claude Opus 4.8 | 70 | 969 | 969 | ok 969, refusal 31 |
| Claude Opus 4.8 | 90 | 968 | 968 | ok 968, refusal 32 |
| Claude Opus 4.8 | **common set** | — | — | 478 events with both variants valid under every condition |
