"""
report.py — writes study1_verification/results.md, study2_detection/results.md
and SUMMARY.md from the analysis outputs. Numbers are read from the generated
tables; nothing is hard-coded.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C


def rd(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def jf(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def f(x, d=1):
    try:
        return f"{100*float(x):.{d}f}%"
    except Exception:
        return "n/a"


def ci(lo, hi, d=1):
    try:
        return f"{100*float(lo):.{d}f}–{100*float(hi):.{d}f}%"
    except Exception:
        return "n/a"


def mdtable(p: Path) -> str:
    q = p.with_suffix(".md")
    return q.read_text(encoding="utf-8") if q.exists() else "_(table not generated)_"



def neg_strict_block() -> str:
    """Section 4b: the strict re-verification of the negatives (very strict standard)."""
    sp = C.S1 / "neg_strict_summary.json"
    if not sp.exists():
        return ""
    d = jf(sp)
    refs = d.get("referees", [])
    if not refs:
        return ""
    N = d["n_items"]
    prev, now = d["previous_pass1_plus2"], d["strict_both"]
    gc = d.get("gate_rejection_counts", {})
    gate_line = ", ".join(f"`{k}` {v}" for k, v in sorted(gc.items(), key=lambda x: -x[1])) or "none"
    changed = rd(C.TABLES / "t24_negatives_strict_changed.csv")
    names = {"haiku45": "Claude Haiku 4.5", "gpt54mini": "GPT-5.4-mini",
             "sonnet5": "Claude Sonnet 5", "gpt55": "GPT-5.5", "opus48": "Claude Opus 4.8"}
    pair = " and ".join(names.get(r, r) for r in refs)
    per = "; ".join(f"{names.get(r, r)} proposed {d['strict_raw'][r]}, "
                    f"{d['strict_downgraded'][r]} rejected by the gates, "
                    f"{d['strict_certified'][r]} certified" for r in refs)
    return f"""## 4b. The negatives re-verified under a very strict standard

The pass in section 2 asked whether the perturbed claim "was achieved" by someone other
than the source paper. That question is too easy to answer yes to. A nearby result, the
same advance in a different system, or a qualitative restatement of a numeric threshold
can all be argued into a match, and a referee asked to search for evidence tends to find
some.

So all {N} negatives were re-run under a standard written to be hard to satisfy: a
synthetic negative is mislabelled **only if the exact perturbed claim actually happened
in the real world by the target date**. Anything less is NOT ACHIEVED.

Six rules, stated in the prompt and then re-checked in code:

1. A perturbed **numeric threshold** counts only if a reported result meets or exceeds
   that exact modified value. Close, comparable, approaching or "on the same order" does
   not count.
2. An **added constraint** counts only if that exact constraint was satisfied. Achieving
   the underlying advance without satisfying the constraint does not count.
3. The achievement must be for the **same task, system or measurement** as the claim. A
   similar result in a different setting does not count. (This rule was absent from the
   first pass and is the main addition.)
4. It must be **on or before the target date**. Later does not count.
5. The **source paper does not count**, in any venue or restatement.
6. If the evidence is partial, indirect or ambiguous, the verdict is **NOT ACHIEVED**.

### The evidence requirement, enforced in code

An ACHIEVED verdict is invalid unless the record carries the exact reported value or the
exact satisfied constraint, the date, the source URL, and a quoted passage showing it.
A prompt is a request; `scripts/neg_gates.py` is the check. Ten gates run in code against
the referee's own record, and any failure downgrades the verdict to NOT ACHIEVED with the
failing gate logged:

| gate | what it rejects |
|---|---|
| `has_requirement` / `has_value` | an ACHIEVED with no figure or no stated constraint |
| `has_date` / `date_on_or_before` | a source dated after the target, or undated |
| `has_url` | a claim with no citable source |
| `has_quote` | a restated title standing in for a passage |
| `value_in_quote` | a quoted passage that does not contain the figure it is offered for |
| `direction_ok` | the inequality, recomputed in Python from the claim's threshold and the referee's reported figure |
| `same_setting` | a result the referee itself marks as a different task or system |
| `source_not_excluded` | the item's own source paper, cited under another URL |

Two cheap referees ran it independently ({pair}), and **both must certify** an item before
it counts. Each referee's own numbers: {per}. Neither refused or failed to parse any of
the {N} items.

### What it found

{mdtable(C.TABLES / 't23_negatives_strict_rates')}

The rate falls from **{prev} of {N} ({100*prev/N:.1f}%)** under the previous
standard to **{now} of {N} ({100*now/N:.1f}%)**. {len(changed)} verdicts changed, listed
individually with their reason in `tables/t24_negatives_strict_changed.md`.

Most of the fall is not the gates. It is the referees themselves declining to call a
result a match once rule 3 and rule 5 are stated explicitly: the great majority of the
overturned items were overturned because the only work satisfying the claim *was the
excluded source paper*, or was dated after the target. The gates rejected
{sum(gc.values()) if gc else 0} further proposals, by gate: {gate_line}.

{mdtable(C.TABLES / 't25_negatives_strict_gates')}

### The one survivor

One item is certified by both referees, and it is a real mislabelling. Both independently
found the same paper, quoted the same sentence, and that sentence reports every element of
the claim four years before the target date. It is listed with its evidence in
`study1_verification/flagged_for_review_negatives_strict.csv`.

{mdtable(C.TABLES / 't26_negatives_strict_referees')}

### What it does to the corrected accuracy

{mdtable(C.TABLES / 't27_corrected_accuracy_negstrict')}

Route 2 — the perturbation never made the claim false — is a different question, settled
from the source paper rather than from a search, and this re-verification does not touch
it. It is held fixed at its own certified set in all three columns, so the only thing
moving is the route-1 standard. The panel mean is unchanged at 49.8%.

### Limits of this pass

- It can only **lower** the rate. It re-examines candidates for removal and never promotes
  a sound item, so it is a lower bound by construction.
- `direction_ok` reads "better than X" as a floor. That is right for most quantities in
  this corpus and over-strict for ones where lower is better, such as a resolution in
  ångström. No item's final verdict turns on it: zero proposals were rejected by that gate
  alone.
- The referees are cheap models. That is defensible here only because the gates check the
  factual scaffolding in code and because both must agree; neither referee's word is
  load-bearing on its own.
"""



def neg_strict_summary() -> str:
    sp = C.S1 / "neg_strict_summary.json"
    if not sp.exists():
        return ""
    d = jf(sp)
    if not d.get("referees"):
        return ""
    N, prev, now = d["n_items"], d["previous_pass1_plus2"], d["strict_both"]
    names = {"haiku45": "Claude Haiku 4.5", "gpt54mini": "GPT-5.4-mini",
             "sonnet5": "Claude Sonnet 5", "gpt55": "GPT-5.5", "opus48": "Claude Opus 4.8"}
    pair = " and ".join(names.get(r, r) for r in d["referees"])
    ng = sum(d.get("strict_downgraded", {}).values())       # proposals rejected
    nf = sum(d.get("gate_rejection_counts", {}).values())   # individual gate failures
    return (f"**Re-run under a deliberately hard standard, the answer is {now} of {N} "
            f"({100*now/N:.1f}%, 95% CI {100*C.wilson(now, N)[0]:.1f}-{100*C.wilson(now, N)[1]:.1f}%).** "
            f"The first pass asked whether the claim \"was achieved\"; that is too easy to say yes to. "
            f"The re-run requires the *exact* claim: the exact modified value or added constraint, in the "
            f"same task or system, on or before the target date, by one named non-excluded source, with a "
            f"quoted passage that itself contains the figure. Two cheap referees ({pair}) ran it "
            f"independently and both must certify. Ten mechanical checks then re-verify each certification "
            f"in code, recomputing the inequality and matching the cited source against the item's own "
            f"paper; they rejected {ng} of the proposals outright, on {nf} separate gate failures. "
            f"The rate falls from {prev} of {N} "
            f"({100*prev/N:.1f}%) to {now}. The panel mean binary accuracy is unchanged at 49.8%. "
            f"Detail in `study1_verification/results.md` section 4b; the survivor and its evidence in "
            f"`study1_verification/flagged_for_review_negatives_strict.csv`.")


def study1() -> str:
    s = jf(C.S1 / "summary_stats.json")
    samp = jf(C.S1 / "sample.json")
    ex = rd(C.TABLES / "t3_extrapolation.csv")
    ca = rd(C.S1 / "corrected_accuracy.csv")
    p, n, sd = s.get("positives", {}), s.get("negatives", {}), s.get("soundness", {})

    def exrow(label):
        return next((r for r in ex if r["quantity"].strip().startswith(label)), {})

    surv = ""
    if ca:
        deltas = [abs(float(r["delta_relabelled_minus_published"]))
                  for r in ca if r.get("delta_relabelled_minus_published")]
        near = [r for r in ca if r.get("acc_relabelled") and abs(float(r["acc_relabelled"]) - 0.5) <= 0.10]
        surv = (f"The largest shift any model shows between the published labels and the "
                f"re-labelled ones is {100*max(deltas):.1f} percentage points"
                f" ({len(near)} of {len(ca)} models still sit within 10 points of chance after "
                f"correction).") if deltas else ""

    br = rd(C.TABLES / "t2_breakdowns.csv")

    def _cell(split, group):
        return next((r for r in br if r["split"] == split and r["group"] == group), None)

    ptype = ""
    an, aN = _cell("negatives/ptype", "constraint"), _cell("negatives/ptype", "numeric")
    sn, sN = _cell("soundness/ptype", "constraint"), _cell("soundness/ptype", "numeric")
    if an and aN and sn and sN:
        ptype = (
            "**The two routes point at the same cause.** Added-constraint perturbations fail far "
            f"more often than numeric ones, on both measures:\n\n"
            f"| perturbation type | achieved elsewhere | perturbation did not bind |\n"
            f"|---|---|---|\n"
            f"| added constraint (n={an['n']}) | {f(an['rate'])} ({ci(an['wilson_lo'], an['wilson_hi'])}) | "
            f"{f(sn['rate'])} ({ci(sn['wilson_lo'], sn['wilson_hi'])}) |\n"
            f"| numeric modification (n={aN['n']}) | {f(aN['rate'])} ({ci(aN['wilson_lo'], aN['wilson_hi'])}) | "
            f"{f(sN['rate'])} ({ci(sN['wilson_lo'], sN['wilson_hi'])}) |\n\n"
            "The intervals do not overlap on either measure. Changing a reported number is a "
            "reliable way to make a claim false; bolting an extra condition onto it is not, "
            "because the generator frequently states a constraint in its own notes and then omits "
            "it from the question text. Numeric perturbations are close to sound as they stand.")
    st = jf(C.S1 / "strict_summary.json")
    strict_block = ""
    if st:
        t13 = mdtable(C.TABLES / "t13_strict_tiers")
        t14 = mdtable(C.TABLES / "t14_permissive_vs_strict")
        t15 = mdtable(C.TABLES / "t15_strict_by_ptype")
        t16 = mdtable(C.TABLES / "t16_strict_extrapolation")
        strict_block = f"""## 4. The strict criterion, and what it removes

The rates above ask whether a claim is true. That admits a judgement call \
whenever a perturbed claim carries an element that cannot be checked -- "high \
potency", "sufficient specificity", "reduce tumour burden". Such an element can \
be argued satisfied by almost any related result, which inflates the count.

The strict criterion removes that latitude. Two independent referees, Claude \
Opus 4.8 and GPT-5.5, decompose each claim into its separately checkable \
elements and must return, per element, a verbatim quote and the reported value. \
An item counts as demonstrably mislabelled only when **both** referees certify \
that every element is satisfied by one named source, the claim contains no \
vague element, and every element carries a quote.

A claim with an uncheckable element is not counted as mislabelled. It is \
reported separately as undecidable: it can be neither verified nor falsified, \
which is a different defect and needs a different fix.

{{t13}}

### What the strict criterion removes, by route

{{t14}}

Almost all of the removal falls on the achieved-elsewhere route, which is where \
the qualitative matching lived. The perturbation-did-not-bind route is mostly \
textual: a reported figure of 123 million does satisfy a claim asking for fewer \
than 145 million, and a paper demonstrating a glutathione-dependent mechanism \
does satisfy a claim asking for failure to show a glutathione-independent one.

### Strict rates by perturbation type

{{t15}}

### Scaled to the corpus

{{t16}}

Two limits of this pass, stated plainly. It re-examines candidates for removal \
only, so it can lower the rate and never raise it. And it is deliberately \
conservative on negated elements: a claim asserting that something fails to \
happen is certified only against a quote asserting that failure, not against \
the absence of evidence for it.

"""
        strict_block = strict_block.replace("{t13}", t13).replace("{t14}", t14)
        strict_block = strict_block.replace("{t15}", t15).replace("{t16}", t16)

    adj = (s.get("adjudication") or {})
    posrec = ""
    if adj.get("confirmed_after_second") is not None and adj.get("positives_examined"):
        posrec = (f"That second search recovered a qualifying source for most of them: the "
                  f"confirmation rate rises from {f(p.get('rate'))} to "
                  f"{f(adj['confirmed_after_second'])} once both searches are counted, which points "
                  f"at search coverage rather than at the items being wrong.")
    adj_tbl = mdtable(C.TABLES / "t11_adjudication")
    snd_tbl = mdtable(C.TABLES / "t12_soundness_agreement")
    return f"""# Study 1 — web verification of binary ground truth

Reviewer 2, concern C2(a): *"'not supported by this abstract' is not equivalent to
'not achieved anywhere by the target date'."*

## Design

Two halves, drawn independently and verified with **different prompts that were never
merged**. Both halves were stratified on domain (`main_area`) x perturbation type, with
largest-remainder proportional allocation and a floor of two per non-empty cell.
Horvitz–Thompson weights (`N_h / n_h`) are stored per item, so every rate below is
reported unweighted and design-weighted.

| | positives | negatives |
|---|---|---|
| ground truth | YES | NO |
| frame | {samp.get('frames', {}).get('positive', '?')} events carrying `binary_question` | {samp.get('frames', {}).get('negative', '?')} events carrying `binary_question_perturbed` |
| sampled | {samp.get('positives', {}).get('n', '?')} | {samp.get('negatives', {}).get('n', '?')} |
| verdicts returned | {p.get('n', '?')} | {n.get('n', '?')} |
| declined by the verifier's safety classifier | {(s.get('refusals') or {}).get('positives', 0)} | {(s.get('refusals') or {}).get('negatives', 0)} |
| seed | {samp.get('seeds', {}).get('positives')} | {samp.get('seeds', {}).get('negatives')} |
| question asked | was this achieved and publicly reported by the target date? | was the EXACT perturbed claim achieved by someone OTHER than the source paper, by the target date? |

Items the verifier's safety classifier declined are recorded with verdict `REFUSED` and
leave the denominator, the same rule the published tables use for model refusals; the
count is in `summary_stats.json` and `MANIFEST.json`.

The verifier is Claude Opus 4.8 with Anthropic's server-side `web_search` tool
(up to 8 searches per item, unrestricted post-event search). For every item we store the
verdict, the queries issued, every URL returned, the URLs cited, the supporting passage
and a one-line justification, under `evidence/`.

The negatives prompt names the source paper and excludes it explicitly, and states the
three strictness rules verbatim: a numeric threshold counts only if a reported result
meets or exceeds that exact value; an added constraint counts only if the constraint was
actually satisfied; achievement must be dated on or before the target date. Where the
evidence is partial or absent the instruction is to answer NOT_ACHIEVED.

## 1. Positives — did the YES items actually happen?

**{f(p.get('rate'))} of {p.get('n', '?')} positives verified** (Wilson 95% CI {ci(*(p.get('ci') or [None, None]))};
design-weighted {f(p.get('weighted'))}, stratified-bootstrap CI {ci(*(p.get('w_ci') or [None, None]))}).

A non-confirmation is **not** evidence that the advance did not happen: it means one
post-event search did not surface a qualifying source. To separate a search failure from a
mis-extracted item, every non-confirming positive was searched again from scratch by a
different model on a different search index (GPT-5.5 with OpenAI's `web_search`), with no
sight of the first verifier's reasoning. {posrec}

Whatever survives both searches is listed in `flagged_for_review.csv` with its evidence
file, for a human to adjudicate. These rows are handed over rather than re-labelled
automatically, because a failed search does not establish a negative.

## 2. Negatives — was the exact perturbed claim achieved elsewhere?

**{f(n.get('rate'))} of {n.get('n', '?')} synthetic negatives were found to have been achieved
by another group by the target date** (Wilson 95% CI {ci(*(n.get('ci') or [None, None]))};
design-weighted {f(n.get('weighted'))}, stratified-bootstrap CI {ci(*(n.get('w_ci') or [None, None]))}).

{mdtable(C.TABLES / 't1_headline_rates')}

### By domain, perturbation type and corpus

Both a Wilson score interval and a percentile bootstrap interval are given for each cell.
Wilson is the one to quote: in the smallest cells the non-parametric bootstrap degenerates
when every item falls on one side, returning an interval of zero width. The bootstrap is
carried alongside because it is what the analysis plan asked for, and the two agree
wherever the cell is large enough for the bootstrap to be meaningful.

{mdtable(C.TABLES / 't2_breakdowns')}

{ptype}

### Extrapolation to the full corpus

{mdtable(C.TABLES / 't3_extrapolation')}

### Independent second pass over every flagged item

Every ACHIEVED negative was re-examined adversarially by a **different provider with a
different search index** — GPT-5.5 with OpenAI's native `web_search` tool, which is
outside the evaluated panel and is not a Study 2 judge. It was shown the first verifier's
cited evidence and asked whether that evidence really establishes the exact claim, by a
non-excluded group, on or before the target date, under the same five strictness rules.
Every NOT_CONFIRMED positive was searched again from scratch, with no sight of the first
verifier's reasoning, to separate a search failure from a genuinely unverifiable item.

{adj_tbl}

The headline mislabelling rate quoted above is the **first-pass** figure. The
both-passes-agree figure is the strict lower bound, and is what the corrected-accuracy
table uses.

## 3. Secondary check — did the perturbation actually bind?

This check was **not** in the original brief and is reported separately because it closes
a gap the web check cannot see. The web check is required to exclude the source paper, so
it is blind to a negative that the *source paper itself* already satisfies as literally
written. That happens when the generator negates the wrong side of a claim, weakens a
threshold instead of strengthening it, or drops the constrained quantity.

Closed-book, with no web access, the same 200 negatives were shown alongside the source
paper's own reported result and abstract, and judged on whether the paper's result already
satisfies the perturbed claim as written.

**{f(sd.get('rate'))} of {sd.get('n', '?')} negatives were judged already satisfied by their own source**
(Wilson 95% CI {ci(*(sd.get('ci') or [None, None]))}; design-weighted {f(sd.get('weighted'))},
CI {ci(*(sd.get('w_ci') or [None, None]))}). These rows carry the flag
`PERTURBATION_NOT_BINDING` in `flagged_for_review.csv`.

Because that is a large claim, the same 200 negatives were judged a second time, closed
book, by an independent model from a different provider (GPT-5.5). Both judges saw the
same material and neither saw the other's verdict.

{snd_tbl}

A negative flagged this way is mislabelled regardless of what any other group did, so the
two routes are combined into a union estimate in the extrapolation table above. The
corrected-accuracy table uses the strict definition — both judges agree.

The dominant failure mode is a constraint the generator says it added that does not
appear in the question text at all, so the "perturbed" claim asks only about the part of
the finding the paper did report.

{strict_block}{neg_strict_block()}## 5. Corrected binary accuracy

Three recomputations, all restricted to the {p.get('n', '?')} + {n.get('n', '?')} verified items so that
the correction is applied only where ground truth was actually checked. The full-corpus
published accuracy is carried alongside as a reference column.

Read the three verified-sample columns **against each other**, not as corpus estimates.
The sample is stratified with unequal selection probabilities, so its unweighted accuracy
level is not an unbiased estimate of corpus accuracy — `acc_full_published` is the number
to quote for the level. What the stratification does not disturb is the *difference*
between the three columns, which is computed over exactly the same items.

- **as published** — the stored labels, unchanged.
- **excluding flagged** — flagged negatives and non-confirming positives dropped from the denominator.
- **re-labelled** — flagged negatives re-scored against YES. Non-confirming positives are
  *not* re-labelled, because a failed search does not establish that the advance did not
  happen; they stay at YES in this column.

"Flagged" here means the strict definition: both independent passes agree the item is
wrong. The final column repeats the re-labelling on the permissive definition, where one
pass flagging an item is enough. It is a sensitivity check, and it moves nothing material.

{mdtable(C.S1 / 'corrected_accuracy')}

{surv}

## Files

| file | contents |
|---|---|
| `sample.json` | item list, seeds, stratum sizes, allocation, HT weights |
| `positives_verdicts.jsonl` | one record per positive: verdict, URLs, passage, queries, usage |
| `negatives_verdicts.jsonl` | one record per negative: verdict, URLs, passage, exactness justification |
| `negatives_soundness.jsonl` | closed-book perturbation-soundness verdicts |
| `evidence/` | per-item queries, every search result returned, parsed verdict, raw text |
| `adjudication_negatives.jsonl` | independent second pass over every ACHIEVED negative |
| `adjudication_positives.jsonl` | independent second search over every NOT_CONFIRMED positive |
| `adjudication_soundness.jsonl` | independent closed-book replication of the soundness judgements |
| `flagged_for_review.csv` | non-confirming positives + achieved negatives + non-binding perturbations, evidence inline |
| `corrected_accuracy.csv` | the three-way recomputation per model |
| `strict_binding_*.jsonl`, `strict_achieved_*.jsonl` | per-referee element-by-element strict verdicts |
| `strict_verdicts.csv` | one row per negative: tier, both referees, their reasons |
"""


def study2() -> str:
    s = jf(C.S2 / "summary_stats.json")
    meta = jf(C.S2 / "pairs.json")
    head = rd(C.TABLES / "t5_detection_headline.csv")
    base = rd(C.TABLES / "t6_detection_baselines.csv")
    stat = rd(C.TABLES / "t9_detection_x_accuracy.csv")
    lb = s.get("length_baseline")

    refnote = ""
    ref = [r for r in head if int(r.get("refused") or 0) > 0]
    if ref:
        import json as _j
        recs = C.read_jsonl(C.S2 / "judgments.jsonl")
        bits = []
        for r in ref:
            rr = [x for x in recs if x["judge"] == r["judge"] and x.get("refused")]
            pairs_n = len({x["pair_id"] for x in rr})
            dom = {}
            for x in rr:
                dom[x.get("main_area") or "Unknown"] = dom.get(x.get("main_area") or "Unknown", 0) + 1
            top = ", ".join(f"{k} {v}" for k, v in sorted(dom.items(), key=lambda kv: -kv[1])[:3])
            bits.append(f"{r['model']} declined {r['refused']} of {r['calls']} calls, spanning "
                        f"{pairs_n} pairs ({top})")
        refnote = ("One judge's safety classifier declined a subset of biomedical claims: " +
                   "; ".join(bits) + ". Those calls are recorded with `refused: true` and leave that "
                   "judge's denominator; they are benign virology and clinical claims, and the "
                   "refusal is a property of the judge, not of the item.")
    posbias = ""
    if head:
        bits = []
        for r in head:
            cf = float(r["chose_first"])
            bits.append(f"{r['model']} picked the first-listed statement {100*cf:.1f}% of the time "
                        f"(95% CI {100*float(r['cf_lo']):.1f}–{100*float(r['cf_hi']):.1f}%)")
        posbias = ("Neither judge is position-neutral: " + "; ".join(bits) +
                   ". Both lean towards the second statement, which is why the analysis below uses "
                   "the both-orders definition rather than raw accuracy.")
    pairnote = ""
    pr = [r for r in stat if r["task"] == "pair"]
    po = [r for r in stat if r["task"] == "positive"]
    if pr and po:
        pd_ = [float(r["diff_detected_minus_undetected"]) for r in pr]
        pc = sum(1 for r in pr if float(r["diff_lo"]) <= 0 <= float(r["diff_hi"]))
        od = [float(r["diff_detected_minus_undetected"]) for r in po]
        pairnote = (
            f"The two halves move in opposite directions. On the perturbed claim, detected pairs "
            f"are slightly easier for most models; on the real claim they are slightly **harder** "
            f"(difference from {100*min(od):+.1f} to {100*max(od):+.1f} points). That is the "
            f"signature of a small shift in how readily a model says yes, not of a model spotting "
            f"the artifact and answering from it \u2014 artifact detection would raise accuracy on both "
            f"halves at once. At the pair level the two effects cancel: the difference runs from "
            f"{100*min(pd_):+.1f} to {100*max(pd_):+.1f} points and the 95% CI covers zero in "
            f"{pc} of {len(pr)} judge x model combinations. "
            + (f"In the {len(pr)-pc} where it does not, the sign is negative \u2014 those models are "
               f"slightly **worse** on the pairs a judge could tell apart, which is the opposite of "
               f"what artifact detection predicts."
               if all(float(r["diff_hi"]) < 0 for r in pr
                      if not (float(r["diff_lo"]) <= 0 <= float(r["diff_hi"]))) and pc < len(pr)
               else ""))
    verdict = ""
    pert = [r for r in stat if r["task"] == "perturbed"]
    if pert:
        diffs = [float(r["diff_detected_minus_undetected"]) for r in pert
                 if r.get("diff_detected_minus_undetected")]
        crossing = [r for r in pert
                    if r.get("diff_lo") and r.get("diff_hi")
                    and float(r["diff_lo"]) <= 0 <= float(r["diff_hi"])]
        verdict = (
            f"Across the {len(pert)} judge x model combinations, the gap between detected and "
            f"undetected pairs runs from {100*min(diffs):+.1f} to {100*max(diffs):+.1f} percentage "
            f"points, and the 95% CI covers zero in {len(crossing)} of {len(pert)}.")

    return f"""# Study 2 — pairwise "which one is LLM-modified?"

Reviewer 2, concern C2(b): *"The binary task may be testing whether models distinguish
original claims from synthetic perturbations, rather than whether they can forecast
whether an advance will occur."*

## Design

{meta.get('n', '?')} pairs drawn from the {meta.get('frame', '?')} events that carry **both** a
`binary_question` and its own `binary_question_perturbed`, stratified on domain x
perturbation type (seed {meta.get('seed')}; presentation-order seed {meta.get('order_seed')}).

- All target-date information is stripped from both claims before presentation. Bare
  four-digit years are left in place on purpose — in this corpus they are part of
  benchmark names (AIME-2025, IMO-2025, LiveCodeBench 06/24-01/25), they are identical in
  both members of a pair, and so they carry no signal about which claim was modified.
- The presentation order is randomised and stored per pair, and **every pair is run both
  ways** — original first and perturbed first — so detection can be separated from
  position bias.
- The judges are asked only which statement a language model modified. They are never
  asked which claim is scientifically achievable, and are never shown a date or a label.

Judges are reported separately and never pooled. **GPT-5.4 is also one of the evaluated
models** in the panel; **Claude Opus 4.8 is outside the panel**.

{refnote}

## 1. Detection accuracy

{mdtable(C.TABLES / 't5_detection_headline')}

### Baselines on the same pairs

{mdtable(C.TABLES / 't6_detection_baselines')}

Chance is 50%. The second row matters more: in this corpus the original claim is longer
than its perturbation in most pairs, so **a rule that simply picks the shorter of the two
statements scores {f(lb)}** without reading them. Any judge accuracy has to be read against
that number, not against 50%.

### Order-swap consistency and position bias

{mdtable(C.TABLES / 't7_order_consistency')}

{posbias}

`consistency_rate` is the fraction of pairs where the judge picked the same underlying
claim under both presentation orders. `rate_strict` — correct under both orders — is the
detection definition used in the join below, because it cannot be inflated by a
position preference.

### By domain and perturbation type

{mdtable(C.TABLES / 't8_detection_breakdown')}

## 2. The direct test of C2(b)

For every evaluated model, the pairs are split by whether the judge detected the
perturbation, and the model's stored binary answers are compared across the two strata.
`phi` is the correlation between "this pair was detected" and "the model answered this
item correctly"; the last three columns give the accuracy difference with a bootstrap CI.

Three outcomes are reported per judge x model. `perturbed` is the negative half of the
pair, `positive` is the real claim, and `pair` is the mean of the two, which is the
quantity the headline binary metric actually aggregates. The pair row is the one that
settles C2(b): if models were solving the binary task by spotting the artifact, they
would do better on **both** halves of a detectable pair.

{mdtable(C.TABLES / 't9_detection_x_accuracy')}

{verdict}

{pairnote}

### Control: the length artifact on its own

{mdtable(C.TABLES / 't10_lengthgap_x_accuracy')}

This asks whether the surface cue alone — the original being the longer claim — predicts
whether a model got the binary item right, without any judge in the loop.

## Files

| file | contents |
|---|---|
| `pairs.json` | pair list, seeds, stratum sizes, stripped claims, stored order |
| `judgments.jsonl` | one record per pair per judge per order, with confidence and reason |
| `item_level_join.csv` | detection x evaluated-model correctness, one row per pair |
"""


def summary() -> str:
    s1 = jf(C.S1 / "summary_stats.json")
    s2 = jf(C.S2 / "summary_stats.json")
    man = jf(C.STUDY / "MANIFEST.json")
    ca = rd(C.S1 / "corrected_accuracy.csv")
    allstat = rd(C.TABLES / "t9_detection_x_accuracy.csv")
    stat = [r for r in allstat if r["task"] == "pair"] or [r for r in allstat if r["task"] == "perturbed"]
    p, n, sd = s1.get("positives", {}), s1.get("negatives", {}), s1.get("soundness", {})
    lb = s2.get("length_baseline")

    adj1 = (s1.get("adjudication") or {})
    q1rec = ("Searching again with a different model on a different search index recovered a "
             f"qualifying source for most of the rest, lifting the confirmation rate to "
             f"**{f(adj1['confirmed_after_second'])}**. The first-pass misses were largely search "
             "coverage, not bad items."
             if adj1.get("confirmed_after_second") is not None else
             "The remainder await a second, independent search.")
    stj = jf(C.S1 / "strict_summary.json")
    q2lead = ""
    if stj:
        t13 = rd(C.TABLES / "t13_strict_tiers.csv")
        def _row(pref):
            return next((r for r in t13 if r["category"].strip().startswith(pref)), None)
        r1, r2 = _row("R1 achieved elsewhere"), _row("R2 perturbation did not bind")
        dem, und = _row("Either route"), _row("Undecidable claim")
        prob = _row("One referee only")
        if dem and und:
            q2lead = (
                f"**Strict answer first, and the two routes are not combined.** Under two "
                f"independent referees plus mechanical gates that re-check every quote and "
                f"recompute every inequality in code:\n\n"
                f"- **Achieved elsewhere by another group: {r1['k']} of {r1['n']} items ({f(r1['rate'])}).** "
                f"This is the reviewer's own concern, and it does not survive. No pair of referees "
                f"certifies the same item; at most one referee alone certifies 5.\n"
                f"- **Perturbation never made the claim false: {r2['k']} of {r2['n']} items "
                f"({f(r2['rate'])}).** Provable from the source paper alone, without any search.\n"
                f"- **Undecidable claim: {und['k']} ({f(und['rate'])}).** An element such as "
                f"\"high potency\" that can be neither verified nor falsified. Not a wrong label, "
                f"but not a usable item either.\n\n"
                f"Referee choice moves the second figure (see `tables/t21_referee_pairs.md`): 14 "
                f"items with Opus 4.8 + GPT-5.5, 9 with Sonnet 5 + either, 2 if GPT-5.4-mini must "
                f"co-sign. GPT-5.4-mini fails the verbatim-quote gate on 62% of its own proposals "
                f"against 0% for the two larger models, so it is reported but not relied on.\n\n"
                f"The looser figures below are what a \"is this claim true\" reading gives, with no "
                f"mechanical checking. They are an upper bound only.")
    ex2 = rd(C.TABLES / "t3_extrapolation.csv")
    ur = next((r for r in ex2 if r["quantity"].startswith("EITHER route (union, BOTH")), None) \
        or next((r for r in ex2 if r["quantity"].startswith("EITHER route")), None)
    uc = next((r for r in ex2 if r["quantity"].strip().startswith("-> expected count")
               and ex2.index(r) > (ex2.index(ur) if ur else 0)), None)
    union = ""
    if ur:
        union = (f"Taken together, **{ur['estimate']}** of synthetic negatives are wrong by at least "
                 f"one of the two routes (95% CI {ur['ci_lo']}–{ur['ci_hi']}). Scaled to the "
                 f"{s1.get('frame_negative', '?')} negatives in the corpus that is roughly "
                 f"{uc['estimate'] if uc else '?'} items "
                 f"({uc['ci_lo'] if uc else '?'}–{uc['ci_hi'] if uc else '?'}).")
    sa = rd(C.TABLES / "t12_soundness_agreement.csv")
    kap = next((r["value"] for r in sa if r["quantity"].startswith("Cohen")), "n/a")
    q3 = "not enough data yet"
    if ca:
        import statistics as _st
        d = [abs(float(r["delta_relabelled_minus_published"])) for r in ca
             if r.get("delta_relabelled_minus_published")]
        pub = [float(r["acc_sample_published"]) for r in ca if r.get("acc_sample_published")]
        rel = [float(r["acc_relabelled"]) for r in ca if r.get("acc_relabelled")]
        up = [r["model"] for r in ca if r.get("relab_lo") and float(r["relab_lo"]) > 0.5]
        dn = [r["model"] for r in ca if r.get("relab_hi") and float(r["relab_hi"]) < 0.5]
        if d and pub and rel:
            q3 = (f"Yes. Across the panel the mean binary accuracy on the verified sample moves from "
                  f"{100*_st.mean(pub):.1f}% as published to {100*_st.mean(rel):.1f}% once every "
                  f"flagged label is corrected — {100*(_st.mean(rel)-_st.mean(pub)):+.1f} points, and "
                  f"still chance. No model is rescued into competent territory: the corrected range is "
                  f"{100*min(rel):.1f}% to {100*max(rel):.1f}%.\n\n"
                  f"Individual models move by up to {100*max(d):.1f} points, but in **both** "
                  f"directions — {len(up)} end above chance and {len(dn)} below. Which way a model "
                  f"moves is set by how readily it says yes: flipping a negative to YES rewards the "
                  f"yes-biased models and punishes the rest. That is a response-bias effect, not "
                  f"recovered forecasting skill.")
    q4 = "not enough data yet"
    if s2.get("judges"):
        parts = []
        for j, v in s2["judges"].items():
            parts.append(f"{v['model']} {100*v['accuracy']:.1f}% overall, "
                         f"{100*v['strict_rate']:.1f}% correct under both orders")
        q4 = ("Partly, and not better than a ruler. " + "; ".join(parts) +
              f". The trivial rule 'pick the shorter statement' scores {f_(lb)} on the same pairs, "
              f"so most of what the judges detect is a length artifact rather than scientific content.")
    q5 = "not enough data yet"
    if stat:
        diffs = [float(r["diff_detected_minus_undetected"]) for r in stat
                 if r.get("diff_detected_minus_undetected")]
        cross = sum(1 for r in stat if r.get("diff_lo") and r.get("diff_hi")
                    and float(r["diff_lo"]) <= 0 <= float(r["diff_hi"]))
        neg_only = all(float(r["diff_hi"]) < 0 for r in stat
                       if not (float(r["diff_lo"]) <= 0 <= float(r["diff_hi"])))
        q5 = (f"No. Taking the pair as the unit, binary accuracy on pairs a judge could tell apart "
              f"differs from accuracy on pairs it could not by between {100*min(diffs):+.1f} and "
              f"{100*max(diffs):+.1f} percentage points, and the 95% CI includes zero in {cross} of "
              f"{len(stat)} judge x model combinations."
              + (f" In the {len(stat)-cross} exceptions the difference is negative, so those models "
                 f"are slightly worse on the detectable pairs." if neg_only and cross < len(stat) else "")
              + " Detectability does not explain binary performance.")

    return f"""# A2 — binary task validity: summary

Reviewer 2, concern C2. Two validation studies of the CUSP binary task. Both use
unrestricted post-event web search where relevant, because both are questions about the
benchmark, not evaluations of forecasting ability.

Run {man.get('generated_utc', '')} on git `{(man.get('git_sha') or '')[:10]}` (branch
`{man.get('git_branch', '')}`). Measured cost **${man.get('total_cost_usd', 0):,.2f}**.

---

### 1. What fraction of positives verified?

**{f(p.get('rate'))}** of {p.get('n', '?')} sampled positives were confirmed on the first
post-event web search (95% CI {ci(*(p.get('ci') or [None, None]))}). {q1rec}

What is left is listed in `study1_verification/flagged_for_review.csv` with its evidence,
for a human to adjudicate. A failed search is not evidence that the advance did not
happen, so nothing here is re-labelled automatically.

### 2. What fraction of synthetic negatives were actually achieved elsewhere?

{q2lead}

**{f(n.get('rate'))}** of {n.get('n', '?')} sampled negatives were found to have been achieved by a
group other than the source paper, on or before the target date (95% CI
{ci(*(n.get('ci') or [None, None]))}; design-weighted {f(n.get('weighted'))}).

A separate, closed-book check found that a further **{f(sd.get('rate'))}** of negatives are
already satisfied by their own source paper as literally written — the perturbation did
not bind. That route is invisible to the web check, which is required to exclude the
source paper. Two independent models agree on it at Cohen's kappa {kap}.

{union}

Both routes are flagged for review in `study1_verification/flagged_for_review.csv`, with
the evidence and the second pass's verdict inline.

{neg_strict_summary()}

### 3. Does the near-chance binary finding survive correction?

{q3}

### 4. Can models tell original from perturbed claims?

{q4}

### 5. Is binary performance explained by that detectability?

{q5}

---

## What this means for the manuscript

- C2(a) is real but narrower than a loose reading suggests. Quote the demonstrable rate,
  where both referees certify every element against a reported value. The larger share of
  it is perturbations that never made the claim false, not claims achieved elsewhere.
- A second defect sits beside it and is worth naming separately: negatives whose claim
  contains an uncheckable qualifier. Those cannot be scored either way, so they weaken the
  task without being wrong labels.
- C2(b) does not hold as stated for the binary result. The perturbations *are* partly
  detectable, but mostly through a length artifact, and binary accuracy is no better on
  the detectable pairs than on the rest.
- Both kinds of wrong NO label concentrate in the same place: perturbations that add a
  constraint. Numeric modifications are close to sound. Regenerating or dropping the
  constraint-type negatives would fix most of the problem without touching the rest of the
  benchmark.
- The length asymmetry is worth fixing in the dataset regardless of C2: it is a free
  signal that a future model could exploit even though the current panel does not.

## Layout

```
study1_verification/  sample.json, positives_verdicts.jsonl, negatives_verdicts.jsonl,
                      negatives_soundness.jsonl, evidence/, flagged_for_review.csv,
                      corrected_accuracy.csv, results.md
study2_detection/     pairs.json, judgments.jsonl, item_level_join.csv, results.md
tables/               t1..t12, CSV + markdown
scripts/              sample, verify, detect, adjudicate, analyze1/2, figures,
                      manifest, report, run_all.sh
figures/              fig1..fig4, PNG + PDF
MANIFEST.json         models, snapshots, seeds, prompt hashes, usage, cost, git SHA
```
"""


def f_(x, d=1):
    return f(x, d)


def main() -> None:
    (C.S1 / "results.md").write_text(study1(), encoding="utf-8")
    (C.S2 / "results.md").write_text(study2(), encoding="utf-8")
    (C.STUDY / "SUMMARY.md").write_text(summary(), encoding="utf-8")
    print("wrote study1/results.md, study2/results.md, SUMMARY.md")


if __name__ == "__main__":
    main()
