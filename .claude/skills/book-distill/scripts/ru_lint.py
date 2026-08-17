#!/usr/bin/env python3
"""Lint Russian output for machine-translation smell and generative cliche.

Mechanical checks only - it catches the tells a reader would flag in the first
paragraph, not the prose rhythm. Run it, fix everything it reports, then still
reread the opening paragraph of every page by hand.

Usage:
    python ru_lint.py <file.html|file.md|file.txt> [--quiet]

Exit code 1 if any finding is reported, so it can gate a publish step.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# rules: (regex, label, hint)
# --------------------------------------------------------------------------- #

BANNED = [
    (r"\bявля(ется|ются|лся|лись)\b", "канцелярит", "заменить на тире или глагол действия"),
    (r"\bпредставля(ет|ют) собой\b", "канцелярит", "это / — "),
    (r"\bосуществля(ть|ет|ется|лся)\b", "канцелярит", "конкретный глагол: делает, проводит, ведёт"),
    (r"\bданн(ый|ая|ое|ые|ого|ой|ом|ых)\b(?!\s+(?:о|по))", "канцелярит", "этот / эта / это"),
    (r"\bв рамках\b", "канцелярит", "в / при / внутри"),
    (r"\bпосредством\b", "канцелярит", "через / с помощью"),
    (r"\bввиду того,? что\b", "канцелярит", "потому что / раз"),
    (r"\b(важно|стоит|следует|необходимо)\s+(отметить|подчеркнуть|понимать|заметить)\b",
     "ватная вводная", "убрать целиком - утверждение обойдётся без анонса"),
    (r"\bнельзя не отметить\b", "ватная вводная", "убрать"),
    (r"\bдавайте\s+(разберёмся|разберемся|посмотрим)\b", "инфостиль", "убрать"),
    (r"\bглубок(ое|ий)\s+(погружени|анализ)", "штамп", "сказать, что именно разбирается"),
    (r"\bключев(ой|ая|ое|ые)\s+(момент|роль|аспект)", "штамп", "назвать вещь своим именем"),
    (r"\bна самом деле\b", "штамп-усилитель", "убрать"),
    (r"\bпо сути\b", "штамп-усилитель", "убрать"),
    (r"\bкрасной нитью\b", "штамп", "убрать"),
    (r"\bне просто [^.,;]{1,40},? а\b", "штамп-конструкция", "сказать прямо, что это"),
    (r"\b(очень|крайне|поистине|буквально|действительно|просто-напросто)\b",
     "мусорный усилитель", "убрать или заменить точной мерой"),
    (r"\b(челлендж|драйвер|инсайт|нарратив)\b", "калька", "русский эквивалент"),
    (r"\bадресовать\s+(проблему|вопрос|риск)", "калька", "заняться / решить / ответить на"),
    (r"\bимеет место\b", "канцелярит", "происходит / есть"),
    (r"\bв конечном (счете|счёте)\b", "штамп", "убрать"),
]

TYPOGRAPHY = [
    (r'"[А-Яа-яЁё]', "английские кавычки", "«ёлочки»"),
    (r"[А-Яа-яЁё]\s-\s[А-Яа-яЁё]", "дефис вместо тире", "длинное тире —"),
    (r"\d{1,3},\d{3}\b", "английский разделитель разрядов", "78 140, не 78,140"),
]

NOMINAL = re.compile(r"\b\w+(?:ание|ения|ение|ений|ания|ению|енной|анной)\b", re.I)
SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+")
PARTICIPLE = re.compile(r"\b\w+(?:вший|вшая|вшие|ющий|ющая|ющие|ащий|ящий|нный|тый|емый|имый)\w*\b", re.I)


def strip_markup(text: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&mdash;", "—").replace("&laquo;", "«").replace("&raquo;", "»")
    return re.sub(r"[ \t]+", " ", text)


def context(text: str, start: int, end: int, pad: int = 34) -> str:
    left = max(0, start - pad)
    right = min(len(text), end + pad)
    snippet = text[left:right].replace("\n", " ")
    return ("…" if left else "") + snippet.strip() + ("…" if right < len(text) else "")


def main() -> int:
    try:  # Windows consoles default to cp866/cp1251 and mangle the report
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--quiet", action="store_true", help="only the summary line")
    args = ap.parse_args()

    src = Path(args.path).expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"not found: {src}")

    raw = src.read_text("utf-8", "replace")
    text = strip_markup(raw) if src.suffix.lower() in {".html", ".htm"} else raw

    findings: list[tuple[str, str, str, str]] = []

    for pattern, label, hint in BANNED + TYPOGRAPHY:
        for m in re.finditer(pattern, text, re.I):
            findings.append((label, m.group(0).strip(), hint, context(text, m.start(), m.end())))

    # two nominalizations in a row
    for m in re.finditer(rf"{NOMINAL.pattern}\s+(?:\w+\s+){{0,1}}{NOMINAL.pattern}", text, re.I):
        findings.append(("цепочка отглагольных", m.group(0).strip(),
                         "переписать через глагол", context(text, m.start(), m.end())))

    # long sentences and participle pile-ups
    long_sentences = 0
    participle_heavy = 0
    for sentence in SENT_SPLIT.split(text):
        words = re.findall(r"[А-Яа-яЁёA-Za-z]+", sentence)
        if len(words) > 45:
            long_sentences += 1
            if not args.quiet:
                findings.append(("длинное предложение", f"{len(words)} слов",
                                 "разбить", sentence.strip()[:110] + "…"))
        if len(PARTICIPLE.findall(sentence)) >= 3:
            participle_heavy += 1
            if not args.quiet:
                findings.append(("причастная каша", "3+ причастия во фразе",
                                 "оставить одно", sentence.strip()[:110] + "…"))

    if not args.quiet:
        by_label: dict[str, list] = {}
        for label, hit, hint, ctx in findings:
            by_label.setdefault(label, []).append((hit, hint, ctx))
        for label in sorted(by_label, key=lambda k: -len(by_label[k])):
            items = by_label[label]
            print(f"\n{label.upper()}  ({len(items)})")
            for hit, hint, ctx in items[:12]:
                print(f"  · {hit!r} -> {hint}")
                print(f"    {ctx}")
            if len(items) > 12:
                print(f"  … ещё {len(items) - 12}")

    words_total = len(re.findall(r"[А-Яа-яЁё]+", text))
    print(f"\nнаходок: {len(findings)} / русских слов: {words_total} "
          f"/ длинных предложений: {long_sentences} / причастных завалов: {participle_heavy}")
    print("линтер ловит механику, не интонацию — вступления каждой страницы всё равно перечитать глазами")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
