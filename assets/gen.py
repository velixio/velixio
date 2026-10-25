#!/usr/bin/env python3
"""Regenerate the profile SVGs. Edit PROJECTS below, then run: python3 assets/gen.py"""
from html import escape
from pathlib import Path

OUT = Path(__file__).parent
W = 880
FONT = "'Space Mono','JetBrains Mono','SF Mono',Menlo,Consolas,monospace"

THEMES = {
    "dark": dict(bg="#0f172a", border="#334155", fg="#f8fafc", muted="#94a3b8", code="#1e293b", accent="#f59e0b"),
    "light": dict(bg="#ffffff", border="#cbd5e1", fg="#0f172a", muted="#475569", code="#f1f5f9", accent="#a16207"),
}

PROJECTS = [
    ("supermetry", "analytics", "Cookie-free web analytics. One Go binary and PostgreSQL.",
     "curl -fsSL https://github.com/velixio/supermetry/releases/latest/download/install.sh | sh"),
    ("paymux", "payments", "One webhook, one ledger, every gateway. GST invoicing built in. Beta.",
     "git clone https://github.com/velixio/paymux && cd paymux && make build"),
    ("meshpanel", "networking", "headscale control panel. Approve devices in the browser or on Telegram.",
     "curl -Lo meshpanel https://github.com/velixio/meshpanel/releases/latest/download/meshpanel_linux_amd64"),
    ("idlogin", "identity", "Passwordless sign-in for Zitadel. No JavaScript, branded per hostname.",
     "go install github.com/velixio/idlogin/cmd/idlogin@latest"),
    ("voicestudio", "maintainer", "Fully local AI voice studio, an ElevenLabs alternative. Core maintainer.",
     "curl -fsSL https://voicestudio.sh/install | sh"),
]


def svg(h, label, body, t):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{escape(label)}">
  <style>text{{font-family:{FONT}}}</style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="6" fill="{t['bg']}" stroke="{t['border']}"/>
{body}
</svg>
'''


def header(t):
    specs = ["one binary, not ten services", "collect only what you need", "fast by default"]
    items = ""
    for n, s in enumerate(specs):
        x = 32 + n * (W - 64) // 3
        items += f'  <rect x="{x}" y="181" width="8" height="8" fill="{t["accent"]}"/>\n'
        items += f'  <text x="{x + 16}" y="190" font-size="13" fill="{t["muted"]}">{s}</text>\n'
    body = f'''  <text x="32" y="46" font-size="13" fill="{t['muted']}">~/velixio <tspan fill="{t['accent']}">$</tspan> whoami</text>
  <text x="32" y="98" font-size="38" font-weight="700" fill="{t['fg']}">Shimul Debnath</text>
  <text x="32" y="132" font-size="16" fill="{t['muted']}">Small, self-hostable software in Go. Nothing that spies on anyone.</text>
  <line x1="32" y1="158" x2="{W - 32}" y2="158" stroke="{t['border']}"/>
{items}'''
    return svg(220, "Shimul Debnath: small, self-hostable software in Go", body, t)


def project(i, name, tag, desc, cmd, t):
    title = "VoiceStudio" if name == "voicestudio" else name
    body = f'''  <text x="28" y="44" font-size="14" font-weight="700" fill="{t['accent']}">{i:02d}</text>
  <text x="72" y="45" font-size="22" font-weight="700" fill="{t['fg']}">{title}</text>
  <text x="{W - 28}" y="44" font-size="12" text-anchor="end" letter-spacing="1.5" fill="{t['muted']}">{tag.upper()}</text>
  <text x="72" y="72" font-size="14" fill="{t['muted']}">{escape(desc)}</text>
  <rect x="72" y="88" width="{W - 100}" height="28" rx="4" fill="{t['code']}"/>
  <text x="84" y="107" font-size="12" fill="{t['fg']}"><tspan fill="{t['accent']}">$</tspan> {escape(cmd)}</text>'''
    return svg(132, f"{title}: {desc} Install: {cmd}", body, t)


for theme, t in THEMES.items():
    (OUT / f"header-{theme}.svg").write_text(header(t))
    for i, p in enumerate(PROJECTS, 1):
        (OUT / f"{p[0]}-{theme}.svg").write_text(project(i, *p, t))
