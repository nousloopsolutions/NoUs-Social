# Input

Mono text fields for commands, paths and arguments (from `forge-input` and `forge-textarea`).

Inputs are mono because what people type here is usually machine-shaped: repo names, programs, arguments. Focus swaps the border to `emerald`; there is no glow. Placeholders use `ink-faint`, which is below 4.5:1, so a placeholder is a hint, never the label. Put a visible label or an `aria-label` on every field.

**The consumer provides** the label, the placeholder (an example in the revolution's words, as in "which company has your data?") and validation messages, shown with an Alert below the field.

Classes: `nl-input`, `nl-textarea`. Type: `input`. Radius: `radius-control`.
