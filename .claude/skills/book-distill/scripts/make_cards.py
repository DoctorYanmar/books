#!/usr/bin/env python3
"""Convert a `cards.md` retrieval deck into an Anki-importable TSV.

Expected card format in cards.md (blank line between cards, `#` headings ignored):

    Q: What does Taleb mean by "fragility"?
    A: Sensitivity to volatility - harm grows faster than benefit as variance rises.
    T: ch3 core-concept

`T:` (tags) is optional. Multi-line answers are supported: any line that is not a
new `Q:`/`A:`/`T:` marker continues the previous field.

Usage:
    python make_cards.py <book-dir>/cards.md [-o <book-dir>/anki.tsv]

Import into Anki: File > Import, field separator = Tab, fields = Front, Back, Tags.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MARKER = re.compile(r"^\s*(?:[-*]\s*)?([QAT])\s*[:.]\s*(.*)$", re.I)


def parse(text: str) -> list[dict]:
    cards: list[dict] = []
    current: dict = {}
    field: str | None = None

    def flush() -> None:
        nonlocal current, field
        if current.get("Q") and current.get("A"):
            cards.append(current)
        current, field = {}, None

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if current.get("Q") and current.get("A"):
                flush()
            field = None
            continue
        if line.lstrip().startswith("#"):
            continue
        m = MARKER.match(line)
        if m:
            key, value = m.group(1).upper(), m.group(2).strip()
            if key == "Q" and current.get("Q") and current.get("A"):
                flush()
            current[key] = value
            field = key
        elif field:
            current[field] = (current[field] + " " + line.strip()).strip()
    flush()
    return cards


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cards", help="path to cards.md")
    ap.add_argument("-o", "--out", help="output .tsv (default: alongside cards.md)")
    args = ap.parse_args()

    src = Path(args.cards).expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"not found: {src}")

    cards = parse(src.read_text("utf-8", "replace"))
    if not cards:
        raise SystemExit("no cards parsed - check that the file uses `Q:` / `A:` lines")

    out = Path(args.out).resolve() if args.out else src.with_suffix(".tsv")
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for card in cards:
            front = card["Q"].replace("\t", " ")
            back = card["A"].replace("\t", " ")
            tags = card.get("T", "").replace("\t", " ")
            fh.write(f"{front}\t{back}\t{tags}\n")

    print(f"{len(cards)} cards -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
