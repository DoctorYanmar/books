#!/usr/bin/env python3
"""Extract a book into per-chapter Markdown files plus a manifest.

Stdlib only (no pip install needed). Supported inputs:

  .epub           parsed via zipfile + OPF spine
  .fb2            parsed as XML (<section> with <title>)
  .pdf            requires `pdftotext` (poppler) on PATH
  .txt / .md      passthrough, split on headings/chapter markers

Usage:
    python extract.py "The Book.epub" [--out DIR] [--target-words 3500]

Output layout. DIR defaults to `source/` beside the book file, which is where it belongs
under the library layout (`library/<book-slug>/<book file>`). A book sitting loose in
`library/` instead gets a directory of its own: `library/<book-slug>/source`.

    <out>/manifest.json          metadata + chapter table (words, est. tokens)
    <out>/chapters/001-slug.md   one file per chapter (or per split block)
    <out>/full.txt               whole book as plain text

Chapters longer than --target-words are split into `NNN-slug--partK.md`
so each file stays inside a comfortable single-read budget.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

BLOCK_TAGS = {
    "p", "div", "br", "li", "tr", "section", "article", "blockquote",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr", "table", "pre",
}
DROP_TAGS = {"script", "style", "head", "nav"}
HEADING_TAGS = {"h1", "h2", "h3"}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def slugify(text: str, maxlen: int = 48) -> str:
    text = re.sub(r"\s+", "-", (text or "").strip().lower())
    text = re.sub(r"[^\w\-]", "", text, flags=re.UNICODE)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return (text[:maxlen] or "untitled").strip("-")


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


class TextExtractor(HTMLParser):
    """Flatten (x)html to text, keeping headings as Markdown."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0
        self.heading: str | None = None
        self.first_heading: str | None = None

    def handle_starttag(self, tag, attrs):
        if tag in DROP_TAGS:
            self.skip_depth += 1
        elif tag in HEADING_TAGS:
            self.heading = tag
            self.parts.append("\n\n## ")
        elif tag in BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_endtag(self, tag):
        if tag in DROP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        elif tag in HEADING_TAGS:
            self.heading = None
            self.parts.append("\n\n")
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip_depth:
            return
        if self.heading and self.first_heading is None:
            stripped = data.strip()
            if stripped:
                self.first_heading = stripped
        self.parts.append(data)

    def result(self) -> str:
        return clean_text("".join(self.parts))


TITLE_WORDS = re.compile(
    r"^(глава|часть|книга|приложение|пролог|эпилог|примечани|"
    r"chapter|part|book|appendix|prologue|epilogue|letter)\b",
    re.I,
)


def guess_title(text: str) -> str | None:
    """Many EPUBs mark chapter titles with styled <p>, not <h1>.

    Fall back to the first line when it looks like a heading: short, no
    sentence-ending punctuation, or starting with a chapter word.
    """
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if TITLE_WORDS.match(line) and len(line) <= 60:
            return line
        if len(line) <= 45 and not line.endswith((".", "!", "?", ",", ";", ":")):
            return line
        return None
    return None


def html_to_text(markup: str) -> tuple[str, str | None]:
    parser = TextExtractor()
    try:
        parser.feed(markup)
        parser.close()
    except Exception:  # malformed markup: fall back to a regex strip
        text = re.sub(r"<[^>]+>", " ", markup)
        return clean_text(html.unescape(text)), None
    return parser.result(), parser.first_heading


# --------------------------------------------------------------------------- #
# format readers -> list[(title, text)]
# --------------------------------------------------------------------------- #

def read_epub(path: Path) -> tuple[dict, list[tuple[str, str]]]:
    meta: dict = {}
    chapters: list[tuple[str, str]] = []
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        container = "META-INF/container.xml"
        opf_path = None
        if container in names:
            root = ET.fromstring(zf.read(container))
            for rf in root.iter():
                if rf.tag.endswith("rootfile"):
                    opf_path = rf.attrib.get("full-path")
                    break
        if opf_path is None:
            opf_path = next((n for n in names if n.endswith(".opf")), None)
        if opf_path is None:
            raise SystemExit("epub: no OPF package file found")

        base = os.path.dirname(opf_path)
        opf = ET.fromstring(zf.read(opf_path))

        for el in opf.iter():
            tag = el.tag.split("}")[-1]
            if tag in {"title", "creator", "language", "publisher", "date"} and el.text:
                meta.setdefault(tag, el.text.strip())

        items: dict[str, str] = {}
        for el in opf.iter():
            if el.tag.endswith("item"):
                items[el.attrib.get("id", "")] = el.attrib.get("href", "")

        spine_ids = [
            el.attrib.get("idref", "")
            for el in opf.iter()
            if el.tag.endswith("itemref")
        ]
        if not spine_ids:
            spine_ids = list(items)

        for idref in spine_ids:
            href = items.get(idref)
            if not href:
                continue
            href = href.split("#")[0]
            full = os.path.normpath(os.path.join(base, href)).replace("\\", "/")
            if full not in names:
                match = next((n for n in names if n.endswith(href)), None)
                if match is None:
                    continue
                full = match
            if not re.search(r"\.x?html?$", full, re.I):
                continue
            markup = zf.read(full).decode("utf-8", "replace")
            text, heading = html_to_text(markup)
            if word_count(text) < 40:  # covers, blank pages, nav stubs
                continue
            title = heading or guess_title(text) or Path(full).stem
            chapters.append((title, text))
    return meta, chapters


def read_fb2(path: Path) -> tuple[dict, list[tuple[str, str]]]:
    root = ET.fromstring(path.read_bytes().decode("utf-8", "replace"))
    meta: dict = {}
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag == "book-title" and el.text:
            meta["title"] = el.text.strip()
        if tag == "lang" and el.text:
            meta.setdefault("language", el.text.strip())

    def node_text(node) -> str:
        return clean_text(" ".join(t for t in node.itertext()))

    chapters = []
    body = next((el for el in root.iter() if el.tag.split("}")[-1] == "body"), None)
    if body is None:
        return meta, [("full-text", node_text(root))]
    for section in body:
        if section.tag.split("}")[-1] != "section":
            continue
        title_el = next(
            (c for c in section if c.tag.split("}")[-1] == "title"), None
        )
        title = node_text(title_el) if title_el is not None else "section"
        text = node_text(section)
        if word_count(text) >= 40:
            chapters.append((title, text))
    if not chapters:
        chapters = [("full-text", node_text(body))]
    return meta, chapters


def read_pdf(path: Path) -> tuple[dict, list[tuple[str, str]]]:
    try:
        out = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError:
        raise SystemExit(
            "pdftotext not found. Install poppler, or convert the PDF to EPUB/TXT first."
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"pdftotext failed: {exc.stderr.decode('utf-8', 'replace')[:400]}")
    text = clean_text(out.stdout.decode("utf-8", "replace"))
    return {"title": path.stem}, split_by_markers(text)


def read_plain(path: Path) -> tuple[dict, list[tuple[str, str]]]:
    text = clean_text(path.read_text("utf-8", "replace"))
    return {"title": path.stem}, split_by_markers(text)


CHAPTER_RE = re.compile(
    r"^(?:#{1,3}\s+.+"
    r"|(?:chapter|part|book|section|глава|часть|раздел)\s+"
    r"(?:\d+|[ivxlcdm]+|one|two|three|four|five|six|seven|eight|nine|ten)\b.*"
    r"|\d{1,2}\.\s+[A-ZА-Я][^\n]{2,60})$",
    re.I | re.M,
)


def split_by_markers(text: str) -> list[tuple[str, str]]:
    """Split flat text on chapter-looking lines; fall back to fixed blocks."""
    marks = [(m.start(), m.group().strip()) for m in CHAPTER_RE.finditer(text)]
    marks = [m for m in marks if len(m[1]) < 90]
    if len(marks) >= 3:
        chapters = []
        for i, (pos, title) in enumerate(marks):
            end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
            body = text[pos:end].strip()
            if word_count(body) >= 60:
                chapters.append((title.lstrip("# ").strip(), body))
        if chapters:
            return chapters
    return [("block", text)]


# --------------------------------------------------------------------------- #
# chunking + writing
# --------------------------------------------------------------------------- #

def split_long(text: str, target_words: int) -> list[str]:
    if word_count(text) <= target_words * 1.35:
        return [text]
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    blocks, current, count = [], [], 0
    for para in paragraphs:
        pw = word_count(para)
        if count and count + pw > target_words:
            blocks.append("\n\n".join(current))
            current, count = [], 0
        current.append(para)
        count += pw
    if current:
        blocks.append("\n\n".join(current))
    return blocks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("book", help="path to .epub/.pdf/.fb2/.txt/.md")
    ap.add_argument("--out", help="output directory (default: source/ beside the book)")
    ap.add_argument("--target-words", type=int, default=3500,
                    help="max words per chapter file before splitting (default 3500)")
    args = ap.parse_args()

    src = Path(args.book).expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"not found: {src}")

    ext = src.suffix.lower()
    reader = {
        ".epub": read_epub,
        ".fb2": read_fb2,
        ".pdf": read_pdf,
        ".txt": read_plain,
        ".md": read_plain,
        ".markdown": read_plain,
    }.get(ext)
    if reader is None:
        raise SystemExit(f"unsupported format: {ext}")

    meta, chapters = reader(src)
    title = meta.get("title") or src.stem
    if args.out:
        out_dir = Path(args.out).resolve()
    elif src.parent.name == "library":
        # dropped loose into the library — give the book a directory of its own
        out_dir = src.parent / slugify(title) / "source"
    else:
        # already in library/<book-slug>/ — the pack goes next to the file
        out_dir = src.parent / "source"
    (out_dir / "chapters").mkdir(parents=True, exist_ok=True)

    entries, total_words = [], 0
    index = 0
    for chapter_title, body in chapters:
        blocks = split_long(body, args.target_words)
        for part_no, block in enumerate(blocks, start=1):
            # drop a leading heading that just repeats the chapter title
            block = re.sub(
                r"^#{1,3}\s*" + re.escape(chapter_title) + r"\s*\n+",
                "",
                block.strip(),
                count=1,
                flags=re.I,
            )
            index += 1
            words = word_count(block)
            total_words += words
            suffix = f"--part{part_no}" if len(blocks) > 1 else ""
            name = f"{index:03d}-{slugify(chapter_title)}{suffix}.md"
            header = f"# {chapter_title}" + (f" (part {part_no})" if suffix else "")
            (out_dir / "chapters" / name).write_text(
                f"{header}\n\n{block}\n", encoding="utf-8"
            )
            entries.append({
                "n": index,
                "file": f"chapters/{name}",
                "title": chapter_title,
                "part": part_no,
                "words": words,
                "est_tokens": round(len(block) / 4),
            })

    (out_dir / "full.txt").write_text(
        "\n\n".join(f"# {t}\n\n{b}" for t, b in chapters), encoding="utf-8"
    )

    manifest = {
        "title": title,
        "author": meta.get("creator"),
        "language": meta.get("language"),
        "source_file": str(src),
        "format": ext.lstrip("."),
        "chapter_files": len(entries),
        "total_words": total_words,
        "est_total_tokens": round(total_words * 1.35),
        "chapters": entries,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"title       : {title}")
    print(f"author      : {meta.get('creator') or '-'}")
    print(f"files       : {len(entries)} in {out_dir / 'chapters'}")
    print(f"words       : {total_words:,} (~{manifest['est_total_tokens']:,} tokens)")
    print(f"manifest    : {out_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
