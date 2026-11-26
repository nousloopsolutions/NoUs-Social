# Badge

A tiny uppercase mono label for the state of a service, key or node (from `status-badge`).

There are three signal variants plus neutral. Each signal is a hue at full strength for text, an 8% tint fill and a 35% line, so the badge still reads in greyscale through its weight and border, not colour alone. Use `ok` (emerald) when a link is cut ("Severed"), `warn` (amber, the Sentinel colour) while data is still leaking or a cut is in progress, and `err` (danger) when data is exposed to a company. The plain badge is for untouched or unknown.

**The consumer provides** one or two words. Never put a sentence in a badge.

Classes: `nl-badge`, `nl-badge--ok|warn|err`. Type: `caps`. Radius: `radius-badge`.
