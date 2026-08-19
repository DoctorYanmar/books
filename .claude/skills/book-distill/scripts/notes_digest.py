#!/usr/bin/env python3
"""Roll every chapter note up into one small digest the orchestrator can hold.

The chapter notes are written by one subagent per chapter and are far too large to read
back into the main context of a run: forty chapters of notes is the book again. Synthesis
does not need them. It needs the load-bearing claims, the concepts, the tensions and where
each of them came from — which is what this script pulls out.

    python3 notes_digest.py library/<slug> [--levels L1,L2,L3] [--claim-chars 220]

Reads  library/<slug>/notes/*.md
Writes library/<slug>/state/digest.md

Run it after the chapter passes; read the digest, not the notes, in passes 3 and 4.
"""

import argparse
import re
import sys
from pathlib import Path

ROLE = re.compile(r"^\*\*(?:Role in the argument|Роль в аргументе)[:：]\*\*\s*(.+)$", re.I)
SKIP = re.compile(r"^\*\*(?:Skip-safe|Можно пропустить)[:：]\*\*\s*([^<]+)", re.I)
CLAIM = re.compile(r"^[-*]\s+\*\*(L[1-5])\*\*\s*(.+)$")
BULLET = re.compile(r"^[-*]\s+(.+)$")
TERM = re.compile(r"\*\*(.+?)\*\*")
HEAD = re.compile(r"^##\s+(.+)$")

# Section headings are translated with the pack, so match them by their first word.
SECTIONS = {
    "claims": ("claims", "утверждения", "тезисы"),
    "concepts": ("concepts", "понятия", "термины"),
    "quotes": ("quotes", "цитаты"),
    "tensions": ("tensions", "противоречия", "напряжения"),
    "open": ("open", "открытые", "вопросы"),
}


def section_of(title):
    low = title.strip().lower()
    for key, prefixes in SECTIONS.items():
        if any(low.startswith(p) for p in prefixes):
            return key
    return None


def trim(text, limit):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def parse(path, levels, claim_chars):
    note = {"file": path.name, "title": path.stem, "role": "", "skip": "",
            "claims": [], "concepts": [], "tensions": [], "open": [], "quotes": 0}
    current, in_quote = None, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            note["title"] = line[2:].strip()
            continue
        head = HEAD.match(line)
        if head:
            current = section_of(head.group(1))
            continue
        if line.startswith(">"):
            if not in_quote:                    # a quote plus its "— ch.N" line is one quote
                note["quotes"] += 1
            in_quote = True
            continue
        in_quote = False
        m = ROLE.match(line)
        if m:
            note["role"] = trim(m.group(1), 160)
            continue
        m = SKIP.match(line)
        if m:
            note["skip"] = m.group(1).strip()
            continue
        if current == "claims":
            m = CLAIM.match(line)
            if m and m.group(1) in levels:
                note["claims"].append((m.group(1), trim(m.group(2), claim_chars)))
        elif current == "concepts":
            m = BULLET.match(line)
            if m:
                term = TERM.search(m.group(1))
                note["concepts"].append(trim(term.group(1) if term else m.group(1), 60))
        elif current in ("tensions", "open"):
            m = BULLET.match(line)
            if m:
                note[current].append(trim(m.group(1), claim_chars))
    return note


def render(notes, levels):
    out = ["# Digest — what every chapter contributed", "",
           f"Chapters: {len(notes)}. Claim levels kept: {', '.join(sorted(levels))}.",
           "Generated from `notes/` by `notes_digest.py` — do not hand-edit, regenerate.", ""]
    for n in notes:
        out.append(f"## {n['title']}  `{n['file']}`")
        if n["role"]:
            out.append(f"- role: {n['role']}")
        if n["skip"]:
            out.append(f"- skip-safe: {n['skip']}")
        if n["quotes"]:
            out.append(f"- quotes on file: {n['quotes']}")
        for level, claim in n["claims"]:
            out.append(f"- **{level}** {claim}")
        if n["concepts"]:
            out.append("- concepts: " + ", ".join(n["concepts"]))
        for t in n["tensions"]:
            out.append(f"- tension: {t}")
        for q in n["open"]:
            out.append(f"- open: {q}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book", help="library/<slug> (or the notes directory itself)")
    ap.add_argument("--levels", default="L1,L2,L3",
                    help="claim levels to carry into the digest (default L1,L2,L3)")
    ap.add_argument("--claim-chars", type=int, default=220,
                    help="hard cap per claim line, in characters (default 220)")
    ap.add_argument("--out", default=None, help="output path (default <book>/state/digest.md)")
    args = ap.parse_args()

    book = Path(args.book)
    notes_dir = book if book.name == "notes" else book / "notes"
    if not notes_dir.is_dir():
        sys.exit(f"no notes directory at {notes_dir}")
    files = sorted(p for p in notes_dir.glob("*.md") if not p.name.startswith("."))
    if not files:
        sys.exit(f"no chapter notes in {notes_dir}")

    levels = {s.strip().upper() for s in args.levels.split(",") if s.strip()}
    notes = [parse(p, levels, args.claim_chars) for p in files]
    text = render(notes, levels)

    out = Path(args.out) if args.out else (notes_dir.parent / "state" / "digest.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")

    words = len(text.split())
    claims = sum(len(n["claims"]) for n in notes)
    print(f"chapters : {len(notes)}")
    print(f"claims   : {claims}")
    print(f"digest   : {out}  ({words:,} words, ~{round(words * 1.5):,} tokens)")
    if words > 6000:
        print("warning  : digest over 6k words — drop L3 (--levels L1,L2) or tighten the notes")


if __name__ == "__main__":
    main()
