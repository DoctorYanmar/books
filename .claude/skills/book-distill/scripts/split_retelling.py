#!/usr/bin/env python3
"""Split an already-written retelling.md back into the per-block files the pipeline edits.

Packs started before the retelling was fanned out across agents have one monolithic
`retelling.md`. Everything downstream — repair agents, cold-read fixes, reassembly —
works on `state/retelling/*`, so bring the old file into that shape once:

    python3 split_retelling.py library/<slug> [--force]

Writes state/retelling/front.md, NNN-<slug>.md per `### ` block, and tail.md when the
file already carries the closing layers. Refuses to overwrite existing blocks unless
--force. After this, `retelling.md` is a generated file: edit the blocks and rerun
`build_retelling.py`.
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

HEADINGS = ("## Пересказ", "## Retelling")
TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c",
    "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu",
    "я": "ya",
}


def slugify(title):
    head = title.split("·")[0].strip().lower()
    out = []
    for ch in unicodedata.normalize("NFC", head):
        if ch in TRANSLIT:
            out.append(TRANSLIT[ch])
        elif ch.isalnum():
            out.append(ch)
        elif ch in " -_":
            out.append("-")
    slug = re.sub(r"-+", "-", "".join(out)).strip("-")
    return slug or "block"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book", help="library/<slug>")
    ap.add_argument("--force", action="store_true", help="overwrite existing block files")
    args = ap.parse_args()

    book = Path(args.book)
    src = book / "retelling.md"
    if not src.is_file():
        sys.exit(f"no retelling at {src}")
    md = src.read_text(encoding="utf-8")

    heading = next((h for h in HEADINGS if h in md), None)
    if not heading:
        sys.exit(f"{src} carries neither {' nor '.join(HEADINGS)}")

    front, rest = md.split(heading, 1)
    parts = re.split(r"\n(?=## )", rest, maxsplit=1)
    body, tail = parts[0], (parts[1] if len(parts) > 1 else "")

    out = book / "state" / "retelling"
    out.mkdir(parents=True, exist_ok=True)
    if not args.force:
        existing = [p.name for p in out.glob("*.md")]
        if existing:
            sys.exit(f"{out} already holds {len(existing)} file(s) — pass --force to overwrite")

    (out / "front.md").write_text(front.strip() + "\n", encoding="utf-8")
    written = ["front.md"]

    chunks = re.split(r"\n### ", body)[1:]
    for i, chunk in enumerate(chunks, 1):
        title = chunk.split("\n", 1)[0].strip()
        name = f"{i:03d}-{slugify(title)}.md"
        (out / name).write_text("### " + chunk.strip() + "\n", encoding="utf-8")
        written.append(name)
    if tail.strip():
        (out / "tail.md").write_text("## " + tail.strip() + "\n", encoding="utf-8")
        written.append("tail.md")

    print(f"blocks : {len(chunks)}")
    print(f"tail   : {'yes' if tail.strip() else 'no — the closing layers are still missing'}")
    print(f"written: {out}  ({len(written)} files)")
    print("next   : edit the blocks, then build_retelling.py to regenerate retelling.md")


if __name__ == "__main__":
    main()
