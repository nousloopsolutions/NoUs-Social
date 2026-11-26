# @NCL{v=1.0;agent=claude;mod=voice-features;tier=L2}
# #S{purpose="Turn text into style measurements: cadence, punctuation, casing, word habits, spelling and grammar quirks"}
# #I{1="Pure functions, Python stdlib only";2="Measures how someone writes, never stores what they wrote: callers keep only aggregates"}
# #F{1="Use an embedding model for style"→"Embeddings mix topic with style; function words and character n-grams are the proven stylometry signal (Burrows 2002, Stamatatos 2009)"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib";next="add part-of-speech n-grams once a local tagger is chosen"}
# #T{status="python3 -m unittest discover -s voice/tests"}
# #X{2026-11-26="Created for the voice profile micro-module"}
"""Style features for one text or many texts. Every number here is a rate or an average, so a
profile built from them holds habits, not content."""
from __future__ import annotations

import re
import statistics
from collections import Counter

# Function words: the classic authorship signal (Mosteller and Wallace 1964; Burrows 2002).
# Topic-free, so they say how someone writes without saying what about.
FUNCTION_WORDS = (
    "a about after all also am an and any are as at be because been but by can could did do does "
    "for from had has have he her him his how i if in into is it its just like me more my no not "
    "now of on one or our out over really so some than that the their them then there they this "
    "to too up us very was we well were what when which who will with would you your yeah ok okay "
    "lol gonna wanna got get thing things actually maybe pretty kinda sure"
).split()

# Contractions people often type without the apostrophe. Seen in samples = a habit, not an error.
NO_APOSTROPHE = {
    "dont": "don't", "cant": "can't", "wont": "won't", "im": "I'm", "ive": "I've", "didnt": "didn't",
    "doesnt": "doesn't", "isnt": "isn't", "thats": "that's", "youre": "you're", "theyre": "they're",
    "wasnt": "wasn't", "couldnt": "couldn't", "wouldnt": "wouldn't", "shouldnt": "shouldn't",
    "havent": "haven't", "whats": "what's", "lets": "let's", "ill": "I'll", "id": "I'd",
}
# "ill", "id", "lets" are real words too; they count only as weak evidence (not used for quirks).
AMBIGUOUS_NO_APOSTROPHE = {"ill", "id", "lets"}

_WORD = re.compile(r"[A-Za-z][A-Za-z'’]*")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
_URL = re.compile(r"https?://\S+|www\.\S+")
_EMAIL = re.compile(r"\S+@\S+\.\S+")


def clean_sample(text: str) -> str:
    """Drop quoted reply lines, signatures, URLs and email addresses before measuring."""
    keep = []
    for line in (text or "").splitlines():
        if line.strip() in ("--", "-- "):
            break  # signature block
        if line.lstrip().startswith(">"):
            continue
        if re.match(r"^On .+ wrote:$", line.strip()) or re.match(r"^-{2,}\s*(Original|Forwarded) [Mm]essage", line.strip()):
            break  # quoted reply or forward below: someone else's words
        if keep and re.match(r"^(From|Sent|To|Subject): ", line.strip()) and any(k.strip() for k in keep):
            break  # Outlook-style quoted header block
        keep.append(line)
    out = "\n".join(keep)
    return _EMAIL.sub(" ", _URL.sub(" ", out)).strip()


def words(text: str) -> list[str]:
    return [w.replace("’", "'") for w in _WORD.findall(text)]


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text) if s and s.strip()]


def char_ngrams(text: str, n: int = 3) -> Counter:
    t = re.sub(r"\s+", " ", text.lower())
    return Counter(t[i:i + n] for i in range(max(0, len(t) - n + 1)))


def _rate(count: int, total: int) -> float:
    return round(count / total, 5) if total else 0.0


def measure(text: str) -> dict:
    """Measurements for one message. Rates are per word or per sentence so lengths compare."""
    text = clean_sample(text)
    ws = words(text)
    sents = sentences(text)
    n_w, n_s = len(ws), max(1, len(sents))
    sent_lens = [len(words(s)) for s in sents] or [0]
    lower = [w.lower() for w in ws]
    starts = [s for s in sents if s[:1].isalpha()]
    return {
        "words": n_w,
        "sentences": len(sents),
        "sent_len_mean": round(statistics.fmean(sent_lens), 3),
        "sent_len_sd": round(statistics.pstdev(sent_lens), 3) if len(sent_lens) > 1 else 0.0,
        "word_len_mean": round(statistics.fmean([len(w) for w in ws]), 3) if ws else 0.0,
        "type_token": _rate(len(set(lower)), n_w),
        "per_word": {
            "comma": _rate(text.count(","), n_w),
            "exclaim": _rate(text.count("!"), n_w),
            "question": _rate(text.count("?"), n_w),
            "ellipsis": _rate(text.count("...") + text.count("…"), n_w),
            "dash": _rate(text.count(" - ") + text.count("—") + text.count("–"), n_w),
            "emdash": _rate(text.count("—"), n_w),
            "semicolon": _rate(text.count(";"), n_w),
            "colon": _rate(text.count(":"), n_w),
            "paren": _rate(text.count("("), n_w),
            "emoji": _rate(len(_EMOJI.findall(text)), n_w),
            "all_caps_word": _rate(sum(1 for w in ws if len(w) > 1 and w.isupper() and w != "I"), n_w),
            "lowercase_i": _rate(sum(1 for w in ws if w == "i"), n_w),
            "no_apostrophe": _rate(sum(1 for w in lower if w in NO_APOSTROPHE and w not in AMBIGUOUS_NO_APOSTROPHE), n_w),
            "contraction": _rate(sum(1 for w in ws if "'" in w), n_w),
        },
        "per_sentence": {
            "lower_start": _rate(sum(1 for s in starts if s[0].islower()), len(starts)),
            "no_end_punct": _rate(sum(1 for s in sents if s[-1:] not in ".!?…)\"'"), n_s),
            "and_start": _rate(sum(1 for s in sents if s.lower().startswith(("and ", "but ", "so "))), n_s),
        },
        "double_space": _rate(text.count("  "), n_w),
        "function_words": {w: _rate(c, n_w) for w, c in Counter(x for x in lower if x in FUNCTION_WORDS).items()},
    }


def edit1(a: str, b: str) -> bool:
    """True if a and b differ by one insert, delete, substitute or adjacent swap."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        diff = [i for i in range(len(a)) if a[i] != b[i]]
        if len(diff) == 1:
            return True
        return len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]
    s, t = (a, b) if len(a) < len(b) else (b, a)
    for i in range(len(t)):
        if t[:i] + t[i + 1:] == s:
            return True
    return False


def spelling_quirks(counts: Counter, wordlist: set[str] | None = None, min_seen: int = 2) -> dict[str, dict]:
    """Map habitual misspellings to {"intended": word, "share": how often the quirk wins}.

    With a wordlist: a word not in the list, seen at least min_seen times, one edit from a listed word
    the person also uses. Without a wordlist: a rare letter-swap of a form the person uses at least
    3 times as often ("teh" next to "the"). Set NOUS_VOICE_WORDLIST for the full check. Proper nouns never reach here because
    callers pass lowercased words that also appeared lowercase."""
    quirks: dict[str, dict] = {}
    vocab = sorted(counts, key=counts.get, reverse=True)
    for w in vocab:
        c = counts[w]
        if c < min_seen or len(w) < 3 or w in NO_APOSTROPHE:
            continue
        if wordlist is not None:
            if w in wordlist:
                continue
            cands = [v for v in vocab if v in wordlist and edit1(w, v)]
        else:
            # No dictionary: only letter swaps count ("teh"), since one-letter changes between real
            # words ("think"/"thing", "then"/"than") are too common to call a misspelling.
            cands = [v for v in vocab if counts[v] >= 3 * c and len(v) == len(w) and sorted(v) == sorted(w) and edit1(w, v)]
        if cands:
            v = max(cands, key=lambda x: counts[x])
            quirks[w] = {"intended": v, "share": round(c / (c + counts[v]), 3)}
    return quirks
