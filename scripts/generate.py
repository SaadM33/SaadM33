"""Generate the animated profile images in ../assets: header, footer, About card, Tech stack card, divider.

Usage (from anywhere, Python 3.8+, no dependencies):

    python3 scripts/generate.py

Then commit the changed files in assets/. Edit the CONTENT section below to change text or tech icons.
Tech icons are downloaded from skillicons.dev and embedded, so the finished SVGs need nothing external.

The SVGs use only CSS animations plus one SMIL gradient sweep (no JavaScript, no external fonts or
images), which is what GitHub allows inside README images.
"""
import math, os, random, re, sys, urllib.request
from xml.sax.saxutils import escape

# =================================================================== CONTENT (edit me)
NAME = "SAAD EL MAAQILI"
HEADER_TAG = "ID: SAADM33"
HEADER_META = "CLASS: FULL-STACK {s} BACKEND: FASTAPI · NESTJS · JAVA {s} UI: REACT"  # {s} = accent "//"

# About card: each line is a list of (text, bold) pieces. Keep lines under ~95 characters.
ABOUT_LINES = [
    [("I'm a software engineering student based in ", 0), ("Rabat, Morocco", 1), (", and I love understanding how complex", 0)],
    [("systems work, then building my own. I started from the ground up in C and C++, and today I", 0)],
    [("build full products end to end: database design, authentication, APIs, frontend, tests and CI.", 0)],
]
ABOUT_BULLETS = [
    ("BACKEND", "FastAPI, NestJS and Java"),
    ("FRONTEND", "React and TypeScript"),
    ("CURRENTLY", "building a hackathon platform with a team of five (Scrum, code review, CI on every merge)"),
    ("LANGUAGES", "Arabic, French, English"),
]

# Tech stack card: (label, comma-separated skillicons.dev ids). Icon list: https://skillicons.dev
STACK_ROWS = [
    ("LANGUAGES", "py,ts,js,java,c,cpp"),
    ("FRAMEWORKS", "fastapi,nestjs,spring,react"),
    ("DATABASES", "postgres,mysql,redis"),
    ("TOOLS", "docker,linux,git,githubactions"),
]
# ===================================================================

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(out, exist_ok=True)
W = 900
MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
SANS = "-apple-system,'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
P = dict(bg="050f1c", bg2="0b2442", glow="1b4f86", pri="bfefff", sec="7fd8ff", acc="5ccfff",
         txt="dbe9f5", star="e8f7ff", line="9fdcff", ice="dff6ff", ice2="7fd0ff")


# ------------------------------------------------------------------ shared defs / css
def base_defs(h, uid):
    return f"""
  <linearGradient id="bgg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#{P['bg']}"/><stop offset="1" stop-color="#{P['bg2']}"/></linearGradient>
  <radialGradient id="neb" cx="78%" cy="35%" r="55%"><stop offset="0" stop-color="#{P['glow']}" stop-opacity=".55"/><stop offset="1" stop-color="#{P['glow']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="neb2" cx="12%" cy="90%" r="45%"><stop offset="0" stop-color="#3b2a7a" stop-opacity=".35"/><stop offset="1" stop-color="#3b2a7a" stop-opacity="0"/></radialGradient>
  <clipPath id="clip"><rect width="{W}" height="{h}" rx="12"/></clipPath>
  <radialGradient id="sglow"><stop offset="0" stop-color="#{P['star']}" stop-opacity=".9"/><stop offset=".35" stop-color="#{P['line']}" stop-opacity=".35"/><stop offset="1" stop-color="#{P['line']}" stop-opacity="0"/></radialGradient>
  <linearGradient id="icebody" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity=".95"/><stop offset=".35" stop-color="#{P['ice']}" stop-opacity=".75"/>
    <stop offset=".8" stop-color="#{P['ice2']}" stop-opacity=".35"/><stop offset="1" stop-color="#{P['ice2']}" stop-opacity=".1"/></linearGradient>
  <linearGradient id="iceback" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#{P['ice']}" stop-opacity=".6"/><stop offset="1" stop-color="#{P['ice2']}" stop-opacity=".04"/></linearGradient>
  <linearGradient id="crust" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity=".95"/><stop offset="1" stop-color="#{P['ice']}" stop-opacity=".55"/></linearGradient>
  <linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".95"/></linearGradient>
  <symbol id="flake" viewBox="-10 -10 20 20" overflow="visible">
    <g stroke="#{P['ice']}" stroke-width="1.1" stroke-linecap="round" fill="none">
      <path d="M0-9V9 M-7.8-4.5 7.8 4.5 M-7.8 4.5 7.8-4.5"/>
      <path d="M-2-6.5 0-4.5 2-6.5 M-2 6.5 0 4.5 2 6.5 M-6.6-1.5-3.9-2.2-4.6-4.9 M6.6 1.5 3.9 2.2 4.6 4.9 M-6.6 1.5-3.9 2.2-4.6 4.9 M6.6-1.5 3.9-2.2 4.6-4.9"/>
    </g>
  </symbol>
  <symbol id="spark" viewBox="-10 -10 20 20" overflow="visible">
    <path d="M0-10Q0 0 10 0Q0 0 0 10Q0 0-10 0Q0 0 0-10Z" fill="#fff"/>
  </symbol>"""


BASE_CSS = """
  .tw{transform-box:fill-box;transform-origin:center;animation:tw ease-in-out infinite}
  @keyframes tw{0%,100%{opacity:.35;transform:scale(.7)}50%{opacity:1;transform:scale(1.15)}}
  .cl{fill:none;stroke-linecap:round;stroke-dasharray:var(--len);stroke-dashoffset:var(--len);animation:draw 2.2s ease-out forwards, breathe 6s ease-in-out infinite}
  @keyframes draw{to{stroke-dashoffset:0}}
  @keyframes breathe{0%,100%{stroke-opacity:.22}50%{stroke-opacity:.5}}
  .fall{animation:fall linear infinite}
  @keyframes fall{from{transform:translate(0,-30px)}to{transform:translate(var(--dx),var(--dy))}}
  .spin{transform-box:fill-box;transform-origin:center;animation:spin linear infinite}
  @keyframes spin{to{transform:rotate(360deg)}}
  .drip{opacity:0;animation:drip ease-in infinite}
  @keyframes drip{0%,62%{transform:translateY(0) scaleY(.4);opacity:0}66%{opacity:1;transform:translateY(0) scaleY(1)}100%{transform:translateY(70px) scaleY(1.3);opacity:0}}
  .glint{transform-box:fill-box;transform-origin:center;opacity:0;animation:glint ease-in-out infinite}
  @keyframes glint{0%,80%,100%{opacity:0;transform:scale(.2) rotate(0)}88%{opacity:1;transform:scale(1) rotate(45deg)}}
  .shoot{opacity:0;animation:shoot 9s ease-in infinite}
  @keyframes shoot{0%,86%{opacity:0;transform:translate(0,0)}88%{opacity:1}100%{opacity:0;transform:translate(-260px,130px)}}
"""


# ------------------------------------------------------------------ layers
def background(h):
    return (f'<rect width="{W}" height="{h}" rx="12" fill="url(#bgg)"/>'
            f'<rect width="{W}" height="{h}" fill="url(#neb)"/><rect width="{W}" height="{h}" fill="url(#neb2)"/>')


def dust(h, seed, n):
    """Far, faint static star dust that twinkles."""
    r = random.Random(seed)
    return "".join(
        f'<circle class="tw" cx="{r.uniform(5, W - 5):.0f}" cy="{r.uniform(5, h - 5):.0f}" r="{r.uniform(.4, 1.1):.1f}" fill="#{P["star"]}" '
        f'style="animation-duration:{r.uniform(2.5, 6):.1f}s;animation-delay:{-r.uniform(0, 6):.1f}s"/>' for _ in range(n))


def constellation(stars, edges, delay, seed):
    """stars: [(x,y,size)], edges: [(i,j)]. Lines draw in one after another, then breathe; stars twinkle with a halo."""
    r = random.Random(seed)
    out = []
    for k, (i, j) in enumerate(edges):
        (x1, y1, _), (x2, y2, _) = stars[i], stars[j]
        ln = math.hypot(x2 - x1, y2 - y1)
        out.append(f'<line class="cl" x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#{P["line"]}" stroke-width="1" '
                   f'style="--len:{ln:.0f};animation-delay:{delay + k * .35:.2f}s,{delay + 2.5:.2f}s"/>')
    for x, y, s in stars:
        d = r.uniform(2.5, 5)
        out.append(f'<g class="tw" style="animation-duration:{d:.1f}s;animation-delay:{-r.uniform(0, d):.1f}s">'
                   f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{s * 4:.1f}" fill="url(#sglow)"/>'
                   f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{s:.1f}" fill="#{P["star"]}"/></g>')
    return "".join(out)


def shooting(x, y, delay):
    return (f'<g class="shoot" style="animation-delay:{delay}s"><line x1="{x}" y1="{y}" x2="{x + 90}" y2="{y - 45}" stroke="url(#trail)" '
            f'stroke-width="1.6" stroke-linecap="round" transform="rotate(180 {x + 45} {y - 22})"/>'
            f'<circle cx="{x}" cy="{y}" r="1.8" fill="#fff"/></g>')


def snow(h, seed, far, near):
    r = random.Random(seed)
    out = []
    for _ in range(far):  # tiny distant flakes, slow
        out.append(f'<circle class="fall" cx="{r.uniform(0, W):.0f}" cy="0" r="{r.uniform(.6, 1.4):.1f}" fill="#{P["ice"]}" opacity="{r.uniform(.25, .55):.2f}" '
                   f'style="--dx:{r.uniform(-25, 25):.0f}px;--dy:{h + 30}px;animation-duration:{r.uniform(9, 16):.1f}s;animation-delay:{-r.uniform(0, 16):.1f}s"/>')
    for _ in range(near):  # real rotating snowflakes, closer and faster
        s = r.uniform(7, 15)
        out.append(f'<g class="fall" style="--dx:{r.uniform(-50, 50):.0f}px;--dy:{h + 40}px;animation-duration:{r.uniform(6, 11):.1f}s;animation-delay:{-r.uniform(0, 11):.1f}s">'
                   f'<use class="spin" href="#flake" x="{r.uniform(0, W):.0f}" y="-10" width="{s:.0f}" height="{s:.0f}" opacity="{r.uniform(.45, .85):.2f}" '
                   f'style="animation-duration:{r.uniform(6, 14):.1f}s"/></g>')
    return "".join(out)


def ice_top(seed, big=True, scale=1.0):
    """Frost crust along the top edge plus two rows of curved icicles with highlights, glints and drips."""
    r = random.Random(seed)
    # crust: lumpy band
    pts, x = [], 0
    while x <= W:
        pts.append((x, r.uniform(5, 12) if big else r.uniform(3, 7)))
        x += r.uniform(14, 30)
    pts.append((W, 6))
    d = f"M0 0H{W}V{pts[-1][1]:.0f}" + "".join(f"L{px:.0f} {py:.0f}" for px, py in reversed(pts)) + "Z"
    crust = f'<path d="{d}" fill="url(#crust)"/>'
    speck = "".join(f'<circle cx="{r.uniform(0, W):.0f}" cy="{r.uniform(1, 7):.0f}" r="{r.uniform(.4, 1):.1f}" fill="#fff" opacity=".9"/>' for _ in range(60))
    if not big:
        return crust + speck

    def icicle(x, w, L, fill, hl):
        d = (f"M{x:.1f} 4 C{x + w * .08:.1f} {L * .45:.1f} {x + w * .38:.1f} {L * .8:.1f} {x + w * .5:.1f} {L:.1f} "
             f"C{x + w * .6:.1f} {L * .78:.1f} {x + w * .9:.1f} {L * .42:.1f} {x + w:.1f} 4Z")
        s = f'<path d="{d}" fill="url(#{fill})"/>'
        if hl:
            s += (f'<path d="M{x + w * .28:.1f} 6 Q{x + w * .33:.1f} {L * .45:.1f} {x + w * .47:.1f} {L * .86:.1f}" '
                  f'stroke="#fff" stroke-opacity=".7" stroke-width="1.1" fill="none" stroke-linecap="round"/>')
        return s

    back, front, extras = [], [], []
    x = -4
    while x < W:  # back row: small, dim
        w, L = r.uniform(8, 16), r.uniform(10, 24) * scale
        back.append(icicle(x, w, L, "iceback", False))
        x += w * r.uniform(.6, 1.1)
    x = 2
    while x < W:  # front row: bigger, varied, some long
        w = r.uniform(10, 22)
        L = (r.uniform(16, 34) if r.random() > .18 else r.uniform(40, 58)) * scale
        front.append(icicle(x, w, L, "icebody", True))
        tip = (x + w / 2, L)
        if L > 30 * scale and r.random() < .55:
            dur = r.uniform(3, 6)
            extras.append(f'<path class="drip" d="M{tip[0]:.1f} {L - 1:.1f}q-2.4 4.2 0 6.2q2.4-2 0-6.2Z" fill="#{P["ice"]}" '
                          f'style="transform-box:fill-box;transform-origin:top;animation-duration:{dur:.1f}s;animation-delay:{r.uniform(0, dur):.1f}s"/>')
        if r.random() < .22:
            dur = r.uniform(3, 7)
            extras.append(f'<use class="glint" href="#spark" x="{tip[0] - 5:.0f}" y="{L * .55 - 5:.0f}" width="10" height="10" '
                          f'style="animation-duration:{dur:.1f}s;animation-delay:{r.uniform(0, dur):.1f}s"/>')
        x += w * r.uniform(.75, 1.25) + r.uniform(0, 10)
    return "".join(back) + "".join(front) + crust + speck + "".join(extras)


# ------------------------------------------------------------------ constellations per piece
def C_header():
    a = constellation([(700, 120, 1.6), (742, 98, 1.3), (790, 108, 1.9), (835, 86, 1.4), (812, 150, 1.5), (760, 165, 1.2)],
                      [(0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (5, 0)], .8, 1)
    b = constellation([(470, 212, 1.3), (520, 200, 1.6), (566, 218, 1.2), (610, 205, 1.5)], [(0, 1), (1, 2), (2, 3)], 1.6, 2)
    return a + b + shooting(860, 70, 3)


def C_footer():
    return (constellation([(80, 72, 1.4), (120, 56, 1.7), (165, 80, 1.2), (205, 64, 1.5)], [(0, 1), (1, 2), (2, 3)], .3, 3)
            + constellation([(700, 84, 1.3), (745, 62, 1.6), (790, 78, 1.3), (830, 58, 1.5)], [(0, 1), (1, 2), (2, 3), (1, 3)], .9, 4))


def C_about(h):
    return (constellation([(735, 52, 1.5), (780, 40, 1.8), (822, 62, 1.3), (850, 40, 1.4)], [(0, 1), (1, 2), (2, 3)], .6, 5)
            + constellation([(640, h - 40, 1.3), (690, h - 58, 1.6), (742, h - 44, 1.2), (790, h - 66, 1.7), (838, h - 48, 1.3)],
                            [(0, 1), (1, 2), (2, 3), (3, 4)], 1.4, 6) + shooting(870, 40, 5))


def C_stack(h):
    return (constellation([(690, 130, 1.6), (742, 104, 1.3), (796, 124, 1.9), (838, 100, 1.3), (812, 176, 1.5), (744, 190, 1.4),
                           (700, 248, 1.2), (782, 268, 1.7), (840, 300, 1.3), (760, 330, 1.4)],
                           [(0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (5, 0), (5, 6), (6, 7), (7, 8), (7, 9)], .6, 7)
            + shooting(860, 60, 6.5))


# ------------------------------------------------------------------ pieces
def svg(h, css, defs, body, uid):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{h}" viewBox="0 0 {W} {h}">'
            f'<style>text{{font-family:{MONO}}}.sans{{font-family:{SANS}}}{BASE_CSS}{css}</style>'
            f'<defs>{base_defs(h, uid)}{defs}</defs>{body}</svg>')


def brackets(h, inset=24, arm=20):
    a, b = inset, W - inset
    return (f'<path d="M{a} {inset + arm}V{inset}h{arm} M{b - arm} {inset}h{arm}v{arm} M{b} {h - inset - arm}v{arm}h-{arm} M{a + arm} {h - inset}H{a}v-{arm}" '
            f'fill="none" stroke="#{P["pri"]}" stroke-width="2.5" opacity=".85"/>')


def tag(x, y, text):
    w = len(text) * 11.7 + 26
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="24" fill="#{P["pri"]}"/>'
            f'<text x="{x + 14}" y="{y + 17}" font-size="14" font-weight="700" letter-spacing="3" fill="#{P["bg"]}">{escape(text)}</text>')


def header():
    h = 240
    css = """
  .rev{clip-path:inset(0 100% 0 0);animation:rv 1.2s steps(15) .3s forwards}
  .ul{stroke-dasharray:300;stroke-dashoffset:300;animation:ul .6s ease-out 1.6s forwards}
  .blink{animation:bk 1.2s steps(1) infinite}
  @keyframes rv{to{clip-path:inset(0 0 0 0)}} @keyframes ul{to{stroke-dashoffset:0}} @keyframes bk{50%{opacity:0}}"""
    defs = (f'<linearGradient id="ng" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#cdf3ff"/><stop offset="1" stop-color="#6fd3ff"/></linearGradient>'
            '<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="-200" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
            '<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="1300 0" dur="3.2s" begin="1.6s" repeatCount="indefinite"/></linearGradient>'
            f'<filter id="nglow" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="6" result="b"/>'
            f'<feFlood flood-color="#{P["acc"]}" flood-opacity=".55"/><feComposite in2="b" operator="in" result="c"/>'
            f'<feMerge><feMergeNode in="c"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    s = f'<tspan fill="#{P["acc"]}">//</tspan>'
    nm = 'font-weight="800" font-size="62" letter-spacing="3"'
    body = (background(h) + f'<g clip-path="url(#clip)">{dust(h, 1, 45)}{C_header()}{snow(h, 2, 40, 9)}{ice_top(3)}</g>'
            + brackets(h, 30, 22)
            + f'<rect x="60" y="62" width="170" height="22" fill="#{P["pri"]}"/>'
            + f'<text x="70" y="78" font-size="13" font-weight="700" letter-spacing="3" fill="#{P["bg"]}">{escape(HEADER_TAG)}</text>'
            + f'<text x="840" y="78" text-anchor="end" font-size="13" letter-spacing="2" fill="#{P["sec"]}"><tspan class="blink" fill="#{P["acc"]}">●</tspan> STATUS: ONLINE</text>'
            + f'<text class="rev" x="60" y="146" {nm} fill="url(#ng)" filter="url(#nglow)">{NAME}</text>'
            + f'<text class="rev" x="60" y="146" {nm} fill="url(#shine)" style="mix-blend-mode:overlay">{NAME}</text>'
            + f'<line class="ul" x1="62" y1="160" x2="362" y2="160" stroke="#{P["acc"]}" stroke-width="4"/>'
            + f'<text x="62" y="186" font-size="13" letter-spacing="2" fill="#{P["sec"]}">{HEADER_META.format(s=s)}</text>')
    return svg(h, css, defs, body, "h")


def footer():
    h = 112
    css = ".blink{animation:bk 1s steps(1) infinite}@keyframes bk{50%{opacity:0}}"
    body = (background(h) + f'<g clip-path="url(#clip)">{dust(h, 11, 25)}{C_footer()}{snow(h, 12, 22, 5)}{ice_top(13, scale=.6)}</g>'
            + f'<text x="450" y="70" text-anchor="middle" font-size="14" font-weight="700" letter-spacing="4" fill="#{P["pri"]}"><tspan class="blink" fill="#{P["acc"]}">■</tspan> END OF TRANSMISSION <tspan class="blink" fill="#{P["acc"]}">■</tspan></text>'
            + f'<text x="450" y="93" text-anchor="middle" font-size="12" letter-spacing="3" fill="#{P["sec"]}">thanks for stopping by // SAADM33</text>')
    return svg(h, css, "", body, "f")


def rich(parts):
    return "".join(f'<tspan font-weight="{700 if b else 400}" fill="#{P["pri"] if b else P["txt"]}">{escape(t)}</tspan>' for t, b in parts)


CARD_CSS = ".in{opacity:0;animation:in .6s ease-out forwards}@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"


def about():
    para, bullets = ABOUT_LINES, ABOUT_BULLETS
    y, parts = 108, []
    for i, line in enumerate(para):
        parts.append(f'<text class="sans in" x="48" y="{y}" font-size="17" style="animation-delay:{.15 * i:.2f}s">{rich(line)}</text>')
        y += 27
    y += 16
    for i, (k, v) in enumerate(bullets):
        parts.append(f'<g class="in" style="animation-delay:{.5 + .15 * i:.2f}s"><use href="#spark" x="48" y="{y - 15}" width="10" height="10" opacity=".9"/>'
                     f'<text x="66" y="{y - 3}" font-size="13" font-weight="700" letter-spacing="2" fill="#{P["sec"]}">{k}</text>'
                     f'<text class="sans" x="176" y="{y - 3}" font-size="16" fill="#{P["txt"]}">{escape(v)}</text></g>')
        y += 30
    h = y + 24
    body = (background(h) + f'<g clip-path="url(#clip)">{dust(h, 21, 40)}{C_about(h)}{snow(h, 22, 25, 5)}{ice_top(23, big=False)}</g>'
            + brackets(h) + tag(48, 44, "// ABOUT ME") + "".join(parts))
    return svg(h, CARD_CSS, "", body, "a")


def fetch_icons(ids):
    url = f"https://skillicons.dev/icons?i={ids}"
    req = urllib.request.Request(url, headers={"User-Agent": "profile-asset-generator"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


def stack():
    rows = STACK_ROWS
    ICON, y, parts = 52, 98, []
    for i, (label, ids) in enumerate(rows):
        s = fetch_icons(ids)
        pre = f"r{i}_"
        s = re.sub(r'id="([^"]+)"', lambda m: f'id="{pre}{m.group(1)}"', s)
        s = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{pre}{m.group(1)})', s)
        s = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{pre}{m.group(1)}"', s)
        vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', s)
        vw, vh = int(vb.group(1)), int(vb.group(2))
        s = re.sub(r'^\s*<svg[^>]*>', f'<svg x="236" y="{y}" width="{ICON * vw / vh:.1f}" height="{ICON}" viewBox="0 0 {vw} {vh}">', s, count=1)
        parts.append(f'<g class="in" style="animation-delay:{.15 * i:.2f}s">'
                     f'<text x="48" y="{y + ICON / 2 + 5:.0f}" font-size="14" font-weight="700" letter-spacing="3" fill="#{P["sec"]}">{label}</text>{s}</g>')
        if i < len(rows) - 1:
            parts.append(f'<line x1="48" y1="{y + ICON + 11}" x2="640" y2="{y + ICON + 11}" stroke="#{P["pri"]}" stroke-opacity=".12"/>')
        y += ICON + 22
    h = y + 22
    body = (background(h) + f'<g clip-path="url(#clip)">{dust(h, 31, 45)}{C_stack(h)}{snow(h, 32, 28, 6)}{ice_top(33, big=False)}</g>'
            + brackets(h) + tag(48, 44, "// TECH STACK") + "".join(parts))
    return svg(h, CARD_CSS, "", body, "s")


def divider():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="18" viewBox="0 0 900 18">\n'
            '<style>.run{animation:run 4s linear infinite}@keyframes run{from{transform:translateX(0)}to{transform:translateX(780px)}}</style>\n'
            f'<rect x="0" y="8" width="900" height="2" fill="#{P["pri"]}" opacity=".35"/>\n'
            f'<rect x="0" y="5" width="90" height="8" fill="#{P["pri"]}"/><rect x="96" y="5" width="14" height="8" fill="#{P["acc"]}"/>\n'
            f'<rect x="116" y="5" width="6" height="8" fill="#{P["sec"]}"/><rect class="run" x="120" y="7" width="60" height="4" fill="#{P["acc"]}"/>\n'
            f'<rect x="852" y="5" width="6" height="8" fill="#{P["sec"]}"/><rect x="864" y="5" width="36" height="8" fill="#{P["acc"]}"/>\n'
            '</svg>\n')


if __name__ == "__main__":
    for name, fn in (("header", header), ("footer", footer), ("about", about), ("stack", stack), ("divider", divider)):
        path = os.path.join(out, name + ".svg")
        with open(path, "w") as f:
            f.write(fn())
        print("wrote", os.path.normpath(path))
