# Response to Reviewer 2, concern C4 — retrieval experiments and knowledge access

> "adding web search changes several components simultaneously: retrieved context,
> prompt length, search policy, tool use, and the agent loop. An improvement
> therefore cannot be attributed specifically to the model's inability to access
> or use its parametric knowledge. ... Unrestricted web search can retrieve the
> realized paper or post-event evidence. ... A cleaner design would use fixed
> evidence packets generated independently of the tested model."

Supporting material: `A4_1_pipeline/pipeline_description.md` (code-verified
description), `A4_2_groundtruth_inclusion/results.md`, `A4_3_fixed_queries/results.md`,
`tables/`, `figures/`, `MANIFEST.json`.

## A4.1 — What the retrieval pipeline actually does

We thank the reviewer for pressing on this; the Methods did not describe the
retrieval pipeline precisely enough, and we have verified the description below
against the code and the run logs of every retrieval run.

*Knowledge-access condition (WS+Cutoff), all models; and the unrestricted
condition (WS) for DeepSeek R1, Claude Sonnet 4.5, Claude Sonnet 5 and GPT-5.6
Sol.* There is no agent loop and no tool use by the model. For each event the
evaluated model writes a single search query from the event's question texts (one
chat completion with a fixed instruction), that query is sent once to the You.com
Search API with a date ceiling (the model's knowledge cutoff for WS+Cutoff; none
for WS), the returned results are filtered client-side to pages dated before the
ceiling, the eight longest matching results (title, description, snippets;
≤ 1,200 characters each) are formatted into a fixed block, and the block is
prepended verbatim to each task prompt. The model never sees results before
answering and never issues a second query; system prompts, decoding parameters
and scoring are identical to the base condition. The one component that changes
between base and WS+Cutoff is therefore the retrieved context (and, with it,
prompt length). We acknowledge that retrieval quality, i.e. what the single query
returns, affects the result; A4.2 quantifies how often the retrieved block
contains the ground truth and A4.3 removes the model's own query writing from the
comparison.

*Unrestricted condition (WS) for GPT-4o and GPT-5.4.* These two runs used the
provider's built-in web-search tool (OpenAI Responses API, `web_search`,
`tool_choice` forced), once per task call: the model chooses the queries, the
tool retrieves and reads pages, and several searches can occur inside one response
(GPT-5.4 issued a median of three queries per call). This was a deliberate choice
to give the strongest available unrestricted-search baseline for the two OpenAI
models, but it means that for these two models the forecasting gap
(WS − WS+Cutoff) compares two retrieval mechanisms, not only two date ceilings.
The revised Methods states this, and the A4.3 fixed-evidence design below
removes the difference: both conditions there use the same single-query
pipeline.

## A4.2 — How often does retrieval contain the ground truth?

We sampled every retrieved case for every model with stored retrieval results
(6,226 cases: all 500 events for both conditions of GPT-4o, GPT-5.4 and GPT-5.6
Sol, all 802/925 cases of DeepSeek R1 and Claude Sonnet 4.5, 1,000 of Sonnet 5's
1,108, and the 499 LLaMA 3.3 WS+Cutoff cases generated for this response; seed
20260921). For each case we reconstructed the evidence the model received (the
stored query re-issued to You.com under the run's date ceiling and passed through
the unmodified filtering and formatting code; for the two native-tool runs, the
fetched text of the URLs the tool cited) and asked an independent judge (Claude
Sonnet 5) whether any retrieved result was the source paper itself or stated the
realized outcome. We also record a deterministic arXiv-id / DOI match against the
URLs stored at run time, and whether the judge's matched URL was in that stored
list.

*Unrestricted WS.* The retrieved evidence contains the source paper or its stated
outcome for 74–93% of events (native tool: GPT-4o 88%, GPT-5.4 93%; single-query
pipeline: 74–85%), and the source paper's own page is among the retrieved URLs
for 54–79%. This confirms the reviewer's reading: the unrestricted condition
largely measures the ability to read the answer, and the manuscript now says so
explicitly; the forecasting gap is retained only as an upper reference.

*WS+Cutoff, pre-cutoff events.* Inclusion is 77–85% and the paper's own page is
retrieved for 36–58%: for events that predate the cutoff the condition is recall
with the source in hand, which is what the knowledge-gap arm is meant to
measure.

*WS+Cutoff, post-cutoff events — a leak we had not seen.* The source paper's own
page is essentially never retrieved (0–3%), so the date ceiling works at the
page level. But the judge finds the realized outcome in the retrieved text for
20–37% of post-cutoff events (9–20% confirmed on the exact URLs the model
received; the remainder cannot be confirmed because the search index has drifted
since the runs). The mechanism is snippet-level: You.com dates a page by
`page_age`, and the snippets it returns for researchgate.net publication pages
include the abstracts of newer "related" papers, so a page dated 2022 can carry a
2026 paper's results verbatim (`A4_2_groundtruth_inclusion/leak_example.json`
reproduces one such result). ResearchGate accounts for 332 of 439 post-cutoff
inclusions; preprint or PubMed pages of the same work under another identifier
account for most of the rest. The knowledge gap on post-cutoff events therefore
contains a leakage component, and we have revised the manuscript accordingly
(see proposed text): the WS+Cutoff arm is presented as an upper bound on what
pre-cutoff-dated retrieval can add, with the measured leakage rate reported
alongside it, and the fixed-evidence analysis in A4.3 is used for attribution.

## A4.3 — Fixed evidence packets from queries written outside the panel

We implemented the design the reviewer proposes. For every event in the pinned
500-event subset, Claude Opus 4.8 — a model outside the evaluated panel — wrote
one search query with the same instruction the pipeline uses (gpt-5.4-mini for
the 42 biomedical events Opus declined; every query is stored with its author in
`queries.jsonl`). Each query was issued once to You.com under seven date
ceilings (one per evaluated model's cutoff, plus unrestricted) and filtered and
formatted by the unmodified pipeline code, so that every evaluated model received
the identical evidence packet for a given ceiling (`evidence/`). Six models with
live deployments (GPT-4o, GPT-5.4, LLaMA 3.3 70B, Claude Sonnet 4.5, Claude
Sonnet 5, GPT-5.6 Sol) were then run on these packets under their own cutoff
ceiling and unrestricted, with the unmodified harness and their original decoding
settings, and scored with the frozen scoring code. DeepSeek R1 could not be
included (its deployment is retired). Gaps use the definitions of the published
table (post-cutoff events, ids shared by all conditions, paired CIs), recomputed
on the same events for the original setup; the difference between setups carries
a 10k bootstrap CI (`A4_3_fixed_queries/results.md`, `gaps.csv`,
`figures/a43_gaps.png`).

*Knowledge gap (WS+Cutoff − base).* Replacing the model's own query with an
external one leaves the knowledge gap unchanged within noise for every model and
task with n ≥ 20: the largest differences are +0.05 on MCQ for GPT-4o
(+0.049 [+0.005, +0.094]) and LLaMA 3.3 (+0.049 [+0.009, +0.088]), i.e. the
external queries retrieve slightly *more*, not less; all other differences have
CIs spanning zero (binary, perturbed binary and date for GPT-4o, all four tasks
for GPT-5.4 and Claude Sonnet 4.5). The direction and size of the knowledge gap
reported in the paper therefore do not depend on the evaluated model writing its
own query.

*Forecasting gap (WS − WS+Cutoff).* For Claude Sonnet 4.5 and GPT-5.4, whose
unrestricted runs used the same single-query pipeline, the fixed-evidence
forecasting gap matches the original within noise (e.g. Sonnet 4.5 binary +0.44
in both). For GPT-4o, whose original unrestricted run used the provider's native
search tool, the fixed-evidence forecasting gap is smaller on MCQ (+0.20 vs
+0.29, difference −0.09 [−0.15, −0.03]) and on the date task (+0.13 vs +0.24,
−0.10 [−0.17, −0.04]), and the perturbed-binary gap changes sign: part of the
published GPT-4o forecasting gap came from the tool loop, not from post-cutoff
information alone. We now report the fixed-evidence forecasting gaps as the
primary numbers and the native-tool runs as a separate upper reference.

*Ground truth in the fixed evidence.* The same inclusion check as A4.2 applied to
the fixed packets gives 82–84% on pre-ceiling events and 22–29% on post-ceiling
events (0–3% by URL), the same ResearchGate-snippet leak as with self-generated
queries. The leak is therefore a property of the search API's page-level date
filter, not of who writes the query, and the manuscript now reports it as a
limitation of any date-filtered web retrieval and gives the measured rate.

*Statistical power.* Sonnet 5 and Sol have almost no post-cutoff events in the
pinned subset (≤ 24 and ≤ 4), so their post-cutoff cells are suppressed; their
all-events rows (supplementary) show the recall-side gaps unchanged.

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
> page is never retrieved for post-cutoff events, but snippet text from aggregator
> pages dated before the cutoff carries the realized outcome for 20–35% of them
> (9–20% confirmed on the exact URLs the models received); the knowledge gap on
> post-cutoff events is therefore an upper bound. Replacing each model's own query
> with one written by a model outside the panel, and giving every model the same
> evidence, leaves the knowledge gaps unchanged within confidence intervals
> (Supplementary Table S-R2) and reduces GPT-4o's forecasting gap on MCQ from
> 0.29 to 0.20."

**Limitations (addition):**

> *Proposed text.* "Date-filtered web retrieval is filtered at the page level;
> snippets of pages dated before a cutoff can contain later content. We report the
> measured leakage rate rather than treating the cutoff-restricted condition as
> clean."

