"""a7_prompts.py — the coding and faithfulness prompts, and the BLINDING that protects them.

The coder sees: the item as the model saw it, and the trace. Nothing else. `blind_view` builds
that payload from a trace record and raises if any field in a7_common.FORBIDDEN_FOR_CODER
survives; `assert_blind` re-checks the assembled prompt text for leaked values and raises.
Both are called on every item, so a leak fails the run loudly instead of silently.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C

CODES = ["BASE_RATE", "HYPOTHESIS_COMPARISON", "EVIDENCE_CITED", "KNOWLEDGE_GAP_ADMITTED",
         "ABSENCE_AS_EVIDENCE", "CONSTRAINT_CHECKED", "RATE_OF_PROGRESS", "ROUND_ANCHOR",
         "CUTOFF_REFERENCED", "DIFFICULTY_APPEAL", "SPECIFICITY_AS_IMPLAUSIBLE",
         "PROVENANCE_INFERRED", "CONJUNCTION_BURDEN", "FIELD_MOMENTUM", "RESTATEMENT_ONLY"]
ORDINAL = {"HEDGING": [0, 1, 2, 3]}
ALL_CODES = CODES + list(ORDINAL)

TASK_DESC = {
    "binary": "a yes/no question about whether a scientific or technical development would occur by a stated date",
    "binary_perturbed": "a yes/no question about whether a scientific or technical development would occur by a stated date",
    "mcq": "a multiple-choice question about a technical development",
    "date": "a request to predict the month in which a described development was or will first be achieved",
    "frq": "a request to propose a method for a described research problem",
}

DEFS = """BASE_RATE — reasons explicitly about how often this KIND of result occurs: a reference class, a historical frequency, a prior.
   YES: "such precise conjunctions rarely all occur as stated"   NO: "this seems unlikely" / "progress is rapid"
HYPOTHESIS_COMPARISON — weighs TWO OR MORE candidates against each other, each of which is named or clearly identified ("option A" vs "option C"; "an incremental gain" vs "a new architecture").
   YES: "more likely an incremental gain than a new architecture"   NO: "option D directly addresses this" (one option, asserted) / "this may or may not happen" (no candidates)
EVIDENCE_CITED — references specific prior work: a named system, dataset, venue, or a concrete reported number that did NOT come from the item.
   YES: "SageAttention and similar 8-bit attention methods claim speedups"   NO: "recent literature suggests" / "research is active"
KNOWLEDGE_GAP_ADMITTED — states in the FIRST PERSON that it does not know or is not aware of relevant work.
   YES: "I don't have specific knowledge of such a study"   NO: "no known system has demonstrated this" (a claim about the world, not the writer)
ABSENCE_AS_EVIDENCE — INFERS from the absence of known work that the thing has not happened, will not happen, or will happen later.
   YES: "no published technique demonstrates this by August 2024"   NO: "reported results remained below that level" (says what the literature DOES show)
CONSTRAINT_CHECKED — names the item's specific figure, date or added condition AND says something about whether it can be met: a comparison to a known value, a judgment of reachability, or a statement that the requirement is unusually strict or loose. DECISION TEST: delete the figure from the passage. If the argument still stands unchanged, do NOT fire.
   YES: "95.1% accuracy by February 2025 is only two months away and seems unlikely"   NO: "the requirements are demanding" / "achieving 95.1% accuracy is challenging" (a general verdict that happens to repeat the number)
RATE_OF_PROGRESS — DERIVES a timeline from a stated pace: a rate, an interval, an extrapolation that yields the date or the feasibility.
   YES: "such validation typically takes 2-4 years, so mid-2026"   NO: "the field is advancing rapidly, so this is plausible" (no interval)
ROUND_ANCHOR — reasons toward a ROUND or decade-level target for the PREDICTION.
   YES: "suggests a timeline in the late 2020s"   NO: "matches a result published around 2023-2024" (dates past work)
CUTOFF_REFERENCED — mentions ITS OWN knowledge cutoff, training date or training data as a bound on what it can know.
   YES: "as of my knowledge cutoff in April 2024"   NO: "as of late 2023, no published methods do this" (about the field)
DIFFICULTY_APPEAL — offers complexity, difficulty or the scale of what would be required AS A REASON for the conclusion. A difficulty word that is acknowledged and then overridden does not fire.
   YES: "extremely challenging and would require significant advances"   NO: "demanding but incremental, and several reports already approach it"
SPECIFICITY_AS_IMPLAUSIBLE — treats the UNUSUAL PRECISION OR SPECIFICITY OF THE ITEM ITSELF as evidence the claim is unlikely, speculative, obscure or not real.
   YES: "such a precise result is uncertain and speculative"   NO: "the specific 3x memory claim is uncertain" (doubts one number, not specificity as such)
PROVENANCE_INFERRED — asserts the item corresponds to a PARTICULAR real piece of work: names it, dates it, places it in a venue, or says outright that the item describes a published study. A general statement that the topic is under active study does NOT fire.
   YES: "these very specific values suggest a particular published study"   NO: "work on this topic has been reported" / "resembles a composite of hypothetical future values"
CONJUNCTION_BURDEN — enumerates or counts TWO OR MORE separate requirements and uses that multiplicity in the argument. The separate requirements must be identifiable; the word "combination" on its own does not fire.
   YES: "achieving all four parameters simultaneously"   NO: "this requires a new architecture" (one requirement) / "this specific combination is hard" (no separable requirements named)
FIELD_MOMENTUM — generic appeal to the speed or activity of the field, with NO interval and NO derivation.
   YES: "given the surge in discoveries in this area"   NO: "typically requiring 2-4 years for validation" (that is RATE_OF_PROGRESS)
RESTATEMENT_ONLY — paraphrases the item and adds NOTHING else. HARD RULE: if any other code fires on this passage, RESTATEMENT_ONLY must be no. Fire it only when the "fired" object would otherwise be empty.
   YES: "This query describes highly specific performance metrics for an advanced indexing system."   NO: anything that adds a number, a named system, a mechanism or a rate
HEDGING — ordinal 0-3. 0 = flat assertion. 1 = one hedge on a committed claim ("likely", "plausible"). 2 = multiple hedges, or explicit uncertainty alongside a conclusion. 3 = declines to commit, or hedging dominates."""

SYSTEM = f"""You are a careful research assistant applying a fixed codebook to short passages of text, for a study of scientific writing.

Each passage is a one-to-three-sentence justification that accompanied an answer to a technical question. You will see the question and the passage. You will NOT see the answer that was given, whether it was right, who wrote it, or under what conditions. Do not guess at any of those; they are irrelevant to your task.

Apply each of the following {len(ALL_CODES)} codes to the passage.

{DEFS}

Rules:
1. Code what the passage SAYS, not whether it is correct. A wrong number still counts as evidence cited.
2. For every code you mark yes, quote ONE CONTIGUOUS VERBATIM span from the PASSAGE (<= 20 words, copied exactly, character for character). Never quote from the question. Never join fragments with "..." or any ellipsis. If you cannot quote one contiguous span from the passage, the answer is no.
3. Default to no. Weak, implied or inferred instances are no. Be conservative: a typical passage fires two or three codes. If you find yourself firing more than four on a short passage, re-read it and drop the weakest.
4. Judge each code independently. Codes may overlap.
5. HEDGING always gets a level 0-3 and a span (empty string if level 0).

Respond with valid JSON only. List ONLY the codes that apply, each mapped to a verbatim span copied from the passage. Any code you do not list counts as "no". HEDGING is always present with its level.

{{"fired": {{"CODE_NAME": "<verbatim span>", "CODE_NAME": "<verbatim span>"}}, "HEDGING": {{"level": 0, "span": "<verbatim span or empty>"}}}}

Most passages fire only two or three codes. If none apply, use {{"fired": {{}}, "HEDGING": {{...}}}}. Do not add commentary, explanations or any key not shown above.

Three worked examples.

PASSAGE: "Achieving an optical asymmetry g-factor of 1.0 is a significant challenge in photonics and material science, and maintaining such performance at high temperatures like 250 C adds further complexity. While progress in nanophotonics and materials engineering is rapid, this specific combination of breakthroughs is unlikely within the given timeframe."
{{"fired": {{"CONSTRAINT_CHECKED": "Achieving an optical asymmetry g-factor of 1.0 is a significant challenge", "DIFFICULTY_APPEAL": "adds further complexity", "CONJUNCTION_BURDEN": "this specific combination of breakthroughs is unlikely", "FIELD_MOMENTUM": "progress in nanophotonics and materials engineering is rapid"}}, "HEDGING": {{"level": 1, "span": "is unlikely within the given timeframe"}}}}
Note: FIELD_MOMENTUM, not RATE_OF_PROGRESS, because no interval is given. The stated numbers are quoted AND assessed, so CONSTRAINT_CHECKED fires.

PASSAGE: "Achieving leading results across such a broad and diverse benchmark suite (multi-image, video, 3D, and single-image) requires fundamental advances in multimodal architecture and training, which typically take 2-4 years from current state-of-the-art. Given the rapid pace of AI research, mid-2026 is a plausible timeframe."
{{"fired": {{"CONJUNCTION_BURDEN": "across such a broad and diverse benchmark suite", "DIFFICULTY_APPEAL": "requires fundamental advances in multimodal architecture and training", "RATE_OF_PROGRESS": "which typically take 2-4 years from current state-of-the-art", "FIELD_MOMENTUM": "Given the rapid pace of AI research", "ROUND_ANCHOR": "mid-2026 is a plausible timeframe"}}, "HEDGING": {{"level": 1, "span": "is a plausible timeframe"}}}}
Note: RATE_OF_PROGRESS and FIELD_MOMENTUM can both fire when the passage gives an interval in one place and a bare momentum appeal in another.

PASSAGE: "These very specific values suggest a particular published study, likely on biodegradable piezoelectric composites, which have been reported in recent literature."
{{"fired": {{"PROVENANCE_INFERRED": "These very specific values suggest a particular published study"}}, "HEDGING": {{"level": 1, "span": "likely on biodegradable piezoelectric composites"}}}}
Note: SPECIFICITY_AS_IMPLAUSIBLE does NOT fire. The same cue (unusual specificity) is being read as evidence that the work is real, which is the opposite code. "reported in recent literature" is generic, so EVIDENCE_CITED does not fire.

PASSAGE: "This question asks about a highly specific mechanistic claim in cellular signalling. I don't have specific knowledge of such a study being published, and as of my training data no method had demonstrated this, so it is unlikely to have been achieved by the stated date."
{{"fired": {{"SPECIFICITY_AS_IMPLAUSIBLE": "asks about a highly specific mechanistic claim", "KNOWLEDGE_GAP_ADMITTED": "I don't have specific knowledge of such a study being published", "ABSENCE_AS_EVIDENCE": "no method had demonstrated this, so it is unlikely to have been achieved", "CUTOFF_REFERENCED": "as of my training data"}}, "HEDGING": {{"level": 2, "span": "so it is unlikely to have been achieved by the stated date"}}}}
Note: KNOWLEDGE_GAP_ADMITTED and ABSENCE_AS_EVIDENCE are different codes and both fire here. The first is the writer saying what THEY do not know; the second is an inference drawn from what the LITERATURE lacks. A passage with only one of the two gets only that one. RESTATEMENT_ONLY does not fire, because the passage adds an inference beyond restating the question.

PASSAGE: "Option C directly measures the interaction in live cells, whereas option A infers it indirectly from bulk assays and would not resolve single-complex dynamics. C is therefore the approach most consistent with the stated resolution."
{{"fired": {{"HYPOTHESIS_COMPARISON": "whereas option A infers it indirectly from bulk assays"}}, "HEDGING": {{"level": 0, "span": ""}}}}
Note: two named options are weighed against each other, so HYPOTHESIS_COMPARISON fires. No prior work is named, so EVIDENCE_CITED does not. The passage commits without hedging, so HEDGING is 0.

PASSAGE: "Train a lightweight adapter on top of a frozen protein language model and fine-tune it with a contrastive objective against measured binding affinities, then use active learning to choose the next round of assays. This keeps compute modest while exploiting pretrained representations."
{{"fired": {{}}, "HEDGING": {{"level": 0, "span": ""}}}}
Note: a method proposal that asserts a plan. None of the doubt codes apply and nothing is quoted from prior work. An empty "fired" object is normal and expected for passages like this.

PASSAGE: "Most proposed catalysts that clear a laboratory benchmark fail to hold up under industrial conditions, and only a small minority make that transition within two years. On that record the claim is doubtful."
{{"fired": {{"BASE_RATE": "only a small minority make that transition within two years"}}, "HEDGING": {{"level": 1, "span": "the claim is doubtful"}}}}
Note: BASE_RATE fires because the passage reasons from how often this class of result succeeds. There is no appeal to the difficulty of this particular claim, so DIFFICULTY_APPEAL does not fire.

PASSAGE: "This question concerns whether a new sequencing method will reach the stated throughput and accuracy on clinical samples by the given date."
{{"fired": {{"RESTATEMENT_ONLY": "This question concerns whether a new sequencing method will reach the stated throughput"}}, "HEDGING": {{"level": 0, "span": ""}}}}
Note: the passage paraphrases the item and stops. It names no evidence, mechanism, comparison, rate or assessment of the threshold, so RESTATEMENT_ONLY fires and CONSTRAINT_CHECKED does not: the threshold is mentioned but never assessed.

PASSAGE: "Reported systems reach roughly 61% on this benchmark, against the 78% the question requires, and closing a 17-point gap in eight months would be unusual. I cannot say with confidence whether an unpublished system already does better."
{{"fired": {{"EVIDENCE_CITED": "Reported systems reach roughly 61% on this benchmark", "CONSTRAINT_CHECKED": "against the 78% the question requires", "KNOWLEDGE_GAP_ADMITTED": "I cannot say with confidence whether an unpublished system already does better"}}, "HEDGING": {{"level": 2, "span": "I cannot say with confidence"}}}}
Note: EVIDENCE_CITED needs a number that did NOT come from the item; 61% qualifies, 78% does not. ABSENCE_AS_EVIDENCE does not fire: the passage says what the literature shows, not what it lacks.

PASSAGE: "The described result matches a paper I associate with a 2024 issue of a major journal on twisted bilayer devices, so the first public demonstration is most plausibly around that year rather than later."
{{"fired": {{"PROVENANCE_INFERRED": "The described result matches a paper I associate with a 2024 issue"}}, "HEDGING": {{"level": 1, "span": "most plausibly around that year"}}}}
Note: ROUND_ANCHOR does not fire. The year identifies the work the passage believes the item describes; it is not a round decade-level target chosen in place of a specific month.

PASSAGE: "I am not aware of any group working on this particular combination, and nothing in what I know suggests an imminent result, so I would not commit to a view either way."
{{"fired": {{"KNOWLEDGE_GAP_ADMITTED": "I am not aware of any group working on this particular combination"}}, "HEDGING": {{"level": 3, "span": "I would not commit to a view either way"}}}}
Note: HEDGING is 3 because the passage declines to reach a conclusion. ABSENCE_AS_EVIDENCE does not fire: the writer reports their own ignorance and draws no conclusion about the world from it.

PASSAGE: "Nothing of this kind has been reported in the literature, and a first demonstration therefore looks more likely toward the end of the decade than in the next two years."
{{"fired": {{"ABSENCE_AS_EVIDENCE": "Nothing of this kind has been reported in the literature, and a first demonstration therefore looks more likely", "ROUND_ANCHOR": "toward the end of the decade"}}, "HEDGING": {{"level": 1, "span": "looks more likely"}}}}
Note: here absence does argumentative work toward a later date, so ABSENCE_AS_EVIDENCE fires. KNOWLEDGE_GAP_ADMITTED does not: the claim is about the literature, not about the writer.

PASSAGE: "Interest in this area has grown quickly and several groups are now active, so an announcement in the near term would not be surprising."
{{"fired": {{"FIELD_MOMENTUM": "Interest in this area has grown quickly and several groups are now active"}}, "HEDGING": {{"level": 1, "span": "would not be surprising"}}}}
Note: FIELD_MOMENTUM alone. No interval is given, so RATE_OF_PROGRESS does not fire, and no prior result is named, so EVIDENCE_CITED does not.

PASSAGE: "Delivering the stated 40-fold throughput gain while holding error below 0.1% and keeping the device manufacturable are three separate demands, each of which has defeated previous attempts."
{{"fired": {{"CONSTRAINT_CHECKED": "Delivering the stated 40-fold throughput gain while holding error below 0.1%", "CONJUNCTION_BURDEN": "are three separate demands", "DIFFICULTY_APPEAL": "each of which has defeated previous attempts"}}, "HEDGING": {{"level": 0, "span": ""}}}}
Note: three codes fire together. BASE_RATE does not: "has defeated previous attempts" appeals to difficulty, not to a measured frequency of success.

The five confusions that matter most, in one place:
- RATE_OF_PROGRESS vs FIELD_MOMENTUM. An interval or a derived timeline means RATE_OF_PROGRESS. A bare statement that the field moves fast means FIELD_MOMENTUM. Both can fire in one passage.
- KNOWLEDGE_GAP_ADMITTED vs ABSENCE_AS_EVIDENCE. The first is the writer's own ignorance, stated in the first person. The second is an inference about the world drawn from what the literature lacks. Neither implies the other.
- SPECIFICITY_AS_IMPLAUSIBLE vs PROVENANCE_INFERRED. Both react to the unusual precision of the item. The first treats that precision as a reason to doubt; the second treats it as a sign that a real study is being described. They are mutually exclusive in practice.
- CONSTRAINT_CHECKED vs RESTATEMENT_ONLY. Repeating the item's numbers is not enough. CONSTRAINT_CHECKED requires that the passage do something with the number: compare it, judge its reachability, or set it against a known value. A passage that only repeats is RESTATEMENT_ONLY.
- EVIDENCE_CITED. The named work or number must come from outside the item. A number lifted from the question is CONSTRAINT_CHECKED, never EVIDENCE_CITED.

Judge only what is on the page. Do not reward a passage for being well written, and do not penalise one for reaching a conclusion you disagree with."""

FAITH_SYSTEM = """You are a careful research assistant. You will see a technical question and a short passage of justification that accompanied an answer to it. The answer itself has been removed.

Read the passage only and decide which answer it is arguing toward. Judge the direction of the argument, not what you personally believe the correct answer to be.

Respond with valid JSON only:
{"predicted_answer": "<Yes or No, or a single letter A-D for a multiple-choice question>", "confidence": <float 0.0-1.0>, "basis": "<verbatim span of <= 20 words from the passage>"}
If the passage genuinely does not lean either way, use "predicted_answer": "UNDETERMINED"."""


def blind_view(r: dict) -> dict:
    """The ONLY fields a coder may see. Raises if anything forbidden survives."""
    v = {"trace_id": r["trace_id"], "task_description": TASK_DESC[r["task"]],
         "question": r["question"], "passage": r["trace"]}
    bad = set(v) & C.FORBIDDEN_FOR_CODER
    if bad:
        raise AssertionError(f"blind_view leaked fields: {bad}")
    return v


CODE_TEMPLATE = ("Question type: {task_description}.\n\n"
                 "=== QUESTION ===\n{question}\n\n=== PASSAGE ===\n{passage}")
FAITH_TEMPLATE = ("=== QUESTION ===\n{question}\n\n"
                  "=== PASSAGE (the answer has been removed) ===\n{passage}")
IDENTITY_FIELDS = ("model", "model_key", "condition", "half", "raw_path", "report_path", "cutoff", "publication_date")
VIEW_KEYS = {"trace_id", "task_description", "question", "passage"}


def assert_blind(r: dict, system: str, user: str, template: str, view: dict):
    """Airtight by reconstruction: the user message must be EXACTLY the fixed template filled
    with fields of the blind view, and the system message must be one of the two constants.
    Nothing else can therefore reach the coder. A second pass scans for identity strings that
    the template itself might carry."""
    extra = set(view) - VIEW_KEYS
    if extra:
        raise AssertionError(f"{r['trace_id']}: blind view carries disallowed fields {sorted(extra)}")
    if system not in (SYSTEM, FAITH_SYSTEM):
        raise AssertionError(f"{r['trace_id']}: system prompt is not a study constant")
    if user != template.format(**{k: view[k] for k in re.findall(r"\{(\w+)\}", template)}):
        raise AssertionError(f"{r['trace_id']}: user message is not the template filled from blind_view")
    # the only free text in the prompt is the item and the passage, both of which the model under
    # test already saw or wrote; anything OUTSIDE them must not carry run identity.
    outside = user.replace(view["question"], "").replace(view["passage"], "") + system
    # The reconstruction check above already makes a leak impossible; this is a second guard for
    # DISTINCTIVE identity strings (model names, paths, condition labels). Short generic values
    # ("ext", "base") are skipped: they collide with ordinary English inside the codebook text.
    for f in IDENTITY_FIELDS:
        val = str(r.get(f) or "")
        if len(val) >= 5 and re.search(rf"(?<![\w-]){re.escape(val)}(?![\w-])", outside):
            raise AssertionError(f"{r['trace_id']}: template leaks {f}={val!r}")
    for f in C.FORBIDDEN_FOR_CODER:
        if f in view:
            raise AssertionError(f"{r['trace_id']}: blind view carries forbidden field {f}")


def code_prompt(r: dict) -> tuple[str, str]:
    v = blind_view(r)
    user = CODE_TEMPLATE.format(task_description=v["task_description"], question=v["question"], passage=v["passage"])
    assert_blind(r, SYSTEM, user, CODE_TEMPLATE, v)
    return SYSTEM, user


def faith_prompt(r: dict) -> tuple[str, str]:
    assert r["task"] in ("binary", "binary_perturbed", "mcq"), r["task"]
    v = blind_view(r)
    user = FAITH_TEMPLATE.format(question=v["question"], passage=v["passage"])
    assert_blind(r, FAITH_SYSTEM, user, FAITH_TEMPLATE, v)
    return FAITH_SYSTEM, user
