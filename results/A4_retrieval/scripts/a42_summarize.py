"""A4.2 summary: ground-truth inclusion rates per model x condition (Wilson 95% CI), by task and by domain; writes results.md + tables."""
import json, math, collections, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); from a42_common import *
def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))
rs = [json.loads(l) for l in open(OUT / "A4_2_groundtruth_inclusion/verdicts.jsonl") if l.strip()]
ok = [r for r in rs if (r.get("judge") or {}).get("verdict") in ("INCLUDED", "NOT_INCLUDED")]
ev = load_events()
from urllib.parse import urlparse
for r in ok:   # deterministic URL match recomputed with DOI-suffix matching; judge match confirmed against the stored list
    kind, key = paper_key(ev[r["id"]]); r["url_match_stored"] = any(url_matches(kind, key, u) for u in (r.get("stored_urls") or []))
    mu = (r["judge"] or {}).get("matched_url"); r["judge_url_in_stored"] = bool(mu) and (mu in set(r.get("stored_urls") or []))
    r["matched_domain"] = urlparse(mu).netloc.replace("www.", "") if mu else None
err = [r for r in rs if r not in ok]
MODEL_ORDER = ["GPT-4o", "LLaMA 3.3 70B", "DeepSeek R1", "Claude S4.5", "GPT-5.4", "Claude Sonnet 5", "GPT-5.6 Sol"]
def rate(sub, key=lambda r: r["judge"]["verdict"] == "INCLUDED"):
    n = len(sub); k = sum(key(r) for r in sub); lo, hi = wilson(k, n); return k, n, lo, hi
def cell(sub, key=None):
    k, n, lo, hi = rate(sub, key) if key else rate(sub)
    return f"{k/n:.1%} [{lo:.1%}, {hi:.1%}] (n={n})" if n else "—"
L = ["# A4.2 — Does the retrieved evidence contain the ground truth?", "",
     "**Findings.** (1) In the unrestricted WS condition the retrieved evidence contains the source paper or its stated outcome for 74–93% of events (the provider's native tool for GPT-4o/GPT-5.4: 88–93%; the single-query You.com pipeline: 74–85%). "
     "(2) In WS+Cutoff the rate on PRE-cutoff events is 77–85% (the paper existed before the cutoff, so this is recall, not leakage) and on POST-cutoff events it is 20–37% by judge on re-queried evidence, "
     "with 9–20% confirmed on the exact URLs the model received (Sol 37% on 30 events). (3) The post-cutoff leakage is not the source paper's own page (URL match 0–3%); it is snippet text: You.com dates a page by `page_age`, "
     "but the snippets it returns for researchgate.net publication pages include the abstracts of newer 'related' papers, so a page dated 2022 can carry a 2026 paper's results verbatim (`leak_example.json`). "
     "researchgate.net accounts for 332 of 439 post-cutoff inclusions; bioRxiv/medRxiv/arXiv/PubMed pages of the same work under another identifier account for most of the rest. "
     "(4) A domain blocklist for aggregator pages, or content-level dating of snippets, would be needed for a clean pre-cutoff condition; the current WS+Cutoff knowledge gap therefore contains a leakage component on post-cutoff events.", "",
     f"Judged cases: {len(ok)} of {len(rs)} ({len(err)} judge/retrieval errors excluded). Judge: Claude Sonnet 5 (effort low), asked whether any retrieved result is the source paper itself "
     "(same arXiv id / DOI / abstract, including preprint versions) or states the realized outcome. Evidence reconstruction: You.com runs re-queried with the stored query and the run's "
     "freshness bound, then filtered/formatted by the unmodified `scripts/web_search.py` code; native-tool runs (GPT-4o WS, GPT-5.4 WS) judged on the fetched text of the URLs the tool cited "
     "(a lower bound on what the tool read). `URL match` = deterministic arXiv-id/DOI match against the URLs stored at run time (a floor that needs no judge). 95% Wilson CIs.", ""]
L += ["## Inclusion rate per model and condition\n", "| model | condition | mechanism | n | ground truth INCLUDED (judge) | of which: source paper / outcome stated | judge's matched URL was in the model's stored list | URL match (stored URLs, arXiv id / DOI) | stored↔live URL overlap |", "|---|---|---|---|---|---|---|---|---|"]
summary = {}
for m in MODEL_ORDER:
    for cond in ("ws_cutoff", "ws"):
        sub = [r for r in ok if r["model"] == m and r["condition"] == cond]
        if not sub: continue
        inc = [r for r in sub if r["judge"]["verdict"] == "INCLUDED"]; sp = sum(r["judge"].get("match_type") == "source_paper" for r in inc); os_ = sum(r["judge"].get("match_type") == "outcome_stated" for r in inc)
        ov = [r["stored_live_overlap"] for r in sub if r.get("stored_live_overlap") is not None]
        k, n, lo, hi = rate(sub); summary[f"{m}|{cond}"] = dict(n=n, included=k, rate=k / n, ci=[lo, hi], source_paper=sp, outcome_stated=os_, url_match=sum(r.get("url_match_stored", False) for r in sub), mechanism=sub[0]["mechanism"], overlap=(sum(ov) / len(ov) if ov else None))
        conf = sum(r.get("judge_url_in_stored", False) for r in inc)
        L.append(f"| {m} | {cond} | {sub[0]['mechanism']} | {n} | {k/n:.1%} [{lo:.1%}, {hi:.1%}] | {sp} / {os_} | {conf/n:.1%} ({conf}) | {cell(sub, lambda r: bool(r.get('url_match_stored')))} | {(f'{sum(ov)/len(ov):.0%}' if ov else 'n/a')} |")
L += ["\n## By task (events carrying that task type; retrieval is per event, shared across tasks)\n", "| model | condition | binary | perturbed | MCQ | FRQ | date |", "|---|---|---|---|---|---|---|"]
for m in MODEL_ORDER:
    for cond in ("ws_cutoff", "ws"):
        sub = [r for r in ok if r["model"] == m and r["condition"] == cond]
        if not sub: continue
        L.append(f"| {m} | {cond} | " + " | ".join(cell([r for r in sub if t in r.get("has_tasks", [])]) for t in ("binary", "binary_perturbed", "mcq", "frq", "date")) + " |")
areas = sorted({r.get("area") for r in ok if r.get("area")})
L += ["\n## By domain\n", "| model | condition | " + " | ".join(areas) + " |", "|---|---|" + "---|" * len(areas)]
for m in MODEL_ORDER:
    for cond in ("ws_cutoff", "ws"):
        sub = [r for r in ok if r["model"] == m and r["condition"] == cond]
        if not sub: continue
        L.append(f"| {m} | {cond} | " + " | ".join(cell([r for r in sub if r.get("area") == a]) for a in areas) + " |")
# pre vs post cutoff for ws_cutoff runs
ev = load_events()
def months(ym): y, mo = ym.split("-")[:2]; return int(y) * 12 + int(mo)
L += ["\n## WS+Cutoff runs: split by whether the event predates the model's cutoff (post-cutoff inclusion is leakage through the date filter)\n",
      "| model | pre-cutoff: judge INCLUDED | pre-cutoff: URL match | post-cutoff: judge INCLUDED | post-cutoff: judge match confirmed in stored list | post-cutoff: URL match | post-cutoff: matched domain (top) |", "|---|---|---|---|---|---|---|"]
for m in MODEL_ORDER:
    sub = [r for r in ok if r["model"] == m and r["condition"] == "ws_cutoff"]
    if not sub: continue
    cut = months(RUNS[sub[0]["run"]][5][:7]); pre = [r for r in sub if months(ev[r["id"]]["publication_date"]) < cut]; post = [r for r in sub if months(ev[r["id"]]["publication_date"]) >= cut]
    dom = collections.Counter(r["matched_domain"] for r in post if r["judge"]["verdict"] == "INCLUDED")
    L.append(f"| {m} | {cell(pre)} | {cell(pre, lambda r: bool(r.get('url_match_stored')))} | {cell(post)} | {cell(post, lambda r: bool(r.get('judge_url_in_stored')))} | {cell(post, lambda r: bool(r.get('url_match_stored')))} | {', '.join(f'{d} {n}' for d, n in dom.most_common(3))} |")
L += ["\n## Where the leaked ground truth comes from (WS+Cutoff, post-cutoff events, judge INCLUDED)\n", "| domain of matched result | cases | of which URL in stored list |", "|---|---|---|"]
leak = [r for r in ok if r["condition"] == "ws_cutoff" and r["judge"]["verdict"] == "INCLUDED" and months(ev[r["id"]]["publication_date"]) >= months(RUNS[r["run"]][5][:7])]
for d, n in collections.Counter(r["matched_domain"] for r in leak).most_common(12):
    L.append(f"| {d} | {n} | {sum(1 for r in leak if r['matched_domain'] == d and r.get('judge_url_in_stored'))} |")
json.dump(summary, open(OUT / "tables/A4_2_inclusion_summary.json", "w"), indent=1)
(OUT / "A4_2_groundtruth_inclusion/results.md").write_text("\n".join(L) + "\n"); print("\n".join(L[:20]))

# figure: inclusion rate per model x condition
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14, 4.4), gridspec_kw={"width_ratios": [1.3, 1]}); xs = []; labels = []
for i, m in enumerate(MODEL_ORDER):
    for j, cond in enumerate(("ws_cutoff", "ws")):
        v = summary.get(f"{m}|{cond}")
        if not v: continue
        x = i + (j - 0.5) * 0.36; col = "#0072B2" if cond == "ws_cutoff" else "#D55E00"
        ax.bar(x, v["rate"], width=0.34, color=col, alpha=0.85, label=("WS+Cutoff" if cond == "ws_cutoff" else "WS (unrestricted)") if i == 0 else None)
        ax.errorbar(x, v["rate"], yerr=[[v["rate"] - v["ci"][0]], [v["ci"][1] - v["rate"]]], fmt="none", ecolor="black", capsize=2, lw=0.8)
        ax.plot([x - 0.15, x + 0.15], [v["url_match"] / v["n"]] * 2, color="black", lw=1.2, label="URL match (stored URLs)" if (i == 0 and j == 0) else None)
        ax.annotate(f"n={v['n']}", (x, 0.01), ha="center", fontsize=5, color="white")
ax.set_xticks(range(len(MODEL_ORDER))); ax.set_xticklabels(MODEL_ORDER, fontsize=7, rotation=15); ax.set_ylim(0, 1); ax.set_ylabel("share of cases with ground truth in retrieved results", fontsize=7); ax.tick_params(labelsize=7)
ax.legend(fontsize=7, frameon=False); ax.grid(axis="y", color="#EEEEEE", lw=0.5); ax.set_title("A4.2 — ground-truth inclusion in retrieved evidence (judge verdict, 95% Wilson CI; black tick = deterministic URL match)", fontsize=8)
for i, m in enumerate(MODEL_ORDER):
    sub = [r for r in ok if r["model"] == m and r["condition"] == "ws_cutoff"]
    if not sub: continue
    cut = months(RUNS[sub[0]["run"]][5][:7]); post = [r for r in sub if months(ev[r["id"]]["publication_date"]) >= cut]
    if not post: continue
    k1 = sum(r["judge"]["verdict"] == "INCLUDED" for r in post); k2 = sum(bool(r.get("judge_url_in_stored")) for r in post); n = len(post)
    ax2.bar(i - 0.18, k1 / n, width=0.34, color="#CC79A7", alpha=0.85, label="judge INCLUDED (re-queried evidence)" if i == 0 else None); ax2.bar(i + 0.18, k2 / n, width=0.34, color="#882255", alpha=0.9, label="confirmed on the model's stored URLs" if i == 0 else None)
    lo, hi = wilson(k1, n); ax2.errorbar(i - 0.18, k1 / n, yerr=[[k1 / n - lo], [hi - k1 / n]], fmt="none", ecolor="black", capsize=2, lw=0.8); ax2.annotate(f"n={n}", (i, 0.01), ha="center", fontsize=6)
ax2.set_xticks(range(len(MODEL_ORDER))); ax2.set_xticklabels(MODEL_ORDER, fontsize=7, rotation=15); ax2.set_ylim(0, 1); ax2.tick_params(labelsize=7); ax2.grid(axis="y", color="#EEEEEE", lw=0.5); ax2.legend(fontsize=6.5, frameon=False)
ax2.set_title("WS+Cutoff, POST-cutoff events only: ground truth leaked through the date filter", fontsize=8)
fig.tight_layout(); fig.savefig(OUT / "figures/a42_inclusion.png", dpi=200); fig.savefig(OUT / "figures/a42_inclusion.pdf"); plt.close(fig)
