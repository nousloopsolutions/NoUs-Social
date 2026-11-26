# NoUs Loop brand: working folder

Everything for the NoUs Loop design system lives here.

- `exports/`: standalone SVGs (animated, still, on the wall), ready to use. See `exports/README.md`.
- `nous-ds/project/`: the design system source: tokens, `components/bundle.css`, previews, brand book (`README.md`).
  It is published at https://claude.ai/artifact/N1PzXUhSz84NEqa54Jj6rJ.
- Generator scripts (run from this folder):
  - `python gen_graffiti.py nous-ds/project`: wordmark, owl, emblem, loader, cover and brand-wall previews
  - `python gen_wall.py nous-ds/project/components/bundle.css`, then `python gen_marks.py ...` and `python gen_falling.py ...`: the war-torn wall, its posters and the falling posters
  - `python gen_twoact.py nous-ds/project/components/bundle.css`: the wordmark's two-act motion (reads `wm_motion.css`)
  - `python export_svgs.py nous-ds/project exports`: re-export the SVGs
  - `python make_test.py nous-ds/project <Component>`: a local test page with the tokens inlined
