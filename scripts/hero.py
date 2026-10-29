"""Render the hero: the name decodes, then an agent works out who aunsh is.

    python3 scripts/hero.py   # writes assets/hero{,-dark,-light}.svg
"""

from theme import MONO, esc, palette_css, write_variants

W, PAD, FS, LH = 760, 28, 15, 30
RESULT_X = 270

NAME = "aunsh"
SCRAMBLE = ["#x9@k", "q7%$a", "a&!zh", "au?1s", "aun/h", "auns_"]
TAGLINE = "builds agents that show their work"

# (call, result lines). Each result line is a list of (text, css class) and
# streams in once the call returns.
CALLS = [
    ([("search", "fn"), ("(", "m"), ('"aunsh"', "arg"), (")", "m")],
     [[("one human. MS ECE, UC Davis. ships agents.", "r")]]),
    ([("career", "fn"), ("()", "m")],
     [[("now   ", "m"), ("co-founder, ", "r"), ("8W Research", "b")],
      [("2024  ", "m"), ("software developer, ", "r"), ("UC Davis", "b")],
      [("2024  ", "m"), ("founding engineer, ", "r"), ("mlpal.ai", "b")],
      [("2023  ", "m"), ("software engineer, ", "r"), ("Prosperix", "b")]]),
    ([("read", "fn"), ("(", "m"), ('"biofred.us"', "arg"), (")", "m")],
     [[("FRED. spatial agents, 11.8M rows, ~1,450 tests", "r")]]),
    ([("prs", "fn"), ("(", "m"), ("author=", "m"), ('"agent"', "arg"), (")", "m")],
     [[("opens, reviews and merges its own", "r")]]),
    ([("check", "fn"), ("(", "m"), ('"status"', "arg"), (")", "m")],
     [[("open to forward-deployed, AI, SWE", "r")]]),
]
ANSWER = "Aunsh builds agents that show their work. Worth an interview."

FRAME = 0.06
CALL_WAIT = 0.22
STREAM_CPS = 150


def tspans(segments):
    return "".join(f'<tspan class="{cls}">{esc(text)}</tspan>' for text, cls in segments)


def typed(x, y, text, cls, start, cps=STREAM_CPS):
    segments = [(text, cls)] if isinstance(text, str) else text
    n = sum(len(t) for t, _ in segments)
    dur = max(n / cps, 0.15)
    return (
        f'<text x="{x}" y="{y}" class="type" '
        f'style="animation-delay:{start:.2f}s;animation-duration:{dur:.2f}s;animation-timing-function:steps({n + 1},jump-none)">'
        f"{tspans(segments)}</text>"
    ), start + dur


def spinner(cx, cy, start, dur):
    return (
        f'<g class="p" style="animation-delay:{start:.2f}s;animation-duration:{dur:.2f}s">'
        f'<circle cx="{cx}" cy="{cy}" r="5.5" fill="none" stroke="var(--line)" stroke-width="2"/>'
        f'<circle cx="{cx}" cy="{cy}" r="5.5" fill="none" stroke="var(--accent)" stroke-width="2" '
        f'stroke-dasharray="9 26" stroke-linecap="round" class="spin"/></g>'
    )


def render(theme):
    out = []

    # Name: scrambled frames flash in turn, then the real name settles.
    t = 0.2
    name_y = 112
    for frame in SCRAMBLE:
        out.append(
            f'<text x="{PAD}" y="{name_y}" class="name flash" '
            f'style="animation-delay:{t:.2f}s;animation-duration:{FRAME}s">{esc(frame)}</text>'
        )
        t += FRAME
    out.append(f'<text x="{PAD}" y="{name_y}" class="name glow a" style="animation-delay:{t:.2f}s" filter="url(#blur)">{NAME}</text>')
    out.append(f'<text x="{PAD}" y="{name_y}" class="name a" style="fill:url(#grad);animation-delay:{t:.2f}s">{NAME}</text>')
    line, t = typed(PAD + 2, name_y + 32, TAGLINE, "m", t + 0.1, cps=90)
    out.append(line)

    y = name_y + 78
    out.append(f'<path d="M{PAD} {y - 22}.5H{W - PAD}" stroke="var(--line)" stroke-dasharray="3 4" class="a" style="animation-delay:{t:.2f}s"/>')

    t += 0.1
    out.append(f'<text x="{PAD}" y="{y}" class="fn a" style="animation-delay:{t:.2f}s">&gt;</text>')
    line, t = typed(PAD + 18, y, "who is aunsh?", "q", t, cps=45)
    out.append(line)
    y += LH + 4
    t += 0.1

    for call, results in CALLS:
        out.append(spinner(PAD + 6, y - 5, t, CALL_WAIT))
        out.append(f'<text x="{PAD + 22}" y="{y}" class="a" style="animation-delay:{t:.2f}s">{tspans(call)}</text>')
        t += CALL_WAIT
        out.append(f'<text x="{PAD + 1}" y="{y}" class="ok a" style="animation-delay:{t:.2f}s">✓</text>')
        out.append(f'<text x="{RESULT_X - 22}" y="{y}" class="m a" style="animation-delay:{t:.2f}s">→</text>')
        t0 = t
        for i, result in enumerate(results):
            line, end = typed(RESULT_X, y, result, "r", t0 + i * 0.12)
            out.append(line)
            t = max(t, end)
            y += LH if i == len(results) - 1 else LH - 6
        t += 0.05

    y += 10
    t += 0.1
    out.append(f'<rect x="{PAD - 10}" y="{y - 21}" width="{W - 2 * PAD + 20}" height="32" rx="6" class="ans a" style="animation-delay:{t:.2f}s"/>')
    out.append(f'<text x="{PAD}" y="{y}" class="ok b a" style="animation-delay:{t:.2f}s">answer</text>')
    line, t = typed(PAD + 80, y, ANSWER, "b", t + 0.05, cps=90)
    out.append(line)
    y += 40
    out.append(
        f'<text x="{PAD}" y="{y}" class="a" style="animation-delay:{t + 0.2:.2f}s"><tspan class="fn">&gt; </tspan>'
        f'<tspan class="cur">█</tspan></text>'
    )
    height = y + 24

    css = f"""{palette_css(theme)}
text{{font-family:{MONO};font-size:{FS}px;fill:var(--text);white-space:pre}}
.m{{fill:var(--muted)}}.fn{{fill:var(--accent)}}.arg{{fill:var(--arg)}}.ok{{fill:var(--ok)}}.b{{font-weight:700}}
.q{{font-weight:600}}.r{{fill:var(--text)}}.hd{{font-size:12.5px;fill:var(--muted)}}
.name{{font-size:64px;font-weight:800;letter-spacing:-1px;fill:var(--text)}}
.glow{{fill:var(--accent);opacity:0}}
.ans{{fill:var(--panel);stroke:var(--line)}}
.a{{opacity:0;animation:in .3s ease-out forwards}}
.glow.a{{animation-name:glow}}
.flash{{opacity:0;animation-name:flash;animation-timing-function:linear;animation-fill-mode:forwards}}
.p{{opacity:0;animation-name:flash;animation-timing-function:linear;animation-fill-mode:forwards}}
.spin{{transform-box:fill-box;transform-origin:center;animation:spin .6s linear infinite}}
.type{{clip-path:inset(0 100% 0 0);animation-name:type;animation-fill-mode:forwards}}
.cur{{fill:var(--accent);animation:blink 1.1s steps(1) infinite}}
.live{{fill:var(--ok);animation:pulse 1.6s ease-in-out infinite}}
@keyframes in{{from{{opacity:0;transform:translateY(3px)}}to{{opacity:1;transform:none}}}}
@keyframes glow{{to{{opacity:.35}}}}
@keyframes flash{{0%,85%{{opacity:1}}to{{opacity:0}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes type{{to{{clip-path:inset(0 0 0 0)}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes pulse{{50%{{opacity:.3}}}}
@media (prefers-reduced-motion: reduce){{
.a,.type,.cur,.live{{animation:none;opacity:1;clip-path:none;transform:none}}
.glow.a{{opacity:.35}}.flash,.p{{display:none}}
}}"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-labelledby="title desc">
<title id="title">aunsh</title>
<desc id="desc">Aunsh builds agents that show their work. An agent asks who aunsh is and calls five tools. search: MS ECE, UC Davis. career: co-founder at 8W Research now, software developer at UC Davis and founding engineer at mlpal.ai from 2024, software engineer at Prosperix in 2023. read: FRED at biofred.us, spatial agents over 11.8 million rows with about 1,450 tests, and an agent that opens, reviews and merges its own PRs. status: open to forward-deployed, AI and SWE roles.</desc>
<defs>
<linearGradient id="grad" x1="0" x2="1" y1="0" y2="0"><stop offset="0" style="stop-color:var(--accent)"/><stop offset="1" style="stop-color:var(--arg)"/></linearGradient>
<filter id="blur" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
</defs>
<style>{css}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="12" fill="var(--bg)" stroke="var(--line)"/>
<circle cx="{PAD + 4}" cy="20" r="4" class="live"/>
<text x="{PAD + 16}" y="24" class="hd">aunsh/agent</text>
<text x="{W - PAD}" y="24" text-anchor="end" class="hd">{len(CALLS)} tool calls · streaming</text>
<path d="M1 38.5H{W - 1}" stroke="var(--line)"/>
{chr(10).join(out)}
</svg>
"""


if __name__ == "__main__":
    write_variants(render, "hero")
