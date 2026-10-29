"""
gates.py — mechanical checks applied to a referee's answer, after the fact.

A judge can be wrong, and the usual failure is not a bad opinion but a bad
premise: a quote that is not in the source, a decomposition that quietly skips
one of the claim's three numbers, a numeric element waved through without a
figure. None of those need a model to detect. Every check here runs in code
against the text the referee was actually shown, so a certification survives
only if its factual scaffolding holds.

An item is certified by a referee only if EVERY gate passes. Gates are reported
individually so a failure can be attributed rather than guessed at.

  verdict_wrong        the referee said WRONG_LABEL
  decidable            the referee found no unquantified qualifier
  no_vague_element     no element was typed "vague"
  all_satisfied        every element satisfied is exactly true
  numbers_covered      every number in the claim appears in some element's text
  numeric_values       every numeric element carries a reported value with a digit
  quotes_in_source     (binding) every evidence quote really occurs in the source
  numeric_direction    every numeric element's inequality is re-checked in code:
                       the threshold is read from the element, the figure from
                       reported_value, and the comparison is done arithmetically,
                       not taken on the referee's word. Unparseable means FAIL.
  source_dated         (achieved) source_date parses and is on or before the target
"""
from __future__ import annotations
import re

_NUM = re.compile(r"\d+(?:[.,]\d+)?")
_WORD = re.compile(r"[a-z0-9]+")
MIN_QUOTE_WORDS = 4

# a leading or trailing "By <Month> <Year>" deadline is not part of the claim's
# testable content -- the referees are told to ignore dates, so the gate must too
_DEADLINE = re.compile(r"\b[Bb]y [A-Z][a-z]+\.? \d{4}\b,?\s*")

_LOWER = (r"(fewer than|less than|below|under|at most|no more than|not exceeding|within|"
          r"or fewer|or less|or lower|or shorter|<=|<)")
_UPPER = (r"(at least|more than|above|over|exceeding|greater than|higher than|beyond|\bplus\b|"
          r"or more|or higher|or greater|or better|or above|or longer|or faster|no fewer than|"
          r"minimum of|at minimum|>=|>)")
_LOWER_RE = re.compile(_LOWER, re.I)
_UPPER_RE = re.compile(_UPPER, re.I)

# thresholds are often spelled out ("at least sixteen targets", "nine or more")
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
            "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
            "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
            "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
            "hundred": 100, "thousand": 1000, "million": 1e6, "billion": 1e9}


def _floats(text: str) -> list[float]:
    out = []
    for m in _NUM.findall(text or ""):
        try:
            out.append(float(m.replace(",", "")))
        except ValueError:
            pass
    for w in _WORD.findall((text or "").lower()):
        if w in _WORDNUM and _WORDNUM[w] < 1000:      # scale words are units, not thresholds
            out.append(float(_WORDNUM[w]))
    return out


def numeric_direction_ok(element: dict) -> bool:
    """Re-do the inequality in code. The referee supplies the threshold (in the
    element text, copied from the claim) and the figure (reported_value); the
    comparison itself is arithmetic here, so a referee cannot assert a match that
    the numbers do not support. Anything unparseable fails."""
    text = str(element.get("text", "") or "")
    thresholds = _floats(text)
    values = _floats(str(element.get("reported_value", "") or ""))
    if not thresholds or not values:
        return False
    lower, upper = bool(_LOWER_RE.search(text)), bool(_UPPER_RE.search(text))
    if lower and not upper:
        return any(v <= t for t in thresholds for v in values)
    if upper and not lower:
        return any(v >= t for t in thresholds for v in values)
    # No explicit direction. Ceilings in this corpus essentially always carry one
    # ("fewer than", "below", "within"), so a bare threshold is read as a floor:
    # the source must report a figure that meets or exceeds it. Equality counts.
    return any(v >= t or abs(v - t) < 1e-9 for t in thresholds for v in values)


def norm(s: str) -> str:
    """Lowercase, strip punctuation and unicode variants, collapse whitespace.
    Tolerates a model tidying a dash or a quote mark; does not tolerate paraphrase."""
    return " ".join(_WORD.findall((s or "").lower()))


def _elements(rec: dict) -> list[dict]:
    els = rec.get("elements")
    return [e for e in els if isinstance(e, dict)] if isinstance(els, list) else []


def numbers_in(text: str) -> set[str]:
    """Distinct numeric tokens, with thousands separators removed so 145,000
    and 145000 compare equal."""
    return {m.replace(",", "") for m in _NUM.findall(text or "")}


def gate_results(rec: dict, mode: str, claim: str, source_text: str = "",
                 target_ym: str | None = None) -> dict:
    els = _elements(rec)
    g = {}
    g["verdict_wrong"] = rec.get("verdict") == "WRONG_LABEL"
    g["decidable"] = rec.get("decidable") is True
    g["no_vague_element"] = not any(str(e.get("kind", "")).lower() == "vague" for e in els)
    g["all_satisfied"] = bool(els) and all(e.get("satisfied") is True for e in els)

    want = numbers_in(_DEADLINE.sub("", claim or ""))
    got = numbers_in(" ".join(str(e.get("text", "")) for e in els))
    g["numbers_covered"] = want.issubset(got)

    numeric_els = [e for e in els if str(e.get("kind", "")).lower() == "numeric"]
    g["numeric_values"] = all(
        bool(re.search(r"\d", str(e.get("reported_value") or ""))) for e in numeric_els)
    g["numeric_direction"] = all(numeric_direction_ok(e) for e in numeric_els)

    if mode == "binding":
        src = norm(source_text)
        ok = bool(els)
        for e in els:
            q = norm(e.get("evidence_quote"))
            if len(q.split()) < MIN_QUOTE_WORDS or q not in src:
                ok = False
                break
        g["quotes_in_source"] = ok
    else:
        d = str(rec.get("source_date") or "")
        m = re.match(r"(\d{4})-(\d{2})", d)
        g["source_dated"] = bool(m and target_ym and f"{m.group(1)}-{m.group(2)}" <= target_ym)
    return g


def certified(rec: dict, mode: str, claim: str, source_text: str = "",
              target_ym: str | None = None) -> bool:
    return all(gate_results(rec, mode, claim, source_text, target_ym).values())


def source_text_for(record: dict) -> str:
    """The exact text the binding prompt showed the referee, truncated identically
    (strict.py build(): results_and_metrics[:1800], source_abstract[:2500])."""
    return ((record.get("results_and_metrics") or "")[:1800] + " "
            + (record.get("source_abstract") or "")[:2500])
