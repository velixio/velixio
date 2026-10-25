#!/usr/bin/env python3
"""Draw the profile desktop (light and dark) with live star counts.

Edit PROJECTS below, then run: python3 assets/gen.py
Star counts come from supermetry, the same source as shimul.me. A failed
lookup exits non-zero so the scheduled workflow never commits a broken image.
"""
import base64
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

OUT = Path(__file__).parent
SRC = OUT / "src"
W, H = 880, 380
FONT = "-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',Inter,Roboto,'Helvetica Neue',Arial,sans-serif"
STARS_API = "https://app.supermetry.com/api/github/stars/"
GITHUB_API = "https://api.github.com/repos/"

THEMES = {
    "light": dict(win="#f6f6f8", win_op=0.9, border="#ffffff", sep="#00000014", text="#1d1d1f",
                  text2="#6e6e73", bar="#f6f6f8", bar_op=0.72, dock="#ffffff", dock_op=0.35, star="#b45309"),
    "dark": dict(win="#202026", win_op=0.86, border="#ffffff24", sep="#ffffff14", text="#f5f5f7",
                 text2="#a1a1a6", bar="#1e1e24", bar_op=0.6, dock="#ffffff", dock_op=0.16, star="#fbbf24"),
}

# (icon file, name, one line, repo)
PROJECTS = [
    ("supermetry", "supermetry", "Cookie-free analytics", "velixio/supermetry"),
    ("paymux", "paymux", "Payments, one ledger", "velixio/paymux"),
    ("meshpanel", "meshpanel", "Panel for headscale", "velixio/meshpanel"),
    ("idlogin", "idlogin", "Sign-in for Zitadel", "velixio/idlogin"),
    ("voicestudio", "VoiceStudio", "Local AI voice", "debpalash/VoiceStudio"),
]


def data_uri(name, mime="image/svg+xml"):
    return f"data:{mime};base64," + base64.b64encode((SRC / name).read_bytes()).decode()


def stars(repo):
    try:
        with urllib.request.urlopen(STARS_API + repo, timeout=15) as r:
            return int(json.load(r)["stars"])
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    # supermetry doesn't track this repo: ask GitHub directly.
    with urllib.request.urlopen(GITHUB_API + repo, timeout=15) as r:
        return int(json.load(r)["stargazers_count"])


def short(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def window(x, y, w, h, title, t, sub=""):
    cx = x + w / 2
    s = f'''  <g filter="url(#shadow)">
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{t['win']}" fill-opacity="{t['win_op']}" stroke="{t['border']}"/>
  </g>
  <line x1="{x}" y1="{y + 34}" x2="{x + w}" y2="{y + 34}" stroke="{t['sep']}"/>
  <circle cx="{x + 18}" cy="{y + 17}" r="6" fill="#ff5f57"/>
  <circle cx="{x + 38}" cy="{y + 17}" r="6" fill="#febc2e"/>
  <circle cx="{x + 58}" cy="{y + 17}" r="6" fill="#28c840"/>
  <text x="{cx}" y="{y + 22}" text-anchor="middle" font-size="13" font-weight="600" fill="{t['text']}">{title}</text>
'''
    if sub:
        s += f'  <text x="{x + w - 16}" y="{y + 22}" text-anchor="end" font-size="12" fill="{t["text2"]}">{sub}</text>\n'
    return s


def desktop(t, counts, date):
    s = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Desktop with a Projects window: supermetry, paymux, meshpanel, idlogin and VoiceStudio">
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="16" stdDeviation="18" flood-color="#080a28" flood-opacity="0.45"/></filter>
    <clipPath id="screen"><rect width="{W}" height="{H}" rx="14"/></clipPath>
    <clipPath id="tile" clipPathUnits="objectBoundingBox"><rect width="1" height="1" rx="0.22"/></clipPath>
    <style>text{{font-family:{FONT}}}</style>
  </defs>
  <g clip-path="url(#screen)">
  <image href="{data_uri('wallpaper.svg')}" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>
''']
    # Menu bar
    s.append(f'''  <rect width="{W}" height="28" fill="{t['bar']}" fill-opacity="{t['bar_op']}"/>
  <image href="{data_uri('favicon.svg')}" x="14" y="6" width="16" height="16"/>
  <text x="40" y="19" font-size="13" font-weight="700" fill="{t['text']}">Shimul Debnath</text>
  <text x="156" y="19" font-size="13" fill="{t['text']}">Projects<tspan dx="18">Elsewhere</tspan><tspan dx="18">Window</tspan></text>
  <text x="{W - 16}" y="19" text-anchor="end" font-size="13" font-weight="500" fill="{t['text']}">{date}</text>
''')
    # Projects window
    w = 680
    x, y = (W - w) / 2, 60
    s.append(window(x, y, w, 210, "Projects", t, f"{len(PROJECTS)} items"))
    for i, (icon, name, line, repo) in enumerate(PROJECTS):
        cx = x + w / 2 + (i - (len(PROJECTS) - 1) / 2) * 128
        top = y + 56
        s.append(f'  <image href="{data_uri(icon + ".svg")}" x="{cx - 32}" y="{top}" width="64" height="64" clip-path="url(#tile)"/>\n')
        s.append(f'  <text x="{cx}" y="{top + 86}" text-anchor="middle" font-size="13" font-weight="600" fill="{t["text"]}">{name}</text>\n')
        s.append(f'  <text x="{cx}" y="{top + 104}" text-anchor="middle" font-size="11.5" fill="{t["text2"]}">{line}</text>\n')
        if counts[repo] > 0:  # like shimul.me, a zero count stays hidden
            s.append(f'  <text x="{cx}" y="{top + 124}" text-anchor="middle" font-size="11.5" font-weight="600" fill="{t["star"]}">★ {short(counts[repo])}</text>\n')

    # Dock
    icons = [p[0] for p in PROJECTS] + [None, "github"]
    size, gap, pad = 48, 10, 12
    dw = sum(21 if i is None else size for i in icons) + gap * (len(icons) - 1) + pad * 2
    dx, dy = (W - dw) / 2, 292
    s.append(f'  <rect x="{dx}" y="{dy}" width="{dw}" height="{size + 16}" rx="20" fill="{t["dock"]}" fill-opacity="{t["dock_op"]}" stroke="#ffffff" stroke-opacity="0.25"/>\n')
    ix = dx + pad
    for icon in icons:
        if icon is None:
            s.append(f'  <line x1="{ix + 10}" y1="{dy + 12}" x2="{ix + 10}" y2="{dy + size + 4}" stroke="#ffffff" stroke-opacity="0.35"/>\n')
            ix += 21 + gap
            continue
        s.append(f'  <image href="{data_uri(icon + ".svg")}" x="{ix}" y="{dy + 8}" width="{size}" height="{size}" clip-path="url(#tile)"/>\n')
        ix += size + gap
    s.append("  </g>\n</svg>\n")
    return "".join(s)


def main():
    try:
        counts = {p[3]: stars(p[3]) for p in PROJECTS}
    except Exception as e:
        sys.exit(f"star lookup failed: {e}")
    date = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%a %-d %b")
    for theme, t in THEMES.items():
        (OUT / f"desktop-{theme}.svg").write_text(desktop(t, counts, date))


if __name__ == "__main__":
    main()
