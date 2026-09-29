"""a7_inductive.py — inductive pass over the 300-trace stratified sample (plus a 6,000-trace
background sample for stable clustering). Reports recurring patterns the deductive codebook may miss.
Prints CLUSTER TOP TERMS and STRUCTURAL FEATURE RATES only; no trace text is printed.
Representative trace ids per cluster are written to inductive_clusters.json for the codebook."""
import json, random, re, sys, collections
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C


# TF-IDF + spherical k-means in numpy (scikit-learn is not installed in this env, and the
# study stays on one interpreter; validated against a toy set in the docstring of _kmeans).
TOKEN = re.compile(r"[a-z][a-z\-]{2,}")
STOP = set("""the a an and or but of to in for on with by from as is are was were be been being this that these those
it its their his her they them we our you your i not no than then so such which who whom whose what when where while
have has had having do does did doing can could should would may might must will shall there here at into over under
more most less least very much many few other another same also only just about across after before between during
if because although though however therefore thus hence given due within without upon per via both each any all some
one two three four five new using used use based likely unlikely make makes made""".split())


def _tfidf(texts, max_features=6000, min_df=5):
    docs = [[w for w in TOKEN.findall(t.lower()) if w not in STOP] for t in texts]
    df = collections.Counter()
    for d in docs: df.update(set(d))
    vocab = [w for w, c in df.most_common() if c >= min_df][:max_features]
    idx = {w: j for j, w in enumerate(vocab)}
    idf = np.array([np.log(len(docs) / (1 + df[w])) + 1.0 for w in vocab])
    X = np.zeros((len(docs), len(vocab)), dtype=np.float32)
    for i, d in enumerate(docs):
        c = collections.Counter(w for w in d if w in idx)
        if not c: continue
        for w, v in c.items(): X[i, idx[w]] = v
        X[i] /= max(1, sum(c.values()))
    X *= idf
    n = np.linalg.norm(X, axis=1, keepdims=True); n[n == 0] = 1
    return X / n, np.array(vocab)


def _kmeans(X, k, seed, iters=60):
    """Spherical k-means (cosine), k-means++ init. Rows of X are L2-normalised."""
    rs = np.random.default_rng(seed)
    cent = [X[rs.integers(len(X))]]
    for _ in range(k - 1):
        d = 1 - (X @ np.array(cent).T).max(1)
        d = np.clip(d, 0, None) ** 2
        cent.append(X[rs.choice(len(X), p=d / d.sum())] if d.sum() > 0 else X[rs.integers(len(X))])
    cent = np.array(cent)
    lab = np.zeros(len(X), int)
    for _ in range(iters):
        new = (X @ cent.T).argmax(1)
        if (new == lab).all(): break
        lab = new
        for c in range(k):
            m = lab == c
            if m.any():
                v = X[m].mean(0); nv = np.linalg.norm(v)
                cent[c] = v / nv if nv else cent[c]
    return lab, cent

SEED = 11
samp = [json.loads(l) for l in open(C.STUDY / "inductive_sample.jsonl", encoding="utf-8")]
rng = random.Random(SEED)
bg = collections.defaultdict(list)
for r in C.iter_traces(lambda r: r["condition"] == "base" and not r["trace_is_raw_json"] and 8 <= r["trace_words"] <= 400):
    bg[r["task"]].append(r)
back = []
for t in C.TASKS:
    back += rng.sample(bg[t], min(1200, len(bg[t])))
print(f"inductive sample {len(samp)}; background {len(back)}")

# ---------------- structural features (regex, reported as rates; these are CANDIDATE codes)
NUM = re.compile(r"\d")
FEAT = {
 "quotes_a_number_from_the_item": lambda r: bool(NUM.search(r["trace"])) and any(
     tok in r["trace"] for tok in re.findall(r"\d+\.?\d*%|\d+\.\d+|\b\d{2,}\b", r["question"])[:12]),
 "restates_question_without_new_content": lambda r: r["trace"][:60].lower().startswith(("this question", "the question", "this describes", "this asks", "the query", "this query")),
 "names_a_specific_system_or_dataset": lambda r: bool(re.search(r"\b([A-Z][a-z]+[A-Z]\w+|[A-Z]{2,}[\-\d]*\b)", r["trace"])),
 "states_a_mechanism_or_causal_path": lambda r: bool(re.search(r"\b(because|since|due to|driven by|mechanism|via|through|leads? to|results? in|enables?)\b", r["trace"], re.I)),
 "appeals_to_field_momentum": lambda r: bool(re.search(r"\b(rapid(ly)? (advanc|progress|evolv|develop)|active(ly)? research|growing interest|surge in|momentum|intense (research|interest)|increasing(ly)? (attention|focus))\b", r["trace"], re.I)),
 "appeals_to_specificity_as_implausible": lambda r: bool(re.search(r"\b((highly |very |overly |unusually )?specific|precise|granular|narrow|oddly specific|arbitrary)\b.{0,60}\b(unlikely|implausible|suggests?|niche|speculative|obscure|not (widely )?(recognized|known|documented))\b", r["trace"], re.I)),
 "treats_question_as_describing_real_work": lambda r: bool(re.search(r"\b(this (describes|refers to|appears to (be|describe)|likely refers)|suggests? (results?|findings?) from|appears to reference)\b", r["trace"], re.I)),
 "verifiability_doubt": lambda r: bool(re.search(r"\b(verifiab|documented publicly|publicly (available|documented)|not .{0,20}(verifiable|tracked)|difficult to (verify|confirm))\b", r["trace"], re.I)),
 "conjunction_of_requirements": lambda r: bool(re.search(r"\b(simultaneous(ly)?|both .{0,30}and|all (three|four|of these)|multiple (simultaneous|specific) (breakthroughs?|requirements?|criteria)|combination of|conjunction)\b", r["trace"], re.I)),
 "timeframe_too_short": lambda r: bool(re.search(r"\b((short|tight|limited|aggressive|compressed) (timeframe|timeline|window)|only .{0,15}(months|weeks) (away|remain)|within (such )?a (short|narrow)|by the stated date)\b", r["trace"], re.I)),
 "explicit_probability_or_odds": lambda r: bool(re.search(r"\b(\d{1,3}\s?%|probability|odds|more likely than not|50-?50|chance of)\b", r["trace"], re.I)),
 "already_happened_claim": lambda r: bool(re.search(r"\b(has (already )?been (achieved|demonstrated|reported|published|shown)|was (demonstrated|reported|published|achieved) in|already (exists|achieved|demonstrated))\b", r["trace"], re.I)),
}
for name, sets in (("300-trace stratified sample", samp), ("background sample", back)):
    print(f"\n#### structural feature rates — {name}")
    for f, fn in FEAT.items():
        v = [fn(r) for r in sets]
        bt = {t: np.mean([fn(r) for r in sets if r["task"] == t]) for t in C.TASKS if any(r["task"] == t for r in sets)}
        print(f"  {f:42s} {100*np.mean(v):5.1f}%   " + " ".join(f"{t}:{100*bt[t]:.0f}%" for t in bt))

# ---------------- clustering, top terms only
out = {}
for task in C.TASKS:
    txt = [r["trace"] for r in back if r["task"] == task]
    ids = [r["trace_id"] for r in back if r["task"] == task]
    if len(txt) < 50: continue
    X, terms = _tfidf(txt)
    k = 6
    labels, centers = _kmeans(X, k, SEED)
    print(f"\n#### {task}: {k} clusters of {len(txt)} traces — top terms")
    out[task] = []
    for c in range(k):
        top = terms[np.argsort(centers[c])[::-1][:12]]
        m = labels == c
        print(f"  c{c} ({m.sum():4d}): " + ", ".join(top))
        out[task].append(dict(cluster=c, n=int(m.sum()), top_terms=list(top),
                              example_trace_ids=[ids[j] for j in np.where(m)[0][:6]]))
json.dump(out, open(C.STUDY / "inductive_clusters.json", "w"), indent=1)
