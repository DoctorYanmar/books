# Contributing

Thanks for looking. This repository is the pipeline only — a set of Markdown instructions and
Python scripts that turn a book *you already own* into your own study material. No book, no
extracted text and no generated pack is ever committed here, and pull requests that add any are
declined on sight.

## Before you open a pull request

**Never commit book content.** `input/` and `library/` are gitignored in full, and the common
ebook extensions are ignored anywhere in the tree. Do not work around this, not even to share an
example. If you need an example in the docs, invent one or use a placeholder — the existing
templates do exactly that.

**Run the checks.** They are plain Python 3 with no dependencies:

```bash
python3 .claude/skills/book-distill/scripts/page_lint.py   library/<slug>/page.html
python3 .claude/skills/book-distill/scripts/retell_lint.py library/<slug>/retelling.md --depth deep
python3 .claude/skills/book-distill/scripts/ru_lint.py     library/<slug>/page.html      # Russian packs
```

`page_lint.py` and `retell_lint.py` exit non-zero on a violation. **Fix the output, never the
limit** — the limits in `reference/retelling-standard.md` each carry the research they come from,
so raising one is a change to the standard and needs its own argument in the pull request.

## What changes are welcome

- **A new output language.** Add an entry to `LANGS` in `retell_lint.py` (slot labels, chain
  openers, causal markers, linkers) and a label row in `reference/retelling-standard.md`. Nothing
  else should need touching.
- **A new input format** in `scripts/extract.py`. Standard library only, please — the pipeline
  runs on a stock Python 3 with no virtualenv, and PDF is the single exception (it shells out to
  `pdftotext`).
- **Sharper checks** in any of the three linters, especially ones that catch a real failure the
  current rules miss. Bring an example of prose that should fail and currently passes.
- **Corrections to the research** behind the standard. Every limit cites a source; if a source
  says something different from what the file claims, that is a bug worth filing.

## What is out of scope

- Anything that reads DRM-protected files or removes access controls.
- Anything that publishes, hosts, or redistributes book content.
- Per-book page designs. Every book renders from the one skeleton in
  `reference/page-template.html`; `page_lint.py` enforces it.

## Style

Prose, comments, identifiers and linter output are English. Russian appears only as data — the
word lists in `ru_lint.py`, the terminology in `reference/ru-style.md`, and the `ru` entry in the
label table. Keep it that way in any language you add: the tool speaks English, the data speaks
whatever it checks.

Commit messages: a short imperative summary line, then a body explaining *why*, not *what*.
