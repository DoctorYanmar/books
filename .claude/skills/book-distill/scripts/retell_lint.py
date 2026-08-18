#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка пересказа на механику ясности.

Читает раздел «## Пересказ» файла retelling.md и меряет каждую главу против
жёстких пределов из reference/retelling-standard.md. Мера механическая: линтер
не видит, потеряна ли микротема, — это остаётся человеческой проверкой.

    python3 retell_lint.py library/<slug>/retelling.md [--depth quick|standard|deep]

Выход 0 — нарушений нет; 1 — есть.
"""

import argparse
import re
import sys

BUDGET = {
    "A": {"quick": (90, 140), "standard": (140, 220), "deep": (190, 300)},
    "B": {"quick": (50, 80), "standard": (80, 130), "deep": (90, 180)},
}

MAX_AVG_SENTENCE = 20
MAX_SENTENCE = 30
MAX_ENTITY_DENSITY = {"A": 11.0, "B": 10.0}   # имён и чисел на 100 слов
MAX_FIRST_SENTENCE = 25           # слов
MAX_FIRST_ENTITIES = 2
SENTENCES_PER_CAUSAL = 3          # хотя бы одна причинная связка на столько предложений
MIN_TOPIC_CHAIN = 0.20

CHAIN_OPENERS = [
    "затем", "дальше", "далее", "потом", "отдельно", "также",
    "в конце главы", "после этого", "кроме того", "наконец",
]
CAUSAL = [
    "поэтому", "потому что", "из-за", "благодаря", "следовательно", "значит",
    "но ", "однако", "зато", "хотя", "если", "чтобы", "оттого", "иначе",
    "в результате", "вследствие", "тем самым", "а не ",
]
LINKERS = ("поэтому", "потому", "но", "однако", "зато", "хотя", "если",
           "значит", "следовательно", "иначе", "оттого", "тем")

LABEL_A = "**Утверждение.**"
LABEL_B = "**Что происходит.**"
LABEL_FORWARD = "**Дальше.**"
LABELS = re.compile(r"\*\*[^*]+\.\*\*\s*")

WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def strip_markup(text):
    text = re.sub(r"^>.*$", "", text, flags=re.M)          # блок разбора не считаем
    text = LABELS.sub("", text)                            # метки слотов не текст
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
    """Имена собственные и числа. Слово с заглавной не в начале предложения."""
    found = set()
    text = re.sub(r"«[^»]*»", " ", text)                   # цитаты не считаем за имена
    for sent in sentences(text):
        toks = re.findall(r"[^\s]+", sent)
        for i, tok in enumerate(toks):
            bare = tok.strip("«»\"'(),.;:—–-")
            if not bare or i == 0:
                continue
            if bare[0].isupper() and bare[0].isalpha():
                found.add(bare)
    nums = re.findall(r"\d+", text)
    return len(found) + len(nums)


def share(text, markers):
    low = " " + text.lower() + " "
    return sum(low.count(m) for m in markers)


def topic_chain(sents):
    """Доля предложений прозы, зацепленных за предыдущее: общим словом в начале либо связкой.

    Считается только по сплошному тексту: пункты перечня стоят рядом как равные,
    и сцеплять их между собой не нужно."""
    if len(sents) < 2:
        return 1.0
    hits = 0
    for i in range(1, len(sents)):
        prev = {w.lower()[:5] for w in words(sents[i - 1]) if len(w) > 3}
        cur_words = [w for w in words(sents[i]) if len(w) > 3]
        head = [w.lower()[:5] for w in cur_words[:5]]
        first = (words(sents[i]) or [""])[0].lower()
        if any(w in prev for w in head) or first in LINKERS:
            hits += 1
    return hits / (len(sents) - 1)


def split_chapters(md):
    body = md.split("## Пересказ", 1)
    if len(body) < 2:
        return []
    body = re.split(r"\n## ", body[1])[0]
    chunks = re.split(r"\n### ", body)
    out = []
    for chunk in chunks[1:]:
        lines = chunk.split("\n")
        out.append((lines[0].strip(), "\n".join(lines[1:]).strip()))
    return out


def check(raw, depth):
    problems = []
    kind = "A" if LABEL_A in raw else ("B" if LABEL_B in raw else None)
    if kind is None:
        problems.append("нет слота «Утверждение.» или «Что происходит.» — глава не по шаблону")
        kind = "A"

    blocks = [b for b in re.split(r"\n\s*\n", raw) if b.strip()]
    if len(blocks) < 2:
        problems.append("один блок на главу — стена; нужно минимум два (ИК3)")

    text = strip_markup(raw)
    ws = words(text)
    lo, hi = BUDGET[kind][depth]
    if not (lo <= len(ws) <= hi):
        problems.append("объём %d слов вне диапазона %d–%d для шаблона %s/%s"
                        % (len(ws), lo, hi, kind, depth))

    sents = sentences(text)
    if sents:
        lens = [len(words(s)) for s in sents]
        avg = sum(lens) / len(lens)
        if avg > MAX_AVG_SENTENCE:
            problems.append("средняя длина предложения %.1f > %d" % (avg, MAX_AVG_SENTENCE))
        if max(lens) > MAX_SENTENCE:
            problems.append("самое длинное предложение %d слов > %d" % (max(lens), MAX_SENTENCE))

    dens = entities(text) / max(1, len(ws)) * 100
    if dens > MAX_ENTITY_DENSITY[kind]:
        problems.append("плотность имён и чисел %.1f на 100 слов > %.0f"
                        % (dens, MAX_ENTITY_DENSITY[kind]))

    label = LABEL_A if kind == "A" else LABEL_B
    m = re.search(re.escape(label) + r"\s*(.+)", raw)
    if m:
        first = sentences(strip_markup(m.group(1)))
        if first:
            fw = len(words(first[0]))
            fe = entities(first[0])
            if fw > MAX_FIRST_SENTENCE:
                problems.append("первое предложение %d слов > %d" % (fw, MAX_FIRST_SENTENCE))
            if fe > MAX_FIRST_ENTITIES:
                problems.append("первое предложение несёт %d имён и чисел > %d — это опись, не утверждение"
                                % (fe, MAX_FIRST_ENTITIES))

    low = text.lower()
    for opener in CHAIN_OPENERS:
        for s in sents:
            if s.lower().startswith(opener):
                problems.append("предложение открывается связкой-цепочкой «%s»" % opener)
                break

    ca = share(low, CAUSAL)
    need = max(1, len(sents) // SENTENCES_PER_CAUSAL)
    if ca < need:
        problems.append("причинных связок %d при %d предложениях — нужно хотя бы %d, иначе цепочка «и потом»"
                        % (ca, len(sents), need))

    prose = re.sub(r"^\s*[-–—].*$", "", raw, flags=re.M)   # списки не цепочка, а перечень
    chain = topic_chain(sentences(strip_markup(prose)))
    if chain < MIN_TOPIC_CHAIN:
        problems.append("сцепка тем %.0f%% < %.0f%% — каждое предложение о новом"
                        % (chain * 100, MIN_TOPIC_CHAIN * 100))

    if LABEL_FORWARD not in raw:
        problems.append("нет слота «Дальше.» — глава не связана со следующей")

    analysis_outside = [ln for ln in raw.split("\n")
                        if "разбор" in ln.lower() and not ln.lstrip().startswith(">")]
    if analysis_outside:
        problems.append("«разбор» вне цитатного блока — слои книги и разбора смешаны")

    return len(ws), problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--depth", default="standard", choices=("quick", "standard", "deep"))
    args = ap.parse_args()

    md = open(args.path, encoding="utf-8").read()
    chapters = split_chapters(md)
    if not chapters:
        print("не найден раздел «## Пересказ» с главами уровня ###")
        return 1

    total, bad = 0, 0
    for title, raw in chapters:
        n, problems = check(raw, args.depth)
        total += n
        if problems:
            bad += 1
            print("\n%s  (%d слов)" % (title, n))
            for p in problems:
                print("   · " + p)

    print("\nглав: %d · слов в пересказе: %d · глав с нарушениями: %d"
          % (len(chapters), total, bad))
    if not bad:
        print("механика чистая. Микротемы проверяются глазами: сверьте список из notes/.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
