import time

import sys

from datetime import datetime

from youdotcom import You


_no_temperature: dict = {}   # models seen to reject `temperature` (query generation then uses the API default)


def _chat(client, model: str, prompt: str, retries: int = 3) -> str:
    """Single-turn chat helper — works with OpenAI, AzureOpenAI, and Anthropic clients.
    Retries on None content or transient errors."""

    last_err = None

    for attempt in range(1, retries + 1):

        try:

            if type(client).__module__.startswith("anthropic"):

                response = client.messages.create(
                    model=model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}],
                )

                text = response.content[0].text if response.content else None

            else:

                kwargs = dict(model=model, messages=[{"role": "user", "content": prompt}])
                if not _no_temperature.get(model):
                    kwargs["temperature"] = 0
                try:
                    response = client.chat.completions.create(**kwargs)
                except Exception as e:
                    # Reasoning models (e.g. gpt-5.6-sol) reject any temperature but the
                    # default with a 400 'unsupported_value'. Drop the parameter for this
                    # model and retry once, instead of failing retrieval for the whole run.
                    if "temperature" in str(e) and "unsupported" in str(e).lower() and "temperature" in kwargs:
                        _no_temperature[model] = True
                        kwargs.pop("temperature")
                        response = client.chat.completions.create(**kwargs)
                    else:
                        raise

                text = (
                    response.choices[0].message.content
                    if response.choices and response.choices[0].message
                    else None
                )

            if text is not None:

                return text.strip()

            last_err = "API returned None content"

            print(
                f"  ⚠ [web_search._chat] attempt {attempt}/{retries}: "
                f"response content is None, retrying in {2 ** attempt}s...",
                file=sys.stderr,
            )

            time.sleep(2**attempt)

        except Exception as e:

            last_err = str(e)

            print(
                f"  ⚠ [web_search._chat] attempt {attempt}/{retries}: "
                f"{e}, retrying in {2 ** attempt}s...",
                file=sys.stderr,
            )

            time.sleep(2**attempt)

    raise RuntimeError(f"web_search._chat failed after {retries} attempts: {last_err}")


def _generate_search_query(client, question: str, model: str = "gpt-4o") -> str:

    return _chat(
        client,
        model,
        f"""
Rewrite the following question into a high-quality web search query optimized for information retrieval.

Guidelines:
- Include key entities, technical terms, and domain-specific keywords
- Add clarifying context if the question is ambiguous
- Prefer precise terminology over vague phrasing
- Avoid conversational or filler words
- Expand with relevant synonyms or related terms if helpful
- Do NOT include time-based words like "latest", "recent"

Output:
- A single optimized search query (not a sentence, no explanation)

Question: {question}

Search query:
""",
    )


def _generate_combined_query(client, questions: list, model: str = "gpt-4o") -> str:

    numbered = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))

    return _chat(
        client,
        model,
        f"""
You have several related questions about the same scientific topic or research paper.
Generate a single high-quality web search query that captures the shared subject across all of them.

Guidelines:
- Focus on core entities, technical concepts, and domain terminology shared across the questions
- Prefer precise, specific terms over broad or vague ones
- Do NOT include time-based words like "latest", "recent"

Output:
- A single optimized search query (not a sentence, no explanation)

Questions:
{numbered}

Search query:
""",
    )


def _extract_and_filter(results, query: str, cutoff_date: datetime):

    docs = []

    web_results = getattr(results.results, "web", None) or []

    for r in web_results:

        if not r.page_age or r.page_age >= cutoff_date:

            continue

        parts = []

        if r.title:

            parts.append(r.title)

        if r.description:

            parts.append(r.description)

        if r.snippets:

            parts.extend(r.snippets)

        seen = set()

        cleaned = []

        for p in parts:

            p = p.strip()

            if p and p not in seen:

                seen.add(p)

                cleaned.append(p)

        text = " ".join(cleaned)

        if len(text) < 100:

            continue

        score = sum(1 for w in query.lower().split() if w in text.lower())

        if score < 1:

            continue

        docs.append({"title": r.title, "text": text, "url": r.url, "length": len(text)})

    docs.sort(key=lambda x: x["length"], reverse=True)

    return docs


def _build_context(docs, max_docs=8, max_chars=1200):

    blocks = []

    for i, d in enumerate(docs[:max_docs]):

        text = d["text"][:max_chars]

        blocks.append(f"[Source {i+1}]\nTitle: {d['title']}\nURL: {d['url']}\n{text}")

    return "\n\n".join(blocks)


def web_search_get_context(
    *, questions: list, client, you_api_key: str, cutoff_date: datetime, model: str = "gpt-4o"
) -> dict:
    """
    Run one web search derived from all question types for a benchmark row.
    client must be a pre-built OpenAI or AzureOpenAI instance.
    Returns {"context": str, "urls": list[str], "query": str}.
    context is "" and urls is [] if no results are found.
    """

    empty = {"context": "", "urls": [], "query": ""}

    if not questions:

        return empty

    you = You(you_api_key)

    query = _generate_combined_query(client, questions, model)

    results = you.search.unified(
        query=query, freshness=f"1900-01-01to{cutoff_date.strftime('%Y-%m-%d')}"
    )

    docs = _extract_and_filter(results, query, cutoff_date)

    if not docs:

        return {**empty, "query": query}

    return {
        "context": _build_context(docs),
        "urls": [d["url"] for d in docs],
        "query": query,
    }


def web_search_answer(
    *,
    question: str = None,
    query: str = None,
    client,
    you_api_key: str,
    cutoff_date: datetime,
    model: str = "gpt-4o",
) -> str:
    """
    Run a full web-search-augmented yes/no answer.
    client must be a pre-built OpenAI or AzureOpenAI instance.
    Provide either question (query auto-generated) or query (used directly).
    """

    if not question and not query:

        raise ValueError("Provide either 'question' or 'query'")

    you = You(you_api_key)

    if query is None:

        query = _generate_search_query(client, question, model)

    results = you.search.unified(
        query=query, freshness=f"1900-01-01to{cutoff_date.strftime('%Y-%m-%d')}"
    )

    docs = _extract_and_filter(results, query, cutoff_date)

    if not docs:

        return "No relevant results found."

    context = _build_context(docs)

    return _chat(
        client,
        model,
        f"""
You are a research assistant making a forward-looking judgment.

The provided context is OPTIONAL supporting information. Use it if helpful, but you may also rely on your own knowledge and reasoning to make the best possible forecast.

Return your answer in STRICT JSON format:
{{
  "reasoning": "clear explanation",
  "answer": "Yes or No",
  "confidence": float (0 to 1)
}}

Rules:
- Answer MUST be "Yes" or "No"
- Do NOT include any text outside the JSON
- Use the context as additional evidence, not a limitation
- Confidence should reflect uncertainty in your forecast

Context:
{context}

Question:
{question}
""",
    )
