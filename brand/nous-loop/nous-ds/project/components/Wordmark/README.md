# Wordmark

The NoUs mark: **NoUs L∞P**. It is built like the owl, as a see-through neon machine, and the ∞ is the "oo" of Loop.

**Construction (steampunk meets cyberpunk, all in neon):**

- Letters are engineered neon tubes at the owl's outline weight, never wobbly hand strokes.
- Every stroke end is a riveted plate.
- The N's joints are sprockets that slowly turn.
- **The o is the owl's lens eye**: aperture blades that open and shut, and a glowing pupil. The name watches back.
- **The P is a pressure gauge**: its needle twitches under the strain, and neon steam vents off its top.

**One connected machine, in two acts (28s cycle).** Every motion causes the next, like change spreading in a revolution.

**Act 1, the transformer (0–14s):**

1. **Locked:** the sign holds as NoUs L∞P.
2. **Transform:** the glyphs jolt loose.
   - No and Us pull apart (**No Us**), the U folds to a lowercase u (**Nous**), the s swells to a capital (**NoUS**).
   - The ∞ tears apart with a red spark and struggles, and L and P blink out.
3. **Reassemble:** the glyphs click home one after another and the ∞ welds shut.
4. **Locked and running:** the sign surges brighter.

**Act 2, the revolution's chain reaction (14–28s), rubber hose meets Rube Goldberg:**

1. **The sign loses power:** letters slump, scatter and go dark, and the ∞ breaks in two.
2. **One bump starts the next:**
   - The N springs upright and lights, and kicks the o.
   - The o rolls home and lights, and bonks the U.
   - The U boings upright, and its landing pops the s up like a jack-in-the-box.
   - The s tips the fallen L back up like a lever.
   - The L knocks the ∞'s halves together; they weld with a flash, the nozzle re-sprays the loop, and it spins up like a flywheel.
   - The flywheel drives the P, which inflates and lights until its steam whistle blows.
3. **NoUs L∞P stands,** surges, and bobs to the beat.

**The ∞ is spray-painted.** Its old paint stays on the wall as a faint ghost. After every weld, and twice while the sign stands, a spray nozzle with a mist cloud re-paints it as a figure 8, the left lobe then the right. Freshly painted, it spins like a working turbine (two turns in Act 1, a flywheel spin in Act 2 that drives the P's gauge). It still tears apart with a red spark and struggles when the sign breaks.

**The owl lives on the sign.** A small mechanical owl perches on top of the ∞ while NoUs L∞P stands. When the sign breaks apart it hops and flies off, wings flapping. When the sign is whole again it swoops back in and lands with a rubber-hose squash.

Every glyph also flickers slightly on its own rhythm, like real neon.

**Escher wink:** at the ∞'s crossing one strand visibly passes over the other. It is an endless knot with no seam for anyone to cut.

**Layers, bottom to top:**

1. **Neon spill** (`nl-spill`): the eerie glow the tubes throw onto the bricks, pulsing every 5s.
2. **Dark halo** (`nl-spray-shadow`): three stacked soft black strokes, pulsing every 3.2s so the neon pops.
3. **Overspray** (`nl-spray-over`): a soft mist around the stroke.
4. **Ink** (`nl-spray-ink`): the thick, grainy neon tube.

**Live paint:** wrap the mark in `nl-live` and the colour drifts from `neon-cyan` to `neon-blue` to `nousloop-teal` over 24s. Every layer uses `currentColor`.

No sparkles or twinkling stars, and no drips (they come back only if they can look like real paint).

**Rules:**

- Use it on the decayed wall or the darkest Sovereign surfaces only.
- Keep it at 420px wide or more.
- Never retype it in a font; copy the SVG from the preview.
- Under `prefers-reduced-motion` everything holds still as NoUs L∞P, the loop whole and L and P lit.

**Engineering notes:**

- Animations change paint (`stroke-opacity`, `fill-opacity`, or the registered `--nl-fade` property), never a group's `opacity`. Chrome draws boxes around SVG groups with animated opacity.
- SVG filters use `filterUnits="userSpaceOnUse"` regions, so perfectly horizontal and vertical strokes don't vanish.

**The consumer provides** an `aria-label` if "NoUs Loop" doesn't fit.

Classes: `nl-wm`, `nl-wm-glyph`, `nl-wm-owl`, `nl-wm-ghost`, `nl-wm-fresh--l|r`, `nl-wm-paint`, `nl-wm-nozzle`, `nl-wm-g--n|o|u|s|l|p`, `nl-wm-flick`, `nl-wm-fade`, `nl-wm-loop`, `nl-wm-lobe--l|r`, `nl-wm-spark`, `nl-wm-weld`, `nl-wm-steam--loop|vent`, `nl-wm-needle`, `nl-weave-cut`, plus the spray layers.
