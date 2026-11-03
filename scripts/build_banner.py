#!/usr/bin/env python3
"""Write assets/banner-dark.svg and assets/banner-light.svg (static; run by hand).

Name, one sentence, a blinking caret. No box, no grid, no ornaments.
"""
from design import ASSETS, SANS, THEMES, font_face, wash

W, H = 1200, 280
SENTENCE = "Training grounds for American superintelligence."
# Rendered width of SENTENCE at 34px in Jost 400 (measured in Chrome), plus a gap.
CARET_X = 712


def render(theme):
    c = THEMES[theme]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">Dakshit Raj</title>
<desc id="d">{SENTENCE} Co-founding Unizel.</desc>
<defs>
<style>{font_face()}</style>
{wash(theme, W, H)}
</defs>
<rect width="{W}" height="{H}" fill="url(#wash)"/>
<text x="0" y="62" font-family="{SANS}" font-size="16" font-weight="400" letter-spacing="4.5" fill="{c['accent']}">CO-FOUNDING UNIZEL</text>
<text x="-4" y="162" font-family="{SANS}" font-size="96" font-weight="400" letter-spacing="-2" fill="{c['ink']}">Dakshit Raj</text>
<text x="0" y="224" font-family="{SANS}" font-size="34" font-weight="400" fill="{c['ink2']}">{SENTENCE}</text>
<rect x="{CARET_X}" y="198" width="2" height="33" fill="{c['accent']}">
<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/>
</rect>
</svg>
"""


def main():
    for theme in THEMES:
        path = ASSETS / f"banner-{theme}.svg"
        path.write_text(render(theme), encoding="utf-8")
        print(f"wrote {path.name} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
