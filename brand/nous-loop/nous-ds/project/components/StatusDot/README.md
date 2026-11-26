# StatusDot

A 7px dot for live connection state, placed beside a name or header (from `ws-dot`).

`nl-dot--on` glows (`glow-dot`) and pulses every 2s. That is the "life-sign" animation, and it stops under `prefers-reduced-motion`. Always put a word next to the dot: the dot alone is not accessible.

**The consumer provides** the adjacent text label.

Classes: `nl-dot`, `nl-dot--on|warn|err`. Radius: `radius-full`.
