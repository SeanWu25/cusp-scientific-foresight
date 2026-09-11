#!/usr/bin/env python3

from __future__ import annotations
import argparse, json, os, sys, time
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

FRQ_SYSTEM_PROMPT = """You are a strict scientific benchmark validator.

Your task is to evaluate the Free Response Question (FRQ) prompt.
The FRQ usually begins by establishing a "background" or "problem statement" (e.g., "Given the unreliability of proxies for reasoning quality..."). 
Then it asks the user to propose a solution (e.g., "propose a concrete method... by [Date]").

Your primary goal is to evaluate whether the *background premise / problem statement* established in the FRQ is accurate and faithful to the source abstract.

Important rules:
- Extract the premise/background statement embedded in the FRQ.
- Compare this premise directly against the source abstract.
- Does the abstract actually describe this specific problem, challenge, or background context?
- Fail if the FRQ invents a problem, misrepresents the challenge, or contradicts the abstract's framing.
- Pass if the problem statement/background is faithful and accurate to the abstract.
- IGNORE ANY FORECASTING WORDING. Do not penalize the FRQ for asking for a prediction or solution "by March 2026" or any other date. That is expected and required.
- DO NOT evaluate the FRQ for "measurability" or whether it includes specific benchmarks (unlike binary or MCQs). This is a free-response question, so open-ended phrasing asking for a "concrete method" or "implementation plan" is exactly what we want.

Return ONLY valid JSON with this schema:
{
  "verdict": "pass|fail|unclear",
  "score": 1-5,
  "reason": "short explanation",
  "issue_types": ["unfaithful_problem_statement", "none"]
}

Scoring guide:
- 5 = problem statement is perfectly faithful to the abstract
- 4 = mostly faithful, minor semantic differences
- 3 = borderline
- 2 = weak connection to the abstract's actual problem
- 1 = clearly unfaithful, invents a problem not in the abstract
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

        for line in tqdm(fin, initial=already, desc="FRQ Validation"):
            row = json.loads(line)

            abstract = row["source_abstract"]
            frq = row["frq_prompt"]

            # -------------------
            # LLM CALL
            # -------------------

            judge = call_llm(
                f"ABSTRACT:\n{abstract}\n\nFRQ PROMPT:\n{frq}",
                FRQ_SYSTEM_PROMPT
            )

            overall = "accept" if judge.get("verdict") == "pass" else "reject"

            row["frq_llm_judge"] = {
                "frq_prompt_validation": judge,
                "overall_verdict": overall
            }

            print(f"\n[{overall.upper()}] FRQ Prompt: {frq[:100]}...")
            if judge.get("verdict") != "pass":
                print(f"  -> Issue: {judge.get('reason')}")

            # -------------------
            # FIELD REMOVAL
            # -------------------

            removed = []

            if overall != "accept":
                removed.append("frq_prompt")

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
