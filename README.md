# books — learn a book without reading it

Drop a book file (`.epub`, `.pdf`, `.fb2`, `.txt`, `.md`) into this folder and ask Claude Code:

```
distill Antifragile.epub
```

You get a directory of plain Markdown you own, plus an interactive page you can open in a browser.

## What comes out

| File | What it is |
|------|-----------|
| `spine.md` | The 10-minute read: thesis, 3–7 load-bearing pillars, evidence quality, vocabulary |
| `argument-map.md` | Every claim as a row — what it rests on, how strong the evidence is, best objection |
| `quotes.md` | Verbatim quotes, sourced by chapter, split into load-bearing / sharp / suspect |
| `critique.md` | Adversarial read: contradictions, anecdote-as-data, what the author never addresses |
| `notes/` | Dense per-chapter notes, every claim tagged L1–L5 |
| `cards.md` + `anki.tsv` | Retrieval deck — import straight into Anki |
| `drills.md` | Free-recall prompts, "why is this true?" questions, spaced schedule |
| `apply.md` | Decisions and experiments the book implies |
| `links.md` | How this book agrees with / contradicts the others in your library |
| `page.html` | Interactive page: expandable claim ladder, quote cards, flip-cards, self-graded quiz |

## Why it is built this way

Re-reading and highlighting are near-useless for retention; retrieval practice and asking
"why is this true?" are what work. So the pack does not stop at a summary — it ends with a deck
you get tested on, and a schedule for when.

The other half of the value is the part summary apps skip: an honest critique, a filler audit
(which chapters were padding), and cross-book connections once you have more than one book here.

## Commands

| Ask for | What happens |
|---------|--------------|
| `distill <file>` | Full pipeline (`quick` / `standard` / `deep` depth) |
| `quiz <book>` | Interactive retrieval session in chat; misses are logged and come first next time |
| `ask <book> <question>` | Answers grounded in the notes, cited by chapter |
| `teach <book> <pillar>` | You explain it; Claude finds where your explanation breaks |
| `sync` | Rebuild cross-book connections across the whole library |
| `page <book>` | Rebuild and republish the interactive page |

## Requirements

- Python 3 (stdlib only) for EPUB/FB2/TXT.
- `pdftotext` (poppler) for PDFs. Scanned PDFs without a text layer will not work — convert first.

## Manual script use

```bash
python .claude/skills/book-distill/scripts/extract.py "Book.epub" --out book-slug/source
python .claude/skills/book-distill/scripts/make_cards.py book-slug/cards.md
```
