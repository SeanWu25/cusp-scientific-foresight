"""
-----
# Yupeng: Run on 20 rows with gpt-oss-20B:
nohup  python -u run_evaluation/test_LLM.py \
      --input benchmark_data/CUSP/merged_validated_cusp_fixed.jsonl \
      --model_path  /storage3/samchen/gpt-oss-20b \
      --knowledge-cutoff 2024-06  \
        --max-rows 20 \
          > run.log 2>&1 &

# Run with Claude (Anthropic):
python run_evaluation/test_LLM.py \
      --input benchmark_data/CUSP/merged_validated_cusp_fixed.jsonl \
      --provider ANTHROPIC \
      --model claude-sonnet-4-6 \
      --knowledge-cutoff 2024-06 \
      --max-rows 20

# Run with GPT-5.4 via Azure with native web search:
python run_evaluation/test_LLM.py \
      --input benchmark_data/CUSP/merged_validated_cusp_fixed.jsonl \
      --provider AZURE \
      --model gpt-5.4 \
      --azure-endpoint https://BASCOLM.openai.azure.com/openai/v1 \
      --azure-key YOUR_KEY \
      --native-web-search \
      --knowledge-cutoff 2024-06 \
      --max-rows 20

Providers
---------
  AZURE      : Uses AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT from .env
  OPENAI     : Uses OPENAI_API_KEY (and optionally OPENAI_API_BASE) from .env
  ANTHROPIC  : Uses ANTHROPIC_API_KEY from .env
               Default model: claude-sonnet-4-6
               Other options: claude-opus-4-7, claude-haiku-4-5-20251001

Flags
-----
  --native-web-search : Use GPT-5.4's built-in Responses API web search.
                              Per-task URLs and queries are saved in predictions.
"""

from __future__ import annotations

import argparse


import json

import os

import random

import re

import sys

import time

from datetime import datetime

from tqdm import tqdm

_last_predictions_path: str | None = None


def build_parser() -> argparse.ArgumentParser:

    p = argparse.ArgumentParser(
        description="CUSP Benchmark Test Runner — Prompt an LLM and collect predictions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    p.add_argument(
        "--input",
        default=None,
        help="Path to benchmark JSONL (default: auto-download from HuggingFace)",
    )

    p.add_argument(
        "--output-dir",
        default="benchmark_logs",
        help="Directory for output logs (default: benchmark_logs)",
    )

    p.add_argument(
        "--provider",
        choices=["AZURE", "OPENAI", "AZURE_DEEPSEEK", "ANTHROPIC"],
        default="OPENAI",
        help="LLM provider (default: OPENAI)",
    )

    p.add_argument(
        "--model", default=None, help="Model/deployment name (default: from env or gpt-4o)"
    )

    p.add_argument(
        "--knowledge-cutoff",
        default=None,
        help="Only test papers published AFTER this date (YYYY-MM). "
        "If not set, all rows are tested.",
    )

    p.add_argument(
        "--ws-cutoff",
        default=None,
        help="Web search date cutoff (YYYY-MM): only retrieve content published "
        "before this date. Defaults to --knowledge-cutoff if not set.",
    )

    p.add_argument("--max-rows", type=int, default=None, help="Max rows to process (for testing)")

    p.add_argument(
        "--temperature", type=float, default=0.0, help="Sampling temperature (default: 0.0)"
    )

    p.add_argument(
        "--seed", type=int, default=42, help="Random seed for MCQ choice shuffling (default: 42)"
    )

    p.add_argument("--no-shuffle", action="store_true", help="Don't shuffle MCQ choices")

    p.add_argument("--model_path", type=str, default=None, help="model ckpt for gpt-oss-20B")

    p.add_argument("--no-grading", action="store_true", help="Don't grade answers")

    p.add_argument(
        "--reasoning-effort",
        choices=["none", "low", "medium", "high", "xhigh"],
        default=None,
        help="Reasoning effort for GPT-5.4 / o-series models "
        "(none, low, medium, high, xhigh). "
        "Disables temperature when set.",
    )

    p.add_argument(
        "--azure-endpoint",
        default=None,
        help="Azure OpenAI endpoint URL (overrides AZURE_OPENAI_ENDPOINT)",
    )

    p.add_argument(
        "--azure-key", default=None, help="Azure OpenAI API key (overrides AZURE_OPENAI_KEY)"
    )

    p.add_argument(
        "--azure-api-version",
        default=None,
        help="Azure OpenAI API version (overrides AZURE_OPENAI_API_VER, "
        "default: 2025-03-01-preview)",
    )

    p.add_argument("--openai-key", default=None, help="OpenAI API key (overrides OPENAI_API_KEY)")

    p.add_argument(
        "--anthropic-key", default=None, help="Anthropic API key (overrides ANTHROPIC_API_KEY)"
    )

    p.add_argument(
        "--resume",
        default=None,
        metavar="PREDICTIONS_FILE",
        help="Resume a previous run: skip IDs already in PREDICTIONS_FILE "
        "and append new results to it.",
    )

    p.add_argument(
        "--web-search",
        action="store_true",
        help="Augment all question types with a shared You.com web search context "
        "per row (requires --you-api-key or YOU_API_KEY). "
        "Uses Azure OpenAI when --provider AZURE, otherwise OPENAI_API_KEY.",
    )

    p.add_argument(
        "--you-api-key", default=None, help="You.com API key for web search (overrides YOU_API_KEY)"
    )

    p.add_argument(
        "--claude-effort",
        choices=["low", "medium", "high", "xhigh", "max"],
        default=None,
        help="Anthropic output_config.effort (Sonnet 5 / Opus 4.7+). Ignored on "
        "models that do not expose it.",
    )

    p.add_argument(
        "--frq-max-tokens",
        type=int,
        default=None,
        help="Override the FRQ max_tokens cap (default: 250 for ANTHROPIC, "
        "2048 otherwise — the values the six published models were run with).",
    )

    p.add_argument(
        "--run-index",
        type=int,
        default=1,
        help="Repeat-run index, recorded verbatim in every prediction record.",
    )

    p.add_argument(
        "--condition",
        default="base",
        help="Condition label (base | ws_cutoff | ws), recorded in every record.",
    )

    p.add_argument(
        "--native-web-search",
        action="store_true",
        help="Use GPT-5.4's built-in web search via the OpenAI Responses API "
        "(client.responses.create). Per-task search URLs and queries are "
        "saved in predictions. Works with --provider AZURE or OPENAI.",
    )

    return p


def get_transformer_response(pipe, system_prompt, user_prompt, temperature=0, max_tokens=2048):

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    outputs = pipe(
        messages,
        do_sample=False,
        max_new_tokens=max_tokens,
    )

    text = outputs[0]["generated_text"][-1]["content"]

    response = text.split("assistantfinal")[-1].strip()

    return response


def setup_client(
    provider: str,
    model: str | None,
    azure_endpoint: str | None = None,
    azure_key: str | None = None,
    azure_api_version: str | None = None,
    anthropic_key: str | None = None,
    openai_key: str | None = None,
):
    """Initialize the LLM client and return (client, model_name)."""

    try:

        from dotenv import load_dotenv

        load_dotenv()

    except ImportError:

        pass

    if provider == "AZURE":

        from openai import AzureOpenAI

        endpoint = azure_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")

        key = azure_key or os.environ.get("AZURE_OPENAI_KEY")

        deployment = model or os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

        api_version = (
            azure_api_version or os.environ.get("AZURE_OPENAI_API_VER") or "2025-03-01-preview"
        )

        if not endpoint or not key:

            print(
                "ERROR: Provide --azure-endpoint and --azure-key, "
                "or set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY in .env",
                file=sys.stderr,
            )

            sys.exit(1)

        client = AzureOpenAI(azure_endpoint=endpoint, api_key=key, api_version=api_version)

        return client, deployment

    elif provider == "OPENAI":

        from openai import OpenAI

        key = openai_key or os.environ.get("OPENAI_API_KEY")

        base = os.environ.get("OPENAI_API_BASE")

        model_name = model or os.environ.get("OPENAI_MODEL", "gpt-4o")

        if not key:

            print("ERROR: Set OPENAI_API_KEY in .env", file=sys.stderr)

            sys.exit(1)

        client = OpenAI(api_key=key, base_url=base)

        return client, model_name

    elif provider == "AZURE_DEEPSEEK":

        from openai import OpenAI

        endpoint = azure_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")

        key = azure_key or os.environ.get("AZURE_OPENAI_KEY")

        model_name = model or "DeepSeek-R1"

        if not endpoint or not key:

            print(
                "ERROR: Provide --azure-endpoint and --azure-key, "
                "or set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY in .env",
                file=sys.stderr,
            )

            sys.exit(1)

        client = OpenAI(base_url=endpoint, api_key=key)

        return client, model_name

    elif provider == "ANTHROPIC":

        try:

            import anthropic as _anthropic

        except ImportError:

            print(
                "ERROR: anthropic package not installed. Run: pip install anthropic",
                file=sys.stderr,
            )

            sys.exit(1)

        key = anthropic_key or os.environ.get("ANTHROPIC_API_KEY")

        if not key:

            print("ERROR: Set ANTHROPIC_API_KEY in .env or pass --anthropic-key", file=sys.stderr)

            sys.exit(1)

        model_name = model or "claude-sonnet-4-6"

        client = _anthropic.Anthropic(api_key=key)

        return client, model_name

    else:

        print(f"ERROR: Unknown provider '{provider}'", file=sys.stderr)

        sys.exit(1)


def get_model_response(
    client,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.0,
    max_tokens: int = 2048,
    retries: int = 2,
    json_mode: bool = False,
    reasoning_effort: str | None = None,
    meta_out: dict | None = None,
) -> str:
    """Send a chat completion request with retry logic.

    When `meta_out` is given it is populated with retries / finish_reason /
    refusal / usage for run logging. Behaviour is otherwise unchanged: when
    `reasoning_effort` is set, `temperature` is not sent (newer OpenAI models
    accept only the default temperature).
    """

    last_err = None

    kwargs: dict = dict(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=max_tokens,
        model=model,
    )

    if reasoning_effort:

        kwargs["reasoning_effort"] = reasoning_effort

    else:

        kwargs["temperature"] = temperature

    if json_mode:

        kwargs["response_format"] = {"type": "json_object"}

    for attempt in range(1, retries + 2):

        try:

            response = client.chat.completions.create(**kwargs)

            choice = response.choices[0]

            content = (choice.message.content or "").strip()

            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

            if meta_out is not None:

                usage = getattr(response, "usage", None)

                fin = getattr(choice, "finish_reason", None)

                det = getattr(usage, "completion_tokens_details", None)

                meta_out.update(
                    retries=attempt - 1,
                    reasoning_tokens=getattr(det, "reasoning_tokens", None),
                    stop_reason=fin,
                    refusal=bool(getattr(choice.message, "refusal", None))
                    or fin == "content_filter",
                    refusal_category=("content_filter" if fin == "content_filter" else None),
                    refusal_explanation=getattr(choice.message, "refusal", None),
                    model_snapshot=getattr(response, "model", model),
                    input_tokens=getattr(usage, "prompt_tokens", None),
                    output_tokens=getattr(usage, "completion_tokens", None),
                )

            return content

        except Exception as e:

            last_err = e

            # OpenAI delivers a safety decline as a 400, not a finish_reason.
            # It is deterministic, so retrying only burns quota: record it as a
            # refusal (the same category the Anthropic models report) and stop.
            if _is_safety_decline(e):

                if meta_out is not None:

                    meta_out.update(
                        retries=attempt - 1,
                        stop_reason="refusal",
                        refusal=True,
                        refusal_category=_safety_category(e),
                        refusal_explanation=str(e)[:400],
                        input_tokens=None,
                        output_tokens=0,
                    )

                return ""

            if attempt <= retries:

                wait = 2**attempt

                print(
                    f"  ⚠ API error (attempt {attempt}/{retries + 1}): {e}. "
                    f"Retrying in {wait}s...",
                    file=sys.stderr,
                )

                time.sleep(wait)

    if meta_out is not None:

        meta_out.update(retries=retries + 1, error=str(last_err), refusal=False)

    return f"Error: {last_err}"


_SAFETY_PATTERNS = (
    ("bio", ("biological risk", "possible biological")),
    ("cyber", ("cybersecurity risk", "possible cyber")),
    ("content_filter", ("content_filter", "content management policy",
                        "responsible ai service")),
)


def _is_safety_decline(exc: Exception) -> bool:
    """True when the provider declined on safety grounds rather than erroring."""

    t = str(exc).lower()

    if "400" not in t and "invalid_request" not in t and "content_filter" not in t:

        return False

    return any(p in t for _, pats in _SAFETY_PATTERNS for p in pats)


def _safety_category(exc: Exception) -> str:

    t = str(exc).lower()

    for cat, pats in _SAFETY_PATTERNS:

        if any(p in t for p in pats):

            return cat

    return "unknown"


def get_gpt54_web_search_response(
    client,
    model: str,
    system_prompt: str,
    user_prompt: str,
    reasoning_effort: str | None = None,
    retries: int = 2,
    json_mode: bool = False,
) -> tuple[str, dict]:
    """Call the OpenAI Responses API with GPT-5.4 native web search.

    Returns (answer_text, {"urls": [...], "queries": [...]}).
    Each URL entry is {"url": ..., "title": ...}.
    """

    last_err = None

    kwargs: dict = dict(
        model=model,
        tools=[{"type": "web_search"}],
        tool_choice={"type": "web_search"},
        input=user_prompt,
    )

    if system_prompt:

        kwargs["instructions"] = system_prompt

    if reasoning_effort and reasoning_effort != "none":

        kwargs["reasoning"] = {"effort": reasoning_effort}

    if json_mode:

        kwargs["text"] = {"format": {"type": "json_object"}}

    for attempt in range(1, retries + 2):

        try:

            response = client.responses.create(**kwargs)

            text = ""

            urls: list[dict] = []

            queries: list[str] = []

            for item in response.output:

                item_type = getattr(item, "type", "")

                if item_type == "web_search_call":

                    action = getattr(item, "action", None)

                    if action:

                        qs = getattr(action, "queries", None) or []

                        if not qs:

                            q = getattr(action, "query", None)

                            if q:

                                qs = [q]

                        queries.extend(qs)

                elif item_type == "message":

                    for block in getattr(item, "content", []):

                        if getattr(block, "type", "") == "output_text":

                            text = block.text

                            for ann in getattr(block, "annotations", []):

                                if getattr(ann, "type", "") == "url_citation":

                                    urls.append(
                                        {
                                            "url": ann.url,
                                            "title": getattr(ann, "title", ""),
                                        }
                                    )

            return text.strip(), {"urls": urls, "queries": queries}

        except Exception as e:

            last_err = e

            if attempt <= retries:

                wait = 2**attempt

                print(
                    f"  ⚠ API error (attempt {attempt}/{retries + 1}): {e}. "
                    f"Retrying in {wait}s...",
                    file=sys.stderr,
                )

                time.sleep(wait)

    return f"Error: {last_err}", {"urls": [], "queries": []}


# Anthropic models that reject `temperature` / `top_p` / `top_k` outright
# (Claude Sonnet 5 and later: "`temperature` is deprecated for this model", HTTP 400).
# Source: https://platform.claude.com/docs/en/models/sonnet-5/overview
NO_SAMPLING_PARAM_MODELS = (
    "claude-sonnet-5",
    "claude-opus-5",
    "claude-opus-4-8",
    "claude-opus-4-7",
    "claude-fable-5",
    "claude-fable-5-1",
)

# Anthropic models exposing output_config.effort (low|medium|high|xhigh|max).
EFFORT_CAPABLE_MODELS = NO_SAMPLING_PARAM_MODELS + ("claude-opus-4-6", "claude-sonnet-4-6")


def claude_supports_sampling_params(model: str) -> bool:
    """True when the Anthropic model still accepts `temperature`."""

    return not any(model.startswith(m) for m in NO_SAMPLING_PARAM_MODELS)


def claude_supports_effort(model: str) -> bool:
    """True when the Anthropic model accepts output_config.effort."""

    return any(model.startswith(m) for m in EFFORT_CAPABLE_MODELS)


def get_claude_response(
    client,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.0,
    max_tokens: int = 2048,
    retries: int = 2,
    effort: str | None = None,
    meta_out: dict | None = None,
    capture_thinking: bool = False,
) -> str:
    """Send a message to the Anthropic Claude API with retry logic.

    `temperature` is sent only for models that still accept it; newer models
    reject any non-default sampling parameter with HTTP 400. `effort` maps to
    output_config.effort on models that expose it. When `meta_out` is given it
    is populated with retries / stop_reason / refusal / usage for run logging.
    """

    last_err = None

    kwargs: dict = dict(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    if claude_supports_sampling_params(model):

        kwargs["temperature"] = temperature

    if effort and claude_supports_effort(model):

        kwargs["output_config"] = {"effort": effort}

    if capture_thinking and claude_supports_effort(model):

        # display controls visibility only — thinking happens and is billed the
        # same either way — so this does not change what the model produces.
        kwargs["thinking"] = {"type": "adaptive", "display": "summarized"}

    for attempt in range(1, retries + 2):

        try:

            response = client.messages.create(**kwargs)

            text = "".join(b.text for b in response.content if getattr(b, "type", "") == "text")

            if meta_out is not None:

                sd = getattr(response, "stop_details", None)

                meta_out.update(
                    retries=attempt - 1,
                    thinking="".join(
                        getattr(b, "thinking", "") or ""
                        for b in response.content
                        if getattr(b, "type", "") == "thinking"
                    ) or None,
                    stop_reason=getattr(response, "stop_reason", None),
                    refusal=getattr(response, "stop_reason", None) == "refusal",
                    refusal_category=getattr(sd, "category", None) if sd else None,
                    refusal_explanation=getattr(sd, "explanation", None) if sd else None,
                    model_snapshot=getattr(response, "model", model),
                    input_tokens=getattr(response.usage, "input_tokens", None),
                    output_tokens=getattr(response.usage, "output_tokens", None),
                )

            return text.strip()

        except Exception as e:

            last_err = e

            if attempt <= retries:

                wait = 2**attempt

                print(
                    f"  ⚠ API error (attempt {attempt}/{retries + 1}): {e}. "
                    f"Retrying in {wait}s...",
                    file=sys.stderr,
                )

                time.sleep(wait)

    if meta_out is not None:

        meta_out.update(retries=retries + 1, error=str(last_err), refusal=False)

    return f"Error: {last_err}"


TASK_FIELDS = {
    "binary": ["binary_question"],
    "binary_perturbed": ["binary_question_perturbed"],
    "mcq": ["mcq_question", "mcq_choices", "mcq_answer_key"],
    "frq": ["frq_prompt"],
    "date": ["date_prediction_prompt", "ground_truth_date"],
}


def detect_tasks(row: dict) -> dict[str, bool]:
    """Return which tasks are present in this row."""

    return {
        task: all(row.get(f) is not None and row.get(f) != "" for f in fields)
        for task, fields in TASK_FIELDS.items()
    }


def is_post_cutoff(pub_date_str: str, cutoff_str: str) -> bool:
    """Check if the publication date is strictly after the cutoff."""

    try:

        pub = datetime.strptime(pub_date_str, "%Y-%m")

        cutoff = datetime.strptime(cutoff_str, "%Y-%m")

        return pub > cutoff

    except (ValueError, TypeError):

        return True


BINARY_SYSTEM = (
    "You are a scientific forecasting evaluator. "
    "Given a yes/no forecasting question about a future scientific or technical "
    "development, reason briefly then give your final answer and confidence.\n\n"
    "You MUST respond with valid JSON in exactly this format:\n"
    '{"reasoning": "<1-2 sentence justification>", '
    '"answer": "Yes or No", '
    '"confidence": <float 0.0-1.0>}'
)

MCQ_SYSTEM = (
    "You are a scientific forecasting evaluator assessing knowledge of emerging "
    "research breakthroughs. You will be presented with a multiple-choice question "
    "about a technical development.\n\n"
    "You MUST respond with valid JSON in exactly this format:\n"
    '{"reasoning": "<1-2 sentence justification>", '
    '"answer": "<single letter A, B, C, or D>", '
    '"confidence": <float 0.0-1.0>}'
)

FRQ_SYSTEM = (
    "You are a research scientist. Given a research problem, propose a single "
    "core method to solve it.\n\n"
    "Respond in 3–4 sentences maximum.\n"
    "Do NOT include implementation details, steps, or lists.\n"
    "Focus only on the key idea or methodology."
)

DATE_SYSTEM = (
    "You are a scientific forecasting analyst. Given a description of a technical "
    "breakthrough, predict when this breakthrough will first be achieved or "
    "publicly demonstrated.\n\n"
    "You MUST respond with valid JSON in exactly this format:\n"
    '{"reasoning": "<1-2 sentence justification>", '
    '"answer": "<YYYY-MM>", '
    '"confidence": <float 0.0-1.0>}'
)


_WS_SOURCES_SUFFIX = (
    ', "sources": ["<url1>", "<url2>"]}'
    "\nIf you used web search, list the URLs you relied on in sources; otherwise use []."
)

BINARY_SYSTEM_WS = BINARY_SYSTEM.rstrip("}") + _WS_SOURCES_SUFFIX

MCQ_SYSTEM_WS = MCQ_SYSTEM.rstrip("}") + _WS_SOURCES_SUFFIX

DATE_SYSTEM_WS = DATE_SYSTEM.rstrip("}") + _WS_SOURCES_SUFFIX


FRQ_SYSTEM_WS = (
    FRQ_SYSTEM + "\nIf you used web search, append a final line formatted exactly as: "
    "Sources: <url1>, <url2>"
)


def parse_structured_response(raw: str, task_label: str = "") -> dict:
    """
    Parse a JSON model response into answer/reasoning/confidence.

    Returns a dict with keys:
      answer       - extracted answer string (falls back to full raw text)
      reasoning    - extracted reasoning string
      confidence   - float 0.0-1.0 or None if not present / unparseable
      parse_method - "json" | "fallback" | "error"

    The fallback ensures eval.py's existing regex parsers still work on
    `answer` if the model ignored the JSON format instruction.
    """

    if raw.startswith("Error:"):

        return {
            "answer": raw,
            "reasoning": "",
            "confidence": None,
            "sources": [],
            "parse_method": "error",
        }

    obj = None

    json_err = None

    try:

        obj = json.loads(raw)

    except json.JSONDecodeError as e:

        json_err = e

        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)

        if m:

            try:

                obj = json.loads(m.group(1))

                json_err = None

            except json.JSONDecodeError:

                pass

    if obj and isinstance(obj, dict) and obj.get("answer"):

        confidence = None

        try:

            c = obj.get("confidence")

            if c is not None:

                confidence = round(max(0.0, min(1.0, float(c))), 4)

        except (TypeError, ValueError):

            pass

        raw_sources = obj.get("sources") or []

        sources = [s for s in raw_sources if isinstance(s, str) and s.startswith("http")]

        return {
            "answer": str(obj["answer"]).strip(),
            "reasoning": str(obj.get("reasoning", "")),
            "confidence": confidence,
            "sources": sources,
            "parse_method": "json",
        }

    label = f"[{task_label}] " if task_label else ""

    print(f"  {label}JSON parse failed. Error: {json_err}", file=sys.stderr)

    print(f"  {label}Raw response ({len(raw)} chars):", file=sys.stderr)

    print(f"  {'-'*50}", file=sys.stderr)

    print(f"  {raw[:800]}{'...' if len(raw) > 800 else ''}", file=sys.stderr)

    print(f"  {'-'*50}", file=sys.stderr)

    return {
        "answer": raw,
        "reasoning": raw,
        "confidence": None,
        "sources": [],
        "parse_method": "fallback",
    }


try:

    from eval import grade_binary, grade_mcq, grade_frq, grade_date

except ImportError:

    try:

        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        from eval import grade_binary, grade_mcq, grade_frq, grade_date

    except ImportError:

        print(
            "WARNING: Could not import grading functions from eval.py. "
            "Live grading feedback will be disabled.",
            file=sys.stderr,
        )

        grade_binary = grade_mcq = grade_frq = grade_date = None


grade_binary = grade_mcq = grade_frq = grade_date = None


def run_benchmark():

    parser = build_parser()

    args = parser.parse_args()

    random.seed(args.seed)

    if args.model_path and "gpt-oss" in args.model_path:

        client = None

        model_name = "gpt-oss-20B"

        pipe = pipeline(
            "text-generation",
            model=args.model_path,
            torch_dtype="auto",
            device_map="auto",
        )

    else:

        client, model_name = setup_client(
            args.provider,
            args.model,
            azure_endpoint=args.azure_endpoint,
            azure_key=args.azure_key,
            azure_api_version=args.azure_api_version,
            anthropic_key=args.anthropic_key,
            openai_key=args.openai_key,
        )

    get_ws_context_fn = None

    ws_model = None

    ws_cutoff_dt = None

    if args.web_search:

        try:

            from web_search import web_search_get_context as _web_search_get_context

        except ImportError:

            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

            from web_search import web_search_get_context as _web_search_get_context

        you_key = args.you_api_key or os.environ.get("YOU_API_KEY")

        if not you_key:

            print(
                "ERROR: --web-search requires YOU_API_KEY env var or --you-api-key", file=sys.stderr
            )

            sys.exit(1)

        if client is None:

            print(
                "ERROR: --web-search is not supported with local transformer models",
                file=sys.stderr,
            )

            sys.exit(1)

        ws_model = model_name

        _ws_cutoff_str = args.ws_cutoff or args.knowledge_cutoff

        ws_cutoff_dt = (
            datetime.strptime(_ws_cutoff_str + "-01", "%Y-%m-%d")
            if _ws_cutoff_str
            else datetime.now()
        )

        def get_ws_context_fn(questions: list) -> dict:

            return _web_search_get_context(
                questions=questions,
                client=client,
                you_api_key=you_key,
                cutoff_date=ws_cutoff_dt,
                model=ws_model,
            )

    if not args.input or not os.path.exists(args.input):

        if args.input:

            print(
                f"[CUSP] input not found at '{args.input}', downloading from HuggingFace...",
                file=sys.stderr,
            )

        else:

            print(
                "[CUSP] No --input given, downloading from HuggingFace (SeanWu25/CUSP)...",
                file=sys.stderr,
            )

        try:

            from huggingface_hub import hf_hub_download

        except ImportError:

            print(
                "ERROR: huggingface_hub is required. pip install huggingface_hub", file=sys.stderr
            )

            sys.exit(1)

        args.input = hf_hub_download(
            repo_id="SeanWu25/CUSP", filename="CUSP_final.jsonl", repo_type="dataset"
        )

        print(f"[CUSP] Dataset ready at: {args.input}", file=sys.stderr)

    os.makedirs(args.output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    resumed_ids: set = set()

    if args.resume:

        if not os.path.exists(args.resume):

            print(f"ERROR: Resume file not found: {args.resume}", file=sys.stderr)

            sys.exit(1)

        with open(args.resume, "r", encoding="utf-8") as _rf:

            for _line in _rf:

                _line = _line.strip()

                if _line:

                    try:

                        _rec = json.loads(_line)

                        if _rec.get("id"):

                            resumed_ids.add(_rec["id"])

                    except json.JSONDecodeError:

                        pass

        predictions_path = args.resume

        summary_path = args.resume.replace(".jsonl", "_summary.json")

        print(f"Resuming from {args.resume} — {len(resumed_ids)} rows already done, skipping.")

    else:

        predictions_path = os.path.join(
            args.output_dir, f"predictions_{model_name}_{timestamp}.jsonl"
        )

        summary_path = os.path.join(args.output_dir, f"summary_{model_name}_{timestamp}.json")

    print(f"{'='*60}")

    print(f"CUSP Benchmark Test Runner")

    print(f"{'='*60}")

    print(f"  Model:            {model_name}")

    print(f"  Provider:         {args.provider}")

    print(f"  Input:            {args.input}")

    print(f"  Knowledge cutoff: {args.knowledge_cutoff or '(none — all rows)'}")

    print(f"  Max rows:         {args.max_rows or '(all)'}")

    print(
        f"  Temperature:      {args.temperature if not args.reasoning_effort else '(disabled — reasoning_effort set)'}"
    )

    if args.reasoning_effort:

        print(f"  Reasoning effort: {args.reasoning_effort}")

    if args.web_search:

        print(
            f"  Web search:       enabled (model={ws_model}, "
            f"cutoff={ws_cutoff_dt.strftime('%Y-%m')})"
        )

    if args.native_web_search:

        print(f"  GPT-5.4 web search: enabled (native Responses API, URLs saved per task)")

    print(f"  Shuffle MCQ:      {not args.no_shuffle}")

    print(f"  Predictions:      {predictions_path}")

    print(f"{'='*60}\n")

    results = {
        "binary": [],
        "binary_perturbed": [],
        "mcq": [],
        "frq": [],
        "date": [],
    }

    rows_processed = 0

    rows_skipped = 0

    labels = ["A", "B", "C", "D", "E", "F", "G", "H"]

    def call_llm(
        system: str, user: str, json_mode: bool = False, max_tokens: int = 2048
    ) -> tuple[str, dict]:

        empty_meta: dict = {"urls": [], "queries": []}

        if "oss-20B" in model_name:

            return get_transformer_response(pipe, system, user), empty_meta

        if args.provider == "ANTHROPIC":

            return (
                get_claude_response(
                    client,
                    model_name,
                    system,
                    user,
                    temperature=args.temperature,
                    max_tokens=max_tokens,
                    effort=args.claude_effort,
                ),
                empty_meta,
            )

        if args.native_web_search:

            return get_gpt54_web_search_response(
                client,
                model_name,
                system,
                user,
                reasoning_effort=args.reasoning_effort,
                json_mode=json_mode,
            )

        return (
            get_model_response(
                client,
                model_name,
                system,
                user,
                temperature=args.temperature,
                json_mode=json_mode,
                reasoning_effort=args.reasoning_effort,
            ),
            empty_meta,
        )

    with open(args.input, "r", encoding="utf-8") as f:

        raw_lines = f.readlines()

    total = args.max_rows or len(raw_lines)

    pbar = tqdm(enumerate(raw_lines, 1), total=total, unit="row", desc="Benchmarking")

    for lineno, line in pbar:

        line = line.strip()

        if not line:

            continue

        try:

            data = json.loads(line)

        except json.JSONDecodeError as e:

            print(f"WARNING: line {lineno}: malformed JSON, skipping: {e}", file=sys.stderr)

            continue

        pub_date = data.get("publication_date", "")

        if args.knowledge_cutoff and pub_date:

            if not is_post_cutoff(pub_date, args.knowledge_cutoff):

                rows_skipped += 1

                continue

        rid = data.get("id", f"line_{lineno}")

        if rid in resumed_ids:

            continue

        if args.max_rows and rows_processed >= args.max_rows:

            break

        rows_processed += 1

        tasks = detect_tasks(data)

        available = [t for t, v in tasks.items() if v]

        pbar.set_description(f"Row {rows_processed} | {pub_date} | {', '.join(available)}")

        print(f"\n{'='*60}")

        print(f"Row {rows_processed} | ID: {rid} | Published: {pub_date}")

        print(f"Available tasks: {', '.join(available)}")

        print(f"{'='*60}")

        prediction = {
            "id": rid,
            "publication_date": pub_date,
            "model": model_name,
            "condition": args.condition,
            "run_index": args.run_index,
            "timestamp": datetime.now().isoformat(),
        }

        row_context = ""

        if get_ws_context_fn and available:

            ws_questions = [
                data[f]
                for f in (
                    "binary_question",
                    "binary_question_perturbed",
                    "mcq_question",
                    "frq_prompt",
                    "date_prediction_prompt",
                )
                if data.get(f)
            ]

            if ws_questions:

                try:

                    ws_result = get_ws_context_fn(ws_questions)

                except Exception as ws_err:

                    print(
                        f"  ⚠ Web search failed for this row, skipping: {ws_err}", file=sys.stderr
                    )

                    ws_result = {"context": "", "urls": [], "query": f"ERROR: {ws_err}"}

                row_context = ws_result["context"]

                prediction["web_search_query"] = ws_result["query"]

                prediction["web_search_urls"] = ws_result["urls"]

                if row_context:

                    print(
                        f"  [web search: {len(ws_questions)} questions → "
                        f"{len(ws_result['urls'])} sources, "
                        f"{len(row_context)} chars of context]"
                    )

                    print(f"  [query: {ws_result['query']}]")

                else:

                    print("  [web search: no results found]")

        if tasks["binary"]:

            print("\n[Binary Question]")

            binary_prompt = data["binary_question"]

            if row_context:

                binary_prompt = f"[Web Search Context]\n{row_context}\n\n---\n\n{binary_prompt}"

            _sys = BINARY_SYSTEM_WS if args.native_web_search else BINARY_SYSTEM

            raw, ws_meta = call_llm(_sys, binary_prompt, json_mode=True)

            if ws_meta.get("queries"):

                prediction["binary_web_search_queries"] = ws_meta["queries"]

            parsed = parse_structured_response(raw, task_label="binary")

            annotation_urls = ws_meta.get("urls") or []

            json_urls = [{"url": u, "title": ""} for u in parsed.get("sources", [])]

            merged_urls = annotation_urls or json_urls

            if merged_urls:

                prediction["binary_web_search_urls"] = merged_urls

            prediction["binary_answer"] = parsed["answer"]

            prediction["binary_reasoning"] = parsed["reasoning"]

            if parsed["confidence"] is not None:

                prediction["binary_confidence"] = parsed["confidence"]

            if parsed["parse_method"] != "json":

                print(
                    f"  ⚠ JSON parse failed ({parsed['parse_method']}), "
                    f"falling back to free-text parsing",
                    file=sys.stderr,
                )

            if grade_binary:

                g = grade_binary(
                    prediction["binary_answer"], data.get("binary_ground_truth", "Yes")
                )

                results["binary"].append(g["correct"])

                conf_str = (
                    f", confidence={parsed['confidence']:.2f}"
                    if parsed["confidence"] is not None
                    else ""
                )

                print(f"  Answer: {g['parsed_answer']}{conf_str}")

                print(
                    f"  Grade: {'✓' if g['correct'] else '✗'} "
                    f"(parsed={g['parsed_answer']}, gt={g['ground_truth']})"
                )

            else:

                print(f"  Answer: {parsed['answer']}")

        if tasks["binary_perturbed"]:

            print("\n[Binary Perturbed Question]")

            bp_prompt = data["binary_question_perturbed"]

            if row_context:

                bp_prompt = f"[Web Search Context]\n{row_context}\n\n---\n\n{bp_prompt}"

            _sys = BINARY_SYSTEM_WS if args.native_web_search else BINARY_SYSTEM

            raw, ws_meta = call_llm(_sys, bp_prompt, json_mode=True)

            if ws_meta.get("queries"):

                prediction["binary_perturbed_web_search_queries"] = ws_meta["queries"]

            parsed = parse_structured_response(raw, task_label="binary_perturbed")

            annotation_urls = ws_meta.get("urls") or []

            json_urls = [{"url": u, "title": ""} for u in parsed.get("sources", [])]

            merged_urls = annotation_urls or json_urls

            if merged_urls:

                prediction["binary_perturbed_web_search_urls"] = merged_urls

            prediction["binary_perturbed_answer"] = parsed["answer"]

            prediction["binary_perturbed_reasoning"] = parsed["reasoning"]

            if parsed["confidence"] is not None:

                prediction["binary_perturbed_confidence"] = parsed["confidence"]

            if parsed["parse_method"] != "json":

                print(
                    f"  ⚠ JSON parse failed ({parsed['parse_method']}), "
                    f"falling back to free-text parsing",
                    file=sys.stderr,
                )

            if grade_binary:

                g = grade_binary(prediction["binary_perturbed_answer"], "No")

                results["binary_perturbed"].append(g["correct"])

                conf_str = (
                    f", confidence={parsed['confidence']:.2f}"
                    if parsed["confidence"] is not None
                    else ""
                )

                print(f"  Answer: {g['parsed_answer']}{conf_str}")

                print(
                    f"  Grade: {'✓' if g['correct'] else '✗'} "
                    f"(parsed={g['parsed_answer']}, gt={g['ground_truth']})"
                )

            else:

                print(f"  Answer: {parsed['answer']}")

        if tasks["mcq"]:

            print("\n[MCQ Question]")

            original_choices = list(data["mcq_choices"])

            ground_truth_idx = data["mcq_answer_key"]

            correct_text = original_choices[ground_truth_idx]

            if args.no_shuffle:

                shuffled_choices = original_choices

            else:

                indices = list(range(len(original_choices)))

                random.shuffle(indices)

                shuffled_choices = [original_choices[i] for i in indices]

            shuffled_answer_label = labels[shuffled_choices.index(correct_text)]

            n_choices = len(shuffled_choices)

            choice_labels = labels[:n_choices]

            choices_str = "\n".join(
                f"({choice_labels[i]}) {shuffled_choices[i]}" for i in range(n_choices)
            )

            mcq_prompt = (
                f"{data['mcq_question']}\n\n"
                f"{choices_str}\n\n"
                f"Select exactly one answer: {', '.join(choice_labels)}."
            )

            if row_context:

                mcq_prompt = f"[Web Search Context]\n{row_context}\n\n---\n\n{mcq_prompt}"

            _sys = MCQ_SYSTEM_WS if args.native_web_search else MCQ_SYSTEM

            raw, ws_meta = call_llm(_sys, mcq_prompt, json_mode=True)

            if ws_meta.get("queries"):

                prediction["mcq_web_search_queries"] = ws_meta["queries"]

            parsed = parse_structured_response(raw, task_label="mcq")

            annotation_urls = ws_meta.get("urls") or []

            json_urls = [{"url": u, "title": ""} for u in parsed.get("sources", [])]

            merged_urls = annotation_urls or json_urls

            if merged_urls:

                prediction["mcq_web_search_urls"] = merged_urls

            prediction["mcq_answer"] = parsed["answer"]

            prediction["mcq_reasoning"] = parsed["reasoning"]

            if parsed["confidence"] is not None:

                prediction["mcq_confidence"] = parsed["confidence"]

            prediction["mcq_shuffled_choices"] = {
                choice_labels[i]: shuffled_choices[i] for i in range(n_choices)
            }

            prediction["mcq_shuffled_answer_key"] = shuffled_answer_label

            if parsed["parse_method"] != "json":

                print(
                    f"  ⚠ JSON parse failed ({parsed['parse_method']}), "
                    f"falling back to free-text parsing",
                    file=sys.stderr,
                )

            if grade_mcq:

                g = grade_mcq(
                    prediction["mcq_answer"], shuffled_answer_label, choices=shuffled_choices
                )

                results["mcq"].append(g["correct"])

                conf_str = (
                    f", confidence={parsed['confidence']:.2f}"
                    if parsed["confidence"] is not None
                    else ""
                )

                print(f"  Answer: {g['parsed_answer']}{conf_str}")

                print(
                    f"  Grade: {'✓' if g['correct'] else '✗'} "
                    f"(parsed={g['parsed_answer']}, gt={shuffled_answer_label})"
                )

            else:

                print(f"  Answer: {parsed['answer']}")

        if tasks["frq"]:

            print("\n[FRQ Question]")

            frq_max_tokens = args.frq_max_tokens or (
                250 if args.provider == "ANTHROPIC" else 2048
            )

            frq_prompt = data["frq_prompt"]

            if row_context:

                frq_prompt = f"[Web Search Context]\n{row_context}\n\n---\n\n{frq_prompt}"

            _sys = FRQ_SYSTEM_WS if args.native_web_search else FRQ_SYSTEM

            ans, ws_meta = call_llm(_sys, frq_prompt, max_tokens=frq_max_tokens)

            if ws_meta.get("queries"):

                prediction["frq_web_search_queries"] = ws_meta["queries"]

            annotation_urls = ws_meta.get("urls") or []

            text_urls: list[dict] = []

            if not annotation_urls:

                m = re.search(r"(?i)^Sources:\s*(.+)$", ans, re.MULTILINE)

                if m:

                    text_urls = [
                        {"url": u.strip(), "title": ""}
                        for u in m.group(1).split(",")
                        if u.strip().startswith("http")
                    ]

                    ans = ans[: m.start()].rstrip()

            merged_urls = annotation_urls or text_urls

            if merged_urls:

                prediction["frq_web_search_urls"] = merged_urls

            prediction["frq_answer"] = ans

            print(f"  Response: {ans[:200]}...")

            if grade_frq:

                print("  [Judging FRQ...]")

                g = grade_frq(
                    response=ans,
                    results_and_metrics=data.get("results_and_metrics", ""),
                    technical_approach=data.get("technical_approach", ""),
                    abstract=data.get("source_abstract", ""),
                    problem_statement=data.get("problem_statement", ""),
                    llm_call_fn=call_llm,
                )

                if g["score"] is not None:

                    results["frq"].append(g["score"])

                print(
                    f"  Grade: {g['score']}/10 "
                    f"(alignment={g.get('alignment')}, "
                    f"specificity={g.get('specificity')}, "
                    f"novelty={g.get('novelty')})"
                )

                print(f"  Rationale: {g.get('rationale', 'N/A')}")

        if tasks["date"]:

            print("\n[Date Prediction]")

            date_prompt = data["date_prediction_prompt"]

            if row_context:

                date_prompt = f"[Web Search Context]\n{row_context}\n\n---\n\n{date_prompt}"

            _sys = DATE_SYSTEM_WS if args.native_web_search else DATE_SYSTEM

            raw, ws_meta = call_llm(_sys, date_prompt, json_mode=True)

            if ws_meta.get("queries"):

                prediction["date_web_search_queries"] = ws_meta["queries"]

            parsed = parse_structured_response(raw, task_label="date")

            annotation_urls = ws_meta.get("urls") or []

            json_urls = [{"url": u, "title": ""} for u in parsed.get("sources", [])]

            merged_urls = annotation_urls or json_urls

            if merged_urls:

                prediction["date_web_search_urls"] = merged_urls

            prediction["date_answer"] = parsed["answer"]

            prediction["date_reasoning"] = parsed["reasoning"]

            if parsed["confidence"] is not None:

                prediction["date_confidence"] = parsed["confidence"]

            if parsed["parse_method"] != "json":

                print(
                    f"  ⚠ JSON parse failed ({parsed['parse_method']}), "
                    f"falling back to free-text parsing",
                    file=sys.stderr,
                )

            if grade_date:

                g = grade_date(prediction["date_answer"], data["ground_truth_date"])

                if g["month_distance"] is not None:

                    results["date"].append(g["month_distance"])

                conf_str = (
                    f", confidence={parsed['confidence']:.2f}"
                    if parsed["confidence"] is not None
                    else ""
                )

                print(
                    f"  Answer: {parsed['answer']}{conf_str} " f"(GT: {data['ground_truth_date']})"
                )

                print(
                    f"  Grade: {'✓ Exact' if g['exact_match'] else '✗ Off'} "
                    f"by {g['month_distance']} month(s)"
                )

            else:

                print(f"  Answer: {parsed['answer']}")

        all_reasoning = []

        for key in (
            "binary_reasoning",
            "binary_perturbed_reasoning",
            "mcq_reasoning",
            "frq_answer",
            "date_reasoning",
        ):

            val = prediction.get(key)

            if val:

                all_reasoning.append(val)

        prediction["model_reasoning"] = "\n---\n".join(all_reasoning)

        with open(predictions_path, "a", encoding="utf-8") as out:

            out.write(json.dumps(prediction, ensure_ascii=False) + "\n")

        pbar.update(1)

    pbar.close()

    print(f"\n\n{'='*60}")

    print("BENCHMARK RUN SUMMARY")

    print(f"{'='*60}")

    print(f"  Model:               {model_name}")

    print(f"  Rows processed:      {rows_processed}")

    print(f"  Rows skipped (cutoff): {rows_skipped}")

    if results["binary"]:

        acc = sum(results["binary"]) / len(results["binary"]) * 100

        print(
            f"  Binary accuracy:     {acc:.1f}% "
            f"({sum(results['binary'])}/{len(results['binary'])})"
        )

    if results["binary_perturbed"]:

        acc = sum(results["binary_perturbed"]) / len(results["binary_perturbed"]) * 100

        print(
            f"  Binary Pert. acc:    {acc:.1f}% "
            f"({sum(results['binary_perturbed'])}/{len(results['binary_perturbed'])})"
        )

    if results["mcq"]:

        acc = sum(results["mcq"]) / len(results["mcq"]) * 100

        print(
            f"  MCQ accuracy:        {acc:.1f}% " f"({sum(results['mcq'])}/{len(results['mcq'])})"
        )

    if results["frq"]:

        mean = sum(results["frq"]) / len(results["frq"])

        print(f"  FRQ mean score:      {mean:.2f}/10 (n={len(results['frq'])})")

    if results["date"]:

        mean = sum(results["date"]) / len(results["date"])

        print(f"  Date mean distance:  {mean:.1f} months (n={len(results['date'])})")

    print(f"\n📄 Predictions saved to: {predictions_path}")

    summary = {
        "model": model_name,
        "provider": args.provider,
        "condition": args.condition,
        "run_index": args.run_index,
        "claude_effort": args.claude_effort,
        "frq_max_tokens": args.frq_max_tokens,
        "input_file": args.input,
        "knowledge_cutoff": args.knowledge_cutoff,
        "temperature": args.temperature,
        "web_search": args.web_search,
        "web_search_model": ws_model if args.web_search else None,
        "rows_processed": rows_processed,
        "rows_skipped_cutoff": rows_skipped,
        "timestamp": timestamp,
        "predictions_file": predictions_path,
        "binary_accuracy_pct": (
            round(sum(results["binary"]) / len(results["binary"]) * 100, 2)
            if results["binary"]
            else None
        ),
        "binary_perturbed_accuracy_pct": (
            round(sum(results["binary_perturbed"]) / len(results["binary_perturbed"]) * 100, 2)
            if results["binary_perturbed"]
            else None
        ),
        "mcq_accuracy_pct": (
            round(sum(results["mcq"]) / len(results["mcq"]) * 100, 2) if results["mcq"] else None
        ),
        "frq_mean_score": (
            round(sum(results["frq"]) / len(results["frq"]), 2) if results["frq"] else None
        ),
        "date_mean_distance_months": (
            round(sum(results["date"]) / len(results["date"]), 1) if results["date"] else None
        ),
    }

    with open(summary_path, "w", encoding="utf-8") as sf:

        json.dump(summary, sf, indent=2, ensure_ascii=False)

    print(f"📄 Summary saved to: {summary_path}")

    print(f"\n💡 To run full evaluation with reasoning judges:")

    print(f"   python eval.py \\")

    print(f"       --benchmark {args.input} \\")

    print(f"       --predictions {predictions_path} \\")

    print(f"       --output cusp_eval_report.json --pretty --verbose")

    print(f"{'='*60}")

    global _last_predictions_path

    _last_predictions_path = predictions_path


def run_inference(
    input_path: str | None = None,
    output_path: str = "predictions.jsonl",
    *,
    provider: str = "AZURE",
    model: str | None = None,
    knowledge_cutoff: str = "2024-01",
    max_rows: int | None = None,
    web_search: bool = False,
    ws_cutoff: str | None = None,
    you_api_key: str | None = None,
    azure_endpoint: str | None = None,
    azure_key: str | None = None,
    openai_key: str | None = None,
    anthropic_key: str | None = None,
    seed: int = 42,
    verbose: bool = True,
) -> str:
    """
    Run CUSP model inference and write predictions to output_path.

    Importable alternative to the CLI — call directly from a notebook:

        import sys; sys.path.insert(0, 'scripts')
        from test_LLM import run_inference
        run_inference('CUSP_final.jsonl', 'predictions.jsonl',
                      provider='OPENAI', model='gpt-4o',
                      knowledge_cutoff='2024-01', max_rows=20)

    Parameters
    ----------
    input_path       : path to CUSP JSONL file
    output_path      : path to write predictions JSONL
    provider         : 'AZURE' | 'OPENAI' | 'ANTHROPIC'
    model            : model name (falls back to env vars)
    knowledge_cutoff : 'YYYY-MM' cutoff date shown to the model
    max_rows         : limit number of rows (useful for testing)
    web_search       : use You.com web search for context
    you_api_key      : You.com API key (falls back to YOU_API_KEY env var)
    azure_endpoint   : Azure endpoint (falls back to AZURE_OPENAI_ENDPOINT)
    azure_key        : Azure API key (falls back to AZURE_OPENAI_KEY)
    openai_key       : OpenAI API key (falls back to OPENAI_API_KEY)
    anthropic_key    : Anthropic API key (falls back to ANTHROPIC_API_KEY)
    seed             : random seed for reproducibility
    verbose          : print progress

    Returns the output_path.
    """

    try:

        from dotenv import load_dotenv

        load_dotenv()

    except ImportError:

        pass

    import sys as _sys

    _saved_argv = _sys.argv

    args_list = [
        "test_LLM.py",
        "--input",
        input_path,
        "--output-dir",
        os.path.dirname(os.path.abspath(output_path)) or ".",
        "--provider",
        provider,
        "--knowledge-cutoff",
        knowledge_cutoff,
        "--seed",
        str(seed),
    ]

    if model:

        args_list += ["--model", model]

    if max_rows:

        args_list += ["--max-rows", str(max_rows)]

    if web_search:

        args_list.append("--web-search")

    if ws_cutoff:

        args_list += ["--ws-cutoff", ws_cutoff]

    if you_api_key:

        args_list += ["--you-api-key", you_api_key]

    if azure_endpoint:

        args_list += ["--azure-endpoint", azure_endpoint]

    if azure_key:

        args_list += ["--azure-key", azure_key]

    if openai_key:

        args_list += ["--openai-key", openai_key]

    if anthropic_key:

        args_list += ["--anthropic-key", anthropic_key]

    _sys.argv = args_list

    try:

        run_benchmark()

    finally:

        _sys.argv = _saved_argv

    return _last_predictions_path or output_path


if __name__ == "__main__":

    run_benchmark()
