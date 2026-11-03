#!/usr/bin/env python3
"""Build assets/stats-dark.svg and assets/stats-light.svg from PUBLIC GitHub data.

Only public, non-fork, non-archived repositories are counted. The user endpoint
returns public repositories only, so private work can never appear here, not even
as a count. Standard library only; run with GITHUB_TOKEN set to avoid rate limits.
"""
import json
import os
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

from design import SANS, THEMES, font_face

USER = "Duckky153"
# Not counted as personal projects: the profile repo, the personal page, and a
# site built for someone else.
EXCLUDE = {"Duckky153", "Duckky153.github.io", "rishab-kumar"}
API = "https://api.github.com"
OUT = Path(__file__).resolve().parent.parent / "assets"

def get(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-stats"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(API + path, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def public_repos():
    repos, page = [], 1
    while True:
        batch = get(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        if not batch:
            break
        repos.extend(batch)
        page += 1
    keep = [r for r in repos
            if not r["private"] and not r["fork"] and not r["archived"]
            and r["name"] not in EXCLUDE]
    return sorted(keep, key=lambda r: r["name"])


def collect():
    repos = public_repos()
    live = [r for r in repos
            if r.get("has_pages") and (r.get("homepage") or "").startswith("http")]
    totals = {}
    for r in repos:
        for lang, n in get(f"/repos/{USER}/{r['name']}/languages").items():
            totals[lang] = totals.get(lang, 0) + n
    total_bytes = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
    shown = ranked[:5]
    other = sum(n for _, n in ranked[5:])
    segments = [(name, n / total_bytes * 100) for name, n in shown]
    if other / total_bytes >= 0.01:
        segments.append(("Other", other / total_bytes * 100))
    languages_used = sum(1 for _, n in ranked if n / total_bytes >= 0.01)
    return dict(projects=len(repos), live=len(live), languages=languages_used,
                segments=segments)


def render(data, theme):
    """Three numbers and one line of language shares between hairlines. No box, no bars."""
    c = THEMES[theme]
    w, h = 1200, 204
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
        f'height="{h}" role="img" aria-labelledby="t">',
        f'<title id="t">Public work: {data["projects"]} projects, {data["live"]} live '
        f'demos, {data["languages"]} languages</title>',
        f'<defs><style>{font_face()}</style></defs>',
        f'<path d="M0 0.5H{w}" stroke="{c["line"]}" stroke-width="1"/>',
    ]
    metrics = [(data["projects"], "public projects"),
               (data["live"], "live demos"),
               (data["languages"], "languages")]
    for i, (value, label) in enumerate(metrics):
        x = i * 400
        parts.append(f'<text x="{x}" y="100" font-family="{SANS}" font-size="64" '
                     f'font-weight="400" letter-spacing="-1" fill="{c["ink"]}">{value}</text>')
        parts.append(f'<text x="{x}" y="136" font-family="{SANS}" font-size="20" '
                     f'font-weight="400" fill="{c["ink2"]}">{escape(label)}</text>')
    shares = "".join(
        f'<tspan fill="{c["ink2"]}">{escape(name)} </tspan>'
        f'<tspan fill="{c["ink3"]}">{pct:.0f}%</tspan>'
        + ('<tspan dx="26"> </tspan>' if i < len(data["segments"]) - 1 else "")
        for i, (name, pct) in enumerate(data["segments"]))
    parts.append(f'<text x="0" y="182" font-family="{SANS}" font-size="18" '
                 f'font-weight="400" xml:space="preserve">{shares}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    data = collect()
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"stats-{theme}.svg").write_text(render(data, theme), encoding="utf-8")
    print(f"projects={data['projects']} live={data['live']} languages={data['languages']}")
    for name, pct in data["segments"]:
        print(f"  {name}: {pct:.1f}%")


if __name__ == "__main__":
    main()
