# NoUs Loop: brand in use

```ncl
@NCL{v=1.0;agent=claude;tier=L1}
@FILE{brand-in-use;brand/nous-loop/BRAND_IN_USE.md;one-page rules for applying the brand}
@SOURCE{brand book;brand/nous-loop/nous-ds/project/README.md;PR 665}
```

This is the short version of the [brand book](nous-ds/project/README.md). Use it when you touch anything people will see: a README, a repo description, a setup page, an app screen, a plan or status page. It is a **guide**, not a hard rule (Brent, 2026-11-26). When the brand book and this page disagree, the brand book wins.

## 1. What we say

- **The promise:** your data stays with you. We never sell your data. Local first, nothing leaves without you.
- **Primary tag:** `safety through severance/` (lowercase, the slash stays: it is the cut).
- **What the product does, in one line:** "Calm, private tools that help a neurodivergent mind get through the day. They run on your own device."
- **Claims stay wellness-only.** Say "helps you", "supports", "notices". Never "treats", "diagnoses", "cures", "clinical" or "medical", until the medical stage (FDA, HIPAA, clinical validation) is done.
- **Product level only.** Public text names products and the promise. It never describes how the memory or learning core works inside. That stays private until the patent filing.

## 2. Two voices, never mixed in one sentence

| The wall (posters, covers, banners) | The product (apps, setup, status, docs) |
| --- | --- |
| Short, lowercase, defiant: three to six words | Plain, calm, sentence case |
| Imperative: "give them nothing/" | Says what happened, then what happens next |
| Names the enemy (big tech, data brokers), never a person | No exclamation marks, no blame, no urgency tricks |
| `tag` font (Sedgwick Ave), 22px and up | Inter for text, JetBrains Mono for labels and buttons |

Product labels are uppercase mono with wide tracking: `DATA HELD LOCALLY`, `SEVERANCE LOG`.

**Placeholder words speak the cause too:**

| Instead of | Write |
| --- | --- |
| Loading… | severing… |
| Submit / Run | Sever |
| Cancel | Not yet |
| Connected / Offline | Severed / Dark |
| No items yet | Nothing to sever yet. Add the first company that has your data. |

Where a calm, literal label is kinder (a school or a first-run screen), plain words win. The audience comes before the slogan.

## 3. The name

| Do | Don't |
| --- | --- |
| **NoUs L∞P** (the mark, as an image) | NOUS LOOP, nousloop, Nous loop |
| **NoUs Loop** (plain text) | No-Us, NoUS |

Product names keep their own spelling (Nousmoji, Hermes, Wonderland) and sit under the NoUs Loop name: "Nousmoji, by NoUs Loop".

## 4. Colors

Two layers share one backbone. Pick the layer by the surface.

**Street (brand wall: banners, covers, social previews, wallpapers).** Blue on black.

| Token | Hex | Use |
| --- | --- | --- |
| `brick` | `#0d0d0e` | ground |
| `neon-cyan` | `#60f0f0` | the ∞ and the NoUs tag, main text on brick (15:1) |
| `neon-blue` | `#4d8dff` | second blue (6.3:1) |
| `nousloop-teal` | `#28efd0` | glow accents only |
| `neon-red` | `#e45c5c` | the cut only: a slash, an X, a strike-through |

**Sovereign (product: desktop, dashboards, setup pages).** A dark HUD.

| Token | Hex | Meaning |
| --- | --- | --- |
| `surface-deep` / `surface-mid` | `#05070a` / `#0d1117` | grounds |
| `border` | `#1e293b` | the one hairline |
| `ink` / `ink-dim` | `#f8fafc` / `#94a3b8` | readable text |
| `emerald` | `#10b981` | life: OK, connected, primary action, the user's voice |
| `amber` | `#f59e0b` | the Sentinel: warnings, in progress, system voice |
| `cyan` | `#22d3ee` | the senses: mic and vision activity |
| `danger` | `#f87171` | failure |

**Clinical (light: documents, onboarding, school material)** uses white and `#f7fafc` with `#1a202c` text. The logo lockup sits on `paper` `#fbf7f5` with `wordmark-ink` `#13252f`, `loop-blue` `#2589d3` (the machine) and `loop-yellow` `#fdd822` (the human).

Rules: `ink-faint` fails contrast, so use it only for placeholders. `loop-blue` and `loop-yellow` are fills, never text on light grounds. State is never color alone: every badge carries a word.

Full values: [`tokens.json`](nous-ds/project/tokens.json). Ready-made classes: [`components/bundle.css`](nous-ds/project/components/bundle.css) (prefix `nl-`).

## 5. Logo and mascot

Use the files in [`exports/`](exports/README.md). Never retype or redraw the mark.

| Surface | File |
| --- | --- |
| README and wiki banner | `nous-loop-wordmark-wall.svg` (animated) or `-wall-still.svg` |
| Print, merch, social preview source | `nous-loop-wordmark-still.svg`, `nous-loop-wordmark-wall-still.svg` |
| App icons, favicons, server cards (16 to 64px) | `nous-ds/project/assets/Logos/nous-loop-mark.svg`, the infinity-loop mark |
| Large avatars and org picture (128px and up) | `nous-loop-emblem-avatar.svg` or `nous-loop-owl-wall.svg` |
| Loading state | `nous-loop-severing-loader.svg` with the word "severing…" |
| Status states | owl `watching` (idle), `severing` (working), `alert` (data exposed), `calm` (safe) |

- Clear space around any ∞ equals one lobe's height.
- Never outline, rotate, stretch or recolor the ∞ outside the palette.
- The neon marks are for dark grounds. On light grounds use the lockup.
- The owl is Athena's owl, a machine. It is never cute and never a cartoon.
- Under `prefers-reduced-motion`, motion stops or calms to a slow fade. The exported SVGs already do this: the marks hold still, and the severing loader keeps only a gentle 2.8s opacity pulse so it still shows that work is happening.

## 6. Do and don't

| Do | Don't |
| --- | --- |
| Lead with the promise: your data stays with you | Lead with features or the tech inside |
| Say "we never sell your data", and mean it in the product | Add tracking, telemetry or a cloud default "just for now" |
| Keep screens calm: one next action, plain words | Use countdowns, red badges for urgency, or dark patterns |
| Use the real exports and tokens | Pick a close-enough blue, or redraw the loop |
| Keep claims wellness-only | Say treat, diagnose, cure, clinical or medical |
| Use fictional, generic corporate slogans on the wall | Name or mock a real company, its logo or its slogan |
| Keep it private until Brent says go | Publish a public page, site or post without Brent's OK |

## 7. Where the brand goes next

The first batch, in order of how much each one makes the work feel real:

| # | Surface | Change | Status |
| --- | --- | --- | --- |
| 1 | Nous-hub README | Wordmark banner, tag, promise line | this PR |
| 2 | This guide | One page every agent loads before visible work | this PR |
| 3 | Wonderland standing order | "Standing Order: Nous Brand" entity carries these rules | done in Wonderland |
| 4 | Wonderland `/setup` page and server card | Sovereign tokens, owl status states, product voice | coordinate with the cloud Claude enrollment thread (icon work is there) |
| 5 | Repo descriptions and social previews | One-line description per repo, wall banner preview image | needs Brent: changing public repo text is public, and previews are set in GitHub settings |
| 6 | Nousmoji (NoMoji) face | Map the 10 affects to Sovereign colors (emerald life, amber Sentinel, cyan senses) | work order, NoMoji repo |
| 7 | NomojiClaWW desktop grid | `nl-` components, VitalCard per worker, owl status per worker | work order, NomojiClaWW repo |
| 8 | NoNu-Note owl | Align the Noetic Owl with Athena's owl and its four states | work order, after the privacy audit |
| 9 | Plan and status pages | Sovereign or Clinical theme, wordmark header, product voice | next PR |

Draft repo descriptions (for Brent to approve, not yet applied):

- **Nous-hub:** "The home base for NoUs Loop: plans, status and the brand. Your data stays with you."
- **NoMoji:** "Nousmoji, by NoUs Loop: a calm face that shows how your day is going. Runs on your device."
- **NomojiClaWW:** "The NoUs Loop desktop: your local helpers on one calm screen. Nothing leaves without you."
- **NoNu-Note:** "NoNu-Note, by NoUs Loop: a private notebook with an owl that helps you think. Local first."
