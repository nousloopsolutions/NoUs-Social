"""Faded wall history: torn big-tech propaganda posters and ghost tags of past revolutions.
Generic, fictional messaging only (no real companies, logos or people). Spliced into .nl-wall as the top background layer."""
import random, sys, urllib.parse
random.seed(2077)
W, H = 1200, 800
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">']
o.append('<defs><filter id="w" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="2" seed="5"/>'
         '<feDisplacementMap in="SourceGraphic" scale="4"/></filter>'
         '<filter id="e" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".35" numOctaves="2" seed="8" result="n"/>'
         '<feColorMatrix in="n" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -3 1.6" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in"/></filter>'
         '<filter id="p" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".5" numOctaves="2" seed="12" result="n"/>'
         '<feColorMatrix in="n" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.1 1.35" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in"/></filter></defs>')
PROP = "Impact, 'Arial Narrow Bold', 'Arial Black', sans-serif"
MONO = "'Courier New', monospace"
HAND = "'Segoe Print', 'Bradley Hand', 'Marker Felt', cursive"

def torn(x, y, w, h, fill, op, rot, flt="e"):
    pts = []
    for i in range(9): pts.append((x + w * i / 8, y + random.uniform(-4, 5)))
    for i in range(1, 9): pts.append((x + w + random.uniform(-6, 3), y + h * i / 8))
    for i in range(7, -1, -1): pts.append((x + w * i / 8, y + h + random.uniform(-10, 4)))
    for i in range(7, 0, -1): pts.append((x + random.uniform(-3, 6), y + h * i / 8))
    p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    return f'<g transform="rotate({rot} {x+w/2} {y+h/2})" opacity="{op}" filter="url(#{flt})"><polygon points="{p}" fill="{fill}"/>'

# 1. Peeling poster: AGREE TO CONTINUE, with an old red X sprayed over it
o.append(torn(820, 60, 220, 300, "#3e3c39", .72, 2.5))
o.append(f'<text x="840" y="140" font-family="{PROP}" font-size="46" fill="#121212">AGREE</text>')
o.append(f'<text x="840" y="186" font-family="{PROP}" font-size="46" fill="#121212">TO</text>')
o.append(f'<text x="840" y="232" font-family="{PROP}" font-size="46" fill="#121212">CONTINUE</text>')
o.append(f'<rect x="840" y="254" width="150" height="22" fill="#121212"/><text x="852" y="270" font-family="{MONO}" font-size="12" fill="#3a3836">I ACCEPT ALL</text>')
o.append(f'<text x="840" y="318" font-family="{MONO}" font-size="10" fill="#1a1a1a">terms updated. again. continued use = consent.</text></g>')
o.append('<g opacity=".42" filter="url(#w)"><path d="M826 80 L1030 350 M1035 90 L835 340" stroke="#7a2626" stroke-width="10" stroke-linecap="round" fill="none"/></g>')

# 2. Billboard remnant, half buffed out by grey paint
o.append(torn(70, 520, 520, 110, "#323234", .62, -1.2))
o.append(f'<text x="96" y="596" font-family="{PROP}" font-size="58" fill="#0e0e0f" letter-spacing="2">CONVENIENCE IS FREEDOM</text></g>')
o.append('<rect x="330" y="512" width="210" height="130" fill="#1b1b1d" opacity=".85" transform="rotate(-3 430 580)" filter="url(#e)"/>')
o.append(f'<text x="352" y="590" font-family="{HAND}" font-size="34" fill="#8a8a90" opacity=".35" transform="rotate(-6 430 580)">is a leash</text>')

# 3. Small privacy poster with a scrawl through it
o.append(torn(640, 470, 170, 200, "#3a3835", .62, -4))
o.append(f'<text x="656" y="520" font-family="{PROP}" font-size="26" fill="#141414">WE CARE</text>')
o.append(f'<text x="656" y="552" font-family="{PROP}" font-size="26" fill="#141414">ABOUT YOUR</text>')
o.append(f'<text x="656" y="584" font-family="{PROP}" font-size="26" fill="#141414">PRIVACY</text>')
o.append(f'<text x="656" y="640" font-family="{MONO}" font-size="9" fill="#1c1c1c">*shared with 1,412 partners</text></g>')
o.append('<path d="M640 560 C690 548 740 576 812 556" stroke="#9b9ba0" stroke-width="3" opacity=".3" fill="none" filter="url(#w)"/>')

# 4. Ghost tags of past revolutions: buffed, faded, overlapping
o.append(f'<text x="40" y="90" font-family="{HAND}" font-size="40" fill="#5f6f75" opacity=".22" transform="rotate(-4 40 90)">we were here</text>')
o.append(f'<text x="420" y="300" font-family="{HAND}" font-size="30" fill="#7c6a5a" opacity=".18" transform="rotate(3 420 300)">no one is mean</text>')
o.append(f'<text x="60" y="420" font-family="{MONO}" font-size="22" fill="#6d6d72" opacity=".2" letter-spacing="6">THEY SOLD THE LAST ONE TOO</text>')
o.append(f'<text x="980" y="470" font-family="{HAND}" font-size="26" fill="#55707a" opacity=".2" transform="rotate(-8 980 470)">unplug</text>')
o.append(f'<text x="560" y="760" font-family="{HAND}" font-size="28" fill="#6a5f70" opacity=".18">read the terms</text>')
# stencil remnant, half gone
o.append(f'<g opacity=".2" filter="url(#e)"><text x="500" y="120" font-family="{PROP}" font-size="64" fill="none" stroke="#8c8c90" stroke-width="2" letter-spacing="10">SEVER</text></g>')
# an old ∞ from an earlier uprising, sprayed and buffed
o.append('<g opacity=".14" filter="url(#w)"><path d="M300 200 C300 170 250 170 250 200 C250 230 300 230 300 200 C300 170 350 170 350 200 C350 230 300 230 300 200" stroke="#7fb5b5" stroke-width="5" fill="none"/></g>')
# tally marks: days counted
o.append('<g opacity=".25" stroke="#8a8a8f" stroke-width="2" stroke-linecap="round">' + "".join(
    f'<path d="M{1080+i*9} {650+random.uniform(-2,2):.1f} v28"/>' for i in range(4)) + '<path d="M1074 670 L1118 656"/>' + "".join(
    f'<path d="M{1132+i*9} {650+random.uniform(-2,2):.1f} v28"/>' for i in range(3)) + '</g>')
# paper scraps
for _ in range(10):
    x, y = random.uniform(0, W), random.uniform(0, H)
    o.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{random.uniform(8,26):.0f}" height="{random.uniform(6,18):.0f}" fill="#3a3836" opacity=".3" transform="rotate({random.uniform(-20,20):.0f} {x:.0f} {y:.0f})"/>')


# 5. War-torn propaganda: big company posters that survived a revolution, burned at the edges,
#    shot through, scorched, some half ripped away, a few with the revolution's red sprayed over them.
o.append('<defs><filter id="burn" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="5"/></filter>'
         '<radialGradient id="sc"><stop offset="0" stop-color="#000" stop-opacity=".9"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient></defs>')
def holes(x, y, w, h, n):
    s = ""
    for _ in range(n):
        hx, hy, r = x + random.uniform(.1, .9) * w, y + random.uniform(.1, .9) * h, random.uniform(2, 4.5)
        s += (f'<circle cx="{hx:.0f}" cy="{hy:.0f}" r="{r+2.5:.1f}" fill="none" stroke="#2a2826" stroke-width="2" opacity=".8"/>'
              f'<circle cx="{hx:.0f}" cy="{hy:.0f}" r="{r:.1f}" fill="#030303"/>'
              f'<path d="M{hx:.0f} {hy:.0f} l{random.uniform(-12,12):.0f} {random.uniform(-12,12):.0f} M{hx:.0f} {hy:.0f} l{random.uniform(-10,10):.0f} {random.uniform(-10,10):.0f}" stroke="#050505" stroke-width="1.2"/>')
    return s
def propaganda(x, y, w, h, rot, lines, sub, mark, ripped=0.0, sprayed=None):
    cx, cy = x + w / 2, y + h / 2
    pts = []
    for k in range(9): pts.append((x + w * k / 8, y + random.uniform(-3, 6)))
    for k in range(1, 9): pts.append((x + w + random.uniform(-8, 3), y + h * k / 8))
    bottom = y + h * (1 - ripped)
    for k in range(8, -1, -1): pts.append((x + w * k / 8, bottom + random.uniform(-16, 6)))
    for k in range(7, 0, -1):
        yy = y + h * k / 8
        if yy < bottom: pts.append((x + random.uniform(-3, 8), yy))
    p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    s = f'<g transform="rotate({rot} {cx:.0f} {cy:.0f})" opacity=".85">'
    s += f'<g filter="url(#e)"><polygon points="{p}" fill="#5d5950"/>'
    s += f'<rect x="{x+12}" y="{y+12}" width="{w-24}" height="{h*0.4:.0f}" fill="#24221f"/>'
    mx, my = cx, y + 12 + h * 0.2
    if mark == "eye":
        s += f'<ellipse cx="{mx:.0f}" cy="{my:.0f}" rx="{w*0.28:.0f}" ry="{h*0.08:.0f}" fill="none" stroke="#77736c" stroke-width="5"/><circle cx="{mx:.0f}" cy="{my:.0f}" r="{h*0.045:.0f}" fill="#77736c"/>'
    elif mark == "smile":
        s += f'<circle cx="{mx:.0f}" cy="{my:.0f}" r="{h*0.11:.0f}" fill="none" stroke="#77736c" stroke-width="5"/><path d="M{mx-h*0.055:.0f} {my+4:.0f} q{h*0.055:.0f} {h*0.05:.0f} {h*0.11:.0f} 0" fill="none" stroke="#77736c" stroke-width="4"/>'
    elif mark == "cloud":
        s += f'<path d="M{mx-w*0.25:.0f} {my+h*0.06:.0f} a{h*0.06:.0f} {h*0.06:.0f} 0 0 1 {w*0.08:.0f} -{h*0.09:.0f} a{h*0.09:.0f} {h*0.09:.0f} 0 0 1 {w*0.3:.0f} 0 a{h*0.06:.0f} {h*0.06:.0f} 0 0 1 {w*0.12:.0f} {h*0.09:.0f} Z" fill="none" stroke="#77736c" stroke-width="5"/>'
    else:  # bars: an endless "more" chart
        for k in range(4):
            bh = h * (0.05 + 0.04 * k)
            s += f'<rect x="{mx - w*0.22 + k*w*0.12:.0f}" y="{my + h*0.12 - bh:.0f}" width="{w*0.08:.0f}" height="{bh:.0f}" fill="#77736c"/>'
    ty = y + 12 + h * 0.4 + w * 0.16
    for ln in lines:
        s += f'<text x="{cx:.0f}" y="{ty:.0f}" text-anchor="middle" font-family="{PROP}" font-size="{w*0.15:.0f}" fill="#0b0b0b" letter-spacing="1">{ln}</text>'
        ty += w * 0.15
    s += f'<text x="{cx:.0f}" y="{y+h-14:.0f}" text-anchor="middle" font-family="{MONO}" font-size="9" fill="#1c1c1c">{sub}</text></g>'
    # burned edges, scorch, bullet holes
    s += f'<polygon points="{p}" fill="none" stroke="#050505" stroke-width="14" filter="url(#burn)" opacity=".9"/>'
    s += f'<ellipse cx="{x + random.uniform(.2,.8)*w:.0f}" cy="{y + random.uniform(.5,.9)*h:.0f}" rx="{w*0.35:.0f}" ry="{h*0.22:.0f}" fill="url(#sc)"/>'
    s += holes(x, y, w, h * (1 - ripped), random.randint(3, 7))
    if sprayed == "x":
        s += f'<path d="M{x+10} {y+20} L{x+w-10} {y+h*0.8:.0f} M{x+w-14} {y+16} L{x+16} {y+h*0.78:.0f}" stroke="#7a2424" stroke-width="9" stroke-linecap="round" opacity=".55" filter="url(#w)"/>'
    elif sprayed == "slash":
        s += f'<path d="M{x+w*0.15:.0f} {y+h*0.9:.0f} L{x+w*0.85:.0f} {y+h*0.1:.0f}" stroke="#7a2424" stroke-width="10" stroke-linecap="round" opacity=".5" filter="url(#w)"/>'
    elif sprayed == "lie":
        s += f'<text x="{cx:.0f}" y="{y+h*0.62:.0f}" text-anchor="middle" font-family="{HAND}" font-size="{w*0.3:.0f}" fill="#8a2a2a" opacity=".55" transform="rotate(-12 {cx:.0f} {y+h*0.6:.0f})">lies</text>'
    return s + '</g>'

o.append(propaganda(40, 250, 156, 220, -3, ["SHARE MORE.", "WORRY LESS."], "sharing is caring*", "smile", ripped=.18, sprayed="slash"))
o.append(propaganda(350, 300, 172, 236, 2.5, ["OPT IN TO", "HAPPINESS"], "consent by default", "bars", sprayed="lie"))
o.append(propaganda(905, 420, 160, 226, -4, ["THE CLOUD", "REMEMBERS", "FOR YOU"], "forever. and ever.", "cloud", ripped=.3))
o.append(propaganda(470, 600, 150, 196, 5, ["SMILE.", "YOU'RE", "SYNCED."], "always on", "eye", sprayed="x"))

o.append('</svg>')
svg = "".join(o)
uri = "data:image/svg+xml," + urllib.parse.quote(svg, safe=" ,.:;=/-'()")
print(len(svg))

css = sys.argv[1]
c = open(css, encoding="utf-8").read()
i = c.index(".nl-wall {"); j = c.index("}", i) + 1
block = c[i:j]
marks = f'    url("{uri}"),\n'
if "/* marks */" in block:
    a = block.index("/* marks */"); b = block.index("\n", block.index("url(", a)) + 1
    block = block[:a] + "/* marks */\n" + marks + block[b:]
else:
    block = block.replace("  background-image:\n", "  background-image:\n    /* marks */\n" + marks, 1)
    block = block.replace("background-size: 100% 100%,", "background-size: 1200px 800px, 100% 100%,", 1)
    block = block.replace("  color: var(--ink);", "  background-position: right -200px top -20px, center, center, center, center, center, center, 0 0;\n  background-repeat: repeat, no-repeat, no-repeat, no-repeat, no-repeat, no-repeat, no-repeat, repeat;\n  color: var(--ink);")
    block = block.replace("grime running down.", "grime running down, and the history on it:\n     torn big-tech propaganda and buffed-out tags of past revolutions (top layer, faded, never louder than the neon).")
c = c[:i] + block + c[j:]
open(css, "w", encoding="utf-8", newline="\n").write(c)
print("spliced")
