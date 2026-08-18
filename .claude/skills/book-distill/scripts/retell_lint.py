#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mechanical check for a chapter retelling.

Reads the retelling section of retelling.md and measures every chapter against the hard
limits in reference/retelling-standard.md. The check is mechanical: it cannot see whether
a unit of meaning was dropped, so that stays a human check.

    python3 retell_lint.py library/<slug>/retelling.md [--depth quick|standard|deep] [--lang en|ru]

Exit 0 when nothing is violated, 1 otherwise.

A pack is written in the book's own language, so slot labels and connective lists are per
language. Add a language by extending LANGS below; the limits themselves are shared.
"""

import argparse
import re
import sys

# Word budget per chapter. Template A is an argumentative chapter, B a narrative one.
BUDGET = {
    "A": {"quick": (90, 140), "standard": (140, 220), "deep": (190, 300)},
    "B": {"quick": (50, 80), "standard": (80, 130), "deep": (90, 180)},
}

MAX_AVG_SENTENCE = 20
MAX_SENTENCE = 30
MAX_ENTITY_DENSITY = {"A": 11.0, "B": 10.0}   # names and numbers per 100 words
MAX_FIRST_SENTENCE = 25                       # words
MAX_FIRST_ENTITIES = 2
SENTENCES_PER_CAUSAL = 3                      # at least one causal link per N sentences
MIN_TOPIC_CHAIN = 0.20

LANGS = {
    "en": {
        "heading": "## Retelling",
        "claim": "**Claim.**",
        "happens": "**What happens.**",
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
    },
    "ru": {
        "heading": "## Пересказ",
        "claim": "**Утверждение.**",
        "happens": "**Что происходит.**",
        "next": "**Дальше.**",
        "analysis": "разбор",
        "chain": ["затем", "дальше", "далее", "потом", "отдельно", "также",
                  "в конце главы", "после этого", "кроме того", "наконец"],
        "causal": ["поэтому", "потому что", "из-за", "благодаря", "следовательно",
                   "значит", "но ", "однако", "зато", "хотя", "если", "чтобы",
                   "оттого", "иначе", "в результате", "вследствие", "тем самым", "а не "],
        "linkers": ("поэтому", "потому", "но", "однако", "зато", "хотя", "если",
                    "значит", "следовательно", "иначе", "оттого", "тем"),
    },
}

LABELS = re.compile(r"\*\*[^*]+\.\*\*\s*")
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


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


def entities(text):
    """Proper nouns and numbers: a capitalised word that does not open a sentence."""
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
    return len(found) + len(re.findall(r"\d+", text))


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


def check(raw, depth, cfg):
    problems = []
    kind = "A" if cfg["claim"] in raw else ("B" if cfg["happens"] in raw else None)
    if kind is None:
        problems.append("no %s or %s slot — the chapter follows neither template"
                        % (cfg["claim"], cfg["happens"]))
        kind = "A"

    blocks = [b for b in re.split(r"\n\s*\n", raw) if b.strip()]
    if len(blocks) < 2:
        problems.append("one block per chapter — a wall; at least two are required")

    text = strip_markup(raw)
    ws = words(text)
    lo, hi = BUDGET[kind][depth]
    if not (lo <= len(ws) <= hi):
        problems.append("%d words, outside %d-%d for template %s at %s"
                        % (len(ws), lo, hi, kind, depth))

    sents = sentences(text)
    if sents:
        lens = [len(words(s)) for s in sents]
        avg = sum(lens) / len(lens)
        if avg > MAX_AVG_SENTENCE:
            problems.append("average sentence %.1f words > %d" % (avg, MAX_AVG_SENTENCE))
        if max(lens) > MAX_SENTENCE:
            problems.append("longest sentence %d words > %d" % (max(lens), MAX_SENTENCE))

    dens = entities(text) / max(1, len(ws)) * 100
    if dens > MAX_ENTITY_DENSITY[kind]:
        problems.append("%.1f names and numbers per 100 words > %.0f"
                        % (dens, MAX_ENTITY_DENSITY[kind]))

    label = cfg["claim"] if kind == "A" else cfg["happens"]
    m = re.search(re.escape(label) + r"\s*(.+)", raw)
    if m:
        first = sentences(strip_markup(m.group(1)))
        if first:
            fw, fe = len(words(first[0])), entities(first[0])
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

    total, bad = 0, 0
    for title, raw in chapters:
        n, problems = check(raw, args.depth, cfg)
        total += n
        if problems:
            bad += 1
            print("\n%s  (%d words)" % (title, n))
            for p in problems:
                print("   . " + p)

    print("\nlanguage: %s . chapters: %d . words in the retelling: %d . chapters with problems: %d"
          % (lang, len(chapters), total, bad))
    if not bad:
        print("mechanics are clean. Units of meaning stay a human check: "
              "list them from notes/ and confirm each one appears.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
