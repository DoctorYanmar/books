# books

A personal book-distillation library. Drop a book file in `library/`; the `book-distill` skill
turns it into a layered study pack plus an interactive page, all of it in the book's own directory.

## Layout

Git holds the skill and these docs. **Everything about every book is local only** — `library/` is
gitignored in full, because the books are the user's copies and the packs quote them at length.

```
.claude/skills/book-distill/   the pipeline (see its SKILL.md)
CLAUDE.md  README.md           committed

library/<book-slug>/           one directory per book — gitignored, never committed
  <Book File>.epub             the user's own copy
  source/                      extracted chapters — generated, never hand-edit
  notes/                       per-chapter passes
  spine.md  argument-map.md  quotes.md  critique.md
  cards.md  anki.tsv  drills.md  apply.md  links.md
  book.json                    run log, coverage, artifact URL
  page.html                    the interactive page (republish to the same path to keep the URL)
```

## Conventions

- **Output language follows the book** — a Russian edition gives a Russian pack, an English one
  gives an English pack. Override per run with `lang:<code>`. Whatever the language, the pack is
  *written* in it, never translated from a draft in another. For Russian output follow
  `.claude/skills/book-distill/reference/ru-style.md` and gate publishing on `ru_lint.py`.
  Quotes follow the quote policy in that file.

- **Depth is the reader's time budget**, calibrated on a 300–400 page book: `quick` ≈ 30 min
  (3.5–5k words, ~15 cards), `standard` ≈ 1 hour (8–11k words, ~40 cards), `deep` ≈ 2 hours
  (18–24k words, ~80 cards). `deep` earns its length with more of the book — denser retelling,
  more scenes, more quotes, more objections — never with padding.

- Invoke the `book-distill` skill for anything involving a book in this folder: distilling,
  quizzing, asking questions about one, or connecting several.
- Book slugs are lowercase-hyphenated short titles: `library/antifragile/`, not
  `library/antifragile-things-that-gain/`.
- `[book]` = the author's claim. `[analysis]` = ours. Never merge the two.
- Quotes are copy-pasted from `source/chapters/`, never regenerated from memory. No verbatim
  match means the quote is dropped.
- Never overstate coverage: if chapters were sampled rather than fully read, `book.json` and
  `spine.md` say which.
- Nothing under `library/` is committed — not the book file, not `source/`, not the pack, not the
  page. `.gitignore` enforces it (`/library/*`, plus the book extensions anywhere in the tree, in
  case a file is dropped outside by mistake). Never work around it to "back up" a pack; the packs
  are the user's private study material, and the repo is the tooling.

## Machine notes (macOS, moved here 2026-08-17)

This library was built on a Windows box under `c:\claude\books` and moved to
`~/Development/books`. Nothing in it was Windows-specific — the pipeline is Python
stdlib only.

- `scripts/extract.py` needs **`pdftotext` (poppler)** on PATH for PDF input only; EPUB, FB2,
  TXT and MD parse with the standard library. Installed here at `/opt/homebrew/bin/pdftotext`
  (`brew install poppler` if it ever goes missing). Verified on this Mac against `1984.epub`:
  29 chapter files, 85,405 words.
- Run the scripts with the system `python3` (3.13 here). No venv, no pip install.
- Git remote: private repo `DoctorYanmar/books` (created 2026-08-17). The library is private
  because the packs quote copyrighted books at length; keep it that way.
