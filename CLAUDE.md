# books

A personal book-distillation library. Drop a book file in the root; the `book-distill` skill turns
it into a layered study pack plus an interactive page.

## Layout

```
<book-slug>/          one directory per book (see .claude/skills/book-distill/SKILL.md)
  source/             extracted chapters — generated, never hand-edit
  notes/              per-chapter passes
  spine.md  argument-map.md  quotes.md  critique.md
  cards.md  anki.tsv  drills.md  apply.md  links.md
  book.json           run log, coverage, artifact URL
  page.html           the interactive page (republish to the same path to keep the URL)
```

## Conventions

- **Output language is Russian by default** — the user reads and thinks in Russian. Packs are
  *written* in Russian, never translated from an English draft. Follow
  `.claude/skills/book-distill/reference/ru-style.md` and gate publishing on `ru_lint.py`.
  Source books stay in their own language; quotes follow the quote policy in that file.

- Invoke the `book-distill` skill for anything involving a book in this folder: distilling,
  quizzing, asking questions about one, or connecting several.
- Book slugs are lowercase-hyphenated short titles (`antifragile`, not `antifragile-things-that-gain`).
- `[book]` = the author's claim. `[analysis]` = ours. Never merge the two.
- Quotes are copy-pasted from `source/chapters/`, never regenerated from memory. No verbatim
  match means the quote is dropped.
- Never overstate coverage: if chapters were sampled rather than fully read, `book.json` and
  `spine.md` say which.
- Original book files stay in the root and are **not committed** — they are the user's copies.
  `.gitignore` enforces it (`*.epub`, `*.pdf`, `*.fb2`, `*.mobi`, `*.azw3`, `*.djvu`).

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
