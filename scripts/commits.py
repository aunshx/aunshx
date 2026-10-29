"""Fill the README's commits block with the latest public commits.

Search only ever sees what the token can see, so a broader token would surface
private repos. The query asks for public commits and the loop checks again.
"""

from datetime import datetime

from gh import LOGIN, rest
from readme import md_escape, replace_block

LIMIT, PER_REPO = 5, 2


def latest():
    data = rest(
        "/search/commits",
        q=f"author:{LOGIN} is:public merge:false",
        sort="author-date",
        order="desc",
        per_page=50,
    )
    picked, per_repo = [], {}
    for item in data["items"]:
        repo = item["repository"]
        name = repo["full_name"]
        if repo["private"] or name == f"{LOGIN}/{LOGIN}" or per_repo.get(name, 0) >= PER_REPO:
            continue
        per_repo[name] = per_repo.get(name, 0) + 1
        picked.append(item)
        if len(picked) == LIMIT:
            break
    return picked


def line(item):
    when = datetime.fromisoformat(item["commit"]["author"]["date"])
    subject = item["commit"]["message"].splitlines()[0][:90]
    repo = item["repository"]
    return (
        f"- [`{item['sha'][:7]}`]({item['html_url']}) "
        f"[**{md_escape(repo['name'])}**]({repo['html_url']}) "
        f"{md_escape(subject)} <sub>{when:%b} {when.day}</sub>"
    )


if __name__ == "__main__":
    items = latest()
    if items:
        replace_block("commits", "\n".join(line(i) for i in items))
    print(f"commits: {len(items)}")
