"""
neg_gates.py — mechanical evidence gates for the strict negatives re-verification.

A synthetic negative is mislabelled only if the EXACT perturbed claim actually
happened by the target date. The prompt in verify_neg_strict.py says so; this
module is what makes it stick, because a prompt is a request and a gate is a
check.

Every gate runs in code against the referee's own record. An ACHIEVED verdict
that fails any gate is invalid and is downgraded to NOT_ACHIEVED with the failing
gate names recorded, per the study brief:

  "For every ACHIEVED verdict, the record must contain the exact reported value
   or the exact satisfied constraint, the date, the source URL, and the quoted
   passage showing it. An ACHIEVED verdict without all four is invalid."

The gates, in the order they are reported:

  has_requirement      the referee named the exact modified value / added constraint
  has_value            numeric -> reported_value carries a digit
                       constraint -> satisfied_constraint is a real statement
  has_date             source_date parses as YYYY-MM or YYYY-MM-DD
  date_on_or_before    that date is on or before the claim's target date
  has_url              exactly one usable http(s) source URL
  has_quote            quoted_passage is a passage, not a restated title
  value_in_quote       (numeric) a figure from reported_value occurs in the quote,
                       so the quote actually shows the number it is offered for
  direction_ok         the inequality is recomputed in code from the claim's
                       threshold and the referee's reported figure
  same_setting         the referee affirmed same task / system / measurement
  source_not_excluded  the cited URL is not the item's own source paper

`numeric` here means "the claim's requirement contains a number", decided from
the text, not from the referee's self-declared kind -- a referee cannot dodge the
arithmetic gate by typing its own requirement as a constraint.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gates import numeric_direction_ok, numbers_in, norm, _floats   # reuse, unchanged

_URL = re.compile(r"https?://[^\s,;\"')\]]+", re.I)
_ARXIV = re.compile(r"(\d{4}\.\d{4,5})")
_DOI = re.compile(r"10\.\d{4,9}/[-._;()/:a-z0-9]+", re.I)
MIN_QUOTE_WORDS = 8
MIN_CONSTRAINT_CHARS = 20

GATE_NAMES = ["has_requirement", "has_value", "has_date", "date_on_or_before",
              "has_url", "has_quote", "value_in_quote", "direction_ok",
              "same_setting", "source_not_excluded"]


def _ym(d: str) -> str | None:
    m = re.match(r"\s*(\d{4})-(\d{1,2})", str(d or ""))
    if m and 1 <= int(m.group(2)) <= 12:
        return f"{m.group(1)}-{int(m.group(2)):02d}"
    m = re.match(r"\s*(\d{4})\s*$", str(d or ""))
    return f"{m.group(1)}-12" if m else None          # bare year: most permissive month


def excluded_ids(paper_link: str) -> set[str]:
    """Identifiers of the item's own source paper, in the forms a URL can carry."""
    s = str(paper_link or "").lower()
    out = set()
    for a in _ARXIV.findall(s):
        out.add(a)
    for d in _DOI.findall(s):
        d = d.rstrip(".;,)")
        out.add(d)
        if "/" in d:
            out.add(d.split("/", 1)[1])               # publisher URLs drop the 10.xxxx/ prefix
    return {x for x in out if len(x) >= 6}


def urls_in(rec: dict) -> list[str]:
    seen, out = set(), []
    for u in [rec.get("source_url")] + list(rec.get("urls") or []):
        for m in _URL.findall(str(u or "")):
            m = m.rstrip(".,);]")
            if m.lower() not in seen:
                seen.add(m.lower())
                out.append(m)
    return out


def gate_results(rec: dict, item: dict) -> dict:
    req = str(rec.get("claim_requirement") or "").strip()
    val = str(rec.get("reported_value") or "").strip()
    con = str(rec.get("satisfied_constraint") or "").strip()
    quote = str(rec.get("quoted_passage") or "").strip()
    title = str(rec.get("source_name") or "").strip()
    urls = urls_in(rec)
    is_numeric = bool(numbers_in(req))

    g = {}
    g["has_requirement"] = len(req) >= 3
    g["has_value"] = (bool(re.search(r"\d", val)) if is_numeric
                      else len(con) >= MIN_CONSTRAINT_CHARS)

    ym = _ym(rec.get("source_date"))
    g["has_date"] = ym is not None
    tgt = str(item.get("target_ym") or "")
    g["date_on_or_before"] = bool(ym and tgt and ym <= tgt)

    g["has_url"] = len(urls) >= 1

    qn = norm(quote)
    g["has_quote"] = len(qn.split()) >= MIN_QUOTE_WORDS and qn != norm(title)

    if is_numeric:
        g["value_in_quote"] = bool(numbers_in(val) & numbers_in(quote))
        g["direction_ok"] = numeric_direction_ok({"text": req, "reported_value": val})
    else:
        g["value_in_quote"] = True        # not applicable to a non-numeric requirement
        g["direction_ok"] = True

    g["same_setting"] = rec.get("same_setting") is True

    bad = excluded_ids(item.get("paper_link"))
    blob = " ".join(urls).lower() + " " + title.lower()
    g["source_not_excluded"] = not any(b in blob for b in bad)
    return g


def adjudicate(rec: dict, item: dict) -> tuple[str, dict, list[str]]:
    """Returns (final_verdict, gate_results, failed_gate_names).

    Only ACHIEVED is gated. NOT_ACHIEVED needs no evidence: it is the default the
    brief asks for whenever the evidence is partial, indirect or absent."""
    if rec.get("verdict") != "ACHIEVED":
        return (rec.get("verdict") or "NOT_ACHIEVED"), {}, []
    g = gate_results(rec, item)
    failed = [k for k in GATE_NAMES if not g.get(k)]
    return ("ACHIEVED" if not failed else "NOT_ACHIEVED"), g, failed
