# Voice micro-module

```ncl
@NCL{v=1.0;agent=claude;tier=L1;ts=2026-11-26}
@FILE{api;voice.py;card(), check(), outcome(): the only calls agents need}
@FILE{profile;voice_profile.py;build/save/load JSON profiles in NOUS_VOICE_HOME}
@FILE{features;features.py;cadence, punctuation, casing, function words, spelling and grammar habits}
@FILE{similarity;similarity.py;draft vs profile, with named deltas}
@FILE{stylize;stylize.py;personal keeps quirks, professional cleans them}
@FILE{importers;importers.py;Gmail mbox, Google Chat and Messenger exports, owner's messages only}
@FILE{detect;detect.py;'sounds generic' signal: heuristic + optional loopback Binoculars}
@FILE{plan;../../../docs/projects/local-ai-hub/VOICE_PROFILE_PLAN.md;evidence, counter-arguments, cards VOICE-02..05}
```

Lets any agent write as Brent (or as the NoUs Loop brand) and tells Brent how close the draft is. It reports; it never rewrites a draft to beat a detector, and Brent reviews before anything is sent.

## Use

```bash
export NOUS_VOICE_HOME=~/.nous-voice            # profiles and learning log live here, never in the repo
export NOUS_VOICE_WORDLIST=/path/to/words.txt    # optional: any free word list, enables full spelling-quirk detection
export NOUS_VOICE_DETECTOR=http://127.0.0.1:8765 # optional: local Binoculars-style server

# Brent's sources (2026-11-26): Gmail, Google Chat, Facebook Messenger. Exports stay on the device;
# only messages the owner sent are read, and no raw copy is written.
python3 voice/cli.py learn brent gmail ~/Takeout/Mail/Sent.mbox --owner <your gmail address>
python3 voice/cli.py learn brent gchat "~/Takeout/Google Chat" --owner <your gmail address>
python3 voice/cli.py learn brent messenger ~/facebook-export/ --owner "<your Facebook display name>"
python3 voice/cli.py build brent text ~/exports/sent-texts/      # or any folder of .txt / .jsonl {"text","register"}
python3 voice/cli.py show brent text                                # review learned words and spelling candidates
python3 voice/cli.py approve-words brent text yeah honestly        # only approved words reach drafting cards
python3 voice/cli.py confirm-quirk brent text teh                   # only confirmed quirks are applied
python3 voice/cli.py card brent email --mode professional         # paste into the drafting agent's prompt
python3 voice/cli.py check brent text "draft here" --mode personal
python3 voice/cli.py outcome <check_id> edited --draft-file d.txt --final-file f.txt
python3 social/cli.py voice <post_id>                             # brand-voice report on a queued post
```

In Python: `import voice; voice.card("brent", "email", "professional")`, `voice.check(text, "brent", "text", "personal")`.

Registers: `text`, `email`, `social`, `chat`. Modes: `personal` (his lowercase i, dropped apostrophes, own misspellings at his own rate, no final period) and `professional` (cleaned).

## What is kept

Rates, averages, favorite words and habit lists only. Favorite words stay local until approved; spelling candidates are not applied until confirmed (or a wordlist confirms them). Quoted replies, signatures, URLs, emails and capitalized words (names) are dropped before measuring. The learning log (`learning.jsonl`) keeps scores, habit names and edit size in the THAOT gap-event v1 shape, never draft text.

## Tests

`python3 -m unittest discover -s voice/tests` (from `projects/NoUS-website`).
