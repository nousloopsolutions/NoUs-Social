import os, sys
os.chdir(sys.argv[1])
S = '<style>html,body{margin:0;background:var(--surface-deep)}body{padding:20px}.row{display:flex;flex-wrap:wrap;gap:var(--space-8);align-items:center}</style>\n'
C = {
"Button": ("Actions", 96, """<div class="nl-root row">
  <button class="nl-btn nl-btn--primary">Run task</button>
  <button class="nl-btn">Cancel</button>
  <button class="nl-btn nl-btn--danger">Revoke key</button>
  <button class="nl-btn" disabled>Queued</button>
  <button class="nl-btn nl-btn--icon" aria-label="Refresh">&#x21bb;</button>
</div>""", """# Button

Uppercase mono buttons for running, cancelling and confirming actions in the Sovereign desktop shell (from `forge-btn`).

**Use** `nl-btn--primary` for the one action a panel exists for: emerald tint, emerald line, emerald text, with a `glow-emerald` halo on hover. Use the default `nl-btn` for everything else. Keep `nl-btn--danger` for actions that can't be undone, and `nl-btn--icon` for single-glyph tools in panel headers.

**The consumer provides** the label: a short verb ("Run task", not "Click here to run"). It is uppercased by CSS, so write it in sentence case. Give an icon button an `aria-label`.

**States:** `:hover` raises the text to `ink` and the border to `border-strong`. `:focus-visible` draws a 2px emerald ring. `:disabled` sits at 40% opacity.

Classes: `nl-btn`, `nl-btn--primary`, `nl-btn--danger`, `nl-btn--icon`. Tokens: `surface-hover`, `border`, `radius-control`, `emerald*`, `danger*`, `glow-emerald`.
"""),
"Badge": ("Status", 72, """<div class="nl-root row">
  <span class="nl-badge nl-badge--ok">Online</span>
  <span class="nl-badge nl-badge--warn">Degraded</span>
  <span class="nl-badge nl-badge--err">Offline</span>
  <span class="nl-badge">Idle</span>
</div>""", """# Badge

A tiny uppercase mono label for the state of a service, key or node (from `status-badge`).

There are three signal variants plus neutral. Each signal is a hue at full strength for text, an 8% tint fill and a 35% line, so the badge still reads in greyscale through its weight and border, not colour alone. Use `ok` (emerald) for healthy or connected, `warn` (amber, the Sentinel colour) for degraded or in progress, and `err` (danger) for failed. The plain badge is for idle or unknown.

**The consumer provides** one or two words. Never put a sentence in a badge.

Classes: `nl-badge`, `nl-badge--ok|warn|err`. Type: `caps`. Radius: `radius-badge`.
"""),
"Input": ("Forms", 150, """<div class="nl-root" style="display:grid;gap:var(--space-10);max-width:520px">
  <input class="nl-input" placeholder="owner/repo-name" aria-label="Repository">
  <input class="nl-input" value="python" aria-label="Program">
  <textarea class="nl-textarea" placeholder="Args (one per line)" aria-label="Arguments"></textarea>
</div>""", """# Input

Mono text fields for commands, paths and arguments (from `forge-input` and `forge-textarea`).

Inputs are mono because what people type here is usually machine-shaped: repo names, programs, arguments. Focus swaps the border to `emerald`; there is no glow. Placeholders use `ink-faint`, which is below 4.5:1, so a placeholder is a hint, never the label. Put a visible label or an `aria-label` on every field.

**The consumer provides** the label, the placeholder (an example of the format, as in "owner/repo-name") and validation messages, shown with an Alert below the field.

Classes: `nl-input`, `nl-textarea`. Type: `input`. Radius: `radius-control`.
"""),
"CommandBar": ("Forms", 80, """<div class="nl-root nl-command">
  <span class="nl-command__lambda">&lambda;</span>
  <input class="nl-command__input" placeholder="Describe task (e.g. build a React web app)" aria-label="Command">
</div>""", """# CommandBar

The λ prompt along the bottom of the Sovereign window, where a person tells the system what to do (from `.lambda` and `.command-input`).

There is one per window. It is borderless and sits on `surface-sunken`, and what you type shows in emerald at the `command` size. The λ glyph is the brand's prompt mark; don't swap it for a chevron.

**The consumer provides** the placeholder, phrased as an example task, and the submit handler (Enter).

Classes: `nl-command`, `nl-command__lambda`, `nl-command__input`.
"""),
"Tabs": ("Navigation", 64, """<div class="nl-root nl-tabs" role="tablist">
  <button class="nl-tab" role="tab" aria-selected="true">Vitals</button>
  <button class="nl-tab" role="tab" aria-selected="false">Forge</button>
  <button class="nl-tab" role="tab" aria-selected="false">Tasks</button>
  <button class="nl-tab" role="tab" aria-selected="false">Settings</button>
</div>""", """# Tabs

The canvas tab bar: uppercase mono labels with an emerald underline on the active tab (from `tab-bar` and `tab-btn`).

Mark the active tab with `aria-selected="true"`. The underline overlaps the bar's bottom border by 1px. Use tabs to switch the main canvas only, never as secondary filters inside a panel.

**The consumer provides** one-word labels and the `role="tablist"` / `role="tab"` wiring.

Classes: `nl-tabs`, `nl-tab`. Type: `button` at 2px tracking.
"""),
"VitalCard": ("Data", 150, """<div class="nl-root" style="display:grid;grid-template-columns:repeat(3,1fr);gap:var(--space-16)">
  <div class="nl-vital"><span class="nl-vital__label">CPU load</span><span class="nl-vital__value">42%</span><span class="nl-vital__sub">8 cores</span><div class="nl-vital__bar"><div class="nl-vital__fill" style="width:42%"></div></div></div>
  <div class="nl-vital"><span class="nl-vital__label">Memory</span><span class="nl-vital__value">78%</span><span class="nl-vital__sub">25 of 32 GB</span><div class="nl-vital__bar"><div class="nl-vital__fill nl-vital__fill--warn" style="width:78%"></div></div></div>
  <div class="nl-vital"><span class="nl-vital__label">GPU temp</span><span class="nl-vital__value">91&deg;C</span><span class="nl-vital__sub">Throttling</span><div class="nl-vital__bar"><div class="nl-vital__fill nl-vital__fill--err" style="width:91%"></div></div></div>
</div>""", """# VitalCard

A metric tile showing one measured value, with a caps label, a big number, a sub-line and an optional bar (from `vital-card`).

Lay them out in an auto-fill grid (`minmax(180px, 1fr)`, gap `space-16`). The bar's fill uses emerald when healthy, amber past the warning threshold and danger past the limit. Say the state in the sub-line too, so colour is never the only signal.

**The consumer provides** the label, the value with its unit, the sub-line, the fill width and the threshold class.

Classes: `nl-vital`, `__label`, `__value`, `__sub`, `__bar`, `__fill(--warn|--err)`. Type: `caps`, `metric`, `small`.
"""),
"StreamLog": ("Data", 170, """<div class="nl-root nl-stream">
  <div class="nl-stream__head">Intel rail</div>
  <p class="nl-stream__msg nl-stream__msg--user">summarise today's tasks</p>
  <p class="nl-stream__msg nl-stream__msg--assistant">3 open, 1 blocked on review.</p>
  <p class="nl-stream__msg nl-stream__msg--system">neural load high: pausing background indexing</p>
</div>""", """# StreamLog

The conversation and event stream in the intel rail, colour-coded by speaker (from `stream-msg`).

Speakers: **user** in emerald, **assistant** in `ink`, **system** in amber (the Sentinel speaking). Each message has a 2px `border` rule on the left, which is the only left-rule pattern in the system; don't reuse it for cards. The header is a `rail-label`.

**The consumer provides** the messages and their speaker, and scrolling (the rail's content is `flex: 1; overflow-y: auto`).

Classes: `nl-stream`, `__head`, `__msg(--user|--assistant|--system)`.
"""),
"Alert": ("Status", 150, """<div class="nl-root" style="display:grid;gap:var(--space-10)">
  <div class="nl-alert nl-alert--err" role="alert">Gateway unreachable. Retrying in 30 s.</div>
  <div class="nl-alert nl-alert--warn">Running on battery: heavy models are paused.</div>
  <div class="nl-alert nl-alert--ok">All keys healthy.</div>
  <div class="nl-alert">No sensory roots configured yet.</div>
</div>""", """# Alert

An inline message box at the top of a panel, saying what happened and what happens next (from `panel-error`, generalised to all signals).

Write it in plain language: what happened, then what the system is doing about it. No exclamation marks and no blame ("No one is mean"). Give errors `role="alert"`.

**The consumer provides** the sentence and, if needed, a Button placed after it.

Classes: `nl-alert`, `nl-alert--err|warn|ok`. Radius: `radius-md`.
"""),
"StatusDot": ("Status", 60, """<div class="nl-root row" style="gap:var(--space-24);font:400 12px/16px var(--font-mono);color:var(--ink-dim)">
  <span><span class="nl-dot nl-dot--on"></span>&nbsp; connected</span>
  <span><span class="nl-dot nl-dot--warn"></span>&nbsp; reconnecting</span>
  <span><span class="nl-dot nl-dot--err"></span>&nbsp; error</span>
  <span><span class="nl-dot"></span>&nbsp; offline</span>
</div>""", """# StatusDot

A 7px dot for live connection state, placed beside a name or header (from `ws-dot`).

`nl-dot--on` glows (`glow-dot`) and pulses every 2s. That is the "life-sign" animation, and it stops under `prefers-reduced-motion`. Always put a word next to the dot: the dot alone is not accessible.

**The consumer provides** the adjacent text label.

Classes: `nl-dot`, `nl-dot--on|warn|err`. Radius: `radius-full`.
"""),
}
for name, (group, h, body, readme) in C.items():
    os.makedirs(name, exist_ok=True)
    with open(f"{name}/preview.html", "w", encoding="utf-8", newline="\n") as f:
        f.write(f'<!-- @dsCard group="{group}" height={h} -->\n<!doctype html>\n<html><head><meta charset="utf-8">{S}</head>\n<body>\n{body}\n</body></html>\n')
    with open(f"{name}/README.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(readme)
print(sorted(os.listdir('.')))
