# A4.3 — Fixed queries: ground-truth inclusion

## Ground-truth inclusion in the fixed-query evidence (same judge as A4.2)

Cutoff-month rule: an event published in the ceiling month counts as PRE-ceiling (post iff publication month > ceiling month).

Judged 3480 of 3500 (bound × event) evidence packets. Post-bound inclusion is leakage through the date filter.

| bound (= cutoff of) | all events | pre-bound events | post-bound events | post-bound: URL match | post-bound leak source (top domains) |
|---|---|---|---|---|---|
| 2023-10-01 (GPT-4o) | 22.1% [18.7%, 26.0%] (n=497) | — | 22.1% [18.7%, 26.0%] (n=497) | 0.0% | researchgate.net 92, sciencedirect.com 4, arxiv.org 2 |
| 2023-12-01 (LLaMA 3.3 70B) | 24.6% [21.0%, 28.6%] (n=496) | — | 24.6% [21.0%, 28.6%] (n=496) | 0.0% | researchgate.net 96, biorxiv.org 5, sciencedirect.com 4 |
| 2025-01-01 (Claude S4.5) | 50.9% [46.5%, 55.3%] (n=497) | 81.7% [76.0%, 86.3%] (n=213) | 27.8% [22.9%, 33.3%] (n=284) | 0.0% | researchgate.net 46, arxiv.org 9, biorxiv.org 9 |
| 2025-08-01 (GPT-5.4) | 66.9% [62.6%, 70.9%] (n=498) | 80.1% [75.7%, 83.8%] (n=376) | 26.2% [19.2%, 34.7%] (n=122) | 0.0% | researchgate.net 17, arxiv.org 4, biorxiv.org 4 |
| 2026-01-01 (Claude Sonnet 5) | 78.7% [74.9%, 82.0%] (n=497) | 81.8% [78.0%, 85.0%] (n=467) | 30.0% [16.7%, 47.9%] (n=30) | 0.0% | researchgate.net 3, biorxiv.org 2, medrxiv.org 1 |
| 2026-02-01 (GPT-5.6 Sol) | 79.3% [75.5%, 82.6%] (n=497) | 79.9% [76.2%, 83.2%] (n=493) | 0.0% [0.0%, 49.0%] (n=4) | 0.0% |  |
| unrestricted (WS (all models)) | 81.5% [77.9%, 84.7%] (n=498) | — | 81.5% [77.9%, 84.7%] (n=498) | 21.3% | nature.com 177, arxiv.org 70, researchgate.net 32 |
