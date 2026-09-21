# Reviewer 2, concern C4 — retrieval experiments and knowledge access

> "adding web search changes several components simultaneously: retrieved context,
> prompt length, search policy, tool use, and the agent loop. An improvement
> therefore cannot be attributed specifically to the model's inability to access
> or use its parametric knowledge. ... Unrestricted web search can retrieve the
> realized paper or post-event evidence. ... A cleaner design would use fixed
> evidence packets generated independently of the tested model."

**Status: analysis complete; ready for PI review.** Everything regenerates from
stored JSONL with the commands in `results/A4_retrieval/README.md`. Supporting
files: `results/A4_retrieval/A4_1_pipeline/pipeline_description.md` (code-verified,
with file/line references), `A4_2_groundtruth_inclusion/results.md`,
`A4_3_fixed_queries/results.md` and `gaps.csv`, `figures/a42_inclusion.png`,
`figures/a43_gaps.png`, `MANIFEST.json` (models, snapshot ids, seeds, prompt hashes,
token usage, costs, git SHA), `response_A4.md` (long-form response).

## 1. What we did

* **A4.1 — verified the pipeline against the code and every run log.** The
  knowledge-access condition (WS+Cutoff) for all models, and the unrestricted
  condition (WS) for DeepSeek R1, Claude Sonnet 4.5, Claude Sonnet 5 and GPT-5.6
  Sol, use one model-written query per event, one You.com Search API call with a
  date ceiling (the model's cutoff, or none), client-side filtering of results by
  page date, and the eight longest results (≤ 1,200 characters each) prepended
  verbatim to each task prompt. No iteration, no tool use, no agent loop; system
  prompts, decoding and scoring identical to base. The unrestricted WS runs of
  GPT-4o and GPT-5.4 instead used OpenAI's native web-search tool once per task
  call (the model chooses queries and may search repeatedly; GPT-5.4 median three
  queries per call). That was a deliberate strongest-baseline choice, but the
  forecasting gap for those two models compares two mechanisms, and the Methods
  must say so. The date ceiling itself is verified: in every WS+Cutoff run the
  latest arXiv identifier retrieved equals the cutoff month.
* **A4.2 — asked whether the retrieved evidence contains the ground truth.** All
  6,226 retrieved cases of the seven models with stored retrieval (all cases per
  model; 1,000 of Sonnet 5's 1,108; seed 20260921; the LLaMA 3.3 WS+Cutoff run
  did not exist and was generated). Evidence reconstructed by re-issuing the
  stored query under the run's date ceiling through the unmodified pipeline code
  (native-tool runs: fetched text of the cited URLs). An independent judge (Claude
  Sonnet 5) decided whether any result is the source paper itself or states the
  realized outcome; a deterministic arXiv-id/DOI match on the stored URLs and a
  "judge's URL was in the stored list" flag are reported alongside.
* **A4.3 — implemented the reviewer's design.** One query per event written by
  Claude Opus 4.8 (outside the panel; gpt-5.4-mini for 42 biomedical events Opus
  declined), issued once per date ceiling (one per evaluated model's cutoff, plus
  unrestricted), so every model received identical evidence for a given ceiling.
  Six models with live deployments (GPT-4o, GPT-5.4, LLaMA 3.3, Claude S4.5,
  Sonnet 5, Sol) were run on these packets with the unmodified harness and their
  original decoding, scored with the frozen scoring code, and the knowledge and
  forecasting gaps computed exactly as in the published table on the same
  events, with paired CIs and a bootstrap CI on the between-setup difference. The
  A4.2 inclusion check was repeated on the fixed evidence. DeepSeek R1 could not
  be included (deployment retired).

## 2. What we found

1. **Unrestricted search reads the answer.** The source paper or its stated
   outcome is in the retrieved evidence for 74–93% of events (native tool 88–93%;
   single-query pipeline 74–85%); the paper's own page is retrieved for 54–79%.
   The reviewer's reading is correct, and the manuscript now uses this condition
   only as an upper reference.
2. **The knowledge-access condition is recall on pre-cutoff events** (inclusion
   77–85%, own page retrieved for 36–58%), which is what it is meant to be.
3. **A leak we had not seen, now measured.** On post-cutoff events under
   WS+Cutoff the paper's own page is essentially never retrieved (0–3%), but the
   realized outcome appears in the retrieved text for 20–37% of events, 9–20%
   confirmed on the exact URLs the models received. You.com dates pages by
   `page_age`, and the snippets it returns for researchgate.net publication pages
   include the abstracts of newer "related" papers: a page dated 2022 carries a
   2026 paper's results verbatim (`leak_example.json`). ResearchGate accounts for
   332 of 439 post-cutoff inclusions. The knowledge gap on post-cutoff events is
   therefore an upper bound with a leakage component.
4. **Knowledge gaps do not depend on the model writing its own query.** Under
   fixed external queries every knowledge gap is unchanged within CI (GPT-4o
   binary +0.29 vs +0.29, perturbed −0.18 vs −0.17, date +0.17 vs +0.20; GPT-5.4
   and Claude S4.5 all four tasks); the two cells that move, MCQ for GPT-4o and
   LLaMA (+0.05, CIs exclude zero), move in favour of the external queries.
5. **Forecasting gaps hold where the mechanism was the same, and shrink where it
   was not.** Claude S4.5 and GPT-5.4: unchanged within CI (S4.5 binary +0.44 in
   both setups). GPT-4o, whose unrestricted run used the native tool: MCQ +0.20
   vs +0.29 (difference −0.09 [−0.15, −0.03]), date +0.13 vs +0.24 (−0.10
   [−0.17, −0.04]). Part of the published GPT-4o forecasting gap came from the
   tool loop.
6. **The leak is a property of the search pipeline, not of the query author.**
   The fixed evidence leaks the ground truth on 22–29% of post-ceiling packets
   through the same channel.
7. Sonnet 5 and Sol have ≤ 24 and ≤ 4 post-cutoff events in the pinned subset;
   their post-cutoff cells are suppressed (supplementary all-events rows show the
   recall-side gaps unchanged).

## 3. Suggested text for the response letter

We thank the reviewer for this concern, which led us to verify the retrieval
pipeline against the code and to run two additional analyses (Supplementary
Section S-R). The knowledge-access condition uses no agent loop: the model writes
one query, the query is sent once to a web-search API with a date ceiling at the
model's cutoff, and the returned snippets are prepended to the prompt; prompts,
decoding and scoring are otherwise identical to the base condition, so the only
component that changes is the retrieved context. We acknowledge that retrieval
quality affects the result and now measure it directly. For two models the
unrestricted condition used the provider's built-in search tool; the revised
Methods states this and we report those two forecasting gaps from the
fixed-evidence replication instead.

Two findings bound what the conditions measure. Under unrestricted search an
independent judge finds the source paper or its stated outcome in the retrieved
text for 74–93% of events, so we treat that condition as an upper reference on
reading rather than forecasting. Under the cutoff-restricted condition the source
paper is never retrieved for post-cutoff events, but snippet text from aggregator
pages dated before the cutoff carries the realized outcome for 20–35% of them; we
report this rate and describe the knowledge gap as an upper bound.

Following the reviewer's suggestion we replicated the experiment with fixed
evidence packets: queries written by a model outside the panel, identical
retrieved text for every model at a given date ceiling. Knowledge gaps are
unchanged within confidence intervals for every model and task, and forecasting
gaps are unchanged for the models whose unrestricted runs used the same pipeline;
GPT-4o's forecasting gap on MCQ falls from 0.29 to 0.20 once its native search
tool is removed. The fixed-evidence numbers are now the primary ones.

## 4. Manuscript changes proposed

* Methods, knowledge-access conditions: replace the description with the
  single-query pipeline (query, API call, ceiling, eight snippets prepended), state
  the native-tool exception for GPT-4o/GPT-5.4 unrestricted runs, and reference the
  fixed-evidence replication.
* Results: one paragraph giving the inclusion rates (unrestricted 74–93%;
  post-cutoff leakage 20–35%, 9–20% confirmed), the unchanged knowledge gaps under
  fixed queries, and the GPT-4o forecasting-gap correction; Supplementary tables
  S-R1 (inclusion by model × condition, pre/post cutoff), S-R2 (gaps original vs
  fixed with CIs), S-R3 (inclusion in fixed evidence by ceiling), figures S-R1–S-R2.
* Limitations: date-filtered web retrieval is filtered at page level; snippets of
  pages dated before a cutoff can contain later content; we report the measured
  rate rather than treating the condition as clean.

## 5. Housekeeping and caveats

* The GPT-4o and GPT-5.4 deployments on the Azure OpenAI resource used by the
  April base runs now return 404; the fixed-query runs used the Azure AI Foundry
  endpoint (snapshots `gpt-4o-2024-11-20`, `gpt-5.4-2026-03-05`, in the manifest).
* Two original retrieval prediction files (DeepSeek R1, Claude Sonnet 4.5) exist
  only in the pre-release backup tree; the manifest records their paths.
* Re-queried evidence overlaps the stored URLs 35–79% (the search index has
  drifted since April), which is why the "confirmed on stored URLs" floor is
  reported next to the judge rate.
* Cost at list prices: A4.2 ≈ $94 (judge $68, ≈ 5,200 search calls $26); A4.3 ≈
  $263 (model runs $200, inclusion judging $41, queries $4, 3,500 search calls
  $18). Total ≈ $360.
