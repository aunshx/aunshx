"""A daily five-letter word, played by opening an issue titled `guess: <word>`.

    python3 scripts/game.py guess      # GUESS_TITLE, GUESS_USER, GAME_SALT, REPLY_PATH
    python3 scripts/game.py rollover   # GAME_SALT; reveals yesterday, resets today

The word list is public; which word is today's is an HMAC of the date under a
repo secret, so reading the repo does not give the answer away. The title is
only ever compared against a regex, never executed or sent anywhere.
"""

import hashlib
import hmac
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

from readme import replace_block

TRIES = 6
STATE, BOARD = "game/state.json", "game/leaderboard.json"
PROFILE = "https://github.com/aunshx"
GREEN, YELLOW, GREY = "\U0001f7e9", "\U0001f7e8", "⬛"

WORDS = sorted(set("""
agent cache query fetch parse merge build token graph stack shell react async
debug array class float index model patch proxy queue route scope slice split
state trace tuple union yield write admin alias batch bytes chunk clone close
cloud crash drift embed empty error event false field flush frame guard hooks
input layer limit local logic macro mutex nodes order owner panic pixel point
print probe quota raise range ready reset retry rules scale score serve setup
shard solve spawn stage start store style table tests timer train tweak typed
valid value vault watch bench blame board boost cargo chain diffs epoch fiber
fleet forks grant heaps infer joins lexer lists loops mount nonce pivot ports
proof rerun sleep smoke specs swift tasks tools width zones label cycle draft
plans ships fixes blobs bound
""".split()))


def today():
    return datetime.now(timezone.utc).date().isoformat()


def word_for(day):
    salt = os.environ.get("GAME_SALT")
    if not salt:
        raise SystemExit("GAME_SALT is not set")
    digest = hmac.new(salt.encode(), day.encode(), hashlib.sha256).digest()
    return WORDS[int.from_bytes(digest[:8], "big") % len(WORDS)]


def score(guess, word):
    marks = [GREY] * 5
    left = Counter()
    for i, (g, w) in enumerate(zip(guess, word)):
        if g == w:
            marks[i] = GREEN
        else:
            left[w] += 1
    for i, g in enumerate(guess):
        if marks[i] != GREEN and left[g]:
            marks[i] = YELLOW
            left[g] -= 1
    return "".join(marks)


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")


def rollover(state):
    day = today()
    if state.get("date") == day:
        return state
    fresh = {"date": day, "players": {}, "solved": [], "yesterday": state.get("yesterday")}
    if state.get("date"):
        fresh["yesterday"] = {
            "date": state["date"],
            "word": word_for(state["date"]),
            "players": len(state["players"]),
            "solved": len(state["solved"]),
        }
    return fresh


def player(login):
    return f"[{login}](https://github.com/{login})"


def render(state, board):
    lines = []
    players = sorted(state["players"].items(), key=lambda kv: kv[1]["seq"], reverse=True)
    n, s = len(players), len(state["solved"])
    lines.append(f"**Today** {n} playing, {s} solved." if n else "**Today** nobody has guessed yet. Be first.")
    if state["solved"]:
        lines.append(f"First to get it: {', '.join(player(p) for p in state['solved'][:3])}.")
    if players:
        lines.append("")
        for login, p in players[:5]:
            lines.append(f"{player(login)} {' '.join(p['rows'])}<br>")
    y = state.get("yesterday")
    if y:
        lines.append("")
        lines.append(f"Yesterday's word was `{y['word']}`. {y['solved']} of {y['players']} got it.")
    if board:
        ranked = sorted(board.items(), key=lambda kv: (-kv[1]["solves"], kv[1]["guesses"] / kv[1]["solves"], kv[0]))
        lines += ["", "| | player | solved | avg tries |", "|---:|---|---:|---:|"]
        for i, (login, b) in enumerate(ranked[:10], 1):
            lines.append(f"| {i} | {player(login)} | {b['solves']} | {b['guesses'] / b['solves']:.1f} |")
    replace_block("game", "\n".join(lines))


def guess():
    title = os.environ.get("GUESS_TITLE", "")
    login = os.environ.get("GUESS_USER", "")
    reply_path = os.environ.get("REPLY_PATH", "reply.md")
    state = rollover(load(STATE, {}))
    board = load(BOARD, {})

    def reply(text):
        with open(reply_path, "w", encoding="utf-8") as f:
            f.write(text.strip() + f"\n\nBack to the [profile]({PROFILE}). New word every day at 00:00 UTC.\n")

    m = re.fullmatch(r"\s*guess:\s*([A-Za-z]{5})\s*", title, re.I)
    if not m or not re.fullmatch(r"[A-Za-z0-9-]{1,39}", login):
        reply("Five letters, a to z, like `guess: cache`. That one didn't parse, so it doesn't count.")
        return
    word, answer = m.group(1).lower(), word_for(state["date"])
    me = state["players"].get(login)
    if me and me["solved"]:
        reply(f"You already got today's word in {len(me['rows'])}. Come back tomorrow.")
        return
    if me and len(me["rows"]) >= TRIES:
        reply("That's all six tries for today. The answer shows up on the profile tomorrow.")
        return

    me = me or {"rows": [], "solved": False}
    me["seq"] = max((p["seq"] for p in state["players"].values()), default=0) + 1
    marks = score(word, answer)
    me["rows"].append(marks)
    state["players"][login] = me
    tries = len(me["rows"])
    head = f"`check(\"{word}\")`\n\n{marks}"

    if word == answer:
        me["solved"] = True
        state["solved"].append(login)
        b = board.setdefault(login, {"solves": 0, "guesses": 0})
        b["solves"] += 1
        b["guesses"] += tries
        b["last"] = state["date"]
        rank = len(state["solved"])
        reply(f"{head}  solved in {tries}\n\nThat's it. You're #{rank} today and on the leaderboard.")
    elif tries == TRIES:
        reply(f"{head}  try {tries} of {TRIES}\n\nOut of tries. The word shows up on the profile tomorrow.")
    else:
        reply(
            f"{head}  try {tries} of {TRIES}\n\n"
            "Green is the right letter in the right spot. Yellow is in the word, somewhere else. "
            "Open another issue to guess again."
        )

    save(STATE, state)
    save(BOARD, board)
    render(state, board)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "guess":
        guess()
    elif cmd == "rollover":
        state = rollover(load(STATE, {}))
        save(STATE, state)
        render(state, load(BOARD, {}))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
