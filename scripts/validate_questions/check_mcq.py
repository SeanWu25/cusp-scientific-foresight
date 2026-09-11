#!/usr/bin/env python3

from __future__ import annotations
import argparse, json, os, sys, time
from typing import Any, Dict, List, Tuple
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI
import openai

# =========================
# ENV
# =========================

load_dotenv()

from dotenv import load_dotenv
load_dotenv()  # auto-discovers .env from cwd or repo root

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not AZURE_OPENAI_ENDPOINT:
    raise RuntimeError("Missing AZURE_OPENAI_ENDPOINT in .env")
if not AZURE_OPENAI_API_KEY:
    raise RuntimeError("Missing AZURE_OPENAI_API_KEY in .env")

client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
)

# =========================
# PROMPTS
# =========================

STEM_SYSTEM_PROMPT = """You are a strict scientific benchmark validator.

Your task is to evaluate the MCQ problem statement only.

You must check two things:
1. Faithfulness: does the problem statement accurately reflect the source abstract?
2. Verifiability: is the problem statement concrete enough to be objectively answered from the source?

Important rules:
- Judge only the MCQ stem/problem statement.
- Do not judge the answer choices in this call.
- IGNORE ANY FORECASTING WORDING. The stem often asks things like "by March 2026, which approach is most likely to achieve X?". You MUST completely ignore the date, the "likelihood prediction" framing, and speculative timelines. DO NOT penalize the stem for asking about the future.
- Only assess if the scientific core of the question accurately reflects the abstract's methodology/results.
- Fail if the scientific core of the stem changes the claim, introduces unsupported details, or misstates the abstract.
- Fail if the scientific core is vague, underspecified, or not operationalizable.
- Pass only if the core scientific claim is both faithful and concrete.

Examples of FAIL:
- The stem adds a benchmark, metric, or threshold that is not in the abstract.
- The stem uses vague language like "improve performance" with no measurable criterion.
- The stem asks about a claim that cannot be verified from the abstract alone.

Return ONLY valid JSON with this schema:
{
  "verdict": "pass|fail|unclear",
  "score": 1-5,
  "reason": "short explanation",
  "issue_types": ["faithfulness", "verifiability", "none"]
}

Scoring guide:
- 5 = fully faithful and clearly verifiable
- 4 = mostly strong with minor ambiguity
- 3 = borderline
- 2 = weak
- 1 = clearly invalid
"""

ANSWER_SYSTEM_PROMPT = """You are a strict scientific benchmark validator.

Your task is to evaluate the marked correct answer choice only.

You must check whether the selected answer is supported by the source abstract as the correct technical approach, mechanism, or result.

Important rules:
- Judge only the marked correct answer choice.
- Do not judge distractors in this call.
- Pass only if the answer choice is supported or clearly implied by the abstract.
- Fail if the answer choice is unsupported, mismatched, or invents a mechanism not present in the abstract.
- If the abstract gives enough evidence for more than one answer, explain the ambiguity.

Return ONLY valid JSON with this schema:
{
  "verdict": "pass|fail|unclear",
  "score": 1-5,
  "reason": "short explanation",
  "issue_types": ["unsupported_answer", "ambiguous_answer", "none"]
}

Scoring guide:
- 5 = correct and directly supported
- 4 = supported with minor interpretive gap
- 3 = borderline
- 2 = likely incorrect
- 1 = clearly wrong
"""

DISTRACTOR_SYSTEM_PROMPT = """You are a strict scientific benchmark validator.

Your task is to evaluate the incorrect answer choices only.

You must check whether the distractors are:
1. plausible enough to require real reasoning,
2. not directly supported by the abstract,
3. not trivially wrong or obviously eliminated.

Important rules:
- Judge the distractors as a set.
- Do not judge the stem or the correct answer in this call.
- Pass only if the distractors are non-trivial and sufficiently plausible.
- Fail if the distractors are too easy, too obviously wrong, or directly supported by the abstract.
- Fail if the distractors are not meaningfully competitive with the correct answer.

Return ONLY valid JSON with this schema:
{
  "verdict": "pass|fail|unclear",
  "score": 1-5,
  "reason": "short explanation",
  "issue_types": ["too_easy", "unsupported_by_abstract", "not_plausible", "none"]
}

Scoring guide:
- 5 = strong distractors, highly plausible
- 4 = good distractors with minor issues
- 3 = borderline
- 2 = weak distractors
- 1 = trivial or obviously bad distractors
"""

# =========================
# HELPERS
# =========================

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--resume", action="store_true")
    return p.parse_args()

def output_paths(base):
    base = base.replace(".jsonl", "")
    return (
        base + ".full.jsonl",
        base + ".cleaned.jsonl",
        base + ".removed.jsonl"
    )

def safe_json(text):
    try:
        return json.loads(text)
    except:
        return {"verdict": "unclear", "score": 1, "reason": "parse_error"}

def call_llm(prompt, system):
    try:
        r = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role":"system","content":system},
                      {"role":"user","content":prompt}],
            temperature=0,
            response_format={"type":"json_object"}
        )
        return safe_json(r.choices[0].message.content)
    except Exception as e:
        if "content_filter" in str(e):
            return {"verdict":"unclear","score":1,"reason":"content_filter"}
        return {"verdict":"unclear","score":1,"reason":str(e)}

# =========================
# MAIN
# =========================

def process(input_path, output_base, resume):

    full_path, clean_path, removed_path = output_paths(output_base)

    if os.path.dirname(full_path):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

    already = 0
    if resume and os.path.exists(full_path):
        with open(full_path) as f:
            already = sum(1 for _ in f)

    mode = "a" if already > 0 else "w"

    with open(input_path) as fin, \
         open(full_path, mode) as f_full, \
         open(clean_path, mode) as f_clean, \
         open(removed_path, mode) as f_removed:

        # skip processed
        for _ in range(already):
            next(fin, None)

        for line in tqdm(fin, initial=already, desc="MCQ Validation"):
            row = json.loads(line)

            abstract = row["source_abstract"]
            q = row["mcq_question"]
            choices = row["mcq_choices"]
            answer = choices[row["mcq_answer_key"]]

            # -------------------
            # 3 LLM CALLS
            # -------------------

            stem = call_llm(
                f"ABSTRACT:\n{abstract}\n\nQUESTION:\n{q}",
                STEM_SYSTEM_PROMPT
            )
            print(stem)

            correct = call_llm(
                f"ABSTRACT:\n{abstract}\n\nQUESTION:\n{q}\n\nCORRECT ANSWER:\n{answer}",
                ANSWER_SYSTEM_PROMPT
            )
            print(correct)

            if isinstance(choices, dict):
                distractor_choices = dict(choices)
                distractor_choices.pop(row["mcq_answer_key"], None)
            else:
                distractor_choices = list(choices)
                idx = int(row["mcq_answer_key"])
                if 0 <= idx < len(distractor_choices):
                    distractor_choices.pop(idx)

            distractors = call_llm(
                f"ABSTRACT:\n{abstract}\n\nQUESTION:\n{q}\n\nDISTRACTORS:\n{distractor_choices}",
                DISTRACTOR_SYSTEM_PROMPT
            )
            print(distractor_choices)
            print(distractors)

            overall = "accept" if (
                stem["verdict"]=="pass" and
                correct["verdict"]=="pass" and
                distractors["verdict"]=="pass"
            ) else "reject"

            judge = {
                "stem": stem,
                "correct_answer": correct,
                "distractors": distractors,
                "overall_verdict": overall
            }

            row["mcq_llm_judge"] = judge

            print(f"\n[{overall.upper()}] MCQ Question: {q[:100]}...")
            if stem["verdict"] != "pass":
                print(f"  -> Stem issue: {stem.get('reason')}")
            if correct["verdict"] != "pass":
                print(f"  -> Correct Answer issue: {correct.get('reason')}")
            if distractors["verdict"] != "pass":
                print(f"  -> Distractor issue: {distractors.get('reason')}")

            # -------------------
            # FIELD REMOVAL
            # -------------------

            removed = []

            if stem["verdict"]!="pass":
                removed.append("mcq_question")

            if correct["verdict"]!="pass":
                removed.append("mcq_answer_key")

            if distractors["verdict"]!="pass":
                removed.append("mcq_choices")

            clean = dict(row)
            for r in removed:
                clean.pop(r, None)

            # -------------------
            # WRITE
            # -------------------

            f_full.write(json.dumps(row)+"\n")
            f_clean.write(json.dumps(clean)+"\n")
            f_removed.write(json.dumps({
                "id": row.get("id"),
                "removed": removed,
                "judge": judge
            })+"\n")

    print("Done")

# =========================

if __name__ == "__main__":
    args = parse_args()
    process(args.input, args.output, args.resume)