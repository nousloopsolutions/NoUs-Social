# VitalCard

A metric tile showing one measured value, with a caps label, a big number, a sub-line and an optional bar (from `vital-card`).

Lay them out in an auto-fill grid (`minmax(180px, 1fr)`, gap `space-16`). The bar's fill uses emerald when healthy, amber past the warning threshold and danger past the limit. Say the state in the sub-line too, so colour is never the only signal.

**The consumer provides** the label, the value with its unit, the sub-line, the fill width and the threshold class.

Classes: `nl-vital`, `__label`, `__value`, `__sub`, `__bar`, `__fill(--warn|--err)`. Type: `caps`, `metric`, `small`.
