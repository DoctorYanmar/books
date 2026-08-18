#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mechanical check for a chapter retelling.

Reads the retelling section of retelling.md and measures every chapter against the hard
limits in reference/retelling-standard.md.

    python3 retell_lint.py library/<slug>/retelling.md [--depth quick|standard|deep] [--lang en|ru]

Exit 0 when nothing is violated, 1 otherwise.

The check is mechanical and it is the smaller half of the gate. It cannot tell whether a
chapter can be understood — the first version of this standard scored a perfect zero on a
retelling nobody could read. Comprehension is checked by the cold read (pass 2.6); a lost
unit of meaning is still checked by eye against notes/.

A pack is written in the book's own language, so slot labels and connective lists are per
language. Add a language by extending LANGS below; the limits themselves are shared.
"""

import argparse
import re
import statistics
import sys

# Word budget per chapter. Template A is an argumentative chapter, B a narrative one.
BUDGET = {
    "A": {"quick": (150, 220), "standard": (260, 380), "deep": (380, 560)},
    "B": {"quick": (110, 170), "standard": (160, 260), "deep": (220, 340)},
}

# Words in the prose blocks between the claim and the evidence — the position and the
# mechanism. This is where the reader's understanding is actually built, so it has a floor.
MIDDLE = {"quick": (60, 110), "standard": (100, 180), "deep": (140, 260)}

AVG_SENTENCE = (15.0, 25.0)                   # a flat 13-15 reads as a telegram
MIN_SENTENCE_SPREAD = 5.0                     # standard deviation, in words
MAX_SENTENCE = 38
MAX_ENTITY_DENSITY = {"A": 11.0, "B": 10.0}   # names and numbers per 100 words
MAX_FIRST_SENTENCE = 28                       # words
MAX_FIRST_ENTITIES = 2
MAX_EVIDENCE_WORDS = 35                       # left half of an evidence bullet
MIN_INFERENCE_WORDS = 3                       # right half — what it proves
SENTENCES_PER_CAUSAL = 2                      # at least one causal link per N sentences
MIN_TOPIC_CHAIN = 0.35

LANGS = {
    "en": {
        "heading": "## Retelling",
        "claim": "**Claim.**",
        "happens": "**What happens.**",
        "evidence": "**What holds it up.**",
        "next": "**Next.**",
        "analysis": "analysis",
        # openers that chain events instead of connecting them
        "chain": ["then", "next", "after that", "later", "also", "separately",
                  "at the end of the chapter", "furthermore", "finally"],
        # markers of cause, consequence or contrast
        "causal": ["because", "therefore", "so that", "which is why", "as a result",
                   "but ", "however", "although", "if ", "since ", "thus", "hence",
                   "otherwise", "rather than"],
        # words that tie a sentence to the previous one when they open it
        "linkers": ("because", "therefore", "but", "however", "although", "if",
                    "so", "thus", "hence", "that", "this", "these", "otherwise"),
        # numerals above ten written out: they duck the density cap and read badly
        "numerals": ["eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                     "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty",
                     "fifty", "sixty", "seventy", "eighty", "ninety", "hundred"],
    },
    "ru": {
        "heading": "## Пересказ",
        "claim": "**Утверждение.**",
        "happens": "**Что происходит.**",
        "evidence": "**Чем держится.**",
        "next": "**Дальше.**",
        "analysis": "разбор",
        "chain": ["затем", "дальше", "далее", "потом", "отдельно", "также",
                  "в конце главы", "после этого", "кроме того", "наконец"],
        "causal": ["поэтому", "потому что", "из-за", "благодаря", "следовательно",
                   "значит", "но ", "однако", "зато", "хотя", "если", "чтобы",
                   "оттого", "иначе", "в результате", "вследствие", "тем самым", "а не ",
                   "раз ", "тогда как", "пока не", "зачем", "почему"],
        "linkers": ("поэтому", "потому", "но", "однако", "зато", "хотя", "если",
                    "значит", "следовательно", "иначе", "оттого", "тем", "раз",
                    "этот", "эта", "это", "эти", "такой", "такая", "такое", "такие"),
        "numerals": ["одиннадцат", "двенадцат", "тринадцат", "четырнадцат",
                     "пятнадцат", "шестнадцат", "семнадцат", "восемнадцат",
                     "девятнадцат", "двадцат", "тридцат", "сорок", "сорока",
                     "пятьдесят", "пятидесят", "шестьдесят", "шестидесят",
                     "семьдесят", "семидесят", "восемьдесят", "восьмидесят",
                     "девяност", "двухсот", "трёхсот", "четырёхсот", "пятисот",
                     "шестисот", "семисот", "восьмисот", "девятисот", "двест",
                     "трист", "четырест", "пятьсот", "шестьсот", "семьсот",
                     "восемьсот", "девятьсот"],
    },
}

LABELS = re.compile(r"\*\*[^*]+\.\*\*\s*")
BLOCK_LABEL = re.compile(r"^\s*\*\*(.+?)\.\*\*")
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)
DASH = re.compile(r"\s+[—–]\s+")


def detect_lang(md):
    for code, cfg in LANGS.items():
        if cfg["heading"] in md or cfg["claim"] in md or cfg["happens"] in md:
            return code
    return "en"


def strip_markup(text):
    text = re.sub(r"^>.*$", "", text, flags=re.M)          # the analysis block is not counted
    text = LABELS.sub("", text)                            # slot labels are not prose
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"^\s*[-–—]\s*", "", text, flags=re.M)
    return text


def sentences(text):
    parts = re.split(r"(?<=[.!?…])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def words(text):
    return WORD.findall(text)


def spelled_numerals(text, cfg):
    """Numerals above ten written out as words. Matched on a word stem, so «сто» never
    fires inside «стоит» — a false positive would push the writer back to a worse style."""
    low = text.lower().replace("ё", "е")
    n = 0
    for stem in cfg["numerals"]:
        n += len(re.findall(r"(?<![^\W\d_])" + stem.replace("ё", "е") + r"[^\W\d_]*", low))
    return n


def entities(text, cfg):
    """Proper nouns and numbers: a capitalised word that does not open a sentence.

    Numerals written out count too — otherwise «пятьдесят семь процентов» is a free way
    round the density cap, which is exactly what happened to the first pack."""
    found = set()
    text = re.sub(r"«[^»]*»|\"[^\"]*\"", " ", text)        # quotations are not names
    for sent in sentences(text):
        toks = re.findall(r"[^\s]+", sent)
        for i, tok in enumerate(toks):
            bare = tok.strip("«»\"'(),.;:—–-")
            if not bare or i == 0:
                continue
            if bare[0].isupper() and bare[0].isalpha():
                found.add(bare)
    return len(found) + len(re.findall(r"\d+", text)) + spelled_numerals(text, cfg)


def count_markers(text, markers):
    low = " " + text.lower() + " "
    return sum(low.count(m) for m in markers)


def topic_chain(sents, linkers):
    """Share of prose sentences tied to the previous one, by a shared word or a connective.

    Measured on running text only: items in a bullet list stand side by side as equals and
    are not meant to chain."""
    if len(sents) < 2:
        return 1.0
    hits = 0
    for i in range(1, len(sents)):
        prev = {w.lower()[:5] for w in words(sents[i - 1]) if len(w) > 3}
        head = [w.lower()[:5] for w in words(sents[i]) if len(w) > 3][:5]
        first = (words(sents[i]) or [""])[0].lower()
        if any(w in prev for w in head) or first in linkers:
            hits += 1
    return hits / (len(sents) - 1)


def split_chapters(md, cfg):
    if cfg["heading"] not in md:
        return []
    body = re.split(r"\n## ", md.split(cfg["heading"], 1)[1])[0]
    out = []
    for chunk in re.split(r"\n### ", body)[1:]:
        lines = chunk.split("\n")
        out.append((lines[0].strip(), "\n".join(lines[1:]).strip()))
    return out


def blocks_of(raw):
    """The chapter as labelled blocks, in order: [(label or None, text), ...]."""
    out = []
    for chunk in re.split(r"\n\s*\n", raw):
        if not chunk.strip():
            continue
        m = BLOCK_LABEL.match(chunk)
        out.append((m.group(1) if m else None, chunk))
    return out


def middle_blocks(bl, cfg):
    """The prose blocks between the claim and the evidence — position and mechanism."""
    claim = cfg["claim"].strip("*.")
    evidence = cfg["evidence"].strip("*.")
    start = end = None
    for i, (label, _) in enumerate(bl):
        if label == claim and start is None:
            start = i + 1
        if label == evidence and start is not None and end is None:
            end = i
    if start is None:
        return []
    if end is None:
        end = len(bl)
    return [b for b in bl[start:end] if not b[1].lstrip().startswith((">", "-", "–", "—"))]


def evidence_bullets(bl, cfg):
    evidence = cfg["evidence"].strip("*.")
    for label, chunk in bl:
        if label == evidence:
            return [ln.strip()[2:].strip() for ln in chunk.split("\n")
                    if ln.strip().startswith("- ")]
    return []


def first_mentions(raw, glossed):
    """Names used here for the first time in the pack, and whether they carry a gloss.

    A gloss is a lowercase description hung on the name — after it behind a comma, dash,
    colon or bracket, or in front of it as a common noun. The cast list does not count:
    the retelling has to read without looking anything up."""
    missing = []
    text = re.sub(r"«[^»]*»", " ", raw)
    text = re.sub(r"\*\*|\[|\]", " ", text)

    units = []                                  # each starts a capital of its own right
    for line in strip_markup(text).split("\n"):
        if not line.strip():
            continue
        halves = DASH.split(line) if line.lstrip().startswith(("-", "–", "—")) \
            or DASH.search(line) else [line]
        for half in halves:
            units.extend(sentences(half))

    for sent in units:
        toks = re.findall(r"[^\s]+", sent)
        prev_capital = False
        for i, tok in enumerate(toks):
            bare = tok.strip("«»\"'(),.;:—–-…")
            capital = bool(bare) and bare[0].isalpha() and bare[0].isupper()
            was_capital, prev_capital = prev_capital, capital
            if len(bare) < 3 or not capital:
                continue
            if i == 0 or was_capital:            # sentence opener, or the tail of a name
                glossed.add(bare.lower())
                continue
            key = bare.lower()
            if key in glossed:
                continue
            tail = tok[len(tok.rstrip("«»\"'(),.;:—–-…")):]
            after = toks[i + 1] if i + 1 < len(toks) else ""
            before = toks[i - 1].strip("«»\"'(),.;:—–-…") if i else ""
            has_after = (tail and tail[0] in ",:—–(" and after[:1].islower()) or \
                        after[:1] == "(" or after[:1] in "—–"
            has_before = len(before) >= 4 and before.islower()
            glossed.add(key)
            if not (has_after or has_before):
                missing.append(bare)
    return missing


def check(raw, depth, cfg, glossed):
    problems = []
    kind = "A" if cfg["claim"] in raw else ("B" if cfg["happens"] in raw else None)
    if kind is None:
        problems.append("no %s or %s slot — the chapter follows neither template"
                        % (cfg["claim"], cfg["happens"]))
        kind = "A"

    bl = blocks_of(raw)
    need_blocks = 4 if kind == "A" else 2
    if len(bl) < need_blocks:
        problems.append("%d blocks — template %s needs at least %d"
                        % (len(bl), kind, need_blocks))

    text = strip_markup(raw)
    ws = words(text)
    lo, hi = BUDGET[kind][depth]
    if not (lo <= len(ws) <= hi):
        problems.append("%d words, outside %d-%d for template %s at %s"
                        % (len(ws), lo, hi, kind, depth))

    if kind == "A":
        mid = middle_blocks(bl, cfg)
        mw = sum(len(words(strip_markup(b[1]))) for b in mid)
        mlo, mhi = MIDDLE[depth]
        if len(mid) < 2:
            problems.append("%d prose block(s) between the claim and the evidence — at least "
                            "2 needed: the position, then the mechanism" % len(mid))
        if not (mlo <= mw <= mhi):
            problems.append("%d words of position and mechanism, outside %d-%d at %s — "
                            "that middle is what the reader cannot reconstruct alone"
                            % (mw, mlo, mhi, depth))

        for b in evidence_bullets(bl, cfg):
            halves = DASH.split(b, 1)
            if len(halves) < 2 or len(words(halves[1])) < MIN_INFERENCE_WORDS:
                problems.append('evidence bullet has no "— what it proves" half: "%s"'
                                % b[:60])
            elif len(words(halves[0])) > MAX_EVIDENCE_WORDS:
                problems.append("evidence bullet runs %d words before the dash > %d"
                                % (len(words(halves[0])), MAX_EVIDENCE_WORDS))

    sents = sentences(text)
    if sents:
        lens = [len(words(s)) for s in sents]
        avg = sum(lens) / len(lens)
        if not (AVG_SENTENCE[0] <= avg <= AVG_SENTENCE[1]):
            problems.append("average sentence %.1f words, outside %.0f-%.0f"
                            % (avg, AVG_SENTENCE[0], AVG_SENTENCE[1]))
        if len(lens) > 2 and statistics.pstdev(lens) < MIN_SENTENCE_SPREAD:
            problems.append("sentence length spread %.1f < %.0f — every sentence the same "
                            "length reads as generated"
                            % (statistics.pstdev(lens), MIN_SENTENCE_SPREAD))
        if max(lens) > MAX_SENTENCE:
            problems.append("longest sentence %d words > %d" % (max(lens), MAX_SENTENCE))

    dens = entities(text, cfg) / max(1, len(ws)) * 100
    if dens > MAX_ENTITY_DENSITY[kind]:
        problems.append("%.1f names and numbers per 100 words > %.0f"
                        % (dens, MAX_ENTITY_DENSITY[kind]))

    spelled = spelled_numerals(text, cfg)
    if spelled:
        problems.append("%d numeral(s) above ten written out — use digits" % spelled)

    unglossed = first_mentions(raw, glossed)
    if unglossed:
        problems.append("first mention without a gloss: %s" % ", ".join(unglossed[:6]))

    label = cfg["claim"] if kind == "A" else cfg["happens"]
    m = re.search(re.escape(label) + r"\s*(.+)", raw)
    if m:
        first = sentences(strip_markup(m.group(1)))
        if first:
            fw, fe = len(words(first[0])), entities(first[0], cfg)
            if fw > MAX_FIRST_SENTENCE:
                problems.append("opening sentence %d words > %d" % (fw, MAX_FIRST_SENTENCE))
            if fe > MAX_FIRST_ENTITIES:
                problems.append("opening sentence carries %d names and numbers > %d — "
                                "an inventory, not a claim" % (fe, MAX_FIRST_ENTITIES))

    for opener in cfg["chain"]:
        if any(s.lower().startswith(opener) for s in sents):
            problems.append('a sentence opens with the chaining word "%s"' % opener)

    causal = count_markers(text.lower(), cfg["causal"])
    need = max(1, len(sents) // SENTENCES_PER_CAUSAL)
    if causal < need:
        problems.append("%d causal links across %d sentences — at least %d needed, "
                        "otherwise it reads as and-then chaining" % (causal, len(sents), need))

    prose = re.sub(r"^\s*[-–—].*$", "", raw, flags=re.M)   # bullets are a list, not a chain
    chain = topic_chain(sentences(strip_markup(prose)), cfg["linkers"])
    if chain < MIN_TOPIC_CHAIN:
        problems.append("topic chaining %.0f%% < %.0f%% — every sentence starts a new subject"
                        % (chain * 100, MIN_TOPIC_CHAIN * 100))

    if cfg["next"] not in raw:
        problems.append("no %s slot — the chapter is not tied to the one after it" % cfg["next"])

    stray = [ln for ln in raw.split("\n")
             if cfg["analysis"] in ln.lower() and not ln.lstrip().startswith(">")]
    if stray:
        problems.append("analysis outside its quoted block — the book's claims and ours are mixed")

    return len(ws), problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--depth", default="standard", choices=("quick", "standard", "deep"))
    ap.add_argument("--lang", default=None, choices=sorted(LANGS))
    args = ap.parse_args()

    md = open(args.path, encoding="utf-8").read()
    lang = args.lang or detect_lang(md)
    cfg = LANGS[lang]

    chapters = split_chapters(md, cfg)
    if not chapters:
        print('no "%s" section with ### chapters found (language: %s)' % (cfg["heading"], lang))
        return 1

    glossed = set()
    total, bad = 0, 0
    for title, raw in chapters:
        n, problems = check(raw, args.depth, cfg, glossed)
        total += n
        if problems:
            bad += 1
            print("\n%s  (%d words)" % (title, n))
            for p in problems:
                print("   . " + p)

    print("\nlanguage: %s . chapters: %d . words in the retelling: %d . chapters with problems: %d"
          % (lang, len(chapters), total, bad))
    if not bad:
        print("mechanics are clean — which is the smaller half. The chapter still has to pass "
              "the cold read (pass 2.6), and units of meaning stay a human check against notes/.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
