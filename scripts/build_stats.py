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

USER = "Duckky153"
# Not counted as personal projects: the profile repo, the personal page, and a
# site built for someone else.
EXCLUDE = {"Duckky153", "Duckky153.github.io", "rishab-kumar"}
API = "https://api.github.com"
OUT = Path(__file__).resolve().parent.parent / "assets"

LANG_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#F1E05A",
    "TypeScript": "#3178C6",
    "HTML": "#E34C26",
    "CSS": "#9B6BDF",
    "Shell": "#89E051",
    "Java": "#B07219",
    "SQL": "#E38C00",
}
OTHER_COLOR = "#8B949E"

THEMES = {
    "dark": dict(bg="#0B0C10", border="#1F2833", fg="#FFFFFF", muted="#8B949E",
                 accent="#66FCF1", track="#1F2833"),
    "light": dict(bg="#F6F8FA", border="#D0D7DE", fg="#0B0C10", muted="#57606A",
                  accent="#0E7C86", track="#D0D7DE"),
}
MONO = "'SF Mono', 'Menlo', 'Consolas', 'DejaVu Sans Mono', monospace"
SANS = "-apple-system, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"


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
    segments = [(name, n / total_bytes * 100, LANG_COLORS.get(name, OTHER_COLOR))
                for name, n in shown]
    if other / total_bytes >= 0.01:
        segments.append(("Other", other / total_bytes * 100, OTHER_COLOR))
    languages_used = sum(1 for _, n in ranked if n / total_bytes >= 0.01)
    return dict(projects=len(repos), live=len(live), languages=languages_used,
                segments=segments)


def render(data, theme):
    c = THEMES[theme]
    w, h, pad = 1000, 250, 40
    bar_x, bar_y, bar_w, bar_h = pad, 168, w - 2 * pad, 12
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
        f'height="{h}" role="img" aria-labelledby="t">',
        f'<title id="t">Public work: {data["projects"]} projects, {data["live"]} live '
        f'demos, {data["languages"]} languages</title>',
        f'<defs><clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" '
        f'height="{bar_h}" rx="6"/></clipPath></defs>',
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" '
        f'fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'<text x="{pad}" y="46" font-family="{MONO}" font-size="13" letter-spacing="3" '
        f'fill="{c["accent"]}">PUBLIC WORK</text>',
    ]
    metrics = [(data["projects"], "projects shipped"),
               (data["live"], "live demos"),
               (data["languages"], "languages")]
    for i, (value, label) in enumerate(metrics):
        x = pad + i * 230
        parts.append(f'<text x="{x}" y="112" font-family="{SANS}" font-size="56" '
                     f'font-weight="700" fill="{c["fg"]}">{value}</text>')
        parts.append(f'<text x="{x}" y="138" font-family="{MONO}" font-size="14" '
                     f'fill="{c["muted"]}">{escape(label)}</text>')
    parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" '
                 f'rx="6" fill="{c["track"]}"/>')
    parts.append('<g clip-path="url(#bar)">')
    x = float(bar_x)
    for name, pct, color in data["segments"]:
        seg = bar_w * pct / 100
        parts.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{seg:.2f}" height="{bar_h}" '
                     f'fill="{color}"/>')
        x += seg
    parts.append('</g>')
    for i, (name, pct, color) in enumerate(data["segments"]):
        col, row = i % 3, i // 3
        lx = pad + col * 300
        ly = 210 + row * 24
        parts.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{color}"/>')
        parts.append(f'<text x="{lx + 18}" y="{ly}" font-family="{MONO}" font-size="13" '
                     f'fill="{c["muted"]}">{escape(name)} {pct:.1f}%</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    data = collect()
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"stats-{theme}.svg").write_text(render(data, theme), encoding="utf-8")
    print(f"projects={data['projects']} live={data['live']} languages={data['languages']}")
    for name, pct, _ in data["segments"]:
        print(f"  {name}: {pct:.1f}%")


if __name__ == "__main__":
    main()
