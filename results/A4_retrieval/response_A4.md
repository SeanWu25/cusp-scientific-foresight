# Response to Reviewer 2, concern C4 — retrieval experiments and knowledge access

> "adding web search changes several components simultaneously: retrieved context,
> prompt length, search policy, tool use, and the agent loop. An improvement
> therefore cannot be attributed specifically to the model's inability to access
> or use its parametric knowledge. ... Unrestricted web search can retrieve the
> realized paper or post-event evidence. ... A cleaner design would use fixed
> evidence packets generated independently of the tested model."

**This document is self-contained**: every table cited below is reproduced in
full. Underlying artefacts remain in `A4_1_pipeline/`, `A4_2_groundtruth_inclusion/`,
`A4_3_fixed_queries/`, `tables/` (JSON), `figures/`, `MANIFEST.json`,
`RAW_HASHES.txt`. Regenerate with the scripts in `scripts/` (see `README.md`).

**Summary of the three findings.**

1. **A4.1** — the knowledge-access arm (WS+Cutoff, every model) has no agent loop
   and no tool use: one model-written query, one search call, a fixed context
   block. The *unrestricted* arm for GPT-4o and GPT-5.4 is different — it used the
   provider's native search tool — so for those two models the forecasting gap
   compares two retrieval mechanisms, not two date ceilings. We state this
   explicitly and replace those numbers with the A4.3 fixed-evidence versions.
2. **A4.2** — unrestricted search retrieves the source paper or its stated outcome
   for **74–93%** of events, so that condition largely measures reading. Under
   the date ceiling the paper's own page is essentially never retrieved (0–3%),
   but **20–37%** of post-cutoff events still carry the realized outcome in the
   retrieved *snippets* — a page-level date filter passing newer content. The
   knowledge gap on post-cutoff events is therefore an upper bound.
3. **A4.3** — with queries written by a model outside the panel and identical
   evidence packets for every model, the **knowledge gaps are unchanged within
   noise**; GPT-4o's forecasting gap shrinks (MCQ 0.29 → 0.20), confirming part
   of it came from the tool loop. The snippet leak persists at **22–43%**, so it
   is a property of the search API, not of who writes the query.

---

## A4.1 — What the retrieval pipeline actually does

We thank the reviewer for pressing on this; the Methods did not describe the
retrieval pipeline precisely enough. The description below is verified against
`scripts/web_search.py`, `scripts/test_LLM.py`, `scripts/run_cusp.py` and the
inference logs of every stored retrieval run (repo git SHA `faa03ec`).

### Two mechanisms were used, and they must be distinguished

| run | search mechanism | queries | cutoff applied | predictions file |
|---|---|---|---|---|
| GPT-4o WS+Cutoff | You.com pipeline (below) | 1 per event, model-written | 2023-10 | `gpt_4o_web_search.jsonl` (full corpus) |
| GPT-4o WS (unrestricted) | **OpenAI Responses API `web_search` tool** | 1 per task call, tool-chosen | none | `gpt_4o_web_search_no_cutoff.jsonl` |
| GPT-5.4 WS+Cutoff | You.com pipeline | 1 per event | 2025-08 | `predictions_gpt-5.4_20260506_055209.jsonl` |
| GPT-5.4 WS (unrestricted) | **OpenAI Responses API `web_search` tool** | 1–12 per task call (median 3), tool-chosen | none | `gpt-5_4_web_search_subset.jsonl` |
| DeepSeek R1 WS+Cutoff | You.com pipeline | 1 per event | 2024-07 | `predictions_deepseek-r1_20260510_120503.jsonl` (backup tree) |
| DeepSeek R1 WS | You.com pipeline | 1 per event | 2026-05 (run date; effectively none) | `predictions_deepseek-r1_20260510_123317.jsonl` (backup tree) |
| Claude S4.5 WS+Cutoff | You.com pipeline | 1 per event | 2025-01 | `claude_500_web_constrained.jsonl` (backup tree) |
| Claude S4.5 WS | You.com pipeline | 1 per event | 2026-05 (run date) | `claude_web_search_full.jsonl` (backup tree) |
| Claude Sonnet 5 WS+Cutoff / WS | You.com pipeline | 1 per event | 2026-01 / none (2100-01-01) | `results_sonnet5_run1/raw/ws_cutoff_500.jsonl`, `ws_500.jsonl` |
| GPT-5.6 Sol WS+Cutoff / WS (re-run 2026-09-20) | You.com pipeline | 1 per event | 2026-02 / none | `results_sol_run1/raw/ws_cutoff_500.jsonl`, `ws_500.jsonl` |
| LLaMA 3.3 WS+Cutoff (generated 2026-09-20) | You.com pipeline | 1 per event | 2023-12 | `results_llama33_run1/raw/ws_cutoff_500.jsonl` |

Cutoffs were confirmed from the run logs (`Web search: enabled (model=…,
cutoff=YYYY-MM)`) and independently from the retrieved arXiv identifiers: in
every WS+Cutoff run the latest arXiv month among retrieved URLs equals the run's
cutoff month, and no retrieved arXiv id postdates it (one 2023-11 id among 3,421
in GPT-4o's full-corpus run, a `page_age` error on You.com's side).

### The You.com pipeline, step by step

1. **Query generation — one LLM call per event, one query.** The event's five
   task prompts are collected and a single chat completion to the evaluated model
   itself returns "a single high-quality web search query" (temperature 0 where
   accepted). There is no per-task query; the same query serves all five tasks.
2. **No iteration, no follow-up, no tool loop.** One completion, one query, sent
   once. The model never sees search results before answering and never issues
   another query.
3. **Search API and cutoff.** `you.search.unified(query=…,
   freshness="1900-01-01to<cutoff>")` — one call, up to 10 results. The cutoff is
   applied twice: as the `freshness` bound sent to the API, and client-side by
   dropping any result whose `page_age` is missing or ≥ the cutoff date.
4. **Filtering and formatting.** Text = title + description + snippets,
   de-duplicated; results under 100 characters or with no query-word overlap are
   dropped; the rest sorted longest-first. The first 8 are kept, each truncated to
   1,200 characters, formatted as `[Source i]…` and prepended verbatim to each
   task prompt. System prompts, decoding and scoring are unchanged from base.
5. **What is stored.** The query and the retrieved URLs (plus source count and
   context length in `run_cusp.py`). The retrieved *text* is not stored; it is
   reconstructed by re-issuing the stored query under the same bound (a probe
   returned 9 of 10 identical URLs four months later).

**The native-tool path** (GPT-4o and GPT-5.4 unrestricted WS only) calls
`client.responses.create` with `tools=[{"type": "web_search"}]` and
`tool_choice` forced, once per task call, with a system-prompt suffix asking the
model to list the URLs it used. The model chooses the queries, the provider's
tool fetches and reads pages, and several searches can occur inside one response
(GPT-5.4: 1–12 queries per call, median 3; GPT-4o: always 1). Only queries and
cited URLs are stored, so that evidence cannot be reconstructed exactly.

### Retrieval coverage of the stored runs (pinned 500 subset)

Events with at least one retrieved source: GPT-4o 500 / 496 (WS+Cutoff / WS),
GPT-5.4 500 / 500, DeepSeek R1 398 / 404, Claude S4.5 463 / 462, Sonnet 5
472 / 471, Sol 500 / 500, LLaMA 3.3 499 (WS+Cutoff only); Sonnet 5 on the
extension subset 82 / 83 of 86. Rows without retrieval are flagged
`retrieval_failed` and excluded from the gap decomposition.

**Consequence.** "No agent loop, model-written queries, web-search API" is true
of every WS+Cutoff run — the knowledge-gap arm for all models — and of the
unrestricted arm for DeepSeek R1, Claude Sonnet 4.5, Claude Sonnet 5 and GPT-5.6
Sol. It is **not** true of the unrestricted arm for GPT-4o and GPT-5.4. The one
component that changes between base and WS+Cutoff is the retrieved context (and
prompt length). A4.2 quantifies what that context contains; A4.3 removes the
model's own query writing from the comparison.

---

## A4.2 — How often does retrieval contain the ground truth?

We sampled every retrieved case for every model with stored retrieval results
(6,226 cases; seed 20260921): all 500 events for both conditions of GPT-4o,
GPT-5.4 and GPT-5.6 Sol, all 802/925 cases of DeepSeek R1 and Claude Sonnet 4.5,
1,000 of Sonnet 5's 1,108, and the 499 LLaMA 3.3 WS+Cutoff cases generated for
this response. For each case we reconstructed the evidence the model received
(the stored query re-issued to You.com under the run's date ceiling, passed
through the unmodified filtering and formatting code; for the two native-tool
runs, the fetched text of the URLs the tool cited) and asked an independent judge
(Claude Sonnet 5, effort low) whether any retrieved result was the source paper
itself or stated the realized outcome. We also record a deterministic
arXiv-id/DOI match against the URLs stored at run time. **Judged: 6,204 of 6,226**
(22 judge/retrieval errors excluded). 95% Wilson intervals.

### Inclusion rate per model and condition

| model | condition | mechanism | n | ground truth INCLUDED (judge) | of which: source paper / outcome stated | judge's matched URL was in the model's stored list | URL match (stored URLs, arXiv id / DOI) | stored↔live URL overlap |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | ws_cutoff | youcom | 497 | 24.7% [21.2%, 28.7%] | 84 / 39 | 9.1% (45) | 0.0% [0.0%, 0.8%] (n=497) | 35% |
| GPT-4o | ws | native | 498 | 88.0% [84.8%, 90.5%] | 414 / 24 | 87.8% (437) | 76.5% [72.6%, 80.0%] (n=498) | n/a |
| LLaMA 3.3 70B | ws_cutoff | youcom | 496 | 20.0% [16.7%, 23.7%] | 74 / 25 | 19.2% (95) | 0.0% [0.0%, 0.8%] (n=496) | 73% |
| DeepSeek R1 | ws_cutoff | youcom | 396 | 35.1% [30.6%, 39.9%] | 111 / 28 | 21.7% (86) | 7.3% [5.1%, 10.3%] (n=396) | 39% |
| DeepSeek R1 | ws | youcom | 402 | 81.3% [77.2%, 84.8%] | 299 / 28 | 57.5% (231) | 54.2% [49.3%, 59.0%] (n=402) | 39% |
| Claude S4.5 | ws_cutoff | youcom | 463 | 49.7% [45.1%, 54.2%] | 211 / 19 | 33.7% (156) | 19.9% [16.5%, 23.7%] (n=463) | 42% |
| Claude S4.5 | ws | youcom | 462 | 80.1% [76.2%, 83.5%] | 345 / 25 | 58.2% (269) | 56.3% [51.7%, 60.7%] (n=462) | 41% |
| GPT-5.4 | ws_cutoff | youcom | 497 | 70.4% [66.3%, 74.3%] | 324 / 26 | 50.9% (253) | 41.0% [36.8%, 45.4%] (n=497) | 40% |
| GPT-5.4 | ws | native | 498 | 93.0% [90.4%, 94.9%] | 440 / 23 | 93.0% (463) | 78.7% [74.9%, 82.1%] (n=498) | n/a |
| Claude Sonnet 5 | ws_cutoff | youcom | 499 | 63.7% [59.4%, 67.8%] | 288 / 30 | 61.3% (306) | 43.7% [39.4%, 48.1%] (n=499) | 70% |
| Claude Sonnet 5 | ws | youcom | 501 | 73.5% [69.4%, 77.1%] | 331 / 37 | 70.3% (352) | 56.1% [51.7%, 60.4%] (n=501) | 70% |
| GPT-5.6 Sol | ws_cutoff | youcom | 497 | 80.7% [77.0%, 83.9%] | 371 / 30 | 78.5% (390) | 54.7% [50.3%, 59.1%] (n=497) | 79% |
| GPT-5.6 Sol | ws | youcom | 498 | 84.9% [81.5%, 87.8%] | 393 / 30 | 82.5% (411) | 57.8% [53.5%, 62.1%] (n=498) | 78% |

### Split by whether the event predates the model's cutoff

Post-cutoff inclusion under a date ceiling is leakage through the filter.

| model | pre-cutoff: judge INCLUDED | pre-cutoff: URL match | post-cutoff: judge INCLUDED | post-cutoff: judge match confirmed in stored list | post-cutoff: URL match | post-cutoff: matched domain (top) |
|---|---|---|---|---|---|---|
| GPT-4o | — | — | 24.7% [21.2%, 28.7%] (n=497) | 9.1% [6.8%, 11.9%] (n=497) | 0.0% [0.0%, 0.8%] (n=497) | researchgate.net 107, biorxiv.org 4, researchsquare.com 3 |
| LLaMA 3.3 70B | — | — | 20.0% [16.7%, 23.7%] (n=496) | 19.2% [15.9%, 22.8%] (n=496) | 0.0% [0.0%, 0.8%] (n=496) | researchgate.net 80, sciencedirect.com 4, biorxiv.org 3 |
| DeepSeek R1 | 79.0% [68.9%, 86.5%] (n=81) | 35.8% [26.2%, 46.7%] (n=81) | 23.8% [19.4%, 28.8%] (n=315) | 12.1% [8.9%, 16.1%] (n=315) | 0.0% [0.0%, 1.2%] (n=315) | researchgate.net 56, biorxiv.org 4, researchsquare.com 2 |
| Claude S4.5 | 83.8% [77.8%, 88.4%] (n=185) | 49.7% [42.6%, 56.9%] (n=185) | 27.0% [22.1%, 32.5%] (n=278) | 13.7% [10.1%, 18.2%] (n=278) | 0.0% [0.0%, 1.4%] (n=278) | researchgate.net 52, arxiv.org 8, biorxiv.org 7 |
| GPT-5.4 | 85.1% [81.0%, 88.4%] (n=355) | 57.2% [52.0%, 62.2%] (n=355) | 33.8% [26.5%, 41.9%] (n=142) | 12.7% [8.2%, 19.1%] (n=142) | 0.7% [0.1%, 3.9%] (n=142) | researchgate.net 23, arxiv.org 7, biorxiv.org 7 |
| Claude Sonnet 5 | 77.0% [72.6%, 81.0%] (n=383) | 56.7% [51.7%, 61.5%] (n=383) | 19.8% [13.6%, 28.0%] (n=116) | 19.8% [13.6%, 28.0%] (n=116) | 0.9% [0.2%, 4.7%] (n=116) | researchgate.net 9, biorxiv.org 5, arxiv.org 3 |
| GPT-5.6 Sol | 83.5% [79.9%, 86.6%] (n=467) | 58.0% [53.5%, 62.4%] (n=467) | 36.7% [21.9%, 54.5%] (n=30) | 36.7% [21.9%, 54.5%] (n=30) | 3.3% [0.6%, 16.7%] (n=30) | researchgate.net 5, arxiv.org 2, biorxiv.org 2 |

**Reading these three blocks:**

* *Unrestricted WS.* Ground truth present for **74–93%** of events (native tool:
  GPT-4o 88.0%, GPT-5.4 93.0%; single-query pipeline: 73.5–84.9%), and the source
  paper's own page is among the retrieved URLs for **54–79%**. The unrestricted
  condition largely measures the ability to read the answer. We retain it only as
  an upper reference.
* *WS+Cutoff, pre-cutoff events.* Inclusion **77.0–85.1%**, paper's own page
  **35.8–58.0%**. For events predating the cutoff this is recall with the source
  in hand — which is what the knowledge-gap arm is meant to measure.
* *WS+Cutoff, post-cutoff events — a leak we had not seen.* The source paper's
  own page is essentially never retrieved (**0.0–3.3%** by URL), so the date
  ceiling works at the page level. But the judge finds the realized outcome in
  the retrieved text for **19.8–36.7%** of post-cutoff events, of which
  **9.1–36.7%** are confirmed on the exact URLs the model received (the remainder
  cannot be confirmed because the search index has drifted since the runs).

### Where the leaked ground truth comes from

| domain of matched result | cases | of which URL in stored list |
|---|---|---|
| researchgate.net | 332 | 180 |
| biorxiv.org | 32 | 23 |
| arxiv.org | 23 | 16 |
| pubmed.ncbi.nlm.nih.gov | 10 | 8 |
| sciencedirect.com | 10 | 6 |
| researchsquare.com | 9 | 6 |
| medrxiv.org | 7 | 6 |
| linkedin.com | 4 | 4 |
| huggingface.co | 4 | 1 |
| discovery.researcher.life | 3 | 3 |
| salk.edu | 3 | 1 |
| academic.oup.com | 2 | 2 |

The mechanism is snippet-level: You.com dates a page by `page_age`, but the
snippets it returns for researchgate.net publication pages include the abstracts
of newer "related" papers, so a page dated 2022 can carry a 2026 paper's results
verbatim (`A4_2_groundtruth_inclusion/leak_example.json` reproduces one).
ResearchGate accounts for **332 of 439** post-cutoff inclusions; preprint or
PubMed pages of the same work under another identifier account for most of the
rest. A domain blocklist for aggregator pages, or content-level dating of
snippets, would be needed for a clean pre-cutoff condition.

### By task

Retrieval is per event and shared across that event's tasks; these rows differ
only through which events carry which task.

| model | condition | binary | perturbed | MCQ | FRQ | date |
|---|---|---|---|---|---|---|
| GPT-4o | ws_cutoff | 29.6% [24.7%, 35.0%] (n=294) | 24.3% [20.3%, 28.8%] (n=391) | 25.0% [21.1%, 29.3%] (n=432) | 24.8% [20.9%, 29.2%] (n=423) | 29.6% [24.7%, 35.0%] (n=294) |
| GPT-4o | ws | 93.9% [90.6%, 96.1%] (n=295) | 88.0% [84.4%, 90.9%] (n=392) | 89.8% [86.6%, 92.3%] (n=433) | 89.2% [85.8%, 91.8%] (n=424) | 93.9% [90.6%, 96.1%] (n=295) |
| LLaMA 3.3 70B | ws_cutoff | 23.1% [18.7%, 28.3%] (n=294) | 19.2% [15.6%, 23.4%] (n=391) | 19.5% [16.0%, 23.5%] (n=431) | 20.6% [17.0%, 24.7%] (n=422) | 23.1% [18.7%, 28.3%] (n=294) |
| DeepSeek R1 | ws_cutoff | 43.3% [37.1%, 49.8%] (n=233) | 33.7% [28.6%, 39.1%] (n=309) | 35.3% [30.4%, 40.4%] (n=346) | 33.5% [28.7%, 38.7%] (n=337) | 43.3% [37.1%, 49.8%] (n=233) |
| DeepSeek R1 | ws | 87.0% [82.1%, 90.7%] (n=238) | 80.6% [75.9%, 84.6%] (n=320) | 82.0% [77.6%, 85.7%] (n=350) | 81.9% [77.6%, 85.6%] (n=349) | 87.0% [82.1%, 90.7%] (n=238) |
| Claude S4.5 | ws_cutoff | 58.1% [52.2%, 63.7%] (n=279) | 49.2% [44.1%, 54.3%] (n=366) | 50.4% [45.5%, 55.2%] (n=403) | 49.2% [44.4%, 54.1%] (n=398) | 58.1% [52.2%, 63.7%] (n=279) |
| Claude S4.5 | ws | 82.0% [77.1%, 86.1%] (n=278) | 78.6% [74.1%, 82.5%] (n=365) | 80.1% [76.0%, 83.8%] (n=403) | 81.4% [77.2%, 84.9%] (n=397) | 82.0% [77.1%, 86.1%] (n=278) |
| GPT-5.4 | ws_cutoff | 78.2% [73.2%, 82.6%] (n=294) | 70.8% [66.2%, 75.1%] (n=391) | 70.6% [66.1%, 74.7%] (n=432) | 71.6% [67.2%, 75.7%] (n=423) | 78.2% [73.2%, 82.6%] (n=294) |
| GPT-5.4 | ws | 94.2% [91.0%, 96.4%] (n=295) | 91.8% [88.7%, 94.2%] (n=392) | 94.0% [91.3%, 95.9%] (n=433) | 95.3% [92.8%, 96.9%] (n=424) | 94.2% [91.0%, 96.4%] (n=295) |
| Claude Sonnet 5 | ws_cutoff | 73.3% [67.8%, 78.1%] (n=281) | 62.5% [57.7%, 67.1%] (n=403) | 64.1% [59.4%, 68.5%] (n=423) | 64.5% [59.9%, 68.9%] (n=431) | 73.3% [67.8%, 78.1%] (n=281) |
| Claude Sonnet 5 | ws | 78.1% [72.8%, 82.5%] (n=278) | 73.6% [69.1%, 77.7%] (n=398) | 73.8% [69.5%, 77.8%] (n=428) | 74.0% [69.6%, 77.9%] (n=430) | 78.1% [72.8%, 82.5%] (n=278) |
| GPT-5.6 Sol | ws_cutoff | 85.4% [80.9%, 89.0%] (n=294) | 79.5% [75.3%, 83.2%] (n=391) | 80.8% [76.8%, 84.2%] (n=432) | 82.0% [78.1%, 85.4%] (n=423) | 85.4% [80.9%, 89.0%] (n=294) |
| GPT-5.6 Sol | ws | 89.2% [85.1%, 92.2%] (n=295) | 83.9% [80.0%, 87.2%] (n=392) | 85.7% [82.1%, 88.7%] (n=433) | 86.8% [83.2%, 89.7%] (n=424) | 89.2% [85.1%, 92.2%] (n=295) |

### By domain

| model | condition | Artificial Intelligence | Biology | Chemistry | Environmental Science | Materials Science | Medicine | Neuroscience | Other | Physics |
|---|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | ws_cutoff | 2.5% [0.9%, 7.1%] (n=120) | 38.8% [30.8%, 47.4%] (n=129) | 52.4% [32.4%, 71.7%] (n=21) | 28.0% [14.3%, 47.6%] (n=25) | 30.8% [18.6%, 46.4%] (n=39) | 13.2% [7.3%, 22.6%] (n=76) | 16.7% [8.3%, 30.6%] (n=42) | 57.1% [25.0%, 84.2%] (n=7) | 50.0% [34.8%, 65.2%] (n=38) |
| GPT-4o | ws | 76.7% [68.3%, 83.3%] (n=120) | 90.0% [83.6%, 94.1%] (n=130) | 100.0% [84.5%, 100.0%] (n=21) | 92.0% [75.0%, 97.8%] (n=25) | 97.4% [86.8%, 99.5%] (n=39) | 84.2% [74.4%, 90.7%] (n=76) | 92.9% [81.0%, 97.5%] (n=42) | 100.0% [64.6%, 100.0%] (n=7) | 97.4% [86.5%, 99.5%] (n=38) |
| LLaMA 3.3 70B | ws_cutoff | 2.5% [0.9%, 7.1%] (n=120) | 30.2% [23.0%, 38.6%] (n=129) | 47.6% [28.3%, 67.6%] (n=21) | 24.0% [11.5%, 43.4%] (n=25) | 17.9% [9.0%, 32.7%] (n=39) | 17.3% [10.4%, 27.4%] (n=75) | 14.3% [6.7%, 27.8%] (n=42) | 14.3% [2.6%, 51.3%] (n=7) | 36.8% [23.4%, 52.7%] (n=38) |
| DeepSeek R1 | ws_cutoff | 8.2% [4.2%, 15.4%] (n=97) | 54.5% [44.8%, 63.8%] (n=101) | 23.5% [9.6%, 47.3%] (n=17) | 35.3% [17.3%, 58.7%] (n=17) | 33.3% [19.8%, 50.4%] (n=33) | 28.1% [18.6%, 40.1%] (n=64) | 34.4% [20.4%, 51.7%] (n=32) | 66.7% [30.0%, 90.3%] (n=6) | 75.9% [57.9%, 87.8%] (n=29) |
| DeepSeek R1 | ws | 64.5% [54.4%, 73.5%] (n=93) | 90.7% [83.8%, 94.9%] (n=108) | 93.8% [71.7%, 98.9%] (n=16) | 81.0% [60.0%, 92.3%] (n=21) | 78.6% [60.5%, 89.8%] (n=28) | 76.9% [65.4%, 85.5%] (n=65) | 90.3% [75.1%, 96.7%] (n=31) | 100.0% [61.0%, 100.0%] (n=6) | 91.2% [77.0%, 97.0%] (n=34) |
| Claude S4.5 | ws_cutoff | 29.2% [21.8%, 37.8%] (n=120) | 64.9% [55.8%, 73.1%] (n=114) | 57.1% [36.5%, 75.5%] (n=21) | 50.0% [31.4%, 68.6%] (n=24) | 52.6% [37.3%, 67.5%] (n=38) | 40.3% [29.0%, 52.7%] (n=62) | 41.0% [27.1%, 56.6%] (n=39) | 71.4% [35.9%, 91.8%] (n=7) | 81.6% [66.6%, 90.8%] (n=38) |
| Claude S4.5 | ws | 63.0% [54.1%, 71.2%] (n=119) | 92.1% [85.7%, 95.8%] (n=114) | 76.2% [54.9%, 89.4%] (n=21) | 83.3% [64.1%, 93.3%] (n=24) | 73.7% [58.0%, 85.0%] (n=38) | 80.6% [69.1%, 88.6%] (n=62) | 89.7% [76.4%, 95.9%] (n=39) | 100.0% [64.6%, 100.0%] (n=7) | 89.5% [75.9%, 95.8%] (n=38) |
| GPT-5.4 | ws_cutoff | 55.8% [46.9%, 64.4%] (n=120) | 81.4% [73.8%, 87.2%] (n=129) | 71.4% [50.0%, 86.2%] (n=21) | 60.0% [40.7%, 76.6%] (n=25) | 71.8% [56.2%, 83.5%] (n=39) | 61.8% [50.6%, 71.9%] (n=76) | 78.6% [64.1%, 88.3%] (n=42) | 100.0% [64.6%, 100.0%] (n=7) | 86.8% [72.7%, 94.2%] (n=38) |
| GPT-5.4 | ws | 85.0% [77.5%, 90.3%] (n=120) | 95.4% [90.3%, 97.9%] (n=130) | 100.0% [84.5%, 100.0%] (n=21) | 84.0% [65.3%, 93.6%] (n=25) | 94.9% [83.1%, 98.6%] (n=39) | 97.4% [90.9%, 99.3%] (n=76) | 97.6% [87.7%, 99.6%] (n=42) | 100.0% [64.6%, 100.0%] (n=7) | 94.7% [82.7%, 98.5%] (n=38) |
| Claude Sonnet 5 | ws_cutoff | 56.6% [47.7%, 65.0%] (n=122) | 73.6% [65.1%, 80.6%] (n=121) | 54.5% [34.7%, 73.1%] (n=22) | 71.4% [52.9%, 84.7%] (n=28) | 56.5% [42.2%, 69.8%] (n=46) | 51.5% [39.8%, 62.9%] (n=68) | 68.3% [53.0%, 80.4%] (n=41) | 54.5% [28.0%, 78.7%] (n=11) | 82.5% [68.0%, 91.3%] (n=40) |
| Claude Sonnet 5 | ws | 59.2% [50.2%, 67.5%] (n=120) | 79.3% [71.3%, 85.6%] (n=121) | 66.7% [45.4%, 82.8%] (n=21) | 88.9% [71.9%, 96.1%] (n=27) | 69.0% [54.0%, 80.9%] (n=42) | 76.7% [65.8%, 84.9%] (n=73) | 75.6% [60.7%, 86.2%] (n=41) | 63.6% [35.4%, 84.8%] (n=11) | 88.9% [76.5%, 95.2%] (n=45) |
| GPT-5.6 Sol | ws_cutoff | 69.2% [60.4%, 76.7%] (n=120) | 88.4% [81.7%, 92.8%] (n=129) | 81.0% [60.0%, 92.3%] (n=21) | 84.0% [65.3%, 93.6%] (n=25) | 84.6% [70.3%, 92.8%] (n=39) | 72.4% [61.4%, 81.2%] (n=76) | 83.3% [69.4%, 91.7%] (n=42) | 100.0% [64.6%, 100.0%] (n=7) | 94.7% [82.7%, 98.5%] (n=38) |
| GPT-5.6 Sol | ws | 80.0% [72.0%, 86.2%] (n=120) | 86.9% [80.1%, 91.7%] (n=130) | 81.0% [60.0%, 92.3%] (n=21) | 88.0% [70.0%, 95.8%] (n=25) | 82.1% [67.3%, 91.0%] (n=39) | 82.9% [72.9%, 89.7%] (n=76) | 88.1% [75.0%, 94.8%] (n=42) | 100.0% [64.6%, 100.0%] (n=7) | 94.7% [82.7%, 98.5%] (n=38) |

Figure: `figures/a42_inclusion.png` (`.pdf`).

---

## A4.3 — Fixed evidence packets from queries written outside the panel

We implemented the design the reviewer proposes. For every event in the pinned
500-event subset, **Claude Opus 4.8 — a model outside the evaluated panel —**
wrote one search query with the same instruction the pipeline uses (gpt-5.4-mini
for the 42 biomedical events Opus declined; every query is stored with its author
in `A4_3_fixed_queries/queries.jsonl`). Each query was issued once to You.com
under seven date ceilings (one per evaluated model's cutoff, plus unrestricted)
and filtered and formatted by the unmodified pipeline code, so **every evaluated
model received the identical evidence packet for a given ceiling**
(`A4_3_fixed_queries/evidence/`).

Six models with live deployments (GPT-4o, GPT-5.4, LLaMA 3.3 70B, Claude Sonnet
4.5, Claude Sonnet 5, GPT-5.6 Sol) were run on these packets under their own
cutoff ceiling and unrestricted, with the unmodified harness and their original
decoding settings, and scored with the frozen scoring code. DeepSeek R1 could not
be included (deployment retired). Gaps follow
`run_evaluation/gap_decomposition.py`: knowledge gap = WS+Cutoff − base,
forecasting gap = WS − WS+Cutoff, post-cutoff events, ids shared by every
condition, retrieval-failed rows dropped, paired normal 95% CIs; the
between-setup difference carries a 10k item bootstrap and two-sided p. FRQ is
omitted (rubric under revision at the time of this run). Original-setup numbers
are recomputed on exactly the same events, so they can differ slightly from the
published table. Cells with n < 20 are suppressed.

### Post-cutoff events (the paper's convention)

| model | task | n | knowledge gap: original | knowledge gap: fixed queries | fixed − original [CI] (p) | forecasting gap: original | forecasting gap: fixed | fixed − original [CI] (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | Binary | 291 | +0.292 [+0.230, +0.354] | +0.285 [+0.223, +0.348] | -0.007 [-0.065, +0.052] (0.86) | +0.354 [+0.285, +0.423] | +0.361 [+0.300, +0.422] | +0.007 [-0.072, +0.086] (0.89) |
| GPT-4o | Binary (pert.) | 388 | -0.165 [-0.213, -0.117] | -0.180 [-0.235, -0.126] | -0.015 [-0.064, +0.031] (0.55) | +0.106 [+0.049, +0.162] | -0.137 [-0.191, -0.083] | -0.242 [-0.314, -0.170] (0) |
| GPT-4o | MCQ | 426 | +0.045 [-0.001, +0.091] | +0.094 [+0.046, +0.142] | +0.049 [+0.005, +0.094] (0.035) | +0.286 [+0.236, +0.337] | +0.197 [+0.152, +0.243] | -0.089 [-0.148, -0.031] (0.0026) |
| GPT-4o | Date (0-1) | 291 | +0.203 [+0.169, +0.237] | +0.173 [+0.140, +0.206] | -0.030 [-0.061, +0.002] (0.065) | +0.235 [+0.175, +0.295] | +0.132 [+0.085, +0.179] | -0.103 [-0.172, -0.035] (0.0044) |
| GPT-5.4 | Binary | 58 | +0.172 [+0.035, +0.310] | +0.224 [+0.079, +0.369] | +0.052 [-0.034, +0.138] (0.33) | +0.172 [+0.063, +0.282] | +0.103 [+0.011, +0.196] | -0.069 [-0.172, +0.034] (0.25) |
| GPT-5.4 | Binary (pert.) | 99 | -0.162 [-0.266, -0.057] | -0.192 [-0.296, -0.088] | -0.030 [-0.111, +0.051] (0.54) | +0.000 [-0.105, +0.105] | +0.071 [-0.036, +0.177] | +0.071 [-0.081, +0.222] (0.39) |
| GPT-5.4 | MCQ | 104 | -0.048 [-0.130, +0.034] | -0.058 [-0.142, +0.026] | -0.010 [-0.087, +0.067] (0.9) | +0.154 [+0.075, +0.233] | +0.135 [+0.059, +0.211] | -0.019 [-0.106, +0.077] (0.75) |
| GPT-5.4 | Date (0-1) | 58 | +0.070 [-0.009, +0.150] | +0.085 [+0.000, +0.170] | +0.015 [-0.046, +0.076] (0.65) | +0.436 [+0.323, +0.550] | +0.373 [+0.281, +0.466] | -0.063 [-0.176, +0.055] (0.3) |
| LLaMA 3.3 70B | Binary | 294 | -0.068 [-0.107, -0.029] | -0.054 [-0.093, -0.016] | +0.014 [-0.027, +0.054] (0.57) | — | +0.085 [+0.046, +0.124] | — |
| LLaMA 3.3 70B | Binary (pert.) | 393 | +0.074 [+0.032, +0.116] | +0.089 [+0.047, +0.131] | +0.015 [-0.025, +0.059] (0.51) | — | +0.005 [-0.038, +0.048] | — |
| LLaMA 3.3 70B | MCQ | 432 | +0.044 [-0.004, +0.092] | +0.093 [+0.043, +0.142] | +0.049 [+0.009, +0.088] (0.02) | — | +0.243 [+0.199, +0.287] | — |
| LLaMA 3.3 70B | Date (0-1) | 294 | -0.020 [-0.056, +0.015] | -0.041 [-0.080, -0.001] | -0.020 [-0.050, +0.009] (0.19) | — | +0.105 [+0.063, +0.148] | — |
| Claude S4.5 | Binary | 130 | +0.077 [-0.018, +0.172] | +0.115 [+0.018, +0.213] | +0.038 [-0.046, +0.123] (0.41) | +0.438 [+0.345, +0.532] | +0.438 [+0.350, +0.527] | +0.000 [-0.108, +0.108] (1) |
| Claude S4.5 | Binary (pert.) | 186 | -0.022 [-0.087, +0.044] | -0.054 [-0.122, +0.014] | -0.032 [-0.086, +0.022] (0.28) | -0.129 [-0.193, -0.065] | -0.108 [-0.173, -0.043] | +0.022 [-0.054, +0.097] (0.64) |
| Claude S4.5 | MCQ | 185 | -0.016 [-0.083, +0.050] | -0.016 [-0.094, +0.061] | +0.000 [-0.065, +0.065] (1) | +0.124 [+0.059, +0.190] | +0.119 [+0.046, +0.192] | -0.005 [-0.086, +0.076] (0.95) |
| Claude S4.5 | Date (0-1) | 128 | +0.016 [-0.037, +0.070] | -0.024 [-0.081, +0.032] | -0.041 [-0.096, +0.014] (0.15) | +0.118 [+0.043, +0.193] | +0.235 [+0.155, +0.315] | +0.117 [+0.014, +0.218] (0.022) |
| Claude Sonnet 5 | Binary | 14 | suppressed (n<20) | | | | | |
| Claude Sonnet 5 | Binary (pert.) | 24 | -0.083 [-0.247, +0.080] | -0.125 [-0.260, +0.010] | -0.042 [-0.208, +0.125] (0.82) | -0.125 [-0.304, +0.054] | -0.042 [-0.185, +0.102] | +0.083 [-0.125, +0.292] (0.51) |
| Claude Sonnet 5 | MCQ | 24 | +0.042 [-0.102, +0.185] | +0.000 [-0.167, +0.167] | -0.042 [-0.125, +0.000] (0.71) | +0.000 [+0.000, +0.000] | +0.083 [-0.030, +0.196] | +0.083 [+0.000, +0.208] (0.24) |
| Claude Sonnet 5 | Date (0-1) | 14 | suppressed (n<20) | | | | | |
| GPT-5.6 Sol | Binary | 1 | suppressed (n<20) | | | | | |
| GPT-5.6 Sol | Binary (pert.) | 4 | suppressed (n<20) | | | | | |
| GPT-5.6 Sol | MCQ | 3 | suppressed (n<20) | | | | | |
| GPT-5.6 Sol | Date (0-1) | 1 | suppressed (n<20) | | | | | |

**Knowledge gap (WS+Cutoff − base).** Replacing the model's own query with an
external one leaves the knowledge gap unchanged within noise for every model and
task with n ≥ 20. The only two differences whose CI excludes zero are MCQ for
GPT-4o (**+0.049 [+0.005, +0.094]**, p = 0.035) and LLaMA 3.3 (**+0.049
[+0.009, +0.088]**, p = 0.020) — i.e. the external queries retrieve slightly
*more*, not less. **The direction and size of the knowledge gap reported in the
paper do not depend on the evaluated model writing its own query.**

**Forecasting gap (WS − WS+Cutoff).** For Claude Sonnet 4.5 and GPT-5.4, whose
unrestricted runs used the same single-query pipeline, the fixed-evidence gap
matches the original within noise (Sonnet 4.5 binary +0.438 in both, difference
+0.000 [−0.108, +0.108]). For **GPT-4o, whose original unrestricted run used the
provider's native search tool**, the fixed-evidence gap is smaller on MCQ
(+0.197 vs +0.286, difference **−0.089 [−0.148, −0.031]**, p = 0.0026) and on
date (+0.132 vs +0.235, **−0.103 [−0.172, −0.035]**, p = 0.0044), and the
perturbed-binary gap changes sign (+0.106 → −0.137, **−0.242 [−0.314, −0.170]**).
Part of the published GPT-4o forecasting gap came from the tool loop, not from
post-cutoff information alone. We now report the fixed-evidence forecasting gaps
as the primary numbers and the native-tool runs as a separate upper reference.

**Statistical power.** Sonnet 5 and Sol have almost no post-cutoff events in the
pinned subset (≤ 24 and ≤ 4), so their post-cutoff cells are largely suppressed;
their all-events rows below show the recall-side gaps unchanged.

### All shared events (pre- and post-cutoff; supplementary)

Mostly recall for the late-cutoff models, included for completeness.

| model | task | n | knowledge gap: original | knowledge gap: fixed queries | fixed − original [CI] (p) | forecasting gap: original | forecasting gap: fixed | fixed − original [CI] (p) |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | Binary | 291 | +0.292 [+0.230, +0.354] | +0.285 [+0.223, +0.348] | -0.007 [-0.065, +0.052] (0.86) | +0.354 [+0.285, +0.423] | +0.361 [+0.300, +0.422] | +0.007 [-0.072, +0.086] (0.89) |
| GPT-4o | Binary (pert.) | 388 | -0.165 [-0.213, -0.117] | -0.180 [-0.235, -0.126] | -0.015 [-0.064, +0.031] (0.55) | +0.106 [+0.049, +0.162] | -0.137 [-0.191, -0.083] | -0.242 [-0.314, -0.170] (0) |
| GPT-4o | MCQ | 426 | +0.045 [-0.001, +0.091] | +0.094 [+0.046, +0.142] | +0.049 [+0.005, +0.094] (0.035) | +0.286 [+0.236, +0.337] | +0.197 [+0.152, +0.243] | -0.089 [-0.148, -0.031] (0.0026) |
| GPT-4o | Date (0-1) | 291 | +0.203 [+0.169, +0.237] | +0.173 [+0.140, +0.206] | -0.030 [-0.061, +0.002] (0.065) | +0.235 [+0.175, +0.295] | +0.132 [+0.085, +0.179] | -0.103 [-0.172, -0.035] (0.0044) |
| GPT-5.4 | Binary | 295 | +0.251 [+0.189, +0.312] | +0.261 [+0.200, +0.322] | +0.010 [-0.027, +0.044] (0.64) | +0.075 [+0.036, +0.114] | +0.031 [-0.003, +0.064] | -0.044 [-0.092, +0.000] (0.066) |
| GPT-5.4 | Binary (pert.) | 393 | -0.023 [-0.085, +0.039] | -0.005 [-0.067, +0.057] | +0.018 [-0.028, +0.061] (0.47) | -0.046 [-0.101, +0.009] | +0.033 [-0.011, +0.077] | +0.079 [+0.010, +0.148] (0.026) |
| GPT-5.4 | MCQ | 434 | +0.055 [+0.018, +0.092] | +0.058 [+0.020, +0.095] | +0.002 [-0.025, +0.030] (0.92) | +0.060 [+0.032, +0.088] | +0.032 [+0.007, +0.058] | -0.028 [-0.060, +0.007] (0.12) |
| GPT-5.4 | Date (0-1) | 295 | +0.368 [+0.316, +0.419] | +0.381 [+0.330, +0.432] | +0.014 [-0.024, +0.052] (0.48) | +0.105 [+0.051, +0.159] | +0.091 [+0.055, +0.128] | -0.013 [-0.071, +0.044] (0.65) |
| LLaMA 3.3 70B | Binary | 294 | -0.068 [-0.107, -0.029] | -0.054 [-0.093, -0.016] | +0.014 [-0.027, +0.054] (0.57) | — | +0.085 [+0.046, +0.124] | — |
| LLaMA 3.3 70B | Binary (pert.) | 393 | +0.074 [+0.032, +0.116] | +0.089 [+0.047, +0.131] | +0.015 [-0.025, +0.059] (0.51) | — | +0.005 [-0.038, +0.048] | — |
| LLaMA 3.3 70B | MCQ | 432 | +0.044 [-0.004, +0.092] | +0.093 [+0.043, +0.142] | +0.049 [+0.009, +0.088] (0.02) | — | +0.243 [+0.199, +0.287] | — |
| LLaMA 3.3 70B | Date (0-1) | 294 | -0.020 [-0.056, +0.015] | -0.041 [-0.080, -0.001] | -0.020 [-0.050, +0.009] (0.19) | — | +0.105 [+0.063, +0.148] | — |
| Claude S4.5 | Binary | 259 | +0.228 [+0.152, +0.303] | +0.247 [+0.175, +0.319] | +0.019 [-0.035, +0.073] (0.53) | +0.239 [+0.175, +0.303] | +0.259 [+0.200, +0.317] | +0.019 [-0.046, +0.085] (0.62) |
| Claude S4.5 | Binary (pert.) | 323 | -0.015 [-0.071, +0.040] | -0.022 [-0.080, +0.036] | -0.006 [-0.046, +0.034] (0.84) | -0.068 [-0.116, -0.020] | -0.065 [-0.110, -0.020] | +0.003 [-0.050, +0.056] (0.97) |
| Claude S4.5 | MCQ | 337 | +0.009 [-0.044, +0.061] | +0.000 [-0.058, +0.058] | -0.009 [-0.059, +0.042] (0.77) | +0.062 [+0.014, +0.111] | +0.059 [+0.008, +0.110] | -0.003 [-0.065, +0.062] (0.97) |
| Claude S4.5 | Date (0-1) | 257 | +0.126 [+0.072, +0.180] | +0.132 [+0.077, +0.186] | +0.005 [-0.046, +0.057] (0.82) | +0.101 [+0.044, +0.157] | +0.081 [+0.020, +0.141] | -0.020 [-0.098, +0.055] (0.61) |
| Claude Sonnet 5 | Binary | 280 | +0.275 [+0.206, +0.344] | +0.282 [+0.212, +0.353] | +0.007 [-0.043, +0.057] (0.83) | +0.014 [-0.035, +0.064] | +0.054 [+0.011, +0.096] | +0.039 [-0.021, +0.100] (0.23) |
| Claude Sonnet 5 | Binary (pert.) | 373 | +0.005 [-0.053, +0.063] | -0.011 [-0.066, +0.044] | -0.016 [-0.056, +0.024] (0.48) | +0.021 [-0.013, +0.055] | +0.008 [-0.024, +0.040] | -0.013 [-0.059, +0.032] (0.62) |
| Claude Sonnet 5 | MCQ | 395 | +0.061 [+0.030, +0.092] | +0.053 [+0.020, +0.087] | -0.008 [-0.030, +0.013] (0.57) | +0.010 [-0.006, +0.026] | +0.020 [+0.003, +0.037] | +0.010 [-0.013, +0.033] (0.44) |
| Claude Sonnet 5 | Date (0-1) | 282 | +0.314 [+0.265, +0.363] | +0.319 [+0.270, +0.368] | +0.005 [-0.026, +0.036] (0.8) | +0.022 [-0.012, +0.055] | +0.034 [+0.005, +0.062] | +0.012 [-0.026, +0.052] (0.55) |
| GPT-5.6 Sol | Binary | 295 | +0.034 [-0.013, +0.081] | +0.017 [-0.031, +0.064] | -0.017 [-0.051, +0.017] (0.38) | -0.007 [-0.041, +0.027] | +0.034 [+0.008, +0.060] | +0.041 [+0.000, +0.081] (0.052) |
| GPT-5.6 Sol | Binary (pert.) | 392 | +0.168 [+0.108, +0.229] | +0.143 [+0.086, +0.199] | -0.026 [-0.069, +0.018] (0.28) | +0.010 [-0.029, +0.050] | +0.003 [-0.028, +0.033] | -0.008 [-0.056, +0.041] (0.78) |
| GPT-5.6 Sol | MCQ | 426 | +0.059 [+0.026, +0.092] | +0.073 [+0.041, +0.105] | +0.014 [-0.007, +0.035] (0.21) | +0.014 [-0.005, +0.034] | +0.014 [+0.001, +0.027] | +0.000 [-0.021, +0.021] (1) |
| GPT-5.6 Sol | Date (0-1) | 296 | +0.415 [+0.364, +0.466] | +0.405 [+0.353, +0.458] | -0.009 [-0.041, +0.021] (0.54) | +0.018 [-0.014, +0.051] | +0.024 [+0.000, +0.048] | +0.006 [-0.030, +0.042] (0.75) |

### Ground-truth inclusion in the fixed evidence

Same judge and method as A4.2, applied to the fixed packets.

Judged 3480 of 3500 (bound × event) evidence packets. Post-bound inclusion is leakage through the date filter.

| bound (= cutoff of) | all events | pre-bound events | post-bound events | post-bound: URL match | post-bound leak source (top domains) |
|---|---|---|---|---|---|
| 2023-10-01 (GPT-4o) | 22.1% [18.7%, 26.0%] (n=497) | — | 22.1% [18.7%, 26.0%] (n=497) | 0.0% | researchgate.net 92, sciencedirect.com 4, arxiv.org 2 |
| 2023-12-01 (LLaMA 3.3 70B) | 24.6% [21.0%, 28.6%] (n=496) | — | 24.6% [21.0%, 28.6%] (n=496) | 0.0% | researchgate.net 96, biorxiv.org 5, sciencedirect.com 4 |
| 2025-01-01 (Claude S4.5) | 50.9% [46.5%, 55.3%] (n=497) | 84.4% [78.7%, 88.8%] (n=199) | 28.5% [23.7%, 33.9%] (n=298) | 0.0% | researchgate.net 48, biorxiv.org 11, arxiv.org 9 |
| 2025-08-01 (GPT-5.4) | 66.9% [62.6%, 70.9%] (n=498) | 83.1% [78.9%, 86.6%] (n=355) | 26.6% [20.0%, 34.4%] (n=143) | 0.7% | researchgate.net 17, biorxiv.org 6, arxiv.org 5 |
| 2026-01-01 (Claude Sonnet 5) | 78.7% [74.9%, 82.0%] (n=497) | 82.4% [78.7%, 85.7%] (n=450) | 42.6% [29.5%, 56.7%] (n=47) | 2.1% | researchgate.net 7, arxiv.org 6, biorxiv.org 2 |
| 2026-02-01 (GPT-5.6 Sol) | 79.3% [75.5%, 82.6%] (n=497) | 82.7% [79.0%, 85.8%] (n=467) | 26.7% [14.2%, 44.4%] (n=30) | 3.3% | biorxiv.org 2, researchgate.net 2, arxiv.org 2 |
| unrestricted (WS (all models)) | 81.5% [77.9%, 84.7%] (n=498) | — | 81.5% [77.9%, 84.7%] (n=498) | 21.3% | nature.com 177, arxiv.org 70, researchgate.net 32 |

Pre-ceiling inclusion is **82.4–84.4%** and post-ceiling inclusion is
**22.1–42.6%** (0.0–3.3% by URL) — the same ResearchGate-snippet channel as with
self-generated queries. **The leak is therefore a property of the search API's
page-level date filter, not of who writes the query.** The manuscript now reports
it as a limitation of any date-filtered web retrieval, with the measured rate.

Figure: `figures/a43_gaps.png` (`.pdf`); per-cell values in
`A4_3_fixed_queries/gaps.csv` and `tables/A4_3_gaps.json`.

---

## Proposed manuscript text

**Methods, "Knowledge-access conditions" (replacing the current two sentences):**

> *Proposed text.* "In the knowledge-access conditions the evaluated model first
> writes a single search query from the event's question texts; the query is sent
> once to the You.com Search API, for the WS+Cutoff condition with a date ceiling
> at the model's knowledge cutoff; the eight longest results (title, description
> and snippets, ≤ 1,200 characters each) are prepended verbatim to each task
> prompt. There is no iterative search, no tool use and no agent loop; prompts,
> decoding and scoring are otherwise identical to the base condition. For the
> unrestricted WS condition of GPT-4o and GPT-5.4 we instead used the provider's
> built-in web-search tool, which the model may invoke repeatedly within a
> response; forecasting gaps for these two models are therefore reported from the
> fixed-evidence replication (Supplementary Section S-R), in which every model
> receives the same evidence retrieved with queries written by a model outside the
> panel."

**Results, knowledge-access paragraph (addition):**

> *Proposed text.* "Two checks bound what the retrieval conditions measure. First,
> an independent judge finds the source paper or its stated outcome in the
> retrieved text for 74–93% of events under unrestricted search, so that condition
> largely measures reading rather than forecasting, and we use it only as an upper
> reference. Second, under the cutoff-restricted condition the source paper's own
> page is essentially never retrieved for post-cutoff events (0–3%), but snippet
> text from aggregator pages dated before the cutoff carries the realized outcome
> for 20–37% of them (9–37% confirmed on the exact URLs the models received); the
> knowledge gap on post-cutoff events is therefore an upper bound. Replacing each
> model's own query with one written by a model outside the panel, and giving
> every model the same evidence, leaves the knowledge gaps unchanged within
> confidence intervals (Supplementary Table S-R2) and reduces GPT-4o's forecasting
> gap on MCQ from 0.29 to 0.20."

**Limitations (addition):**

> *Proposed text.* "Date-filtered web retrieval is filtered at the page level;
> snippets of pages dated before a cutoff can contain later content. We measured
> this directly: the realized outcome appears in 20–37% of post-cutoff retrievals
> under self-written queries and 22–43% under queries written outside the panel,
> while the source paper's own page is retrieved for at most 3%. We report the
> measured leakage rate rather than treating the cutoff-restricted condition as
> clean."

---

## Corrections made when consolidating (2026-09-27)

Three summary ranges in the previous version of this response did not match the
tables they summarised. All three understated the leak; the tables themselves
were correct and are unchanged.

| claim | was | is | why |
|---|---|---|---|
| A4.2, post-cutoff inclusion confirmed on the model's stored URLs | 9–20% | **9.1–36.7%** | GPT-5.6 Sol's 36.7% (n = 30) was omitted from the upper end, although its 36.7% judge rate was included in the neighbouring range |
| A4.3, ground truth in the fixed evidence, post-ceiling | 22–29% | **22.1–42.6%** | the 2026-01-01 ceiling (Claude Sonnet 5, n = 47) sits at 42.6% and was omitted; n = 47 is above the n < 20 suppression threshold applied elsewhere, and the smaller n = 30 cell was included |
| proposed Results text, post-cutoff snippet leakage | 20–35% | **20–37%** | did not match the 20–37% stated in the same document |

`A4_3_fixed_queries/results.md` carried the same "22–29%" in its findings line
and has been corrected there too. No table, figure, stored output or scoring
artefact changed; only the prose summarising them.
