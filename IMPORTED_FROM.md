# Imported from Nous-hub

On 2026-11-26 these folders were copied from `nousloopsolutions/nous-hub` at commit `01552034b45c` (branch `alpha`), so social work can happen here without access to the main hub. The originals in Nous-hub were not changed or removed. When the two differ, Nous-hub is the source until Brent decides otherwise.

| Here | Source in Nous-hub |
| --- | --- |
| `brand/github/` | `brand/github/` |
| `brand/nous-loop/` | `brand/nous-loop/` |
| `social-tools/social/` | `projects/NoUS-website/social/` |
| `social-tools/voice/` | `projects/NoUS-website/voice/` (tests left out, see below) |
| `social-tools/brand-rules.json` | `projects/NoUS-website/brand-rules.json` |
| `automation/cheshire-herald/` | `cloudflare/workers/cheshire-herald/` (without `package-lock.json`) |
| `automation/cheshire-herald/docs/` | `docs/plans/2026-05-29-cheshire-herald-cloudflare.md` |
| `automation/cheshire-herald/herald_client.py` | `scripts/herald_client.py` |
| `assets/manifesto/observer-hero.png` | `content/manifesto/observer-hero.png` |

## Left out on purpose

- `projects/NoUS-website/voice/tests/test_voice.py`: its fixtures include a named person and a health detail. They are probably synthetic, but this repo is public, so the file stays in Nous-hub until Brent confirms it is safe.

## Paths that may need fixing

Some copied docs link to Nous-hub paths (for example the Cheshire-Herald README links to `docs/plans/`). Those links point to the old layout.
