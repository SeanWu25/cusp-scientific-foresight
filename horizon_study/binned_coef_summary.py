"""Compact tables + narrative for the binned-coefficient analysis, written from tables/binned_coef.json.
Emits tables/binned_coef_summary.md and splices it into RESULTS.md and REVIEWER_RESPONSE_R1_C4.md between markers."""
import json, re, sys
from pathlib import Path
H = Path(__file__).resolve().parent; R = json.load(open(H / "tables/binned_coef.json"))
ROOT = H.parent


def c(est, key, ds=None):
    r = (R["base"][ds] if ds else R["ws"])[key]; return r[est].get("coef") or {}


def f(v, dec=2):
    return f"{v['mean']:+.{dec}f} [{v['ci_lo']:+.{dec}f}, {v['ci_hi']:+.{dec}f}]" if v and not v.get("ref") else "0 (ref)"


def omni(ds, key):
    r = R["base"][ds][key]; g, s = r["glmm"], r["stratified"]
    return f"GLMM p = {g.get('lr_p', float('nan')):.2g}; stratified p = {s.get('wald_p', float('nan')):.2g}"


L = ["### Base performance, original corpus, 3-month bins (β_b = change vs the 1–3-month bin)", "",
     "| horizon | n binary | binary β_b (log-odds) GLMM / stratified | n MCQ | MCQ β_b (log-odds) GLMM / stratified | FRQ β_b (points) GLMM / stratified | date score β_b GLMM / stratified |",
     "|---|---|---|---|---|---|---|"]
kb, km, kf, kd = "binary_merged:y:3m", "mcq:y:3m", "frq:frq_score:3m", "date:date_score:3m"
for b in R["base"]["orig"][kb]["bins"]:
    gb, sb = c("glmm", kb, "orig").get(b), c("stratified", kb, "orig").get(b)
    gm, sm = c("glmm", km, "orig").get(b), c("stratified", km, "orig").get(b)
    gf, sf = c("glmm", kf, "orig").get(b), c("stratified", kf, "orig").get(b)
    gd, sd = c("glmm", kd, "orig").get(b), c("stratified", kd, "orig").get(b)
    L.append(f"| {b} | {gb['n'] if gb else ''} | {f(gb)} / {f(sb)} | {gm['n'] if gm else ''} | {f(gm)} / {f(sm)} | {f(gf)} / {f(sf)} | {f(gd)} / {f(sd)} |")
L += ["", f"Omnibus (bin block = 0): binary {omni('orig', kb)}; MCQ {omni('orig', km)}; FRQ {omni('orig', kf)}; date score {omni('orig', kd)}.", ""]

L += ["### Retrieval effect by horizon bin (β₂ + β₃_b), pinned 500 subset, 3-month bins, stratified estimator", "",
      "| horizon | n pairs (binary) | binary: WS − base (log-odds) | MCQ: WS − base (log-odds) | date score: WS − base | date abs. error: WS − base (months) | FRQ: WS − base (points) |", "|---|---|---|---|---|---|---|"]
wb, wm, wd, wa, wf = "binary_merged:y:3m", "mcq:y:3m", "date:date_score:3m", "date:abs_err:3m", "frq:frq_score:3m"
for b in R["ws"][wb]["bins"]:
    def w(k):
        v = c("stratified", k).get(b); return f(v["ws_effect"]) if v else "—"
    nb = c("stratified", wb).get(b, {}).get("n", "")
    L.append(f"| {b} | {nb} | {w(wb)} | {w(wm)} | {w(wd)} | {w(wa)} | {w(wf)} |")
def wp(k, est="stratified"):
    r = R["ws"][k][est]; return r.get("wald_p") if est == "stratified" else r.get("lr_p")
L += ["", f"Interaction omnibus (all β₃_b = 0), stratified Wald / GLMM LR: binary p = {wp(wb):.2g} / {wp(wb,'glmm'):.2g}; MCQ {wp(wm):.2g} / {wp(wm,'glmm'):.2g}; "
      f"date score {wp(wd):.2g} / (GLMM LR negative, optimiser artefact); date abs. error {wp(wa):.2g} / {wp(wa,'glmm'):.2g}; FRQ {wp(wf):.2g} / {wp(wf,'glmm'):.2g}.", ""]
(H / "tables/binned_coef_summary.md").write_text("\n".join(L) + "\n")
print("wrote tables/binned_coef_summary.md")
