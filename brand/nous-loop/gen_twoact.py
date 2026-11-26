"""Two-act wordmark timeline (28s).
ACT 1 (0–50%): the transformer sequence from wm_motion.css, time-compressed.
ACT 2 (50–100%): the revolution's chain reaction. The sign loses power and falls apart (letters slump,
scatter, go dark, the loop breaks); then one bump changes the next: each part that is knocked into place
lights up and knocks the next, until the whole thing stands as NoUs L∞P and surges."""
import re, sys

src = open('wm_motion.css', encoding='utf-8').read()

def halve(body):
    return re.sub(r'(\d+(?:\.\d+)?)%', lambda m: f"{float(m.group(1))/2:g}%", body)

kf = {m.group(1): m.group(2) for m in re.finditer(r'@keyframes ([\w-]+) \{(.*?\})\s*\}', src, re.S)}

B = {
 'nl-g-n': "50% { transform: none; } 53%, 55.5% { transform: translateY(10px) rotate(-14deg) scale(.95); } 56.5% { transform: scale(1.14,.8); } 57.5% { transform: scale(.9,1.18) rotate(7deg); } 58.5% { transform: rotate(-3deg) skewX(4deg); } 60% { transform: none; } 76.5% { transform: scale(1.08,.9); } 77.5% { transform: translateY(-6px) scale(.96,1.06); } 79% { transform: none; } 84% { transform: translateY(-5px) scaleY(1.05); } 86% { transform: scale(1.05,.95); } 88% { transform: none; } 92% { transform: translateY(-4px); } 94%, 100% { transform: none; }",
 'nl-g-o': "50% { transform: rotate(360deg); } 53%, 57.5% { transform: translate(-10px,16px) rotate(220deg) scale(.9); } 59% { transform: translateX(8px) rotate(400deg); } 60% { transform: translateX(4px) rotate(380deg) scale(1.08,.9); } 61.5% { transform: rotate(360deg); } 77% { transform: translateY(-8px) rotate(360deg) scale(.95,1.08); } 78.5% { transform: rotate(360deg) scale(1.08,.92); } 80% { transform: rotate(360deg); } 86.5% { transform: translateY(-5px) rotate(360deg); } 88.5%, 100% { transform: rotate(360deg); }",
 'nl-g-u': "50% { transform: none; } 53%, 60% { transform: translateY(6px) rotate(-28deg) scale(.92); } 61% { transform: scale(1.28,.72); } 62% { transform: translateY(-16px) scale(.86,1.2); } 63% { transform: scale(1.14,.86); } 64% { transform: skewX(-6deg); } 65% { transform: skewX(3deg); } 66% { transform: none; } 78% { transform: scale(1.08,.92); } 79.5% { transform: translateY(-6px) scale(.96,1.05); } 81% { transform: none; } 85.5% { transform: translateY(-5px); } 87.5% { transform: none; } 93% { transform: translateY(-4px); } 95%, 100% { transform: none; }",
 'nl-g-s': "50% { transform: none; } 53%, 62.5% { transform: translateY(4px) rotate(88deg) scale(.82); } 63.5% { transform: scale(1.15,.75); } 64.5% { transform: translateY(-14px) scale(.85,1.4) rotate(-6deg); } 65.5% { transform: translateY(-2px) rotate(14deg); } 66.5% { transform: rotate(-5deg) skewX(-6deg); } 68% { transform: none; } 79% { transform: translateY(-6px) scaleY(1.08); } 80.5% { transform: none; } 87% { transform: translateY(-5px); } 89% { transform: none; } 94% { transform: translateY(-4px); } 96%, 100% { transform: none; }",
 'nl-g-l': "50% { transform: none; } 53%, 65.5% { transform: rotate(-72deg) translateY(4px); } 66.5% { transform: rotate(8deg) skewX(-8deg); } 67.5% { transform: rotate(-4deg) skewX(5deg); } 68.5% { transform: none; } 80.5% { transform: translateY(-6px); } 82% { transform: none; } 88% { transform: translateY(-5px); } 90%, 100% { transform: none; }",
 'nl-g-p': "50% { transform: none; } 53%, 70.5% { transform: translateY(10px) rotate(16deg) scale(.82); } 71.5% { transform: scale(1.08); } 72.5% { transform: scale(1.18,1.1); } 73.5% { transform: scale(1.22,1.14) rotate(-3deg); } 74.5% { transform: scale(.92,1.05); } 76% { transform: scale(1.04,.96); } 77.5% { transform: none; } 89% { transform: translateY(-5px); } 91%, 100% { transform: none; }",
 'nl-wm-surge': "50% { stroke-opacity: .12; } 53%, 75% { stroke-opacity: .05; } 77% { stroke-opacity: .36; } 82% { stroke-opacity: .16; } 86% { stroke-opacity: .3; } 92% { stroke-opacity: .14; } 100% { stroke-opacity: .12; }",
 'nl-wm-spin': "50%, 69.5% { transform: rotate(720deg); } 70.5% { transform: rotate(720deg) scale(1.22,.84); } 71.5% { transform: rotate(720deg) scale(.92,1.08); } 72.5% { transform: rotate(720deg); animation-timing-function: cubic-bezier(.4,0,.3,1); } 79% { transform: rotate(1800deg); } 81% { transform: rotate(1832deg); } 83% { transform: rotate(1795deg); } 85%, 100% { transform: rotate(1800deg); }",
 'nl-wm-struggle-l': "50% { transform: translateX(0); } 53%, 67.5% { transform: translateX(-16px); } 68.5% { transform: translateX(2.5px); } 69.5%, 100% { transform: translateX(0); }",
 'nl-wm-struggle-r': "50% { transform: translateX(0); } 53%, 67.5% { transform: translateX(16px); } 68.5% { transform: translateX(-2.5px); } 69.5%, 100% { transform: translateX(0); }",
 'nl-wm-spark': "50%, 100% { stroke-opacity: 0; }",
 'nl-wm-weld': "50%, 68% { fill-opacity: 0; } 68.5% { fill-opacity: 1; } 72%, 100% { fill-opacity: 0; }",
 'nl-steam-loop': "50%, 68% { stroke-opacity: 0; transform: translateY(0) scale(.5); } 70% { stroke-opacity: .5; } 82%, 100% { stroke-opacity: 0; transform: translateY(-30px) scale(1.8); }",
 'nl-steam-vent': "50%, 72.5% { stroke-opacity: 0; transform: translateY(0) scale(.5); } 75% { stroke-opacity: .65; } 90%, 100% { stroke-opacity: 0; transform: translate(10px, -26px) scale(1.9); }",
 'nl-needle': "50%, 70.5% { transform: rotate(-60deg); } 72.5% { transform: rotate(60deg); } 73.5% { transform: rotate(48deg); } 74.5% { transform: rotate(75deg); } 76% { transform: rotate(-50deg); } 78% { transform: rotate(-34deg); } 80%, 100% { transform: rotate(-40deg); }",
}

out = src
for name, body in kf.items():
    if name in ('nl-wm-flick', 'nl-wm-fade'):
        continue
    assert name in B, name
    newbody = halve(body).rstrip() + '\n  ' + B[name] + '\n}'
    out = re.sub(r'@keyframes ' + re.escape(name) + r' \{.*?\}\s*\}', lambda m, nb=newbody, n=name: '@keyframes ' + n + ' {' + nb, out, count=1, flags=re.S)

# power per glyph (--nl-fade): Act 1 — L and P blink (from nl-wm-fade), the rest stay lit;
# Act 2 — everything powers down at 50–54%, then each glyph lights at the moment the chain reaction bumps it.
fade_a1 = halve(kf['nl-wm-fade']).rstrip()
on_at = {'n': 56, 'o': 59, 'u': 61, 's': 64, 'l': 66.5, 'p': 72}
power = ''
for g, T in on_at.items():
    a1 = fade_a1 if g in 'lp' else "0%, 50% { --nl-fade: 1; }"
    a2 = (f"50% {{ --nl-fade: 1; }} 51% {{ --nl-fade: .4; }} 51.5% {{ --nl-fade: .85; }} 52.5% {{ --nl-fade: .12; }} 53% {{ --nl-fade: .3; }} "
          f"54%, {T - .1:g}% {{ --nl-fade: .08; }} {T:g}% {{ --nl-fade: .9; }} {T + .4:g}% {{ --nl-fade: .3; }} {T + .8:g}%, 100% {{ --nl-fade: 1; }}")
    power += f"@keyframes nl-pw-{g} {{ {a1}\n  {a2} }}\n"
out = re.sub(r'/\* L and P blink out like failing neon.*?\n@keyframes nl-wm-fade \{.*?\}\s*\}\n',
             '/* power: each glyph goes dark when the sign falls apart and lights the moment the chain reaction bumps it */\n' + power, out, count=1, flags=re.S)
for g in 'nousl' + 'p':
    pass
out = re.sub(r'\.nl-wm \.nl-wm-g--([nous]) \{ animation-name: nl-g-\1; \}',
             lambda m: f'.nl-wm .nl-wm-g--{m.group(1)} {{ animation-name: nl-g-{m.group(1)}, nl-pw-{m.group(1)}; animation-timing-function: cubic-bezier(.68,-.25,.27,1.35), steps(1); }}', out)
out = out.replace('animation-name: nl-g-l, nl-wm-fade;', 'animation-name: nl-g-l, nl-pw-l;').replace('animation-name: nl-g-p, nl-wm-fade;', 'animation-name: nl-g-p, nl-pw-p;')
out = out.replace('.nl-wm .nl-wm-g--l .nl-spill-path, .nl-wm .nl-wm-g--p .nl-spill-path { stroke-opacity: calc(.12 * var(--nl-fade)); animation: none; }',
                  '.nl-wm .nl-wm-glyph .nl-spill-path { stroke-opacity: calc(.14 * var(--nl-fade)); animation: none; }')
out = out.replace(' 14s ', ' 28s ')
head = '''/* ── NoUs L∞P: one coordinated neon machine in TWO ACTS (28s) ─────────────────────────────────
   ACT 1 (0–50%), the transformer: locked → jolt loose → No Us → Nous → NoUS while the ∞ tears and
   struggles and L/P blink out → glyphs click home, the ∞ welds → locked, surge, the ∞ spins like a turbine.
   ACT 2 (50–100%), the revolution's chain reaction (rubber hose meets Rube Goldberg): the sign loses power
   and falls apart (letters slump, scatter and go dark, the ∞ breaks). Then one bump changes the next: the N
   springs upright and lights → kicks the o, which rolls home and lights → bonks the U, which boings upright
   → its landing pops the s up like a jack-in-the-box → the s tips the fallen L back up like a lever → the L
   knocks the ∞'s halves together, they weld and spin up like a flywheel → the flywheel drives the P, which
   inflates and lights until its steam whistle blows → NoUs L∞P stands, surges, and bobs to the beat. */
'''
out = re.sub(r'/\* ── NoUs L∞P: one coordinated neon machine, 14s master cycle.*?\*/\n', head, out, count=1, flags=re.S)
assert out.count('{') == out.count('}'), (out.count('{'), out.count('}'))
open('wm_motion_2act.css', 'w', encoding='utf-8', newline='\n').write(out)

b = sys.argv[1]
c = open(b, encoding='utf-8').read()
a0 = c.index('/* ── NoUs L∞P: one coordinated neon machine')
a1 = c.index('/* Escher winks:')
owl = '''/* Rubber-hose owl: the whole owl squashes and stretches to its own beat, a different gait per expression */
.nl-owl.nl-live { transform-origin: 50% 92%; }
.nl-owl--watch.nl-live { animation: nl-paint-shift 24s ease-in-out infinite, nl-owl-bob 2.6s cubic-bezier(.68,-.25,.27,1.35) infinite; }
.nl-owl--think.nl-live { animation: nl-paint-shift 24s ease-in-out infinite, nl-owl-jitter .9s steps(3) infinite; }
.nl-owl--alert.nl-live { animation: nl-paint-shift 24s ease-in-out infinite, nl-owl-hop 1.4s cubic-bezier(.68,-.25,.27,1.35) infinite; }
.nl-owl--calm.nl-live  { animation: nl-paint-shift 24s ease-in-out infinite, nl-owl-sway 5s ease-in-out infinite; }
@keyframes nl-owl-bob    { 0%, 100% { transform: none; } 20% { transform: scale(1.04,.95); } 45% { transform: translateY(-6px) scale(.97,1.04); } 70% { transform: scale(1.02,.98); } }
@keyframes nl-owl-jitter { 0%, 100% { transform: none; } 33% { transform: skewX(-2deg) translateX(-1px); } 66% { transform: skewX(2deg) translateX(1px); } }
@keyframes nl-owl-hop    { 0%, 100% { transform: none; } 15% { transform: scale(1.1,.86); } 35% { transform: translateY(-14px) scale(.92,1.1); } 55% { transform: scale(1.08,.9); } 70% { transform: none; } }
@keyframes nl-owl-sway   { 0%, 100% { transform: rotate(-2deg); } 50% { transform: rotate(2deg) scale(1.01,.99); } }

'''
c = c[:a0] + out + '\n' + owl + c[a1:]
c = c.replace('  .nl-wm-glyph, .nl-wm-flick, .nl-wm-fade { animation: none !important; }', '  .nl-wm-glyph, .nl-wm-flick { animation: none !important; }')
open(b, 'w', encoding='utf-8', newline='\n').write(c)
print('ok', c.count('@keyframes nl-pw-'), c.count('@keyframes nl-owl-bob'), c.count('@keyframes nl-wm-fade'))
