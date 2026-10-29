"""Render the hero: an agent answering "who is aunsh?" one tool call at a time.

    python3 scripts/hero.py   # writes assets/hero{,-dark,-light}.svg
"""

from theme import MONO, esc, palette_css, write_variants

W, PAD, FS, LH, TOP = 760, 28, 15, 24, 64

# (kind, segments). Segments are (text, css class); kind drives the timing.
SCRIPT = [
    ("prompt", [("who is aunsh?", "t")]),
    ("gap", []),
    ("call", [("search", "fn"), ("(", "m"), ('"aunsh"', "arg"), (")", "m")]),
    ("out", [("Aunsh Bandivadekar. MS ECE, UC Davis. Software engineer.", "t")]),
    ("call", [("retrieve", "fn"), ("(", "m"), ("projects", "arg"), (", limit=", "m"), ("3", "arg"), (")", "m")]),
    ("out", [("fred         ", "b"), ("an agent loop over an 11.8M-row PostGIS store", "t")]),
    ("out", [("switchboard  ", "b"), ("routes 191 tools down to the few a query needs", "t")]),
    ("out", [("watchtower   ", "b"), ("2,774 GitHub threads in, 5 worth answering out", "t")]),
    ("call", [("rank", "fn"), ("(", "m"), ("by=", "m"), ('"shipped"', "arg"), (")", "m")]),
    ("out", [("1  fred  ", "b"), ("live at biofred.us, ~1,450 tests, merges its own PRs", "t")]),
    ("call", [("check", "fn"), ("(", "m"), ("status", "arg"), (")", "m")]),
    ("out", [("open to forward-deployed, AI and SWE roles", "t")]),
    ("out", [("Bay Area, NYC, Seattle or remote. F-1 STEM OPT.", "m")]),
    ("gap", []),
    ("answer", [("answer  ", "ok"), ("Aunsh builds agents that show their work, then ships them.", "b")]),
]

TYPE_START, TYPE_DUR = 0.4, 0.9
CALL_WAIT = 0.7
OUT_STEP = 0.18


def tspans(segments):
    return "".join(f'<tspan class="{cls}">{esc(text)}</tspan>' for text, cls in segments)


def render(theme):
    rows, t = [], TYPE_START + TYPE_DUR + 0.3
    calls = sum(1 for kind, _ in SCRIPT if kind == "call")
    y = TOP
    for kind, segs in SCRIPT:
        if kind == "gap":
            y += LH // 2
            continue
        if kind == "prompt":
            n = len(segs[0][0])
            rows.append(
                f'<text x="{PAD}" y="{y}"><tspan class="fn">&gt; </tspan>'
                f'<tspan class="type" style="animation-delay:{TYPE_START}s;animation-timing-function:steps({n})">'
                f"{esc(segs[0][0])}</tspan></text>"
            )
        elif kind == "call":
            if t > TYPE_START + TYPE_DUR + 0.3:
                y += 8
            rows.append(f'<text x="{PAD + 18}" y="{y}" class="a" style="animation-delay:{t:.2f}s">{tspans(segs)}</text>')
            rows.append(
                f'<text x="{W - PAD}" y="{y}" text-anchor="end" class="p m" '
                f'style="animation-delay:{t:.2f}s;animation-duration:{CALL_WAIT}s">running</text>'
            )
            t += CALL_WAIT
            rows.append(f'<text x="{W - PAD}" y="{y}" text-anchor="end" class="a ok" style="animation-delay:{t:.2f}s">ok</text>')
            t += 0.1
        elif kind == "out":
            rows.append(f'<text x="{PAD + 36}" y="{y}" class="a" style="animation-delay:{t:.2f}s">{tspans(segs)}</text>')
            t += OUT_STEP
        elif kind == "answer":
            t += 0.3
            rows.append(f'<text x="{PAD + 18}" y="{y}" class="a" style="animation-delay:{t:.2f}s">{tspans(segs)}</text>')
        y += LH

    y += 10
    cursor = (
        f'<text x="{PAD}" y="{y}" class="a" style="animation-delay:{t + 0.4:.2f}s"><tspan class="fn">&gt; </tspan>'
        f'<tspan class="cur" style="animation-delay:{t + 0.4:.2f}s">_</tspan></text>'
    )
    height = y + 30

    css = f"""{palette_css(theme)}
text{{font-family:{MONO};font-size:{FS}px;fill:var(--text);white-space:pre}}
.m{{fill:var(--muted)}}.fn{{fill:var(--accent)}}.arg{{fill:var(--arg)}}.ok{{fill:var(--ok)}}.b{{font-weight:600}}
.hd{{font-size:13px;fill:var(--muted)}}
.a{{opacity:0;animation:in .35s ease-out forwards}}
.p{{opacity:0;animation-name:pend;animation-timing-function:linear;animation-fill-mode:forwards}}
.type{{clip-path:inset(0 100% 0 0);animation-name:type;animation-duration:{TYPE_DUR}s;animation-fill-mode:forwards}}
.cur{{animation:blink 1.1s steps(1) infinite}}
@keyframes in{{from{{opacity:0;transform:translateY(3px)}}to{{opacity:1;transform:none}}}}
@keyframes pend{{0%{{opacity:0}}1%,40%{{opacity:1}}55%,70%{{opacity:.35}}85%,99%{{opacity:1}}100%{{opacity:0}}}}
@keyframes type{{to{{clip-path:inset(0 0 0 0)}}}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion: reduce){{
.a,.type,.cur{{animation:none;opacity:1;clip-path:none;transform:none}}.p{{display:none}}
}}"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-labelledby="title desc">
<title id="title">who is aunsh?</title>
<desc id="desc">An agent answers who Aunsh is by calling four tools. search finds an MS ECE from UC Davis. retrieve lists fred, switchboard and watchtower. rank puts fred first: live at biofred.us, about 1,450 tests, merges its own PRs. check says open to forward-deployed, AI and SWE roles. Answer: Aunsh builds agents that show their work, then ships them.</desc>
<style>{css}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="10" fill="var(--bg)" stroke="var(--line)"/>
<path d="M1 36.5H{W - 1}" stroke="var(--line)"/>
<rect x="1" y="1" width="{W - 2}" height="35" rx="9" fill="var(--panel)"/>
<rect x="1" y="20" width="{W - 2}" height="16" fill="var(--panel)"/>
<text x="{PAD}" y="23" class="hd">agent run</text>
<text x="{W - PAD}" y="23" text-anchor="end" class="hd">{calls} tool calls</text>
{chr(10).join(rows)}
{cursor}
</svg>
"""


if __name__ == "__main__":
    write_variants(render, "hero")
