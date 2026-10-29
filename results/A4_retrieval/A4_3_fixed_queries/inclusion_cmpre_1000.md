# A4.3 — Fixed queries: ground-truth inclusion

## Ground-truth inclusion in the fixed-query evidence (same judge as A4.2)

Cutoff-month rule: an event published in the ceiling month counts as PRE-ceiling (post iff publication month > ceiling month).

Judged 6971 of 7000 (bound × event) evidence packets. Post-bound inclusion is leakage through the date filter.

| bound (= cutoff of) | all events | pre-bound events | post-bound events | post-bound: URL match | post-bound leak source (top domains) |
|---|---|---|---|---|---|
| 2023-10-01 (GPT-4o) | 18.4% [16.1%, 20.9%] (n=996) | — | 18.4% [16.1%, 20.9%] (n=996) | 0.0% | researchgate.net 162, sciencedirect.com 4, arxiv.org 2 |
| 2023-12-01 (LLaMA 3.3 70B) | 19.7% [17.3%, 22.3%] (n=995) | — | 19.7% [17.3%, 22.3%] (n=995) | 0.0% | researchgate.net 167, biorxiv.org 5, sciencedirect.com 4 |
| 2025-01-01 (Claude S4.5) | 34.6% [31.7%, 37.6%] (n=996) | 81.7% [76.0%, 86.3%] (n=213) | 21.8% [19.1%, 24.9%] (n=783) | 0.1% | researchgate.net 110, biorxiv.org 26, arxiv.org 13 |
| 2025-08-01 (GPT-5.4) | 46.6% [43.6%, 49.7%] (n=997) | 80.1% [75.7%, 83.8%] (n=376) | 26.4% [23.1%, 30.0%] (n=621) | 0.2% | researchgate.net 83, biorxiv.org 33, arxiv.org 17 |
| 2026-01-01 (Claude Sonnet 5) | 53.7% [50.6%, 56.8%] (n=996) | 81.8% [78.0%, 85.0%] (n=467) | 28.9% [25.2%, 32.9%] (n=529) | 0.2% | researchgate.net 66, biorxiv.org 38, arxiv.org 21 |
| 2026-02-01 (GPT-5.6 Sol) | 54.9% [51.8%, 57.9%] (n=995) | 79.9% [76.2%, 83.2%] (n=493) | 30.3% [26.4%, 34.4%] (n=502) | 0.2% | researchgate.net 64, biorxiv.org 37, arxiv.org 22 |
| unrestricted (WS (all models)) | 81.0% [78.5%, 83.3%] (n=996) | — | 81.0% [78.5%, 83.3%] (n=996) | 37.6% | nature.com 349, arxiv.org 133, science.org 53 |
