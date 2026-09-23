# Novelty — candidate proxies, and why we are not stratifying on it

**Status: OPEN — team decision required. Nothing in this file was computed.**

Reviewer 1 asks us to stratify by novelty alongside journal, repository,
visibility and latency. We have no gold standard for novelty and no agreed
proxy, and per the study instruction we did not invent one. This file sets out
what is actually available, what each candidate would and would not capture, and
two objections that apply to all of them.

## What the metadata could support

| # | candidate proxy | built from | coverage | what it captures | what it does not |
|---|---|---|---|---|---|
| 1 | **Citation count** | `citation_count` (external file) | 481 events (8.6%) | received attention | novelty. A highly-cited paper may be a careful confirmation; a paradigm shift may be uncited at 4 months. Confounded by time since publication, field size, author visibility |
| 2 | **Venue prestige** | `source` | 100% | nothing usable — all three journals are flagship and the two AI feeds are both curated "top paper" lists | any variance at all: the proxy is near-constant by construction |
| 3 | **Semantic distance from prior literature** | `source_abstract` (99%) + an external pre-publication reference corpus | 99% *if* a reference corpus is built | lexical/topical unusualness relative to what came before — the Uzzi-style "atypical combination" tradition | conceptual significance; it scores a paper that uses unusual words alongside one that makes an unusual claim. Requires choosing an embedding model, a reference corpus and a date cut — each a substantive modelling decision, not a lookup |
| 4 | **Rarity of the `sub_categories` combination** | `sub_categories` (100%) | 100% | topical atypicality *within our own taxonomy* | anything the taxonomy does not resolve. The labels are coarse (8 main areas) and were LLM-assigned during construction, so this measures our annotation pipeline as much as the science |
| 5 | **Novelty claims in the abstract** ("first", "novel", "unprecedented") | `source_abstract` (99%) | 99% | authorial rhetoric and venue writing convention | novelty. *Nature* abstracts assert priority as a matter of house style; arXiv preprints do so at a different rate. This would mostly recover `source`, which we already stratify on |
| 6 | **LLM-judged departure from prior work** | `problem_statement` + `technical_approach` (99%) | 99% | the most direct reading of the construct | independence. It requires a new judge and a new rubric outside the frozen scoring stack, and it would be graded by the same model family that produces FRQ scores |

Proxies 1, 2 and 5 we consider unusable on their face. Proxies 3, 4 and 6 are
defensible research choices, but each is a *new instrument* that would need its
own validation before it could carry a claim in this paper.

## Two objections that apply to every proxy

**1. Circularity.** Novelty is close to the construct CUSP is built to measure.
A result that departs sharply from prior work is, almost by definition, harder
to forecast from pre-cutoff knowledge. If we stratified on a novelty score and
found performance falls in the high-novelty stratum, we would not have shown
that benchmark composition biases our results — we would have re-measured the
benchmark's own target through a noisier instrument. To be informative about
*selection bias*, a novelty stratification would have to show a stratum effect
that persists **after** conditioning on the pre/post-cutoff contrast, which is
the comparison our design already makes.

**2. Range restriction — and this is the more important one.** Every event in
CUSP was selected for being notable: published in *Nature*, *Science* or *Cell*,
or curated onto a "top AI paper" list. The sampling frame is already truncated
at the high end of both novelty and visibility. Any within-benchmark
stratification — including the citation-quartile analysis we *did* run — probes
variation inside an already-selected band, and can neither detect nor correct
the selection that produced the band. We think this is the honest answer to the
reviewer's underlying concern, and we say so directly in `response_A5.md` rather
than letting a novelty table imply a control we do not have.

## What we would need to do this properly

A defensible novelty stratification needs, at minimum: a stated definition; an
instrument (most plausibly proxy 3 with a fixed pre-cutoff reference corpus, or
proxy 6 with a published rubric); a validation against human ratings on a
sample; and inter-rater agreement. That is a study, not a table. We recommend
deciding as a team whether it belongs in this revision or is named as future
work.

**Our recommendation:** name novelty as a dimension we deliberately do not
stratify on, give the two reasons above, and report the range-restriction
limitation as a property of the benchmark rather than a gap in the analysis.
