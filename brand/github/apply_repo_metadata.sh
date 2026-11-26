#!/usr/bin/env bash
# Sets descriptions and topics on nousloopsolutions repos (see brand/github/README.md, section 2).
# Run where `gh` is signed in as nousloopsolutions. Safe to re-run. Changes no code and no visibility.
# @NCL{v=1.0;agent=claude;mod=github-presentation;tier=L2}
# #S{purpose="Apply plain descriptions and topics to nousloopsolutions repos"}
# #I{1="Product-level text only, no memory or learning internals";2="Never changes visibility, code or settings beyond description and topics"}
# #F{1="Remote auto mode blocks repo visibility changes; this script deliberately does not touch visibility"}
set -euo pipefail
O=nousloopsolutions
set_repo () { # repo, description, topics...
  local repo=$1 desc=$2; shift 2
  if [ "$(gh repo view "$O/$repo" --json isArchived -q .isArchived)" = "true" ]; then
    echo "skipped $repo (archived, read-only)"; return 0
  fi
  gh repo edit "$O/$repo" --description "$desc"
  local args=(); for t in "$@"; do args+=(--add-topic "$t"); done
  gh repo edit "$O/$repo" "${args[@]}"
  echo "updated $repo"
}
set_repo Nous-hub "Home base for NoUs Loop: plans, status, brand and shared tooling." nous-loop local-first privacy neurodivergent monorepo
set_repo NoUsClaWW "A local-first agent stack. Runs on your machine and works with any model." nous-loop local-first privacy autonomous-agents python
set_repo NoNu-Note "Private, local-first notes that help you remember what matters. Android." nous-loop local-first privacy neurodivergent android kotlin
set_repo NoMoji "Nousmoji: a calm, expressive face for NoUs Loop apps." nous-loop local-first typescript ui
set_repo NomojiClaWW "The NoUs Loop desktop: local coding helpers on one calm screen." nous-loop local-first tauri typescript ollama
set_repo lassy "LASSY: a local AI stack that sets itself up. Early work." nous-loop local-first self-hosted
set_repo NoUs-Social "Brand art and campaign content for NoUs Loop." nous-loop brand
set_repo open-claw-hybrid "Reference web front end for a hybrid local agent. Not maintained." nous-loop nextjs reference
set_repo openclaw-privacy "Early privacy page prototype. Not maintained." nous-loop archived-prototype
set_repo OpenClaWW "Early agent workspace prototype. Superseded by NoUsClaWW." nous-loop
set_repo BiGGBrute-RPG "First-person RPG prototype on Unreal Engine 5 with local-model NPCs." unreal-engine game-dev local-llm
set_repo nous-containers-template "Retired. Moved into Nous-hub." nous-loop
