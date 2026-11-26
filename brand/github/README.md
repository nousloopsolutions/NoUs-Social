# GitHub presentation

```ncl
@NCL{v=1.0;agent=claude;tier=L1}
@FILE{github-presentation;brand/github/README.md;how the nousloopsolutions GitHub presents NoUs Loop}
@SOURCE{brand;brand/nous-loop/BRAND_IN_USE.md}
```

This page is the plan for making the nousloopsolutions GitHub look like what it is: a small, serious product company. It follows the [brand-in-use guide](../nous-loop/BRAND_IN_USE.md).

Public text stays at the product level. It never describes how the memory or learning core works until the provisional patent is filed. Claims stay wellness-only.

## 1. Profile

[`PROFILE_README.md`](PROFILE_README.md) is the profile page. GitHub shows it when it is the README of a public repo named `nousloopsolutions/nousloopsolutions`. That repo also holds `profile.png` (the banner, from `social/`).

## 2. Descriptions and topics

[`apply_repo_metadata.sh`](apply_repo_metadata.sh) sets these with the GitHub CLI. Run it from a machine where `gh` is signed in as nousloopsolutions.

| Repo | Visibility | Description | Topics |
| --- | --- | --- | --- |
| Nous-hub | private | Home base for NoUs Loop: plans, status, brand and shared tooling. | nous-loop, local-first, privacy, neurodivergent, monorepo |
| NoUsClaWW | private (from 2026-11-26) | A local-first agent stack. Runs on your machine and works with any model. | nous-loop, local-first, privacy, autonomous-agents, python |
| NoNu-Note | private | Private, local-first notes that help you remember what matters. Android. | nous-loop, local-first, privacy, neurodivergent, android, kotlin |
| NoMoji | private | Nousmoji: a calm, expressive face for NoUs Loop apps. | nous-loop, local-first, typescript, ui |
| NomojiClaWW | private | The NoUs Loop desktop: local coding helpers on one calm screen. | nous-loop, local-first, tauri, typescript, ollama |
| lassy | public | LASSY: a local AI stack that sets itself up. Early work. | nous-loop, local-first, self-hosted |
| NoUs-Social | public | Brand art and campaign content for NoUs Loop. | nous-loop, brand |
| open-claw-hybrid | public | Reference web front end for a hybrid local agent. Not maintained. | nous-loop, nextjs, reference |
| openclaw-privacy | public | Early privacy page prototype. Not maintained. | nous-loop, archived-prototype |
| OpenClaWW | private | Early agent workspace prototype. Superseded by NoUsClaWW. | nous-loop |
| BiGGBrute-RPG | private | First-person RPG prototype on Unreal Engine 5 with local-model NPCs. | unreal-engine, game-dev, local-llm |
| nous-containers-template | private | Retired. Moved into Nous-hub. | nous-loop |

## 3. Social previews and pins

GitHub has no API for these, so they are set by hand in each repo's **Settings → General → Social preview**. The images are in [`social/`](social/), 1280 × 640, made by [`gen_social_previews.mjs`](gen_social_previews.mjs) from the brand exports.

Previews exist for the profile and the seven repos that are active or public. The other five (open-claw-hybrid, openclaw-privacy, OpenClaWW, BiGGBrute-RPG and nous-containers-template) are retired, archived or private prototypes, and they don't get one unless they become active again.

Pinned (profile → Customize your pins), in order: NoUsClaWW (once public again), lassy, NoUs-Social. Pin only repos that have a real README.

## 4. One README layout

Every repo README follows this order. Keep it short; link to docs for depth.

1. Banner image (the repo's social preview) and one sentence: what it is, for whom.
2. **Status:** one of `active`, `early`, `maintenance` or `archived`, and one line on what works today.
3. **What it does:** three to five plain bullets. No internals.
4. **Run it:** requirements, install, first command.
5. **Privacy:** what stays on the device and what, if anything, leaves.
6. **Contributing** (link to CONTRIBUTING) and **Security** (link to SECURITY).
7. **License.**

No badge walls (at most CI, license, language), no emoji headings, no "powered by AI" filler, no placeholder badges.

## 5. Commits and pull requests

- Titles: plain imperative sentence case, about 70 characters, no emoji. Example: "Add sensor-range recall to the memory index". An optional scope prefix is fine: "gateway: fix batch replay".
- Bodies: what changed and why, how it was checked, and a rollback note for risky changes.
- Agent attribution goes in trailers (`Co-Authored-By:`), not in the title. No "AI generated" banners in the body.
- One purpose per PR. Drafts that sit for 30 days get closed with a note or folded into a newer PR.
- The PR template is [`.github/pull_request_template.md`](../../.github/pull_request_template.md).

## 6. Needs Brent's OK

**Archive (read-only, reversible):** nous-containers-template, openclaw-privacy, OpenClaWW.

**Make private:** NoUs-Social holds campaign drafts and duplicate files ("- Copy (2).png"). Clean it up or make it private before it is pinned.

**Stale pull requests:** 29 Nous-hub PRs opened before 2026-11-01 are still open. Four of them are still named as needed work in the plan, roadmap, task queue or STATUS files, so they stay open: #574, #600, #601 and #619. Proposal for the other 25: close each one with a note saying it is superseded by the plan of record (PR 662) and its history stays in the hub log. A closed PR can be reopened.

| PR | Opened | Title |
| --- | --- | --- |
| #630 | 2026-10-28 | Add canonical Windows document entry and controlled chunk export |
| #629 | 2026-10-21 | Archive: bounded acquisition, Golden source provenance and optional gateway |
| #628 | 2026-10-21 | Protected manifest: require Golden assessment and recover exact corpus references |
| #627 | 2026-10-21 | Golden Memory: fail-closed declared-inventory completeness gate |
| #626 | 2026-10-21 | MVP: actual read-only reconciliation and recovered archive source |
| #625 | 2026-10-21 | RAD: newest-first discovery, retained transcripts and fresh board comparison |
| #624 | 2026-10-21 | docs: unify onboarding, memory definitions and Windows evidence |
| #623 | 2026-10-21 | Plan MVP-first R&D and daily department broker reports |
| #620 | 2026-10-21 | ops: verified private index containment and source-bound recovery status |
| #617 | 2026-10-18 | feat: context continuity alpha local retrieval and provenance tests |
| #609 | 2026-10-18 | docs: cognitive symbiosis vision and memory audit for ROADMAP-AUTO-001 |
| #607 | 2026-10-18 | feat: restricted permanent Windows test lab runner — installation blocked pending review |
| #606 | 2026-10-18 | fix: restore offline-tested MVP board adapter with strict project identity |
| #605 | 2026-10-17 | ops: pilot Langfuse with isolated synthetic traces and regression scores |
| #604 | 2026-10-17 | test: source-bound indexing regression and Windows archive restore evidence |
| #602 | 2026-10-17 | docs: reconcile shared resources and Windows MVP progress |
| #599 | 2026-10-17 | Repair phase helper into a local-only fail-closed draft |
| #598 | 2026-10-16 | Preserve PR555 design proposals without activating authority |
| #597 | 2026-10-16 | Reconcile PR589 workflow controls with current alpha |
| #596 | 2026-10-16 | Fix website static export and explicit Wrangler assets config |
| #595 | 2026-10-16 | Port inactive replay-safe dispatcher with local verification |
| #594 | 2026-10-16 | Preserve librarian references with explicit historical classification |
| #593 | 2026-10-16 | Add bounded local agent skills and root test discovery |
| #592 | 2026-10-16 | Preserve historical module evidence without current-pass claims |
| #591 | 2026-10-15 | Consolidate MVP sources and define the PC-first Severance plan |

## 7. Stale PRs that stay open

| PR | Why |
| --- | --- |
| #574 | Named in `docs/projects/mvp/STATUS.md` |
| #600 | Foundation prerequisite in README start line S3, the local-ai-hub ROADMAP and the Hermes task queue |
| #601 | Named in the local-ai-hub ROADMAP, STATUS and task queue |
| #619 | Named in the local-ai-hub ROADMAP, STATUS and task queue |
