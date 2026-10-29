# A4.1 — The retrieval pipeline, verified against the code

Verified 2026-09-21 against `scripts/web_search.py`, `scripts/test_LLM.py` (the
harness that produced the six published models' runs) and `scripts/run_cusp.py`
(the harness for Claude Sonnet 5, GPT-5.6 Sol and the new LLaMA 3.3 retrieval
run), plus the inference logs of every stored retrieval run (repo git SHA
`faa03ec`; the archived copy of `web_search.py` in
`archive/scripts/evaluate_models_misc/` is identical to the one used, modulo
whitespace). Line numbers refer to the current files.

## Two mechanisms were used, and the response must distinguish them

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

The cutoffs above were confirmed from the run logs (`Web search: enabled
(model=…, cutoff=YYYY-MM)`) and independently from the retrieved arXiv
identifiers: in every WS+Cutoff run the latest arXiv month among retrieved URLs
equals the run's cutoff month, and no retrieved arXiv id postdates it (one
2023-11 id among 3,421 in GPT-4o's full-corpus run, a `page_age` error on
You.com's side). The native-tool runs were logged as `GPT-5.4 web search:
enabled (native Responses API, URLs saved per task)`.

**Consequence.** "No agent loop, model-written queries, web-search API" is true
of every WS+Cutoff run (the knowledge-gap arm for all models) and of the
unrestricted WS arm for DeepSeek R1, Claude Sonnet 4.5, Claude Sonnet 5 and
GPT-5.6 Sol. It is **not** true of the unrestricted WS arm for GPT-4o and
GPT-5.4, which used the provider's built-in search tool (an in-API tool loop:
the model decides when and what to search, the tool fetches and reads pages,
and the model may search repeatedly). This was the intended design for those
two models, but the response and the Methods must say so, and the forecasting
gap (WS − WS+Cutoff) for those two models compares two retrieval mechanisms.

## The You.com pipeline (`scripts/web_search.py`)

1. **Query generation — one LLM call per event, one query.**
   `web_search_get_context` (l. 211–245) collects the event's task prompts
   (binary, perturbed binary, MCQ, FRQ, date; `test_LLM.py` l. 1323–1333,
   `run_cusp.py` l. 262–269) and calls `_generate_combined_query` (l. 112–136),
   a single chat completion to the evaluated model itself (`model=model_name`,
   `test_LLM.py` l. 1052–1059; `run_cusp.py` l. 399) with a fixed prompt asking
   for "a single high-quality web search query" (temperature 0; for models that
   reject the parameter, the default). There is no per-task query: the same
   query serves all five tasks of the event.
2. **No iteration, no follow-up, no tool loop.** `_chat` (l. 13–83) makes one
   completion (with up to 3 retries on transport errors only); the query is
   sent once; the model never sees search results before answering and never
   issues another query. `web_search_get_context` contains no loop over
   queries or results. The `web_search_answer` function (l. 248–…) that would
   let the model answer from context in one shot is not used by either harness.
3. **Search API and cutoff.** `you.search.unified(query=…, freshness=
   "1900-01-01to<cutoff>")` (l. 231–233), a single call to the You.com Search
   API returning up to 10 web results. The cutoff is applied twice: as the
   `freshness` upper bound sent to the API, and client-side by dropping any
   result whose `page_age` is missing or ≥ the cutoff date (l. 147). For the
   WS+Cutoff condition the cutoff is the model's knowledge cutoff (first day of
   the month); for the You.com-based WS runs it is the run date (DeepSeek,
   Claude S4.5) or 2100-01-01 (`run_cusp.py` l. 395–396).
4. **Result filtering and formatting.** For each result, text = title +
   description + snippets, de-duplicated (l. 151–179); results with < 100
   characters or no query-word overlap are dropped (l. 181–189); the rest are
   sorted by text length, longest first (l. 193). `_build_context` (l. 198–208)
   keeps the first 8, truncates each to 1,200 characters, and formats them as
   `[Source i]\nTitle: …\nURL: …\n<text>`. The block (median ≈ 9–10 sources,
   ≈ 9–11k characters) is prepended verbatim to each task's user prompt as
   `[Web Search Context]\n<block>\n\n---\n\n<original prompt>` (`test_LLM.py`
   l. 1377, 1448, 1549, 1630, 1702; `run_cusp.py` l. 279). System prompts,
   decoding parameters and scoring are unchanged from the base condition.
5. **What is stored.** Per event: the query, the list of retrieved URLs and,
   in `run_cusp.py`, the number of sources and context length. The retrieved
   text itself is not stored; it can be reconstructed by re-issuing the stored
   query with the same `freshness` bound (a probe returned 9 of 10 identical
   URLs four months later).

## The native-tool path (`scripts/test_LLM.py`, GPT-4o and GPT-5.4 unrestricted WS only)

`get_gpt54_web_search_response` (l. 522–589) calls `client.responses.create`
with `tools=[{"type": "web_search"}]` and `tool_choice={"type": "web_search"}`
(l. 541–542), once per task call, with the task's system prompt as
`instructions` plus a suffix asking the model to list the URLs it relied on
(`_WS_SOURCES_SUFFIX`, l. 829–838; so the system prompt differs from the base
condition in this arm). The model chooses the queries; the provider's tool
fetches and reads pages; several searches can occur inside one response
(GPT-5.4 issued 1–12 queries per task call, median 3; GPT-4o always 1). Only the
queries and the cited URLs are stored (no result text), so the evidence the
model saw cannot be reconstructed exactly.

## Retrieval coverage of the stored runs (pinned 500 subset)

Events with at least one retrieved source: GPT-4o 500 / 496 (WS+Cutoff / WS),
GPT-5.4 500 / 500, DeepSeek R1 398 / 404, Claude S4.5 463 / 462, Sonnet 5
472 / 471, Sol 500 / 500, LLaMA 3.3 499 (WS+Cutoff only); Sonnet 5 on the
extension subset 82 / 83 of 86. Rows without retrieval are flagged
`retrieval_failed` and excluded from the gap decomposition.
