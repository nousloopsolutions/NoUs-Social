# Rules for AI collaborators

This repo is the only place an AI helper on social work (for example Muse) gets access. It has no access to Nous-hub or any other NoUs Loop repo, and it should never ask for it.

## What you may do

- Draft posts in `drafts/<platform>/` and campaign ideas in `content-calendar.md`.
- Edit website copy in `website-content/` and update `SOCIAL_PROGRESS.md`.
- Run the brand check (`social-tools/social/lint.py`) on every draft before you propose it.
- Follow the brand rules in [brand/nous-loop/BRAND_IN_USE.md](brand/nous-loop/BRAND_IN_USE.md). The brand book is a guide, and the audience comes before the slogan.

## How you work

- Work on a branch and open a pull request. Never push to `main`.
- Brent approves the exact text of every post. Nothing goes live without that approval.
- Say in the pull request what you changed and why, in plain words.

## What you must not do

- Publish, schedule or send anything. The publisher and Cheshire-Herald run only with Brent's go.
- Create, sign in to or change any social account.
- Add, read or ask for passwords, tokens, keys or account details. They live in local environment variables, never in this repo.
- Put personal information in any file. This repo is **public**. No names of private people, no health, school or student details, no locations, and no customer data.
- Describe how the NoUs Loop memory or learning core works. Public text stays at the product level.
- Make medical claims. Say "helps", "supports" or "notices", never "treats", "diagnoses" or "cures".
- Change `brand/`, `social-tools/`, `automation/` or `.github/` without a request from Brent.
