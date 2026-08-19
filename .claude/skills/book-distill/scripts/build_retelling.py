#!/usr/bin/env python3
"""Assemble retelling.md out of the per-chapter blocks the chapter agents wrote.

The retelling is the longest file in the pack, and writing it in one place means holding
the whole book in one context. So each chapter block is written by its own agent into
`state/retelling/NNN-*.md`, the front matter and the closing layers are written into
`front.md` and `tail.md`, and this script stitches them together in order.

    python3 build_retelling.py library/<slug> [--lang ru|en]

Reads  library/<slug>/state/retelling/front.md      (# What the book is, cast, world)
       library/<slug>/state/retelling/NNN-*.md      (one `### ` block per entry)
       library/<slug>/state/retelling/tail.md       (key scenes, timeline, self-check)
Writes library/<slug>/retelling.md

It refuses to write a file the linter would reject outright: a block that does not start
with `### `, a duplicated or missing number, an empty front matter. Run `retell_lint.py`
on the result — this script checks assembly, not prose.
"""

import argparse
import re
import sys
from pathlib import Path

HEADING = {"ru": "## Пересказ", "en": "## Retelling"}
NUM = re.compile(r"^(\d+)")
CYRILLIC = re.compile(r"[а-яё]", re.I)


def detect_lang(text):
    return "ru" if len(CYRILLIC.findall(text)) > 40 else "en"


def read(path):
    return path.read_text(encoding="utf-8").strip() if path.is_file() else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book", help="library/<slug>")
    ap.add_argument("--lang", choices=sorted(HEADING), default=None)
    ap.add_argument("--out", default=None, help="default <book>/retelling.md")
    args = ap.parse_args()

    book = Path(args.book)
    parts = book / "state" / "retelling"
    if not parts.is_dir():
        sys.exit(f"no block directory at {parts}")

    front = read(parts / "front.md")
    tail = read(parts / "tail.md")
    if not front:
        sys.exit(f"{parts / 'front.md'} is missing or empty — the front matter comes first")

    blocks, seen, errors = [], {}, []
    for path in sorted(parts.glob("*.md")):
        if path.name in ("front.md", "tail.md"):
            continue
        text = read(path)
        if not text:
            errors.append(f"{path.name}: empty")
            continue
        if not text.startswith("### "):
            errors.append(f"{path.name}: does not start with '### '")
            continue
        m = NUM.match(path.name)
        if not m:
            errors.append(f"{path.name}: no NNN- number prefix")
            continue
        n = int(m.group(1))
        if n in seen:
            errors.append(f"{path.name}: number {n:03d} already used by {seen[n]}")
            continue
        seen[n] = path.name
        blocks.append((n, text))
    if errors:
        sys.exit("assembly refused:\n  " + "\n  ".join(errors))
    if not blocks:
        sys.exit(f"no chapter blocks in {parts}")

    numbers = sorted(seen)
    gaps = [n for n in range(numbers[0], numbers[-1] + 1) if n not in seen]
    if gaps:
        print("warning : missing block numbers " + ", ".join(f"{n:03d}" for n in gaps))

    lang = args.lang or detect_lang(front)
    body = "\n\n".join(text for _, text in sorted(blocks))
    doc = f"{front}\n\n{HEADING[lang]}\n\n{body}\n"
    if tail:
        doc += f"\n{tail}\n"

    out = Path(args.out) if args.out else (book / "retelling.md")
    out.write_text(doc, encoding="utf-8")

    words = len(doc.split())
    print(f"blocks    : {len(blocks)}")
    print(f"language  : {lang}")
    print(f"retelling : {out}  ({words:,} words)")
    print("next      : retell_lint.py on this file, then the cold read")


if __name__ == "__main__":
    main()
