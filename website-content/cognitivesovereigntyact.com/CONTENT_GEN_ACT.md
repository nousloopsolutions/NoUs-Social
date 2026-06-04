# Generative Assembly Line — cognitivesovereigntyact.com (The Law)

Use these specs to generate the CARB S-Rating hero and the Act landing UI.

---

## 1. CARB S-Rating hero graphic (Nano Banana / image gen)

**Purpose:** Hero asset for the Act landing; legislative/authoritative, suitable for MN State Legislature and public advocates.

**Spec:**
- **Content:** A single, bold **“S”** inside a shield or seal, with a subtle “SEVERANCE” or “CARB” label below.
- **Style:** Official, governmental—high contrast, serif or clean sans. Think state seal / legislative letterhead, not corporate.
- **Colors:** Dark navy or slate background (#0f172a or #1e3a5f); the “S” and border in amber/gold (#f59e0b / #fbbf24) for the Sentinel/CARB S motif. Optional thin rule or wreath in the same gold.
- **Format:** SVG preferred (scalable for print and web); PNG at 2x (e.g. 512×512 or 1024×1024) for fallback.
- **Usage:** Hero above the fold on the Act landing; also for presentations and print one-pagers.
- **No:** Chatbots, casual or playful tone, non-sovereign branding.

**Nano Banana / image prompt (adapt to your tool):**
> Legislative seal style: shield or round seal with a single bold letter “S” in the center, gold/amber (#f59e0b) on dark navy (#0f172a). Small “SEVERANCE” or “CARB” text below. Clean, authoritative, minimal. No people, no icons. Vector-style, high contrast. Suitable for Minnesota State Legislature letterhead.

**Where it lives:**  
- Repo: `assets/carb-icons/` (we already have `carb-S.svg`; this hero can be a larger, hero-specific variant).  
- R2: `the-act/assets/hero-carb-s.svg` (or equivalent) so the Act page can reference it.

---

## 2. v0.app prompt — Act landing page UI

Paste the block below into [v0.dev](https://v0.dev) (or similar) to generate the React/UI for the Act’s landing page. Then port the structure and styling to static HTML/CSS for `content/cognitivesovereigntyact.com/index.html` (or keep as a component if you use a stack that supports it).

**v0.app prompt:**

```
Design a single-page, governmental-style landing page for "The Cognitive Sovereignty Act" — an official legislative portal for a US state bill. Audience: state legislators and public advocates.

Requirements:
- Hero section: large, clear title "The Cognitive Sovereignty Act" and a one-line tagline (e.g. "Official legislative text, whitepapers, and lobbyist resources"). Leave a prominent placeholder (rectangle or dashed area) for a CARB S-Rating seal/hero graphic (shield with "S", gold on dark).
- Typography: high-contrast, readable. Prefer serif for headings (e.g. Georgia, "Times New Roman") and clear hierarchy (H1, H2, H3). Sections: "Section 1: Definitions", "Section 2: Findings and purpose", "Section 3: Rights and standards", plus a short "Whitepapers and resources" block.
- Style: clean, document-like. Light background (#f8fafc), dark text (#0f172a). Accent color for links and key elements: blue (#1e40af) or amber (#f59e0b). No cards or heavy shadows; keep it formal.
- Footer: space for the CARB S-Rating badge (small seal + "CARB Severance Level: S") and a line like "Cognitive Sovereignty Act · Legislative Portal".
- Accessibility: semantic HTML (header, main, sections, footer), sufficient contrast, no decorative-only images without alt text.
- No chatbots, no chat widgets, no casual copy. Tone: official, sovereign, legislative.
```

**After generation:**  
- Export or copy the component structure and styles.  
- Map to our existing `content/cognitivesovereigntyact.com/index.html` and `style.css` (or replace with the generated layout).  
- Ensure `<meta name="carb-severance-level" content="S">` stays in `<head>` and the hero/footer use the CARB S asset from R2 or `/assets/`.

---

## 3. R2 sync after new assets

When the hero graphic and any new assets are ready:

```bash
npm run r2:sync
```

Add to `scripts/r2-sync.js` SYNC_MAP if you put the hero in a path not already synced (e.g. `content/cognitivesovereigntyact.com/assets/` → `the-act/assets/`).

---

*Fortress locked. Content assembly line ready.*
