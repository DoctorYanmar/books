# books

A personal book-distillation library. Drop a book file in `input/`; the `book-distill` skill
files it into `library/<book-slug>/` and turns it into a layered study pack plus an interactive
page, all of it in the book's own directory.

## Layout

Git holds the skill and these docs. **Everything about every book is local only** — `input/` and
`library/` are gitignored in full, because the books are the user's copies and the packs quote
them at length.

```
.claude/skills/book-distill/   the pipeline (see its SKILL.md)
  reference/page-template.html the shared page skeleton — same sections for every new book
  reference/retelling-standard.md how chapter retellings are written and checked
CLAUDE.md  README.md           committed

input/                         the drop zone — gitignored, emptied by ingest
  <Any Book File>.epub         a new book waits here until pass 0 files it away

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

- **`input/` is the only drop zone.** A book file sitting there is not a library entry yet —
  pass 0 derives the slug, creates `library/<book-slug>/`, moves the file in (`mv`, so the
  user's copy is never duplicated), extracts, and leaves `input/` empty again. A book file
  found anywhere else in the tree is treated the same way. Never distill a book in place in
  `input/`, and never leave a copy behind there.

- **The chapter retelling follows `reference/retelling-standard.md`.** It is written for someone
  who has not read the book, so the test it has to pass is comprehension, not compression: a
  claim-first heading, then the position, then the mechanism spelled out step by step, then
  evidence bullets that carry both the fact and what it proves, then a link to the next chapter.
  Every name is glossed where it first appears. Two gates, and the second one matters more:
  `scripts/retell_lint.py` measures the mechanics, and the pass 2.6 **cold read** puts the chapter
  in front of a reader who has never seen the book and fails it on any term they did not know or
  sentence they had to read twice. Fix the prose, never the limit.

- **Every page has the same skeleton.** `library/<slug>/page.html` is built from
  `.claude/skills/book-distill/reference/page-template.html`: one scroll, a collapsible left menu,
  and the same nine sections in the same order — `retelling`, `pillars`, `map`, `quotes`,
  `reception`, `critique`, `recall`, `apply`, `links` — with the same components and the same
  JavaScript. Per book only the content, the depth and the palette change. Never design a page
  layout per book. `scripts/page_lint.py` checks this before publishing. `1984` and `frankenstein`
  predate the skeleton and keep their pages.

- **The pillars and map sections are node graphs, not lists.** Pillars are `<details>` nodes joined
  by labelled edges: solid along the load-bearing chain, dashed to the side pillars and to
  objections. Both graphs carry a path switch and an open-all button, and the map keeps the table
  behind a graph/table switch. Markup and behaviour come from the template — never per book.

- **The palette comes from the book's cover** — dominant colour to `--stamp`, second colour to
  `--ochre`, neutrals biased toward the accent hue, contrast computed in both themes (text ≥4.5:1,
  graph wires ≥3:1). Red is reserved for weak claims and objections, so a red cover yields the
  accent to its second colour and `book.json` says why. That is the one place a pack is allowed to
  look different from its neighbours.

- **Pass 5 requires the `ui-ux-pro-max` skill.** Load it before touching the page; its
  pre-delivery checklist is the gate before publishing.

- **The main context never reads book text.** A big book fills it during the chapter passes and
  every later pass then runs degraded. Chapters, notes and retelling blocks are written by one
  subagent each, in waves, returning receipts instead of text; the run's working memory lives in
  `library/<slug>/state/` (`recon.md`, `digest.md`, `retelling/`, `cold-read.md`). `notes_digest.py`
  rolls the notes up into the digest that synthesis reads, and `build_retelling.py` stitches the
  per-chapter blocks into `retelling.md`. Both files are generated — edit the parts, regenerate.

- Invoke the `book-distill` skill for anything involving a book in this folder: distilling,
  quizzing, asking questions about one, or connecting several.
- Book slugs are lowercase-hyphenated short titles: `library/antifragile/`, not
  `library/antifragile-things-that-gain/`.
- `[book]` = the author's claim. `[analysis]` = ours. Never merge the two.
- Quotes are copy-pasted from `source/chapters/`, never regenerated from memory. No verbatim
  match means the quote is dropped.
- Never overstate coverage: if chapters were sampled rather than fully read, `book.json` and
  `spine.md` say which.
- Nothing under `input/` or `library/` is committed — not the book file, not `source/`, not the
  pack, not the page. `.gitignore` enforces it (`/input/*`, `/library/*`, plus the book extensions
  anywhere in the tree, in case a file is dropped outside by mistake). Never work around it to
  "back up" a pack; the packs are the user's private study material, and the repo is the tooling.

## Machine notes (macOS, moved here 2026-08-17)

This library was built on a Windows box under `c:\claude\books` and moved to
`~/Development/books`. Nothing in it was Windows-specific — the pipeline is Python
stdlib only.

- `scripts/extract.py` needs **`pdftotext` (poppler)** on PATH for PDF input only; EPUB, FB2,
  TXT and MD parse with the standard library. Installed here at `/opt/homebrew/bin/pdftotext`
  (`brew install poppler` if it ever goes missing). Verified on this Mac against `1984.epub`:
  29 chapter files, 85,405 words.
- Run the scripts with the system `python3` (3.13 here). No venv, no pip install.
- Git remote: **public** repo `DoctorYanmar/books`, MIT licensed (opened 2026-08-18 on a fresh
  history; the previous repository was deleted because force-pushed commits containing the 1984 and
  frankenstein packs stayed reachable on GitHub by SHA). The repo is public, the library is not:
  `input/` and `library/` are gitignored in full because the packs quote copyrighted books at
  length. Never commit book content — once pushed it stays reachable by commit SHA even after a
  force-push, which is what forced the repo migration in the first place.
