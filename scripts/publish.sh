#!/usr/bin/env bash
# usage: publish.sh "<commit message>" <command...>
# Re-runs the command on a fresh main until the push lands, so the daily job
# and guesses arriving together never overwrite each other's state.
set -euo pipefail
msg=$1
shift
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
for attempt in 1 2 3 4 5; do
  git fetch -q origin main
  git reset -q --hard origin/main
  "$@"
  git add -A README.md assets game
  if git diff --cached --quiet; then
    echo "nothing changed"
    exit 0
  fi
  git commit -q -m "$msg"
  if git push -q origin HEAD:main; then
    exit 0
  fi
  sleep $((attempt * 3 + RANDOM % 5))
done
echo "gave up after 5 tries" >&2
exit 1
