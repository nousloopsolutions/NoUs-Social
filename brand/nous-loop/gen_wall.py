"""Generate a decayed, soot-black brick wall tile (SVG data URI) and splice it into bundle.css as .nl-wall."""
import math, random, sys, urllib.parse
random.seed(1000)
W, H, BW, BH, M = 480, 320, 96, 40, 4  # tile, brick, mortar
out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">')
out.append('<defs>'
           '<filter id="g" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" seed="9" stitchTiles="stitch"/>'
           '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.6 1.15"/></filter>'
           '<filter id="s" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012 .05" numOctaves="3" seed="3" stitchTiles="stitch"/>'
           '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.2 1.25"/></filter>'
           '</defs>')
# crumbling mortar bed: dirty, uneven
out.append(f'<rect width="{W}" height="{H}" fill="#060606"/>')
for _ in range(40):  # gaps where mortar has fallen out
    x, y = random.randrange(W), random.randrange(H)
    out.append(f'<rect x="{x}" y="{y}" width="{random.randint(6,30)}" height="{random.randint(2,6)}" fill="#030303"/>')
rows = H // BH
for r in range(rows):
    off = 0 if r % 2 == 0 else -BW // 2
    x = off
    while x < W:
        w = BW + random.randint(-6, 5)
        bx, by = x + M / 2 + random.uniform(-1, 1), r * BH + M / 2 + random.uniform(-1, 1)
        bw, bh = w - M - random.uniform(0, 2), BH - M - random.uniform(0, 2)
        tone = random.randint(13, 30)
        warm = random.choice([0, 0, 0, 2, 3, 5])  # some bricks keep a burnt, charred warmth
        c = f"#{tone+warm:02x}{tone:02x}{max(tone-warm,0)+1:02x}"
        # chipped corners: polygon with random bites
        ch = lambda: random.choice([0, 0, 0, random.uniform(2, 9)])
        a, b, cc, d = ch(), ch(), ch(), ch()
        pts = [(bx + a, by), (bx + bw - b, by), (bx + bw, by + b), (bx + bw, by + bh - cc), (bx + bw - cc, by + bh),
               (bx + d, by + bh), (bx, by + bh - d), (bx, by + a)]
        for xx in (bx, bx + W, bx - W):  # wrap for seamless tiling
            p = " ".join(f"{px - bx + xx:.1f},{py:.1f}" for px, py in pts)
            out.append(f'<polygon points="{p}" fill="{c}"/>')
            # worn top edge highlight, very faint
            if random.random() < .5:
                out.append(f'<rect x="{xx+a:.1f}" y="{by:.1f}" width="{bw-a-b:.1f}" height="1.5" fill="#3a3a3e" opacity=".55"/>')
            # pitting
            for _ in range(random.randint(0, 3)):
                out.append(f'<circle cx="{xx+random.uniform(4,bw-4):.1f}" cy="{by+random.uniform(4,bh-4):.1f}" r="{random.uniform(.6,2.2):.1f}" fill="#020202" opacity=".8"/>')
            # cracks
            if random.random() < .28:
                cx, cy = xx + random.uniform(10, bw - 10), by
                d_ = f"M{cx:.1f} {cy:.1f}"
                for _ in range(4):
                    cx += random.uniform(-7, 7); cy += bh / 4
                    d_ += f" L{cx:.1f} {cy:.1f}"
                out.append(f'<path d="{d_}" stroke="#000" stroke-width="{random.uniform(.6,1.3):.1f}" fill="none" opacity=".9"/>')
        x += w
# war damage: blasted-out chunks, bullet pockmark clusters, scorch blooms
for _ in range(5):  # chunks blown out of the wall
    x, y, r = random.uniform(0, W), random.uniform(0, H), random.uniform(14, 30)
    pts = " ".join(f"{x + r*random.uniform(.6,1.2)*math.cos(a):.0f},{y + r*random.uniform(.5,1.1)*math.sin(a):.0f}" for a in [k*math.pi/5 for k in range(10)])
    out.append(f'<polygon points="{pts}" fill="#020202"/><polygon points="{pts}" fill="none" stroke="#2b2b2e" stroke-width="1.5" opacity=".6"/>')
for _ in range(4):  # bullet clusters
    bx, by = random.uniform(30, W - 30), random.uniform(30, H - 30)
    for _ in range(random.randint(3, 7)):
        hx, hy, r = bx + random.uniform(-26, 26), by + random.uniform(-20, 20), random.uniform(1.6, 3.4)
        out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{r+2:.1f}" fill="#2a2a2d" opacity=".5"/><circle cx="{hx:.1f}" cy="{hy:.1f}" r="{r:.1f}" fill="#010101"/>')
out.append('<defs><radialGradient id="sb"><stop offset="0" stop-color="#000" stop-opacity=".85"/><stop offset=".6" stop-color="#000" stop-opacity=".4"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient></defs>')
for _ in range(3):  # scorch blooms
    out.append(f'<ellipse cx="{random.uniform(0,W):.0f}" cy="{random.uniform(0,H):.0f}" rx="{random.uniform(60,120):.0f}" ry="{random.uniform(40,80):.0f}" fill="url(#sb)"/>')
# soot and grime streaks running down (rain-washed decay), and fine grain
out.append(f'<rect width="{W}" height="{H}" filter="url(#s)" opacity=".78"/>')
out.append(f'<rect width="{W}" height="{H}" filter="url(#g)" opacity=".5"/>')
out.append('</svg>')
svg = "".join(out)
uri = "data:image/svg+xml," + urllib.parse.quote(svg, safe=" ,.:;=/-'()")
print(len(svg), len(uri))

css_path = sys.argv[1]
c = open(css_path, encoding="utf-8").read()
i = c.index(".nl-wall {"); j = c.index("}", i) + 1
block = (".nl-wall {\n"
 "  /* a building left for a thousand years: soot-black brick, chipped, cracked, mortar crumbling out, grime running down.\n"
 "     Large soot patches on top break the 480x320 tile so it never reads as a pattern. */\n"
 "  background-color: var(--brick);\n"
 "  background-image:\n"
 "    radial-gradient(ellipse 60% 45% at 18% 12%, rgba(0, 0, 0, 0.6), transparent 70%),\n"
 "    radial-gradient(ellipse 50% 60% at 82% 70%, rgba(0, 0, 0, 0.5), transparent 70%),\n"
 "    radial-gradient(ellipse 35% 30% at 55% 40%, rgba(24, 24, 28, 0.35), transparent 70%),\n"
 "    radial-gradient(ellipse 30% 25% at 70% 18%, rgba(0, 0, 0, 0.55), transparent 70%),\n"
 "    radial-gradient(ellipse 25% 30% at 30% 80%, rgba(0, 0, 0, 0.5), transparent 70%),\n"
 "    linear-gradient(180deg, rgba(0, 0, 0, 0.55), transparent 22%, transparent 74%, rgba(0, 0, 0, 0.7)),\n"
 f"    url(\"{uri}\");\n"
 "  background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 480px 320px;\n"
 "  color: var(--ink);\n"
 "}")
c = c[:i] + block + c[j:]
open(css_path, "w", encoding="utf-8", newline="\n").write(c)
print("spliced")
