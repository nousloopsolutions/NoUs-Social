"""Falling company propaganda: two big posters that hang, sway, peel at a corner and drop off the wall,
then get pasted up again. Generic fictional big-tech slogans (no real companies). CSS-only, on .nl-wall."""
import sys, urllib.parse, random
random.seed(77)
PROP = "Impact, 'Arial Narrow Bold', 'Arial Black', sans-serif"
MONO = "'Courier New', monospace"

def poster(w, h, lines, sub, mark):
    pts = []
    for i in range(7): pts.append((w * i / 6, random.uniform(0, 4)))
    for i in range(1, 7): pts.append((w - random.uniform(0, 4), h * i / 6))
    for i in range(5, -1, -1): pts.append((w * i / 6, h - random.uniform(0, 8)))
    for i in range(5, 0, -1): pts.append((random.uniform(0, 4), h * i / 6))
    p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h+10}">',
         '<defs><filter id="g" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".6" numOctaves="2" seed="4" result="n"/>'
         '<feColorMatrix in="n" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.2 1.3" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in"/></filter></defs>',
         f'<g filter="url(#g)"><polygon points="{p}" fill="#5a564e"/>',
         f'<rect x="14" y="14" width="{w-28}" height="{h*0.42:.0f}" fill="#22201e"/>']
    # the mark: a hollow, smiling corporate logo shape (generic)
    cx, cy = w / 2, 14 + h * 0.21
    if mark == "eye":
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{w*0.28:.0f}" ry="{h*0.09:.0f}" fill="none" stroke="#8a8680" stroke-width="5"/><circle cx="{cx}" cy="{cy}" r="{h*0.05:.0f}" fill="#8a8680"/>')
    else:
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{h*0.12:.0f}" fill="none" stroke="#8a8680" stroke-width="5"/><path d="M{cx-h*0.06:.0f} {cy+4} q{h*0.06:.0f} {h*0.05:.0f} {h*0.12:.0f} 0" fill="none" stroke="#8a8680" stroke-width="4"/>')
    y = 14 + h * 0.42 + 40
    for ln in lines:
        o.append(f'<text x="{w/2}" y="{y:.0f}" text-anchor="middle" font-family="{PROP}" font-size="{w*0.16:.0f}" fill="#0b0b0b" letter-spacing="1">{ln}</text>')
        y += w * 0.16
    o.append(f'<text x="{w/2}" y="{h-16}" text-anchor="middle" font-family="{MONO}" font-size="9" fill="#262626">{sub}</text>')
    o.append('</g>')
    # burned edges, a scorch bloom, bullet holes: it survived a revolution
    o.append('<defs><filter id="b" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="5"/></filter>'
             '<radialGradient id="s"><stop offset="0" stop-color="#000" stop-opacity=".85"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient></defs>')
    o.append(f'<polygon points="{p}" fill="none" stroke="#040404" stroke-width="14" filter="url(#b)"/>')
    o.append(f'<ellipse cx="{w*0.7:.0f}" cy="{h*0.78:.0f}" rx="{w*0.38:.0f}" ry="{h*0.2:.0f}" fill="url(#s)"/>')
    for _ in range(5):
        hx, hy, r = random.uniform(.15,.85)*w, random.uniform(.1,.9)*h, random.uniform(2,4)
        o.append(f'<circle cx="{hx:.0f}" cy="{hy:.0f}" r="{r+2.5:.1f}" fill="none" stroke="#242220" stroke-width="2"/><circle cx="{hx:.0f}" cy="{hy:.0f}" r="{r:.1f}" fill="#020202"/>')
    o.append('</svg>')
    return "data:image/svg+xml," + urllib.parse.quote("".join(o), safe=" ,.:;=/-'()")

A = poster(170, 250, ["TRUST", "THE FEED"], "by continuing you agree", "eye")
B = poster(160, 236, ["ALWAYS", "CONNECTED.", "ALWAYS", "CARED FOR."], "we value your privacy*", "smile")

block = f'''/* falling-posters */
/* Falling company propaganda: two big posters hang on the wall, sway, peel at a corner and drop away,
   then a new one is pasted up to fail again. Generic fictional slogans. Behind the content, faded. */
.nl-wall {{ position: relative; isolation: isolate; overflow: hidden; }}
.nl-wall::before, .nl-wall::after {{
  content: ""; position: absolute; z-index: -1; pointer-events: none;
  background-repeat: no-repeat; background-size: contain; opacity: 0;
}}
.nl-wall::before {{ width: 170px; height: 260px; top: 6%; right: 7%; background-image: url("{A}");
  transform-origin: 100% 0; animation: nl-poster-fall 19s cubic-bezier(.5,0,.75,0) infinite; }}
.nl-wall::after  {{ width: 160px; height: 246px; top: 38%; left: 46%; background-image: url("{B}");
  transform-origin: 0 0; animation: nl-poster-fall-b 23s cubic-bezier(.5,0,.75,0) infinite -9s; }}
@keyframes nl-poster-fall {{
  0%   {{ opacity: 0; transform: rotate(-3deg); }}
  6%   {{ opacity: .62; transform: rotate(-3deg); }}
  30%  {{ transform: rotate(-5deg); }}  36% {{ transform: rotate(-2deg); }}
  46%  {{ transform: rotate(-16deg); }} 50% {{ transform: rotate(-12deg); }} 56% {{ transform: rotate(-24deg); opacity: .62; }}
  74%  {{ transform: translate(-60px, 900px) rotate(-55deg); opacity: .35; }}
  75%, 100% {{ opacity: 0; transform: translate(-60px, 900px) rotate(-55deg); }}
}}
@keyframes nl-poster-fall-b {{
  0%   {{ opacity: 0; transform: rotate(4deg); }}
  7%   {{ opacity: .58; transform: rotate(4deg); }}
  34%  {{ transform: rotate(6deg); }}  40% {{ transform: rotate(3deg); }}
  50%  {{ transform: rotate(18deg); }} 55% {{ transform: rotate(13deg); }} 60% {{ transform: rotate(27deg); opacity: .58; }}
  78%  {{ transform: translate(70px, 900px) rotate(62deg); opacity: .3; }}
  79%, 100% {{ opacity: 0; transform: translate(70px, 900px) rotate(62deg); }}
}}
@media (prefers-reduced-motion: reduce) {{
  .nl-wall::before, .nl-wall::after {{ animation: none; opacity: .4; }}
}}
/* /falling-posters */
'''
css = sys.argv[1]
c = open(css, encoding="utf-8").read()
if "/* falling-posters */" in c:
    i = c.index("/* falling-posters */"); j = c.index("/* /falling-posters */") + len("/* /falling-posters */\n")
    c = c[:i] + block + c[j:]
else:
    k = c.index("}", c.index(".nl-wall {")) + 2
    c = c[:k] + "\n" + block + c[k:]
open(css, "w", encoding="utf-8", newline="\n").write(c)
print("ok", len(A), len(B))
