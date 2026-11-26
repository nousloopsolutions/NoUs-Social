# StreamLog

The conversation and event stream in the intel rail, colour-coded by speaker (from `stream-msg`).

Speakers: **user** in emerald, **assistant** in `ink`, **system** in amber (the Sentinel speaking). Each message has a 2px `border` rule on the left, which is the only left-rule pattern in the system; don't reuse it for cards. The header is a `rail-label`.

**The consumer provides** the messages and their speaker, and scrolling (the rail's content is `flex: 1; overflow-y: auto`).

Classes: `nl-stream`, `__head`, `__msg(--user|--assistant|--system)`.
