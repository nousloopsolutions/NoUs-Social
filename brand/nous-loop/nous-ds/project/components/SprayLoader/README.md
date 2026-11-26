# SprayLoader

The loading indicator ("severing…"): a spray nozzle tags the NoUs loop (a long figure 8 on its side) over and over.

**How it moves:** each 2.8s cycle has three phases.

1. A nozzle with a mist cloud travels the sideways 8, starting from the crossing. The paint lays down behind it: soft overspray plus a thick, grainy neon stroke (0–70%).
2. The fresh loop holds and glows (70–88%).
3. It fades out, and the nozzle starts again.

A faint ghost of old paint and a pulsing black halo stay under the loop. The colour drifts from `neon-cyan` to `neon-blue` to `nousloop-teal` (`nl-live`). Under `prefers-reduced-motion` the loop stays painted and only pulses its opacity.

**Sizes:**

- `nl-spray--lg` (300px) for full-screen loading on the wall.
- The default (120px) for panels and empty states.
- `nl-spray--sm` (34px) for inline "severing…" beside text, with no nozzle.

**The consumer provides** the accessible text: `role="status"` with `aria-label="Severing"`, or a visible word beside the small size: always "severing…", never "loading" or "thinking". Use it on dark grounds only; the neon washes out on Clinical light.

Copy the SVG from the preview. The loop path is a lemniscate with a slight hand wobble, so keep it as is.

Classes: `nl-spray`, `nl-spray--sm|lg`, `__ghost`, `__over`, `__paint`, `__head`, `__mist`, `__nozzle`, plus `nl-spray-shadow`, `nl-live`.
