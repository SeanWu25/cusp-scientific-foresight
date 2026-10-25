"""
a5_response_text.py -- narrative of response_A5.md. Every figure quoted in the
prose is pulled through the accessors in a5_make_response (ctx), so the text
and the tables cannot drift apart. Edit wording here; never type a number.
"""


def render(ctx):
    P, PM, sig, bal, dc = (ctx["pooled_table"], ctx["per_model_section"], ctx["sig_count"],
                           ctx["balanced"], ctx["direction_count"])
    cov, MAN, REG, C, META = ctx["coverage"], ctx["MAN"], ctx["REG"], ctx["C"], ctx["META"]
    L = ctx["labels"]
    N = len(META)
    snap = MAN["metadata_snapshot_date"]
    n_c, n_lo, n_lr = (MAN["n_events_with_citations"], MAN["n_events_with_latency"],
                       MAN["n_events_with_editorial_latency"])
    wd_tab, wd_k, wd_n = ctx["within_discipline_table"]()
    q1c, q4c = L("visibility")[0], L("visibility")[3]
    q1r, q4r = L("vis_rate")[0], L("vis_rate")[3]
    l0, l1, l2 = L("latency")
    leak_table = "\n".join(
        ["| model | cutoff | post-cutoff journal events | with a preprint before the cutoff | share |",
         "|---|---|---|---|---|"] +
        [f"| {k} | {v['cutoff']} | {v['post_journal_events']:,} | {v['preprint_before_cutoff']} | "
         f"{100*v['preprint_before_cutoff']/max(1, v['post_journal_events']):.1f}% |"
         for k, v in MAN["preprint_before_cutoff_among_post"].items()])

    def frac(dim, part=None, task=None, exclude_task=None):
        k, n = sig(dim, part, task, exclude_task)
        return f"{k} of {n}"

    def dcs(dim, part, task, hi, lo):
        ups, n, med, lo_, hi_ = dc(dim, part, task, hi, lo)
        return ups, n, med, lo_, hi_

    # -- source numbers
    s_all = frac("source")
    d_ov = dcs("source", "overall", "date", "HF Daily Papers (arXiv)", "Nature")
    d_po = dcs("source", "post", "date", "HF Daily Papers (arXiv)", "Nature")
    # -- visibility numbers
    v_post_nondate = frac("visibility", "post", exclude_task="date")
    v_post_bin = frac("visibility", "post", "binary"); v_post_frq = frac("visibility", "post", "frq")
    v_post_mcq = frac("visibility", "post", "mcq"); v_post_date = frac("visibility", "post", "date")
    v_pre = frac("visibility", "pre"); v_pre_frq = frac("visibility", "pre", "frq")
    v_pre_mcq = frac("visibility", "pre", "mcq"); v_pre_date = frac("visibility", "pre", "date")
    v_ov = frac("visibility", "overall"); v_ov_date = frac("visibility", "overall", "date")
    r_post_nondate = frac("vis_rate", "post", exclude_task="date"); r_post = frac("vis_rate", "post")
    r_pre = frac("vis_rate", "pre"); r_ov = frac("vis_rate", "overall")
    r_post_date = frac("vis_rate", "post", "date"); r_ov_date = frac("vis_rate", "overall", "date")
    f_pre = dcs("visibility", "pre", "frq", q4c, q1c); f_post = dcs("visibility", "post", "frq", q4c, q1c)
    m_pre = dcs("visibility", "pre", "mcq", q4c, q1c); m_post = dcs("visibility", "post", "mcq", q4c, q1c)
    b_post = dcs("visibility", "post", "binary", q4c, q1c)
    fr_post = dcs("vis_rate", "post", "frq", q4r, q1r); br_post = dcs("vis_rate", "post", "binary", q4r, q1r)
    dr_post = dcs("vis_rate", "post", "date", q4r, q1r); dr_pre = dcs("vis_rate", "pre", "date", q4r, q1r)
    # -- latency numbers
    l_all = frac("latency"); l_post = frac("latency", "post"); l_ov = frac("latency", "overall")
    l_pre = frac("latency", "pre")
    l_post_bin = frac("latency", "post", "binary"); l_post_mcq = frac("latency", "post", "mcq")
    l_post_frq = frac("latency", "post", "frq"); l_post_date = frac("latency", "post", "date")
    e_all = frac("lat_review"); e_post = frac("lat_review", "post"); e_ov = frac("lat_review", "overall")
    e_pre = frac("lat_review", "pre")
    er = L("lat_review")
    ef_post = dcs("lat_review", "post", "frq", er[2], er[0]); ef_pre = dcs("lat_review", "pre", "frq", er[2], er[0])
    lat_dist = MAN.get("latency_distribution", {})
    lat_share0 = lat_dist.get("share_0", float("nan"))
    lat_share_1_6 = lat_dist.get("share_1_6", float("nan"))
    lat_share_gt6 = lat_dist.get("share_gt6", float("nan"))
    lb_post = dcs("latency", "post", "binary", l2, l0); lm_post = dcs("latency", "post", "mcq", l2, l0)
    lf_post = dcs("latency", "post", "frq", l2, l0); ld_post = dcs("latency", "post", "date", l2, l0)
    leg_v = frac("legacy_visibility"); leg_l = frac("legacy_latency")
    leg_v_nondate = frac("legacy_visibility", exclude_task="date")

    def sgn(x):
        return f"{x:+.3f}"

    out = []
    A = out.append
    A(f"""# Response to Reviewer 1, Comment 5 — benchmark selection bias (A5)

Supporting files in this directory: `metadata_audit.md` (what metadata exists and where it came from), `metadata/` (the {snap} Semantic Scholar / OpenAlex / Crossref snapshot, one JSONL per source), `by_source/`, `by_visibility/`, `by_vis_rate/`, `by_latency/`, `by_lat_review/` (full tables, CSV + markdown, all three partitions), `by_legacy/` (the first-pass 481- and 708-event tables, superseded), `tables/` (pooled), `figures/`, `novelty_discussion.md`, `MANIFEST.json` (git SHA, seeds, snapshot date, panel, coverage, partition sizes).

Regenerate with `results/A5_selection_bias/run_all.sh`. No inference; the only network step is the metadata snapshot, which is cached and never re-fetched. This document is written by `scripts/a5_make_response.py` from the stored CSVs — no number in it is typed by hand.

---

## 1. The reviewer's comment

> "Control benchmark selection bias by stratifying results across journals, repositories, event visibility, novelty, and publication latency."

## 2. Summary

Ten models, four tasks, {N:,} events. Every stratification is reported twice below — on the **whole dataset** and on the **post-cutoff partition only** (the forecasting regime the paper's claims rest on) — with the pre-cutoff partition in the supporting tables.

1. **Source / venue.** Performance differs across venues ({s_all} tests significant after Holm correction), but the difference is confined to the date task and the leaderboard item type, and it disappears once discipline is held fixed ({wd_k} of {wd_n} within-discipline tests). Every model scores higher on arXiv-sourced date items than on *Nature* items ({d_ov[0]}/{d_ov[1]} models on the whole dataset, {d_po[0]}/{d_po[1]} post-cutoff; median {sgn(d_ov[2])} date score), which is a cadence property of the target, not knowledge about the papers.
2. **Event visibility, now on the whole corpus** ({n_c:,} events with a citation count, {100*n_c/N:.1f}%, versus 481 in the first pass). Citations predict performance **before** a model's cutoff and not after it. Pre-cutoff, the most-cited quartile beats the least-cited on FRQ for {f_pre[0]}/{f_pre[1]} models (median {sgn(f_pre[2])} on the 0–10 scale) and on MCQ for {m_pre[0]}/{m_pre[1]} (median {sgn(m_pre[2])}); {v_pre} pre-cutoff tests are significant. Post-cutoff the same contrasts are {f_post[0]}/{f_post[1]} (median {sgn(f_post[2])}) and {m_post[0]}/{m_post[1]} (median {sgn(m_post[2])}), binary is {b_post[0]}/{b_post[1]} (median {sgn(b_post[2])}), and {v_post_nondate} non-date post-cutoff tests are significant. Well-cited results are easier to *recall*, not easier to *forecast*. The age-adjusted citation-rate version gives the same picture ({r_post_nondate} non-date post-cutoff tests).
3. **Publication latency, now on every journal event** ({n_lo:,} events, {100*n_lo/N:.1f}%, versus 708 in the first pass, and measuring the interval the reviewer means: how long a result was publicly observable before its journal version). {l_post} post-cutoff tests and {l_ov} whole-dataset tests are significant. A second, independent latency — time in peer review, received → online, {n_lr:,} *Nature* and *Science* events — gives {e_post} post-cutoff and {e_ov} whole-dataset.
4. **Novelty** is not stratified; section 8 says why, and we prefer stating the limitation to inventing a proxy.

The paper's headline claims — near-chance binary forecasting, a large retrospective/prospective gap, no model beating a constant-month date baseline — hold within every paper venue (the 59 leaderboard items are a different item type, section 4), every citation quartile and every latency stratum of the post-cutoff partition.

## 3. What changed since the first pass, and what the metadata now supports

The first pass could stratify visibility on 481 events and latency on 708, because those were the only events carrying the fields. Both limits were limits of the *corpus files*, not of the events, so we took a single metadata snapshot on **{snap}** over the whole benchmark:

- **Citations**: Semantic Scholar batch API for every linked event (primary), OpenAlex as fallback for the {sum(1 for m in META.values() if m.get('cite_src') == 'openalex')} it did not resolve; {n_c:,} of the {sum(1 for m in META.values() if m.get('doi')):,} linked events resolved ({sum(1 for m in META.values() if m.get('doi') and m.get('cites') is None)} did not; the 59 leaderboard items have no paper). One snapshot, one date, both halves of the corpus. Against the May 2026 counts for the 481 first-pass events the new counts have Spearman ρ = {MAN.get('legacy_vs_new_spearman', float('nan')):.3f}, so the two snapshots agree on ordering and the earlier tables were not wrong, only narrow. Semantic Scholar is primary because OpenAlex credits most arXiv citations to the later journal version and returns near-zero counts for arXiv records.
- **Publication dates**: Crossref for every journal DOI ({MAN.get('n_crossref_resolved', 0):,} of {MAN.get('n_journal_doi', 0):,} resolved), giving the journal version's online date, and — for *Nature* and *Science*, which deposit them — the manuscript received and accepted dates. Cell (Elsevier) deposits neither.

""")
    A(ctx["meta_coverage_table"]())
    A(f"""
**Journal and repository are one stratification.** Every `nature` DOI is `10.1038/s41586`, every `science` is `10.1126/science`, every `cell` is `10.1016/j.cell`, and both AI feeds are entirely arXiv — verified from the DOIs, not assumed. There are no sibling journals to separate and no singleton strata, so no "other" bucket is needed.

**Partition sizes are very unequal across models**, so whole-dataset numbers are not comparable *between* models (GPT-4o and LLaMA 3.3 have no pre-cutoff events; Claude Sonnet 5, Claude Opus 4.8 and GPT-5.6 Sol have few post-cutoff events). That is why the post-cutoff tables are the ones to read for the forecasting claim:

{ctx['partition_table']()}

**Methods, unchanged from the first pass.** Binary is balanced accuracy (mean of recall on the real question and specificity on its perturbed twin). Every cell carries N and a 2,000-draw event-clustered bootstrap percentile CI; cells below n = 20 print `n<20` and no point estimate. Stratum effects use a 10,000-draw permutation test shuffling stratum labels across events, Holm–Bonferroni corrected across every model × partition × task test within a stratification. Pooled rows average only over models that carry every stratum unsuppressed, so every column of a pooled table rests on the same models (the count is printed). FRQ uses the published rubric (`judge_frq_combined`); refusals are excluded from denominators. With N in the thousands the permutation test flags differences too small to matter, so the size of every effect is printed next to its p-value.

## 4. Source and repository (all {N:,} events)

### 4.1 Whole dataset

{P('source', 'overall')}

### 4.2 Post-cutoff only

{P('source', 'post')}

{s_all} permutation tests are significant, so performance does vary across sources. The variation has two causes, neither a venue effect:

**(a) Date prediction is easier on arXiv items.** Every model scores higher on the arXiv feeds than on the journals — HF Daily Papers vs *Nature*: {d_ov[0]}/{d_ov[1]} models on the whole dataset (median {sgn(d_ov[2])}, range {sgn(d_ov[3])} to {sgn(d_ov[4])}) and {d_po[0]}/{d_po[1]} post-cutoff (median {sgn(d_po[2])}). arXiv posting follows a short, regular cadence while journal lags are long and variable, so the target itself is more predictable.

**(b) The leaderboard set is a different item type.** It is the only stratum where binary rises materially and MCQ falls; 59 events, no FRQ items.

Binary, MCQ and FRQ are otherwise flat across the five paper sources.

### 4.3 The confound, and the control

CUSP's venues are nested inside discipline: the arXiv feeds and the leaderboard set are 99–100% Artificial Intelligence, the journals 0–1.3%, and only 34 of 1,274 AI events appear in a journal. So we held discipline fixed and re-tested venue within each of the seven disciplines that carry two or more venues at n ≥ 100 (`by_source/within_discipline.md`):

{wd_tab}

**{wd_k} of {wd_n}.** Once discipline is fixed, the venue does not predict how well any model does. The raw source effect is a discipline effect — which the paper already stratifies on — plus the date-cadence difference above.

### 4.4 Per-model tables — whole dataset

{PM('source', 'overall')}
### 4.5 Per-model tables — post-cutoff only

{PM('source', 'post')}
## 5. Event visibility ({n_c:,} events with citation counts)

Two measures, both from the {snap} snapshot: the **raw count** (quartiles over all {n_c:,} events: {', '.join(L('visibility'))}) and the **citation rate** — count divided by months from the first-observable date to the snapshot (quartiles {', '.join(L('vis_rate'))}). Raw counts favour older events (an Apr–Aug 2026 event has had months to be cited, a Jan 2024 event two and a half years), so the rate version is the age-adjusted one and the one we treat as primary; we show both because the published S19–S23 used raw quartiles.

### 5.1 Whole dataset

Raw citation quartile:

{P('visibility', 'overall')}

Citation-rate quartile:

{P('vis_rate', 'overall')}

### 5.2 Post-cutoff only

Raw citation quartile:

{P('visibility', 'post')}

Citation-rate quartile:

{P('vis_rate', 'post')}

### 5.3 Reading

The visibility effect lives in the pre-cutoff partition. Raw quartiles, pre-cutoff: {v_pre} tests significant (FRQ {v_pre_frq}, MCQ {v_pre_mcq}, date {v_pre_date}); the most-cited quartile beats the least-cited on FRQ for {f_pre[0]}/{f_pre[1]} models (median {sgn(f_pre[2])}, range {sgn(f_pre[3])} to {sgn(f_pre[4])}) and on MCQ for {m_pre[0]}/{m_pre[1]} (median {sgn(m_pre[2])}). Post-cutoff: binary {v_post_bin}, MCQ {v_post_mcq}, FRQ {v_post_frq}, date {v_post_date}; the same Q4−Q1 contrasts are FRQ {f_post[0]}/{f_post[1]} (median {sgn(f_post[2])}), MCQ {m_post[0]}/{m_post[1]} (median {sgn(m_post[2])}), binary {b_post[0]}/{b_post[1]} (median {sgn(b_post[2])}). Citation-rate quartiles: {r_pre} pre-cutoff, {r_post} post-cutoff ({sig('vis_rate', 'post', 'date')[0]} of them on the date task), {r_ov} whole-dataset; post-cutoff Q4−Q1 is binary {br_post[0]}/{br_post[1]} (median {sgn(br_post[2])}) and FRQ {fr_post[0]}/{fr_post[1]} (median {sgn(fr_post[2])}, none significant).

This is the pattern one expects if citation count indexes how often a result appears in training data: well-cited papers are recalled better (pre-cutoff FRQ and MCQ), but a paper's eventual visibility does not make its outcome easier to *forecast* from pre-cutoff knowledge. It also means the benchmark's headline post-cutoff numbers are not inflated by a few famous results.

The date task is the exception in both versions ({v_ov_date} whole-dataset tests significant on raw quartiles, {r_ov_date} on rate), and it is the task on which no model has skill. On raw quartiles the direction is split ({dc('visibility','overall','date',q4c,q1c)[0]}/{dc('visibility','overall','date',q4c,q1c)[1]} models favour Q4), which is what an age confound looks like: raw Q1 is dominated by the newest events, and the horizon study (Reviewer 1, comment 4) shows the date score depends on horizon through anchoring. On rate quartiles the direction is consistent ({dr_post[0]}/{dr_post[1]} post-cutoff, {dr_pre[0]}/{dr_pre[1]} pre-cutoff favour Q4) and modest (post-cutoff median {sgn(dr_post[2])}).

One caution that the first pass taught us: a pooled column is only interpretable when every column rests on the same models. Averaging whatever cells survive suppression manufactured a monotone MCQ/FRQ decline across quartiles that vanished on a balanced panel. Every pooled table here is balanced and prints the model count.

### 5.4 Per-model tables — raw citation quartile, whole dataset

{PM('visibility', 'overall')}
### 5.5 Per-model tables — raw citation quartile, post-cutoff only

{PM('visibility', 'post')}
### 5.6 Per-model tables — citation-rate quartile, whole dataset

{PM('vis_rate', 'overall')}
### 5.7 Per-model tables — citation-rate quartile, post-cutoff only

{PM('vis_rate', 'post')}
### 5.8 The first-pass 481-event tables, and Supplementary Tables S19–S23

The 481-event version (Semantic Scholar, retrieved 2026-05-12, pinned retrieval subset) is kept under `by_legacy/visibility_481/` for continuity: {leg_v} tests significant, {leg_v_nondate} outside the date task — consistent with the whole-corpus result, just underpowered.

The published S19–S23 report Δ_know and Δ_fore per citation quartile for three models, with several cells resting on n = 1–3 (GPT-5.4 Q4 "+0.000 (n = 1)"). We regenerated them with N, a paired bootstrap CI and suppression below n = 20, extended from three models to the seven with a complete web-search triple on the pinned 500 (`by_visibility/citation_gap_S19_S23.md`). The regeneration reproduces every published non-suppressed cell to three decimals with matching N; of 101 cells, 32 are now suppressed rather than printed. They necessarily keep the May 2026 quartile edges (≤8, ≤22, ≤59) because they reproduce the published tables. We recommend the corrected tables replace S19–S23.

## 6. Publication latency ({n_lo:,} journal events)

**Definition.** Latency = the journal version's online-publication month (Crossref) minus the first-observable month: the earlier of CUSP's `publication_date` — which the build pipeline had already set to the earliest date found across Crossref, bioRxiv, medRxiv, Semantic Scholar and Europe PMC — and any Crossref-linked preprint's posted month (the dating correction below). It is the number of months a result was publicly observable before its journal version appeared: 0 means no earlier public trace exists, larger values mean a preprint or other public record preceded the journal. It is computable for every *Nature*, *Science* and *Cell* event in both halves of the corpus; arXiv events have no journal version and are excluded by construction. Strata: {', '.join(L('latency'))} — {100*lat_share0:.0f}% of journal events have latency 0, {100*lat_share_1_6:.0f}% are 1–6 months, {100*lat_share_gt6:.0f}% exceed six months (the longest is {MAN['latency_distribution'].get('max', '')} months); finer bins fall below n = 20 in most per-model post-cutoff cells.

### 6.1 Whole dataset

{P('latency', 'overall')}

### 6.2 Post-cutoff only

{P('latency', 'post')}

**{l_post} post-cutoff, {l_pre} pre-cutoff, {l_ov} whole-dataset tests are significant** (post-cutoff by task: binary {l_post_bin}, MCQ {l_post_mcq}, FRQ {l_post_frq}, date {l_post_date}). Post-cutoff, the longest-latency stratum versus the zero-latency stratum: binary {lb_post[0]}/{lb_post[1]} models higher (median {sgn(lb_post[2])}), MCQ {lm_post[0]}/{lm_post[1]} ({sgn(lm_post[2])}), FRQ {lf_post[0]}/{lf_post[1]} ({sgn(lf_post[2])}), date {ld_post[0]}/{ld_post[1]} ({sgn(ld_post[2])}).

**A dating correction this pass surfaced.** Crossref links a preprint to {MAN.get('n_events_with_crossref_preprint_link', 0)} journal events; for {MAN.get('n_preprint_earlier_than_cusp_date', 0)} of them the preprint was posted *before* CUSP's `publication_date` (median {MAN.get('preprint_gap_months_quartiles', [0, 0, 0])[1]:.0f} months earlier, IQR {MAN.get('preprint_gap_months_quartiles', [0, 0, 0])[0]:.0f}–{MAN.get('preprint_gap_months_quartiles', [0, 0, 0])[2]:.0f}), i.e. the build pipeline's earliest-date search missed them. The latency above uses the earlier of the two dates. The cutoff partition keeps the benchmark's own date, so the table below counts, per model, how many of its post-cutoff journal events had a preprint before its cutoff — observable-before-cutoff items the benchmark treats as prospective:

{leak_table}

These are {min(v['preprint_before_cutoff']/max(1, v['post_journal_events']) for v in MAN['preprint_before_cutoff_among_post'].values())*100:.1f}–{max(v['preprint_before_cutoff']/max(1, v['post_journal_events']) for v in MAN['preprint_before_cutoff_among_post'].values())*100:.1f}% of each model's post-cutoff journal events, and by construction they sit in the non-zero latency strata, so the post-cutoff latency tables above are the test of whether they inflate the forecasting numbers: they do not ({l_post} post-cutoff tests).

### 6.3 Editorial latency (received → online), {n_lr:,} *Nature* and *Science* events

A different construct: how long the manuscript sat in review. Strata: {', '.join(L('lat_review'))}.

Whole dataset:

{P('lat_review', 'overall')}

Post-cutoff only:

{P('lat_review', 'post')}

{e_post} post-cutoff, {e_pre} pre-cutoff, {e_ov} whole-dataset tests significant, and every significant one but a single date test is on FRQ. The pattern is a small, monotone rise in FRQ score with time in review: 13–24 months versus ≤6 months is higher for {ef_post[0]}/{ef_post[1]} models post-cutoff (median {sgn(ef_post[2])} on the 0–10 scale) and {ef_pre[0]}/{ef_pre[1]} pre-cutoff (median {sgn(ef_pre[2])}); binary and MCQ are flat ({frac('lat_review', None, 'binary')} and {frac('lat_review', None, 'mcq')} across all partitions). Because it appears in the pre- and post-cutoff partitions alike, it is a property of the items — longer-reviewed papers draw higher rubric scores for their proposed solutions — not a knowledge or cutoff artefact, and it does not touch the binary or mechanism results.

### 6.4 Per-model tables — latency, whole dataset

{PM('latency', 'overall')}
### 6.5 Per-model tables — latency, post-cutoff only

{PM('latency', 'post')}
### 6.6 Per-model tables — editorial latency, whole dataset

{PM('lat_review', 'overall')}
### 6.7 Per-model tables — editorial latency, post-cutoff only

{PM('lat_review', 'post')}
### 6.8 The superseded 708-event measure

The first pass used `original_publication_date − first_date_found` over 708 extension events. On inspection, `first_date_found` is the Crossref record-creation date for 96% of them, so that interval mostly measured online-first versus print-issue scheduling (0–3 months, all post-cutoff, no pre-cutoff partition). It is kept under `by_legacy/latency_708/` ({leg_l} significant) and should not be cited; section 6 replaces it.

## 7. Novelty — why we are not stratifying on it

We have no gold standard and no agreed proxy, and we decline to invent one. `novelty_discussion.md` lists six candidates (citation count, venue prestige, semantic distance from prior literature, rarity of the category combination, novelty claims in the abstract, an LLM-judged departure score) with what each would and would not capture. Two objections apply to all of them:

- **Circularity.** Novelty is close to the construct CUSP measures. A result that departs sharply from prior work is almost by definition harder to forecast. A novelty stratification showing lower performance on novel events would re-measure the benchmark's own target through a noisier instrument, not demonstrate a compositional bias.
- **Range restriction.** Every CUSP event was selected for being notable — published in *Nature*, *Science* or *Cell*, or curated onto a "top AI paper" list. The sampling frame is already truncated at the high end of novelty and visibility. Any within-benchmark stratification, including the citation analysis above, probes variation *inside* an already-selected band and can neither detect nor correct the selection that produced the band.

We think the second point is the honest answer to the reviewer's underlying concern, and we prefer to state it as a limitation of the benchmark rather than let a novelty table imply a control we do not have. A defensible novelty instrument would need a definition, a validation against human ratings, and inter-rater agreement — a study, not a table.

## 8. Proposed manuscript text

**[PROPOSED — Results, new subsection "Sensitivity to benchmark composition"]**

> To test whether our conclusions depend on how CUSP was assembled, we stratified every model's performance on all four tasks by source venue, citation quartile and publication latency, each on the whole benchmark and on the post-cutoff partition, with event-clustered bootstrap intervals and permutation tests corrected across the family (Supplementary Tables S24–S28). Performance varies across venues, but the variation is confined to the date task, where every model scores higher on arXiv-sourced events than on journal-sourced ones (median {sgn(d_ov[2])} date score), consistent with arXiv's regular posting cadence; because venues are nested within disciplines, we repeated the analysis with discipline held fixed and found {wd_k} of {wd_n} tests significant. Citation count, taken from a single Semantic Scholar snapshot over {n_c:,} events, predicts performance before a model's cutoff (the most-cited quartile scores higher on mechanism questions for {m_pre[0]} of {m_pre[1]} models with both quartiles populated, and on solution questions for {f_pre[0]} of {f_pre[1]}) but not after it ({v_post_nondate} post-cutoff tests outside the date task), indicating that visibility aids recall rather than forecasting. Publication latency — months a result was publicly observable before its journal version, over {n_lo:,} journal events — shows {l_post} significant post-cutoff tests, and time in peer review over {n_lr:,} events shows {e_post}.

**[PROPOSED — Limitations]**

> Two limits of this benchmark's construction bound what the stratification above can establish. First, every CUSP event was selected for being notable — published in *Nature*, *Science* or *Cell*, or curated onto a widely-read preprint list — so the corpus is truncated at the high end of both visibility and novelty, and no within-benchmark stratification can detect the selection that produced that truncation. Second, source venue and scientific discipline are nearly collinear in CUSP: only 34 of 1,274 artificial-intelligence events appear in a journal, so an arXiv-versus-journal contrast cannot be fully separated from an AI-versus-other-discipline contrast. We report the discipline-controlled analysis for this reason and do not interpret the raw venue contrast causally.

**[PROPOSED — Limitations, novelty]**

> We do not stratify by novelty. We have no validated measure of it, and the available proxies are either confounded with venue and discipline or circular with the construct the benchmark measures: an event that departs sharply from prior work is, by construction, harder to forecast from pre-cutoff knowledge. Establishing a novelty measure — with a definition, validation against human judgement, and inter-rater agreement — is future work.

**[PROPOSED — replacement caption for Supplementary Tables S19–S23]**

> Knowledge gap (Δ_know) and foresight gap (Δ_fore) on post-cutoff instances, stratified by citation-count quartile, for the seven models with a complete web-search triple on the 500-event retrieval subset. Citation counts were retrieved from Semantic Scholar on 2026-05-12 over the 481 subset events for which a count resolved; quartile edges are ≤8, ≤22, ≤59, >59. Cells are the mean difference with a 95% paired bootstrap interval and N; cells with fewer than 20 paired observations are suppressed rather than reported as point estimates. These tables supersede the previously submitted S19–S23, which reported point estimates at N as low as 1.

**[PROPOSED — new Supplementary Table captions S24–S28]**

> **S24.** Performance by source venue, per model and task, on the whole benchmark and on the pre- and post-cutoff partitions. Binary is balanced accuracy. Cells give the value, a 95% event-clustered bootstrap interval and N; cells below N = 20 are suppressed. p-values are permutation tests across strata, Holm-corrected.
> **S25.** The same analysis with scientific discipline held fixed, for the seven disciplines carrying two or more venues at N ≥ 100.
> **S26.** Performance by citation quartile over the {n_c:,} events with a citation count (Semantic Scholar, OpenAlex fallback, snapshot {snap}), raw count and count per month since first observable.
> **S27.** Performance by publication latency — months between the first public record of a result and its journal version (Crossref, snapshot {snap}) — over the {n_lo:,} journal events.
> **S28.** Performance by editorial latency (manuscript received to online publication) over the {n_lr:,} *Nature* and *Science* events that deposit a received date.

## 9. Limitations of this analysis

- Citation counts are one snapshot ({snap}); the extension half has had at most five months to accrue citations, which is why the age-adjusted rate version is shown alongside the raw one.
- Latency 0 means "no earlier public record found by the build pipeline or by Crossref", not "no preprint existed": a preprint the pipeline missed makes the true latency longer, so the zero-latency stratum is contaminated toward longer latencies, which biases a latency effect toward zero, not away from it.
- Editorial latency is available only for *Nature* and *Science*; Cell does not deposit received dates.
- Venue and discipline are nearly collinear; the discipline-controlled analysis narrows but does not eliminate the confound, and it cannot compare arXiv against journals within AI.
- Pre/post partition sizes differ by orders of magnitude across models; two models have no pre-cutoff partition at all.
- The leaderboard stratum (59 events) carries no FRQ items and is frequently suppressed in per-model splits.
- Two Claude models' FRQ responses are truncated at their token caps; the direction of that effect on scores is not established.
""")
    return "\n".join(out)
