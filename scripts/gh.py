"""Tiny GitHub API client on urllib. Reads GITHUB_TOKEN from the environment."""

import json
import os
import urllib.parse
import urllib.request

API = "https://api.github.com"
LOGIN = os.environ.get("PROFILE_LOGIN", "aunshx")


def _request(url, body=None):
    req = urllib.request.Request(url, data=body)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", f"{LOGIN}-profile")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def graphql(query, **variables):
    data = _request(f"{API}/graphql", json.dumps({"query": query, "variables": variables}).encode())
    if data.get("errors"):
        raise RuntimeError(data["errors"][0].get("message", "graphql error"))
    return data["data"]


def rest(path, **params):
    return _request(f"{API}{path}?{urllib.parse.urlencode(params)}")
