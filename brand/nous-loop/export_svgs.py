"""Export the NoUs Loop marks as standalone SVG files: styles, colours and animation embedded, no fonts needed.
Animated, still (print), and on-the-wall versions."""
import json, os, re, sys

ROOT = sys.argv[1]          # .../nous-ds/project
OUT = sys.argv[2]           # export folder
os.makedirs(OUT, exist_ok=True)

# reuse the generator's drawing functions (it also rewrites the previews, identically)
sys.argv = ['gen_graffiti.py', ROOT]
g = {'__name__': 'gen'}
exec(open('gen_graffiti.py', encoding='utf-8').read(), g)

# --- styles: token values + the component CSS, minus the page-only parts ---
t = json.load(open(os.path.join(ROOT, 'tokens.json'), encoding='utf-8'))
first = t['color']['themes'][0]['id']
vars_ = []
for k in t['color']['tokens']:
    v = k['value'] if isinstance(k['value'], str) else k['value'].get(first)
    vars_.append(f"--{k['name']}:{v}")
for fam in ('spacing', 'radius', 'shadow'):
    for k in t[fam]['tokens']:
        vars_.append(f"--{k['name']}:{k['value']}")
for key, stack in t['type']['families'].items():
    vars_.append(f"--font-{key}:{stack}")
css = open(os.path.join(ROOT, 'components/bundle.css'), encoding='utf-8').read()
wall_tile = re.findall(r'url\("(data:image/svg\+xml,[^"]+)"\)', css[css.index('.nl-wall {'):css.index('}', css.index('.nl-wall {'))])[-1]
css = re.sub(r'@import url\([^)]*\);\n', '', css)
i = css.index('.nl-wall {'); css = css[:i] + css[css.index('}', i) + 1:]                       # wall block
i = css.index('/* falling-posters */'); j = css.index('/* /falling-posters */') + len('/* /falling-posters */')
css = css[:i] + css[j:]
i = css.index('/* Nous Loop components'); j = css.index('/* ── The owl:') if '/* ── The owl:' in css[i:] else None
STYLE = ':root, svg { ' + '; '.join(vars_) + ' }\n' + css
STILL = '''
/* still version: every motion off, the mark shown whole and lit */
*, *::before, *::after { animation: none !important; transition: none !important; }
.nl-live { color: var(--neon-cyan); }
.nl-wm-nozzle, .nl-spray__head, .nl-spray__mist, .nl-spray__nozzle { stroke-opacity: 0; fill-opacity: 0; visibility: hidden; }
.nl-spray__paint, .nl-spray__over, .nl-wm-paint, .nl-wm-paint-over { stroke-dashoffset: 0 !important; }
'''

def esc(s):
    return s.replace(']]>', ']]]]><![CDATA[>')

def doc(inner_svg, vb, w, h, still=False, wall=False, title='NoUs Loop'):
    """Wrap a generated mark (an <svg> string) into a standalone SVG document."""
    x0, y0, vw, vh = vb
    style = STYLE + (STILL if still else '')
    bg = ''
    if wall:
        bg = (f'<defs><pattern id="nl-wall" patternUnits="userSpaceOnUse" width="480" height="320">'
              f'<image href="{wall_tile}" width="480" height="320"/></pattern>'
              f'<radialGradient id="nl-vig" cx="50%" cy="50%" r="75%"><stop offset=".55" stop-color="#000" stop-opacity="0"/>'
              f'<stop offset="1" stop-color="#000" stop-opacity=".75"/></radialGradient></defs>'
              f'<rect x="{x0}" y="{y0}" width="{vw}" height="{vh}" fill="#0d0d0e"/>'
              f'<rect x="{x0}" y="{y0}" width="{vw}" height="{vh}" fill="url(#nl-wall)"/>'
              f'<rect x="{x0}" y="{y0}" width="{vw}" height="{vh}" fill="url(#nl-vig)"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {vw} {vh}" width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'<title>{title}</title><style><![CDATA[\n{esc(style)}\n]]></style>{bg}{inner_svg}</svg>')

def nest(svg, x, y, w, h):
    return svg.replace('<svg ', f'<svg x="{x}" y="{y}" width="{w}" height="{h}" overflow="visible" ', 1)

files = {}
WM = g['wordmark']('nl-graffiti nl-live')
files['nous-loop-wordmark.svg'] = doc(nest(WM, 0, 0, 640, 140), (-10, -40, 660, 200), 1320, 400)
files['nous-loop-wordmark-still.svg'] = doc(nest(WM, 0, 0, 640, 140), (-10, -40, 660, 200), 1320, 400, still=True)
files['nous-loop-wordmark-wall.svg'] = doc(nest(WM, 0, 0, 640, 140), (-60, -110, 760, 380), 1520, 760, wall=True)
files['nous-loop-wordmark-wall-still.svg'] = doc(nest(WM, 0, 0, 640, 140), (-60, -110, 760, 380), 1520, 760, still=True, wall=True)

for cls, name in [('watch', 'watching'), ('think', 'severing'), ('alert', 'alert'), ('calm', 'calm')]:
    O = g['owl'](f'nl-graffiti nl-live nl-owl nl-owl--{cls}', f'The NoUs owl, {name}')
    files[f'nous-loop-owl-{name}.svg'] = doc(nest(O, 6, 8, 228, 290), (-14, -12, 268, 330), 536, 660, title=f'The NoUs owl, {name}')
O = g['owl']('nl-graffiti nl-live nl-owl nl-owl--watch', 'The NoUs owl')
files['nous-loop-owl-still.svg'] = doc(nest(O, 6, 8, 228, 290), (-14, -12, 268, 330), 536, 660, still=True, title='The NoUs owl')
files['nous-loop-owl-wall.svg'] = doc(nest(O, 6, 8, 228, 290), (-66, -40, 372, 372), 744, 744, wall=True, title='The NoUs owl')

E = g['emblem']()
files['nous-loop-emblem.svg'] = doc(nest(E, 0, 0, 280, 250), (-10, -10, 300, 270), 600, 540, title='The impossible pyramid')
files['nous-loop-emblem-still.svg'] = doc(nest(E, 0, 0, 280, 250), (-10, -10, 300, 270), 600, 540, still=True, title='The impossible pyramid')
files['nous-loop-emblem-avatar.svg'] = doc(nest(E, 0, 0, 280, 250), (-40, -50, 360, 360), 720, 720, wall=True, title='The impossible pyramid')

L = g['loader']('lg').replace('role="status" aria-label="Severing"', '')
files['nous-loop-severing-loader.svg'] = doc(nest(L, 0, 0, 200, 92), (-10, -10, 220, 112), 440, 224, title='Severing')

for name, text in files.items():
    open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n').write(text)
print('\n'.join(f'{n}  {len(v)//1024} KB' for n, v in files.items()))
