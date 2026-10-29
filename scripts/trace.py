"""Draw the last year of contributions as an agent trace: one span per month.

    python3 scripts/trace.py [calendar.json]   # writes assets/trace{,-dark,-light}.svg

Without a file it reads the calendar from GraphQL. The public calendar already
counts private contributions as plain numbers, so the default token is enough.
"""

import json
import math
import sys
from datetime import date

from gh import LOGIN, graphql
from theme import MONO, esc, palette_css, write_variants

QUERY = """query($login: String!) {
  user(login: $login) { contributionsCollection { contributionCalendar {
    totalContributions weeks { contributionDays { date contributionCount } }
  } } }
}"""

W, PAD, LABEL_W = 760, 28, 150
X0, X1 = PAD + LABEL_W, W - PAD
ROW, TOP = 22, 70


def load(path=None):
    if path:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = graphql(QUERY, login=LOGIN)
    cal = data["user"]["contributionsCollection"]["contributionCalendar"]
    days = [(date.fromisoformat(d["date"]), d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]
    return cal["totalContributions"], days


def streaks(days):
    best = (0, None, None)
    run, start = 0, None
    for d, c in days:
        if c:
            run, start = run + 1, start if run else d
            if run > best[0]:
                best = (run, start, d)
        else:
            run = 0
    current = 0
    for _, c in reversed(days):
        if not c:
            break
        current += 1
    return best, current


def fmt_day(d):
    return f"{d:%b} {d.day}"


def render(theme, total, days):
    n = len(days)
    dx = (X1 - X0) / n
    x_of = {d: X0 + i * dx for i, (d, _) in enumerate(days)}
    peak_day, peak = max(days, key=lambda dc: dc[1])

    months = {}
    for d, c in days:
        months.setdefault((d.year, d.month), []).append((d, c))

    out = []

    y = TOP
    out.append(f'<text x="{PAD}" y="{y + 11}" class="b">year</text>')
    out.append(f'<text x="{X0 - 14}" y="{y + 11}" text-anchor="end" class="m">{total:,}</text>')
    out.append(f'<rect x="{X0}" y="{y - 2}" width="{X1 - X0}" height="18" rx="3" fill="var(--panel)"/>')
    bars = []
    for d, c in days:
        if c:
            h = 3 + 13 * math.log1p(c) / math.log1p(peak)
            bars.append(f'<rect x="{x_of[d]:.2f}" y="{y + 16 - h:.2f}" width="{max(dx - 0.4, 0.8):.2f}" height="{h:.2f}"/>')
    out.append(f'<g class="f" fill="var(--accent)">{"".join(bars)}</g>')
    y += ROW + 12

    top_month = max(sum(c for _, c in v) for v in months.values()) or 1
    for i, ((yr, mo), v) in enumerate(months.items()):
        first = v[0][0]
        label = f"{first:%b}".lower() + (f" {yr}" if i == 0 or mo == 1 else "")
        count = sum(c for _, c in v)
        active = sum(1 for _, c in v if c)
        x, w = x_of[first], len(v) * dx
        delay = 0.15 + i * 0.05
        out.append(f'<text x="{PAD}" y="{y + 9}">{label}</text>')
        out.append(f'<text x="{X0 - 14}" y="{y + 9}" text-anchor="end" class="m">{count:,}</text>')
        if count:
            op = 0.3 + 0.7 * math.sqrt(count / top_month)
            out.append(
                f'<rect x="{x:.2f}" y="{y}" width="{w:.2f}" height="10" rx="2" fill="var(--accent)" '
                f'fill-opacity="{op:.2f}" class="g" style="animation-delay:{delay:.2f}s"/>'
            )
        else:
            out.append(f'<rect x="{x:.2f}" y="{y + 0.5}" width="{w:.2f}" height="9" rx="2" fill="none" stroke="var(--line)" stroke-dasharray="2 2"/>')
        note = f"{active}/{len(v)}d"
        if x + w + 60 < X1:
            out.append(f'<text x="{x + w + 8:.2f}" y="{y + 9}" class="s">{note}</text>')
        else:
            out.append(f'<text x="{x - 8:.2f}" y="{y + 9}" text-anchor="end" class="s">{note}</text>')
        y += ROW

    y += 10
    out.append(f'<path d="M{PAD} {y - 4}.5H{X1}" stroke="var(--line)" stroke-dasharray="2 3"/>')
    y += 8

    (best, b0, b1), current = streaks(days)
    events = []
    if best:
        events.append(("streak", f"{best}d", b0, b1, f"longest, {fmt_day(b0)} to {fmt_day(b1)}"))
    if current:
        events.append(("now", f"{current}d", days[-current][0], days[-1][0], "current streak"))
    events.append(("peak", f"{peak:,}", peak_day, peak_day, f"on {fmt_day(peak_day)}"))
    for name, value, a, b, note in events:
        x, w = x_of[a], max((x_of[b] - x_of[a]) + dx, 3)
        out.append(f'<text x="{PAD}" y="{y + 9}" class="okt">{name}</text>')
        out.append(f'<text x="{X0 - 14}" y="{y + 9}" text-anchor="end" class="m">{value}</text>')
        out.append(f'<rect x="{x:.2f}" y="{y}" width="{w:.2f}" height="10" rx="2" fill="var(--ok)" class="f"/>')
        if x + w + 8 + len(note) * 7.3 < X1:
            out.append(f'<text x="{x + w + 8:.2f}" y="{y + 9}" class="s">{esc(note)}</text>')
        else:
            out.append(f'<text x="{x - 8:.2f}" y="{y + 9}" text-anchor="end" class="s">{esc(note)}</text>')
        y += ROW

    y += 14
    out.append(f'<text x="{PAD}" y="{y}" class="s">redrawn daily by an Action. private work is counted, never shown.</text>')
    height = y + 22

    span = f"{fmt_day(days[0][0])} {days[0][0].year} to {fmt_day(days[-1][0])} {days[-1][0].year}"
    css = f"""{palette_css(theme)}
text{{font-family:{MONO};font-size:13px;fill:var(--text);white-space:pre}}
.m{{fill:var(--muted)}}.s{{font-size:11.5px;fill:var(--muted)}}.b{{font-weight:600}}.okt{{fill:var(--ok)}}
.hd{{fill:var(--muted)}}.fn{{fill:var(--accent)}}
.g{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow .5s ease-out forwards}}
.f{{opacity:0;animation:in .6s ease-out .1s forwards}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
@keyframes in{{to{{opacity:1}}}}
@media (prefers-reduced-motion: reduce){{.g,.f{{animation:none;transform:none;opacity:1}}}}"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-labelledby="title desc">
<title id="title">contributions as a trace</title>
<desc id="desc">{total:,} contributions from {span}, one span per month. Longest streak {best} days. Busiest day {peak} contributions on {fmt_day(peak_day)}.</desc>
<style>{css}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="10" fill="var(--bg)" stroke="var(--line)"/>
<rect x="1" y="1" width="{W - 2}" height="35" rx="9" fill="var(--panel)"/>
<rect x="1" y="20" width="{W - 2}" height="16" fill="var(--panel)"/>
<path d="M1 36.5H{W - 1}" stroke="var(--line)"/>
<text x="{PAD}" y="23" class="hd"><tspan class="fn">trace</tspan>  contributions(last=365d)</text>
<text x="{W - PAD}" y="23" text-anchor="end" class="hd">{span}</text>
{chr(10).join(out)}
</svg>
"""


if __name__ == "__main__":
    total, days = load(sys.argv[1] if len(sys.argv) > 1 else None)
    write_variants(render, "trace", total, days)
    print(f"trace: {total} contributions over {len(days)} days")
