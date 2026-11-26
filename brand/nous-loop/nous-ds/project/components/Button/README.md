# Button

Uppercase mono buttons for running, cancelling and confirming actions in the Sovereign desktop shell (from `forge-btn`).

**Use** `nl-btn--primary` for the one action a panel exists for: emerald tint, emerald line, emerald text, with a `glow-emerald` halo on hover. Use the default `nl-btn` for everything else. Keep `nl-btn--danger` for actions that can't be undone, and `nl-btn--icon` for single-glyph tools in panel headers.

**The consumer provides** the label: a short verb ("Sever", "Wipe their copy", not "Click here to continue"). It is uppercased by CSS, so write it in sentence case. Give an icon button an `aria-label`.

**States:** `:hover` raises the text to `ink` and the border to `border-strong`. `:focus-visible` draws a 2px emerald ring. `:disabled` sits at 40% opacity.

Classes: `nl-btn`, `nl-btn--primary`, `nl-btn--danger`, `nl-btn--icon`. Tokens: `surface-hover`, `border`, `radius-control`, `emerald*`, `danger*`, `glow-emerald`.
