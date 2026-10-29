"""Replace the text between <!-- name:start --> and <!-- name:end --> in README.md."""

import re

PATH = "README.md"


def replace_block(name, content):
    with open(PATH, encoding="utf-8") as f:
        text = f.read()
    pattern = re.compile(rf"(<!-- {name}:start -->).*?(<!-- {name}:end -->)", re.S)
    if not pattern.search(text):
        raise SystemExit(f"README.md has no {name} block")
    text = pattern.sub(lambda m: f"{m.group(1)}\n{content.strip()}\n{m.group(2)}", text)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(text)


def md_escape(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"([\\`*_\[\]|])", r"\\\1", text)
