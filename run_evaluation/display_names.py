"""Display names for figures (2026-10-22): Claude Opus 4.8 -> Claude O4.8, Claude Sonnet 5 -> Claude S5.
Data keys stay unchanged; install() rewrites only the text matplotlib draws (titles, labels, ticks, legends, annotations)."""
import re
MAP = [(re.compile(r"Claude[ ~]Opus[ ~]4\.8"), "Claude O4.8"), (re.compile(r"Claude[ ~]Sonnet[ ~]5(?!\.\d|\d)"), "Claude S5")]
def display(s):
    for pat, rep in MAP: s = pat.sub(rep, s)
    return s
def install():
    import matplotlib.text as mtext
    if getattr(mtext.Text, "_cusp_display", False): return
    orig = mtext.Text.set_text
    def set_text(self, s):
        return orig(self, display(s) if isinstance(s, str) else s)
    mtext.Text.set_text = set_text; mtext.Text._cusp_display = True
