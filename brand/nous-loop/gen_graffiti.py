"""Builds the NoUs spray wordmark, the elongated sideways-8 loop, and the previews that use them."""
import math, os, random, sys

ROOT = sys.argv[1]  # .../nous-ds/project
random.seed(11)

def lemniscate(cx, cy, a, n=140, wobble=1.0, tilt=-0.04):
    """Lemniscate of Bernoulli (a figure 8 on its side), starting at the crossing, hand-wobbled."""
    pts = []
    for i in range(n + 1):
        t = math.pi / 2 + 2 * math.pi * i / n
        d = 1 + math.sin(t) ** 2
        x = a * math.cos(t) / d
        y = a * math.sin(t) * math.cos(t) / d
        y += x * tilt  # slight hand tilt
        if 0 < i < n:
            x += random.uniform(-wobble, wobble)
            y += random.uniform(-wobble, wobble) * 0.7
        pts.append((cx + x, cy + y))
    pts[-1] = pts[0]
    # Catmull-Rom -> cubic beziers for a smooth, hand-feeling stroke
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[-2]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else pts[1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d

# --- hand-drawn single-stroke letters: N o U s (thin tag, slanted, imperfect) ---
LETTERS = [
    "M12 96 C13 74 15 44 18 20 C30 44 44 70 54 92 C56 66 58 42 61 16",           # N
    "M102 60 C96 48 78 49 74 66 C70 84 84 98 98 88 C108 80 108 62 100 55",         # o
    "M124 22 C121 50 120 78 132 90 C144 100 162 94 168 76 C172 60 171 40 172 18",  # U
    "M226 56 C220 46 202 46 198 58 C195 70 222 70 224 84 C226 98 202 102 190 90",  # s
]
WORD_DRIPS = [(13, 96, 22, -0.0), (55, 92, 12, -2.6), (133, 92, 30, -4.1), (171, 79, 9, -1.3), (208, 98, 17, -5.2)]

LOOP_W = lemniscate(360, 58, 104)
LOOP_DRIPS = [(300, 89, 30, -1.7), (418, 88, 20, -4.4), (352, 66, 11, -3.1), (446, 74, 8, -5.8)]

DEFS = ('<defs><filter id="nl-grain" filterUnits="userSpaceOnUse" x="-100" y="-100" width="900" height="500">'
        '<feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="4" result="n"/>'
        '<feDisplacementMap in="SourceGraphic" in2="n" scale="3.2"/></filter>'
        # spray body: rough, speckled edges like a can moving at speed
        '<filter id="nl-spray-edge" filterUnits="userSpaceOnUse" x="-100" y="-100" width="900" height="500">'
        '<feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="11" result="n"/>'
        '<feDisplacementMap in="SourceGraphic" in2="n" scale="5" result="d"/>'
        '<feTurbulence type="fractalNoise" baseFrequency="2.4" numOctaves="1" seed="2" result="s"/>'
        '<feColorMatrix in="s" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.4 2.1" result="speck"/>'
        '<feComposite in="d" in2="speck" operator="in"/></filter>'
        # wide filter regions so blurs never clip into boxes
        '<filter id="nl-halo" filterUnits="userSpaceOnUse" x="-100" y="-100" width="900" height="500"><feGaussianBlur stdDeviation="8"/></filter>'
        '<filter id="nl-mist" filterUnits="userSpaceOnUse" x="-100" y="-100" width="900" height="500"><feGaussianBlur stdDeviation="4.5"/></filter>'
        '<filter id="nl-spill" filterUnits="userSpaceOnUse" x="-100" y="-100" width="900" height="500"><feGaussianBlur stdDeviation="16"/></filter></defs>')

# The original spray look (pulsing dark halo, soft overspray, grainy neon ink), thicker.
def strokes(paths, w_ink=7.5, w_over=22):
    def layer(cls, w):
        return "".join(f'<path class="{cls}" stroke-width="{w}" d="{p}"/>' for p in paths)
    halo = layer("nl-spray-shadow", w_over + 26) + layer("nl-spray-shadow", w_over + 14) + layer("nl-spray-shadow", w_over + 4)
    return (f'<g class="nl-spray-layer nl-spray-shadows">{halo}</g>'
            f'<g class="nl-spray-layer">{layer("nl-spray-over", w_over)}</g>'
            f'<g class="nl-spray-layer" filter="url(#nl-grain)">{layer("nl-spray-ink", w_ink)}</g>')

def drips(lst):
    out = []
    for x, y, ln, delay in lst:
        out.append(f'<g class="nl-drip" style="animation-delay:{delay}s"><path class="nl-drip__run" d="M{x} {y} v{ln}"/>'
                   f'<ellipse class="nl-drip__bead" cx="{x}" cy="{y+ln}" rx="1.9" ry="2.4"/></g>'
                   f'<circle class="nl-drip__drop" style="animation-delay:{delay}s" cx="{x}" cy="{y+ln+1}" r="2"/>')
    return "".join(out)

def lobe(cx, cy, a, side, n=70):
    """One half of the lemniscate (a figure 8 on its side), from the crossing round and back."""
    t0 = math.pi / 2 if side == "l" else -math.pi / 2
    pts = []
    for i in range(n + 1):
        t = t0 + math.pi * i / n
        d = 1 + math.sin(t) ** 2
        pts.append((cx + a * math.cos(t) / d, cy + a * math.sin(t) * math.cos(t) / d))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)

def spill(paths, w=34):
    """Eerie neon spill: the live colour thrown onto the bricks behind the main strokes."""
    return ('<g filter="url(#nl-spill)">'
            + "".join(f'<path class="nl-spill-path" stroke-width="{w}" d="{p}"/>' for p in paths) + '</g>')


def lobe_seg(cx, cy, a, side, frac=0.14, n=24):
    """The first stretch of a lobe leaving the crossing: drawn again on top so one strand passes OVER the other."""
    t0 = math.pi / 2 if side == "l" else -math.pi / 2
    pts = []
    for i in range(n + 1):
        t = t0 + math.pi * frac * i / n
        d = 1 + math.sin(t) ** 2
        pts.append((cx + a * math.cos(t) / d, cy + a * math.sin(t) * math.cos(t) / d))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)

def over(path, w_ink, w_over, cut=None):
    """Escher's over-under: cut a dark gap through what lies beneath, then lay the strand back on top."""
    cut = cut or (w_over + 6)
    return (f'<path class="nl-weave-cut" stroke-width="{cut}" d="{path}"/>' + strokes([path], w_ink, w_over))

def emblem(cls="nl-graffiti nl-live nl-emblem", label="The impossible pyramid: the surveillance pyramid turned upside down, its bars woven so it cannot exist, with the owl's lens inside watching back"):
    """The surveillance pyramid flipped: three bars woven over-under in a cycle (an impossible structure),
    the owl's lens eye where the all-seeing eye used to be."""
    A, B, C = (40, 40), (240, 40), (140, 213)
    def bar(p, q, ext=24):
        import math as _m
        dx, dy = q[0] - p[0], q[1] - p[1]; L = _m.hypot(dx, dy); ux, uy = dx / L, dy / L
        return (p[0] - ux * ext, p[1] - uy * ext), (q[0] + ux * ext, q[1] + uy * ext), (ux, uy)
    bars = [bar(A, B), bar(B, C), bar(C, A)]
    def seg(b, start, length):
        (x0, y0), _, (ux, uy) = b
        return f"M{x0 + ux*start:.1f} {y0 + uy*start:.1f} L{x0 + ux*(start+length):.1f} {y0 + uy*(start+length):.1f}"
    def tube(p, w=15):
        return (strokes([p], w, w + 16) + f'<path class="nl-tube-core" stroke-width="{w - 8}" d="{p}"/>')
    full = [f"M{b[0][0]:.1f} {b[0][1]:.1f} L{b[1][0]:.1f} {b[1][1]:.1f}" for b in bars]
    body = "".join(tube(p) for p in full)
    # cyclic weave: at every corner the arriving bar passes over the one it meets -> impossible
    weave = ""
    for b in bars:
        weave += f'<path class="nl-weave-cut" stroke-width="25" d="{seg(b, 12, 26)}"/>' + tube(seg(b, 0, 62))
    eye_c = (140, 98)
    lens = (strokes([circle(eye_c[0], eye_c[1], 24)], 6, 16)
            + part("wm-aperture", eye_c, strokes([circle(eye_c[0], eye_c[1], 12), f"M140 74 L144 86", f"M162 102 L152 100", f"M124 116 L132 108"], 3, 8))
            + f'<circle class="nl-owl-pupil" cx="{eye_c[0]}" cy="{eye_c[1]}" r="4.5"/>')
    rivets = "".join(f'<circle class="nl-owl-rivet" cx="{x}" cy="{y}" r="2.2"/>' for x, y in [(A[0]+30, A[1]), (B[0]-30, B[1]), (C[0], C[1]-30)])
    return (f'<svg class="{cls}" viewBox="0 0 280 250" role="img" aria-label="{label}">{DEFS}'
            + spill(full, 40) + body + weave + lens + rivets + '</svg>')

def wordmark(cls="nl-graffiti nl-live", label="NoUs Loop"):
    """NoUs L∞P as one coordinated neon machine (14s master cycle): locked as NoUs L∞P, then every glyph
    transforms on its own pivot (No Us → Nous → NoUS, the loop tears and struggles, L and P blink out),
    then they click back one by one and the mark locks, surges, and the ∞ spins like a working engine."""
    def rivets(pts):
        return "".join(f'<circle class="nl-owl-rivet" cx="{x}" cy="{y}" r="2"/>' for x, y in pts)
    def glyph(name, pivot, dx, inner, spill_paths, flick_delay, extra_cls=""):
        px, py = pivot
        return (f'<g class="nl-wm-glyph nl-wm-g--{name} {extra_cls}" style="transform-origin:{px}px {py}px">'
                f'<g class="nl-wm-flick" style="animation-delay:{flick_delay}s" transform="translate({dx} 0)">'
                f'{spill(spill_paths)}{inner}</g></g>')
    def steam(cls_, pts):
        return "".join(f'<circle class="nl-wm-steam {cls_}" style="animation-delay:{d}s" cx="{x}" cy="{y}" r="{r}"/>' for x, y, r, d in pts)

    tN = "M16 98 L16 24 L60 98 L60 24"
    tO = circle(24, 76, 22)
    tU = "M8 22 L8 70 C8 88 20 98 36 98 C52 98 64 88 64 70 L64 22"
    ts = "M40 58 C34 49 24 46 15 48 C4 51 2 64 12 69 L32 78 C43 83 42 96 30 99 C19 102 8 98 3 91"
    tL = "M8 22 L8 98 L50 98"
    tP = "M8 98 L8 22 L34 22 C62 22 62 64 34 64 L8 64"
    CX, CY, A = 478, 76, 74
    lobes_l, lobes_r = lobe(CX, CY, A, "l"), lobe(CX, CY, A, "r")

    N = (strokes([tN], 6.5, 18) + strokes(["M9 98 L23 98", "M53 24 L67 24"], 3.2, 9)
         + part("wm-spin", (16, 24), strokes([gear(16, 24, 8, 5.5, 8), circle(16, 24, 2.2)], 2.6, 7))
         + part("wm-spin nl-wm-spin--rev", (60, 98), strokes([gear(60, 98, 8, 5.5, 8), circle(60, 98, 2.2)], 2.6, 7))
         + rivets([(9, 98), (23, 98), (53, 24), (67, 24)]))
    o = (strokes([tO], 6.5, 18)
         + part("wm-aperture", (24, 76), strokes([circle(24, 76, 11), "M24 54 L28 65", "M44 80 L35 78", "M10 92 L18 85"], 3, 8))
         + '<circle class="nl-owl-pupil" cx="24" cy="76" r="4"/>')
    U = (strokes([tU], 6.5, 18) + strokes(["M1 22 L15 22", "M57 22 L71 22"], 3.2, 9)
         + rivets([(1, 22), (15, 22), (57, 22), (71, 22)]))
    s = strokes([ts], 6.5, 18) + rivets([(40, 58), (3, 91)])
    L = (strokes([tL], 6.5, 18) + strokes(["M1 22 L15 22", "M50 91 L50 105"], 3.2, 9)
         + rivets([(1, 22), (15, 22), (50, 91), (50, 105)]))
    P = (strokes([tP], 6.5, 18) + strokes(["M1 98 L15 98"], 3.2, 9)
         + strokes([circle(30, 43, 10), "M22 50 L24 48", "M38 50 L36 48", "M30 33 L30 35"], 2.4, 6)
         + '<path class="nl-wm-needle" style="transform-origin:30px 43px" d="M30 43 L30 35"/>'
         + '<circle class="nl-owl-rivet" cx="30" cy="43" r="2.2"/>'
         + rivets([(1, 98), (15, 98)])
         + steam("nl-wm-steam--vent", [(54, 26, 4, 0), (58, 20, 3, .35), (52, 14, 5, .7)]))

    loop = (f'<g class="nl-wm-loop" style="transform-origin:{CX}px {CY}px">'
            + spill([lobes_l, lobes_r])
            + f'<g class="nl-wm-lobe--l"><g class="nl-wm-ghost">{strokes([lobes_l], 8, 22)}</g><g class="nl-wm-fresh nl-wm-fresh--l"><path class="nl-wm-paint-over" pathLength="100" d="{lobes_l}"/><g filter="url(#nl-grain)"><path class="nl-wm-paint" pathLength="100" d="{lobes_l}"/></g><path class="nl-wm-nozzle" pathLength="100" d="{lobes_l}"/></g></g>'
            + f'<g class="nl-wm-lobe--r"><g class="nl-wm-ghost">{strokes([lobes_r], 8, 22)}{over(lobe_seg(CX, CY, A, "r", .1), 8, 22, 15)}</g><g class="nl-wm-fresh nl-wm-fresh--r"><path class="nl-wm-paint-over" pathLength="100" d="{lobes_r}"/><g filter="url(#nl-grain)"><path class="nl-wm-paint" pathLength="100" d="{lobes_r}"/></g><path class="nl-wm-nozzle" pathLength="100" d="{lobes_r}"/></g></g>'
            + f'<path class="nl-wm-spark" d="M{CX} {CY-14} L{CX+4} {CY-5} L{CX-3} {CY} L{CX+4} {CY+6} L{CX} {CY+14}"/>'
            + f'<circle class="nl-wm-weld" cx="{CX}" cy="{CY}" r="4"/>'
            + '</g>'
            + steam("nl-wm-steam--loop", [(CX - 6, CY - 10, 4, 0), (CX + 6, CY - 14, 3, .15), (CX, CY - 20, 5, .3)]))

    return (f'<svg class="{cls} nl-wm" viewBox="0 0 640 140" role="img" aria-label="{label}">{DEFS}'
            + glyph("n", (38, 98), 0, N, [tN], -0.0)
            + glyph("o", (120, 76), 96, o, [tO], -1.3)
            + glyph("u", (186, 98), 150, U, [tU], -2.9)
            + glyph("s", (243, 99), 240, s, [ts], -0.7)
            + glyph("l", (355, 98), 330, L, [tL], -2.1, "nl-wm-fade")
            + loop
            + glyph("p", (598, 98), 568, P, [tP], -3.6, "nl-wm-fade")
            # the owl perches on the ∞ when the sign is whole, and flies off when it breaks apart
            + '<g class="nl-wm-owl" style="transform-origin:523px 52px">'
            + owl("nl-owl nl-owl--watch", "", with_loop=False).replace('<svg class=', '<svg x="491" y="-14" width="64" height="82" aria-hidden="true" class=', 1)
            + '</g></svg>')

# --- loader: the elongated sideways 8 alone, sprayed by a moving nozzle ---
LOOP_L = lemniscate(100, 40, 88, wobble=0.6)
def loader(size=""):
    cls = "nl-spray nl-live" + (f" nl-spray--{size}" if size else "")
    head = ("" if size == "sm" else
            f'<g class="nl-spray__head"><circle class="nl-spray__mist" r="9"/><circle class="nl-spray__nozzle" r="2.4"/>'
            f'<animateMotion dur="2.8s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;0.7;1" calcMode="linear" path="{LOOP_L}"/></g>')
    drp = ""
    return (f'<svg class="{cls}" viewBox="0 0 200 92" role="status" aria-label="Severing">{DEFS}'
            f'<g class="nl-spray-shadows"><path class="nl-spray-shadow" stroke-width="40" d="{LOOP_L}"/><path class="nl-spray-shadow" stroke-width="28" d="{LOOP_L}"/><path class="nl-spray-shadow" stroke-width="18" d="{LOOP_L}"/></g>'
            f'<path class="nl-spray__ghost" stroke-width="7" d="{LOOP_L}"/>'
            f'<path class="nl-spray__over" pathLength="100" stroke-width="22" d="{LOOP_L}"/>'
            f'<path class="nl-spray__paint" pathLength="100" stroke-width="{11 if size=="sm" else 7}" d="{LOOP_L}"/>'
            f'{drp}{head}</svg>')

# --- the mascot: Athena's owl rebuilt as a neon machine that holds all the knowledge ---
# Jointed parts: each part is its own group with a pivot, so CSS can move it mechanically.
def gear(cx, cy, r_out, r_in, teeth):
    pts = []
    for i in range(teeth * 2):
        a0 = math.pi * i / teeth
        r = r_out if i % 2 == 0 else r_in
        for da in (-0.11, 0.11):
            a = a0 + da
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"

def circle(cx, cy, r):
    return f"M{cx-r} {cy} a{r} {r} 0 1 0 {2*r} 0 a{r} {r} 0 1 0 {-2*r} 0"

def part(name, pivot, inner):
    px, py = pivot
    return f'<g class="nl-owl-{name}" style="transform-origin:{px}px {py}px">{inner}</g>'

def sprocket(name, cx, cy, ro, ri, teeth):
    return part(name, (cx, cy), strokes([gear(cx, cy, ro, ri, teeth), circle(cx, cy, 2.5)], 2.6, 7))

OWL_LOOP = lemniscate(120, 250, 100, wobble=0.8)

HEAD_SHELL = "M120 38 C158 38 182 56 182 86 C182 104 172 114 164 118 L76 118 C68 114 58 104 58 86 C58 56 82 38 120 38Z"
BODY = "M76 118 C60 154 66 192 96 214 L144 214 C174 192 180 154 164 118"
BEAK = "M120 104 L111 116 L120 128 L129 116 Z"
WING_L = ["M72 132 C56 158 60 190 88 208", "M70 152 L86 160", "M72 176 L88 184"]
WING_R = ["M168 132 C184 158 180 190 152 208", "M170 152 L154 160", "M168 176 L152 184"]
TAIL = ["M108 214 L104 232", "M120 214 L120 236", "M132 214 L136 232"]
TALONS = ["M104 212 L98 236 L106 242", "M112 214 L110 238", "M136 212 L142 236 L134 242", "M128 214 L130 238"]
CROWN = ["M100 44 L92 28", "M120 40 L120 22", "M140 44 L148 28"]
NODES = [(92, 26), (120, 19), (148, 26)]
RIVETS = [(68, 96), (172, 96), (84, 112), (156, 112), (82, 200), (158, 200)]

def loop_eye(side, cx, cy):
    """A lens sitting inside one lobe of the owl's ∞ eyes: aperture ring with blades, glowing pupil."""
    blades = [f"M{cx} {cy-9} L{cx+2.5} {cy-4}", f"M{cx+8} {cy+3} L{cx+3.5} {cy+1.5}", f"M{cx-6} {cy+7} L{cx-2} {cy+3.5}"]
    return part(f"eye nl-owl-eye--{side}", (cx, cy),
                part("aperture", (cx, cy), strokes([circle(cx, cy, 7.5)] + blades, 2.6, 7))
                + f'<circle class="nl-owl-pupil" cx="{cx}" cy="{cy}" r="3.4"/>')

def eye(side, cx, cy):
    blades = [f"M{cx} {cy-16} L{cx+4} {cy-7}", f"M{cx+14} {cy+4} L{cx+6} {cy+2}", f"M{cx-10} {cy+12} L{cx-3} {cy+6}"]
    return part(f"eye nl-owl-eye--{side}", (cx, cy),
                strokes([circle(cx, cy, 16)], 3.2, 9)
                + part("aperture", (cx, cy), strokes([circle(cx, cy, 8)] + blades, 3, 8))
                + f'<circle class="nl-owl-pupil" cx="{cx}" cy="{cy}" r="3.6"/>')

def owl(cls="nl-graffiti nl-live nl-owl nl-owl--watch",
        label="The NoUs owl: Athena's owl as a neon machine that holds all the knowledge", with_loop=True):
    nodes = "".join(f'<circle class="nl-owl-node" style="animation-delay:{i*0.25}s" cx="{x}" cy="{y}" r="3.2"/>'
                    for i, (x, y) in enumerate(NODES))
    rivets = "".join(f'<circle class="nl-owl-rivet" cx="{x}" cy="{y}" r="2"/>' for x, y in RIVETS)
    head = part("head", (120, 118),
                strokes([HEAD_SHELL, BEAK], 6.5, 18)
                + part("crown", (120, 44), strokes(CROWN, 3.2, 9) + nodes)
                + part("brow nl-owl-brow--l", (93, 72), strokes(["M70 64 L116 80"], 4, 10))
                + part("brow nl-owl-brow--r", (147, 72), strokes(["M170 64 L124 80"], 4, 10))
                + strokes([lemniscate(120, 94, 42, wobble=0, tilt=0)], 4.8, 13)
                + loop_eye("l", 95, 94) + loop_eye("r", 145, 94))
    return (f'<svg class="{cls}" viewBox="6 8 228 290" role="img" aria-label="{label}">{DEFS}'
            + spill(([OWL_LOOP] if with_loop else []) + [BODY, HEAD_SHELL], 30)
            + (strokes([OWL_LOOP], 8, 24) if with_loop else '')
            + part("wing nl-owl-wing--l", (74, 130), strokes(WING_L, 5, 14))
            + part("wing nl-owl-wing--r", (166, 130), strokes(WING_R, 5, 14))
            + strokes([BODY], 6.5, 18) + strokes(TAIL + TALONS, 3.2, 9)
            + part("heart", (120, 162), strokes([gear(120, 162, 16, 11, 10), circle(120, 162, 4)], 3.4, 9))
            + strokes(["M120 178 L120 196"], 3.2, 9)
            + sprocket("sprocket nl-owl-sprocket--l", 74, 130, 9, 6, 8)
            + sprocket("sprocket nl-owl-sprocket--r", 166, 130, 9, 6, 8)
            + sprocket("sprocket nl-owl-sprocket--neck", 120, 118, 7, 4.5, 6)
            + head + rivets + '</svg>')

def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

HEAD = '<!doctype html>\n<html><head><meta charset="utf-8">'

# Owl component
STATES = [("watch", "watching"), ("think", "severing"), ("alert", "alert"), ("calm", "calm")]
write("components/Owl/preview.html", f'''<!-- @dsCard group="Brand" height=640 -->
{HEAD}<style>html,body{{margin:0;background:var(--brick)}}
.s{{padding:24px 32px;min-height:640px;display:grid;grid-template-columns:300px 1fr;gap:28px;align-items:center}}
.big{{display:grid;justify-items:center;gap:10px}}.big .nl-owl{{width:280px;height:auto}}
.row{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}
.st{{display:grid;justify-items:center;gap:6px}}.st .nl-owl{{width:120px;height:auto}}
.cap{{font:500 9.6px/14px var(--font-mono);letter-spacing:2px;text-transform:uppercase;color:var(--ink-dim)}}
.now{{font:400 24px/30px var(--font-tag);color:var(--ink)}}</style></head>
<body><div class="nl-wall s">
<div class="big">{owl("nl-graffiti nl-live nl-owl nl-owl--watch")}<span class="now" id="now" aria-live="polite">watching</span></div>
<div class="row">{"".join(f'<div class="st">{owl(f"nl-graffiti nl-live nl-owl nl-owl--{k}", f"The NoUs owl, {v}")}<span class="cap">{v} · nl-owl--{k}</span></div>' for k, v in STATES)}</div>
</div>
<script>
(function(){{
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var owl=document.querySelector('.big .nl-owl'), now=document.getElementById('now');
  var states=[["watch","watching"],["think","severing…"],["alert","alert"],["calm","calm"]], i=0;
  setInterval(function(){{
    owl.classList.remove('nl-owl--'+states[i][0]); i=(i+1)%states.length;
    owl.classList.add('nl-owl--'+states[i][0]); now.textContent=states[i][1];
  }}, 3200);
}})();
</script></body></html>
''')

# Emblem component
write("components/Emblem/preview.html", f'''<!-- @dsCard group="Brand" height=420 -->
{HEAD}<style>html,body{{margin:0;background:var(--brick)}}.s{{padding:24px 36px;display:flex;gap:36px;align-items:center;min-height:420px}}
.s .nl-emblem{{width:320px;height:auto}}.cap{{font:400 26px/32px var(--font-tag);color:var(--ink);max-width:300px}}.cap b{{font-weight:400;color:var(--neon-red)}}</style></head>
<body><div class="nl-wall s">
{emblem()}
<p class="cap">the system is impossible.<br>we watch back<b>/</b></p>
</div></body></html>
''')

# Wordmark component
write("components/Wordmark/preview.html", f'''<!-- @dsCard group="Brand" height=420 -->
{HEAD}<style>html,body{{margin:0;background:var(--brick)}}.s{{padding:28px 36px;display:grid;gap:18px}}
.s .nl-graffiti{{width:100%;max-width:720px;height:auto}}.cap{{font:500 9.6px/14px var(--font-mono);letter-spacing:2px;text-transform:uppercase;color:var(--ink-dim)}}</style></head>
<body><div class="nl-wall s">
{wordmark()}
<span class="cap">Live paint: one even spray weight, colour drifting from cyan to electric blue, a dark halo pulsing so it pops</span>
</div></body></html>
''')

# SprayLoader component
write("components/SprayLoader/preview.html", f'''<!-- @dsCard group="Status" height=240 -->
{HEAD}<style>html,body{{margin:0;background:var(--brick)}}.s{{display:flex;align-items:center;gap:48px;padding:28px 40px;flex-wrap:wrap;min-height:240px}}
.think{{display:inline-flex;align-items:center;gap:10px;font:400 12.8px/18px var(--font-mono);color:var(--ink-dim)}}</style></head>
<body><div class="nl-wall s">
{loader("lg")}
{loader()}
<span class="think" role="status">{loader("sm").replace('role="status" aria-label="Severing"', 'aria-hidden="true"')} severing…</span>
</div></body></html>
''')

# Cover
write("components/Cover/preview.html", f'''<!-- @dsCard height=320 -->
{HEAD}<style>html,body{{margin:0;background:var(--brick)}}
.cover{{position:relative;width:960px;height:320px;overflow:hidden}}
.cover.nl-wall{{background-position:left 50px top 0,center,center,center,center,center,center,0 0}}
.mark{{position:absolute;left:28px;top:14px;width:820px;height:auto}}
.tagline{{position:absolute;left:44px;bottom:22px;margin:0;font:400 30px/34px var(--font-tag);color:var(--ink);text-shadow:0 0 8px #000,0 0 18px #000}}
.tagline b{{font-weight:400;color:var(--neon-red);text-shadow:var(--glow-neon-red)}}</style></head>
<body><div class="cover nl-wall">
<!-- derivation
     blocks: none; ground = brick with mortar running bond (.nl-wall), the brand's own wall
     arrangement: the hand-sprayed NoUs wordmark + elongated sideways-8 loop across the width, tagline beneath
     pattern row: literal motif (the loop) as a sprayed stroke; the ∞ IS the logo and the "loop" in NoUs
     scales: ink stroke 4.2, overspray 13, shadow 23; colour cycles neon-cyan → neon-blue → nousloop-teal -->
{wordmark("nl-graffiti nl-live mark")}
<p class="tagline">safety through severance<b>/</b></p>
</div></body></html>
''')

# BrandWall page
write("components/BrandWall/preview.html", f'''<!-- @dsCard group="Brand" height=1320 page -->
{HEAD}<style>
html,body{{margin:0;background:var(--brick)}}
.wall{{min-height:1320px;padding:48px 44px;display:grid;gap:44px;align-content:start;overflow:hidden}}.wall>*{{min-width:0}}
.hero{{width:100%;max-width:820px;height:auto}}
.slogans{{display:grid;gap:6px}}
.slogans p{{margin:0;font:400 40px/48px var(--font-tag)}}
.slogans b{{font-weight:400;color:var(--neon-red);text-shadow:var(--glow-neon-red)}}
.name{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:24px;max-width:960px}}
.name p{{margin:0;font:400 15px/24px var(--font-sans);color:var(--ink-dim)}}
.name strong{{display:block;font:500 11.2px/16px var(--font-mono);letter-spacing:2px;text-transform:uppercase;color:var(--neon-cyan);margin-bottom:6px}}
.art{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}
.art figure{{margin:0;border:1px solid var(--mortar);background:#000;border-radius:var(--radius-sm);overflow:hidden}}
.art img{{display:block;width:100%;aspect-ratio:1;object-fit:cover}}
.art figcaption{{font:500 9.6px/14px var(--font-mono);letter-spacing:2px;text-transform:uppercase;color:var(--ink-dim);padding:8px 10px}}
.owlfig{{margin:0;display:grid;justify-items:center;align-content:center;aspect-ratio:1}}.owlfig .nl-owl{{height:88%;width:auto}}.owlfig figcaption{{font:500 9.6px/14px var(--font-mono);letter-spacing:2px;text-transform:uppercase;color:var(--ink-dim)}}
</style></head>
<body><div class="nl-wall wall">
{wordmark("nl-graffiti nl-live hero")}
<div class="slogans nl-live">
  <p class="nl-tag-text">safety through severance<b>/</b></p>
  <p class="nl-tag-text">free your data<b>/</b></p>
  <p class="nl-tag-text">give them nothing<b>/</b></p>
  <p class="nl-tag-text">take back everything<b>/</b></p>
</div>
<div class="name">
  <p><strong>No Us</strong>No company, no platform, no middleman between a person and their own data. We sever big tech from your personal data.</p>
  <p><strong>Nous</strong>Greek for mind. The thing we protect: your thoughts, signals and history stay on your machine.</p>
  <p><strong>The loop ∞</strong>Not a word, a mark: a figure 8 on its side, sprayed fast and never perfect. You and your tools in a closed loop.</p>
</div>
<div style="display:flex;align-items:center;gap:20px;font:400 12.8px/18px var(--font-mono);color:var(--ink-dim)">{loader()} severing… the loop is sprayed over and over</div>
<div class="art">
  <figure><img src="/_blob/c3e4cd650ec0e4e61fcef200c7d45537" alt="Rebellion room: hooded figures, a neon cyan infinity loop and a red X over 'our data'"><figcaption>Our sign of rebellion in an endless winter</figcaption></figure>
  <figure><img src="/_blob/e051d5623a2ef53533382e7943ba36de" alt="Night highway billboard reading Let's sever humans, with neon infinity loops"><figcaption>Let's sever ∞ humans</figcaption></figure>
  <figure class="owlfig">{owl("nl-graffiti nl-live nl-owl")}<figcaption>The owl of Athena, as a machine</figcaption></figure>
</div>
</div></body></html>
''')
print("ok")
