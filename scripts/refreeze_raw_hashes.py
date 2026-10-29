#!/usr/bin/env python3
"""
refreeze_raw_hashes.py — refresh a results dir's RAW_HASHES.txt without losing history.

Raw run artefacts stay out of git; RAW_HASHES.txt (sha256, one per line) is the
provenance record. When a raw file is regenerated -- as Sol's two web-search
runs were on 2026-09-20 after the scripts/web_search.py fix -- the recorded
hash goes stale, and silently overwriting it would erase the fact that an
earlier artefact existed at all.

So this never drops a line. Output has three parts:

    # current   sha256 of every file now under raw/ (plus any top-level file
                the previous record listed and that still exists)
    # superseded   every previously recorded hash whose file has since changed
                or disappeared, kept verbatim with the date it was superseded

Files whose hash is unchanged are simply carried forward. Idempotent: running
it twice produces the same file.
"""

from __future__ import annotations

import argparse, hashlib, os, re, sys
from datetime import date

LINE = re.compile(r"^\s*([0-9a-f]{64})\s+\*?(\S+)\s*$")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse(path: str):
    """Return (current: {rel: sha}, superseded: [raw lines]) from an existing file."""
    current, superseded = {}, []
    if not os.path.exists(path):
        return current, superseded
    section = "current"
    for line in open(path, encoding="utf-8"):
        s = line.rstrip("\n")
        if s.startswith("# superseded"):
            section = "superseded"
            continue
        if section == "superseded":
            if s.strip() and not s.startswith("#"):
                superseded.append(s)
            continue
        m = LINE.match(s)
        if m:
            current[m.group(2)] = m.group(1)
    return current, superseded


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir")
    ap.add_argument("--note", default="", help="one-line reason, recorded in the header")
    ap.add_argument("--out", help="write here instead of <results_dir>/RAW_HASHES.txt")
    a = ap.parse_args()

    rd = a.results_dir.rstrip("/")
    target = a.out or os.path.join(rd, "RAW_HASHES.txt")
    prev, superseded = parse(os.path.join(rd, "RAW_HASHES.txt"))
    today = date.today().isoformat()

    # everything under raw/, plus previously listed top-level files that still exist
    files = []
    rawdir = os.path.join(rd, "raw")
    if os.path.isdir(rawdir):
        for f in sorted(os.listdir(rawdir)):
            p = os.path.join(rawdir, f)
            if os.path.isfile(p):
                files.append("raw/" + f)
    for rel in prev:
        if not rel.startswith("raw/") and os.path.isfile(os.path.join(rd, rel)):
            files.append(rel)
    files = sorted(set(files))

    now = {rel: sha256(os.path.join(rd, rel)) for rel in files}

    changed, gone = [], []
    for rel, old in prev.items():
        if rel not in now:
            gone.append(rel)
            superseded.append(f"{old}  {rel}   # file absent as of {today}")
        elif now[rel] != old:
            changed.append(rel)
            superseded.append(f"{old}  {rel}   # superseded {today}: file regenerated")
    added = [rel for rel in now if rel not in prev]

    with open(target, "w", encoding="utf-8") as f:
        f.write("# sha256 of raw run artifacts kept out of git\n")
        f.write(f"# refrozen {today}" + (f": {a.note}" if a.note else "") + "\n")
        f.write("# current\n")
        for rel in files:
            f.write(f"{now[rel]}  {rel}\n")
        if superseded:
            f.write("\n# superseded -- earlier hashes kept for provenance; never delete\n")
            for line in superseded:
                f.write(line + "\n")

    print(f"{target}: {len(files)} current"
          f"{f', {len(added)} newly recorded' if added else ''}"
          f"{f', {len(changed)} superseded (regenerated)' if changed else ''}"
          f"{f', {len(gone)} absent' if gone else ''}")
    for rel in changed:
        print(f"  regenerated: {rel}")
    for rel in added:
        print(f"  new:         {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
