# Owl

The NoUs mascot: the owl of Athena, rebuilt as a machine that holds all the knowledge, perched on the crossing of the loop.

**Why this owl:** the little owl (*Athene noctua*) was Athena's bird. Athena is the goddess of wisdom and strategic war, and NoUs is the mind (*nous*) fighting back. Ours is a machine because the knowledge corporations hoarded now lives in it, and it is on our side.

**Anatomy:**

- **Shape:** a round, riveted head shell with no ear tufts (true to the little owl), and stern angular brow plates in a V.
- **Eyes: the ∞.** The two eye sockets are one infinity loop: each lobe is an eye, with the crossing as the bridge between them, like the ring of an owl's facial disc. A lens with aperture blades and a glowing pupil sits in each lobe. The loop is how it sees.
- **Chest:** a clockwork gear heart, with one trace running down from it.
- **Joints:** neon sprockets at both shoulders and at the neck, the visible machinery that drives the wings and head.
- **Wings and tail:** plated feathers and tail blades.
- **Knowledge:** a crown of three data traces ending in lit nodes.
- **Talons:** steel talons gripping the ∞.

**Expressions: it is a machine, so it changes mechanically.** The whole owl stays a see-through neon outline. Every part is jointed on its own pivot and moves with a slight mechanical overshoot (0.7s): the brow plates pivot on their rivets, the lens apertures open and shut, the head turns on its neck, and the wings swing on neon sprockets at the shoulders. The sprockets turn whenever the part they drive moves. Set one class on the `<svg>`:

| Class | Expression | What moves |
| --- | --- | --- |
| `nl-owl--watch` | **watching** (default) | Steady stare, gear heart turning slowly (18s), knowledge nodes breathing. |
| `nl-owl--think` | **severing** | Head cocks on the neck sprocket, brows press down, apertures focus to pinpoints, gear heart races (2.4s), knowledge chases through the crown. Use while NoUs is working. |
| `nl-owl--alert` | **alert** | Brow plates slam down, eyes open wide and burn `neon-red`, head rises, wings flare out on the shoulder sprockets, crown fully lit. Use when data is exposed or a tracker is caught. |
| `nl-owl--calm` | **calm** | Brows level out, lenses half-shutter, head tilts, wings tuck, gear barely turns (40s), crown dims. Use when a link is severed and you are safe. |

Swap classes to change expression; the transition is the animation. Under `prefers-reduced-motion` the parts snap to the new pose with no motion, and the gear and glow stop.

**Rubber-hose gait:** the whole owl squashes and stretches to its own beat, and the gait changes with the expression: it bobs while watching, jitters while severing, hops while alert, and sways when calm.

**Style:** the same thick, grainy neon spray as the Wordmark, with the pulsing dark halo and the live colour drift (`nl-live`). It is never cute, never cartoonish, never sparkly. It is the wise, watchful machine of the revolution.

**Rules:**

- Always on the decayed wall or the darkest surfaces, perched on the loop.
- Keep it at 200px tall or more; below that, use the loop alone.
- Don't add eyelashes, smiles, sparkles or speech bubbles.
- Under `prefers-reduced-motion` the gear stops and the eyes hold steady.

**The consumer provides** an `aria-label` if the default doesn't fit. Copy the SVG from the preview.

Classes: `nl-owl` plus one of `nl-owl--watch|think|alert|calm`. The parts are `nl-owl-head`, `nl-owl-brow--l|r`, `nl-owl-eye--l|r`, `nl-owl-aperture`, `nl-owl-pupil`, `nl-owl-crown`, `nl-owl-node`, `nl-owl-wing--l|r`, `nl-owl-sprocket--l|r|neck`, `nl-owl-heart` and `nl-owl-rivet`, plus the spray layers and `nl-live`.
