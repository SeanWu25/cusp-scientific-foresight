# Post-cutoff N per dataset × model × task (h ≥ 1; base condition)

N = events with a scored item; binary counts events with either the original or the perturbed question.


## 1. original corpus (Jan 2024–Mar 2026), base — condition `base`

| model | cutoff | binary events (items) | MCQ events | date events | horizon range (months) |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 4285 (6408) | 4126 | 2573 | 3–29 (median 16) |
| LLaMA 3.3 70B | 2023-12 | 4250 (6359) | 4087 | 2731 | 1–27 (median 14) |
| GPT-OSS 20B | 2024-06 | 3500 (5191) | 3380 | 2126 | 1–21 (median 11) |
| DeepSeek R1 | 2024-07 | 3310 (4885) | 2818 | 1702 | 1–20 (median 10) |
| Claude S4.5 | 2025-01 | 2206 (3259) | 2129 | 1293 | 1–14 (median 7) |
| GPT-5.4 | 2025-08 | 1048 (1546) | 1014 | 612 | 1–7 (median 4) |
| Claude Sonnet 5 | 2026-01 | 209 (317) | 190 | 122 | 1–2 (median 1) |
| GPT-5.6 Sol | 2026-02 | 12 (17) | 7 | 5 | 1–1 (median 1) |
| DeepSeek-V4-Pro | 2026-04 | 0 (0) | 0 | 0 | — |
| Claude Opus 4.8 | 2026-01 | 209 (316) | 190 | 121 | 1–2 (median 1) |

## 2. extension (Apr–Aug 2026), base — condition `base`

| model | cutoff | binary events (items) | MCQ events | date events | horizon range (months) |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 680 (845) | 606 | 193 | 30–34 (median 32) |
| LLaMA 3.3 70B | 2023-12 | 680 (845) | 606 | 195 | 28–32 (median 30) |
| GPT-OSS 20B | 2024-06 | 680 (845) | 606 | 190 | 22–26 (median 24) |
| DeepSeek R1 | 2024-07 | 0 (0) | 0 | 0 | — |
| Claude S4.5 | 2025-01 | 573 (712) | 473 | 169 | 15–19 (median 17) |
| GPT-5.4 | 2025-08 | 680 (845) | 606 | 153 | 8–12 (median 10) |
| Claude Sonnet 5 | 2026-01 | 659 (821) | 569 | 193 | 3–7 (median 5) |
| GPT-5.6 Sol | 2026-02 | 680 (845) | 602 | 194 | 2–6 (median 4) |
| DeepSeek-V4-Pro | 2026-04 | 532 (661) | 478 | 153 | 1–4 (median 2) |
| Claude Opus 4.8 | 2026-01 | 653 (814) | 569 | 193 | 3–7 (median 5) |

## 4. merged original + extension, base — condition `base`

| model | cutoff | binary events (items) | MCQ events | date events | horizon range (months) |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 4965 (7253) | 4732 | 2766 | 3–34 (median 18) |
| LLaMA 3.3 70B | 2023-12 | 4930 (7204) | 4693 | 2926 | 1–32 (median 16) |
| GPT-OSS 20B | 2024-06 | 4180 (6036) | 3986 | 2316 | 1–26 (median 12) |
| DeepSeek R1 | 2024-07 | 3310 (4885) | 2818 | 1702 | 1–20 (median 10) |
| Claude S4.5 | 2025-01 | 2779 (3971) | 2602 | 1462 | 1–19 (median 8) |
| GPT-5.4 | 2025-08 | 1728 (2391) | 1620 | 765 | 1–12 (median 5) |
| Claude Sonnet 5 | 2026-01 | 868 (1138) | 759 | 315 | 1–7 (median 4) |
| GPT-5.6 Sol | 2026-02 | 692 (862) | 609 | 199 | 1–6 (median 4) |
| DeepSeek-V4-Pro | 2026-04 | 532 (661) | 478 | 153 | 1–4 (median 2) |
| Claude Opus 4.8 | 2026-01 | 862 (1130) | 759 | 314 | 1–7 (median 4) |

## 3. WS+Cutoff on the pinned 500 subset — condition `base`

| model | cutoff | binary events (items) | MCQ events | date events | horizon range (months) |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 456 (690) | 435 | 275 | 3–29 (median 17) |
| LLaMA 3.3 70B | 2023-12 | 454 (687) | 433 | 292 | 1–27 (median 15) |
| GPT-OSS 20B | 2024-06 | 0 (0) | 0 | 0 | — |
| DeepSeek R1 | 2024-07 | 342 (509) | 294 | 174 | 1–20 (median 10) |
| Claude S4.5 | 2025-01 | 241 (360) | 220 | 139 | 1–14 (median 6) |
| GPT-5.4 | 2025-08 | 108 (159) | 105 | 59 | 1–7 (median 4) |
| Claude Sonnet 5 | 2026-01 | 26 (37) | 23 | 14 | 1–2 (median 1) |
| GPT-5.6 Sol | 2026-02 | 1 (1) | 0 | 0 | 1–1 (median 1) |
| DeepSeek-V4-Pro | 2026-04 | 0 (0) | 0 | 0 | — |
| Claude Opus 4.8 | 2026-01 | 26 (37) | 22 | 13 | 1–2 (median 1) |

## 3. WS+Cutoff on the pinned 500 subset — condition `ws_cutoff`

| model | cutoff | binary events (items) | MCQ events | date events | horizon range (months) |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | 456 (690) | 435 | 295 | 3–29 (median 17) |
| LLaMA 3.3 70B | 2023-12 | 456 (690) | 435 | 296 | 1–27 (median 14) |
| GPT-OSS 20B | 2024-06 | 0 (0) | 0 | 0 | — |
| DeepSeek R1 | 2024-07 | 342 (511) | 327 | 193 | 1–20 (median 10) |
| Claude S4.5 | 2025-01 | 236 (353) | 216 | 110 | 1–14 (median 6) |
| GPT-5.4 | 2025-08 | 108 (159) | 105 | 59 | 1–7 (median 4) |
| Claude Sonnet 5 | 2026-01 | 26 (38) | 23 | 15 | 1–2 (median 1) |
| GPT-5.6 Sol | 2026-02 | 1 (1) | 0 | 0 | 1–1 (median 1) |
| DeepSeek-V4-Pro | 2026-04 | 0 (0) | 0 | 0 | — |
| Claude Opus 4.8 | 2026-01 | 26 (36) | 22 | 13 | 1–2 (median 1) |

## Cutoff verification (2026-09-20)

| model | cutoff used | source / status | sensitivity value |
|---|---|---|---|
| GPT-4o | 2023-10 | developers.openai.com models/gpt-4o: 'Oct 01, 2023 knowledge cutoff' (verified) | — |
| LLaMA 3.3 70B | 2023-12 | huggingface.co meta-llama/Llama-3.3-70B-Instruct model card: 'December 2023' (verified) | — |
| GPT-OSS 20B | 2024-06 | developers.openai.com models/gpt-oss-20b: 'Jun 01, 2024 knowledge cutoff' (verified) | — |
| DeepSeek R1 | 2024-07 | NOT VERIFIABLE: DeepSeek publishes no cutoff. 2024-07 follows the V3 system-prompt reports; the model self-reports Oct/Dec 2023. Sensitivity uses 2023-12. | 2023-12 |
| Claude S4.5 | 2025-01 | platform.claude.com models/sonnet-4-5: reliable knowledge cutoff Jan 2025 (used); training data cutoff Jul 2025 (sensitivity) | 2025-07 |
| GPT-5.4 | 2025-08 | developers.openai.com models/gpt-5.4: 'Aug 31, 2025 knowledge cutoff' (verified) | — |
| Claude Sonnet 5 | 2026-01 | platform.claude.com models/overview: reliable and training cutoff Jan 2026 (verified) | — |
| GPT-5.6 Sol | 2026-02 | developers.openai.com models/gpt-5.6-sol: 'Feb 16, 2026 knowledge cutoff' (verified; mid-month, so h=0 is excluded) | — |
| DeepSeek-V4-Pro | 2026-04 | April 2026, confirmed by the authors (2026-09-20); the vendor publishes no cutoff and the model was released 2026-04-24. Original corpus is entirely pre-cutoff for it. | — |
| Claude Opus 4.8 | 2026-01 | platform.claude.com models/opus-4-8/overview: reliable and training cutoff Jan 2026 (verified 2026-09-22). Same cutoff as Sonnet 5, so the two share a horizon grid. | — |

Notes: GPT-5.6 Sol's WS+Cutoff run was re-generated on 2026-09-20 after a fix to scripts/web_search.py (the original run had `web_search_error` on all 500 rows and no retrieval context). DeepSeek R1 has no extension run (deployment retired). DeepSeek-V4-Pro has no post-cutoff items on the original corpus.
