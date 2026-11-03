"""Shared look for the profile images: the unizel.com system, reduced to its essentials.

Transparent ground (so there is no box and no edge on any GitHub theme), one soft
aqua wash in the top left, Jost 400 for everything, hairlines, aqua used sparingly.
Jost (SIL Open Font License, see assets/fonts/OFL.txt) is embedded as a data URI
because an SVG shown through <img> cannot load fonts from anywhere else.
Standard library only.
"""
import base64
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
FONT_FILE = ASSETS / "fonts" / "jost-latin.woff2"

SANS = "'Jost', 'Avenir Next', 'Helvetica Neue', Helvetica, Arial, sans-serif"

THEMES = {
    "dark": dict(ink="#F2F5F5", ink2="#AAB5B7", ink3="#6F7B7E", line="#2B3336",
                 accent="#66FCF1", wash=(0.17, 0.06)),
    "light": dict(ink="#0A0F10", ink2="#475255", ink3="#6B7679", line="#D0D7DE",
                  accent="#0E7C86", wash=(0.13, 0.045)),
}


def font_face():
    data = base64.b64encode(FONT_FILE.read_bytes()).decode("ascii")
    return ("@font-face{font-family:'Jost';font-style:normal;font-weight:300 600;"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")


def wash(theme, width, height):
    """A soft aqua glow, as on unizel.com, kept inside the image.

    On the site the wash bleeds off the screen edge. Here the image sits mid-page,
    so the glow must reach zero before every edge or it reads as a box.
    """
    a0, a1 = THEMES[theme]["wash"]
    rx, ry = width * 0.30, height * 0.43
    cx, cy = rx, ry
    return (
        f'<radialGradient id="wash" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="1" '
        f'gradientTransform="translate({cx:.0f} {cy:.0f}) scale({rx:.0f} {ry:.0f})">'
        f'<stop offset="0" stop-color="#66FCF1" stop-opacity="{a0}"/>'
        f'<stop offset="0.4" stop-color="#66FCF1" stop-opacity="{a1}"/>'
        f'<stop offset="1" stop-color="#66FCF1" stop-opacity="0"/>'
        f'</radialGradient>'
    )
