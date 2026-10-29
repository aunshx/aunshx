"""Shared palette and SVG helpers. Standard library only, so Actions need no installs."""

from xml.sax.saxutils import escape

PALETTES = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#161b22",
        "line": "#30363d",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "accent": "#ff7b5c",
        "arg": "#79c0ff",
        "ok": "#3fb950",
        "warn": "#d29922",
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#f6f8fa",
        "line": "#d0d7de",
        "text": "#1f2328",
        "muted": "#59636e",
        "accent": "#c4371a",
        "arg": "#0550ae",
        "ok": "#1a7f37",
        "warn": "#9a6700",
    },
}

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def vars_block(theme):
    return ";".join(f"--{k}:{v}" for k, v in PALETTES[theme].items())


def palette_css(theme):
    """Fixed palette for the light/dark files, or both behind a media query for the auto file."""
    if theme in PALETTES:
        return f":root{{{vars_block(theme)}}}"
    return (
        f":root{{{vars_block('light')}}}"
        f"@media (prefers-color-scheme: dark){{:root{{{vars_block('dark')}}}}}"
    )


def esc(text):
    return escape(str(text), {'"': "&quot;"})


def write_variants(render, stem, *args):
    """Write stem-dark.svg, stem-light.svg and stem.svg (follows the viewer's OS)."""
    for theme, suffix in (("dark", "-dark"), ("light", "-light"), ("auto", "")):
        with open(f"assets/{stem}{suffix}.svg", "w", encoding="utf-8") as f:
            f.write(render(theme, *args))
