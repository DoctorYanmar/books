# books — learn a book without reading it

A local pipeline that turns **a book you already own** into your own layered study material:
a chapter-by-chapter retelling, an argument graph, verbatim quotes checked against the source,
an adversarial critique, flashcards and a quiz — plus one interactive page to read it all in.

Drop a book file (`.epub`, `.pdf`, `.fb2`, `.txt`, `.md`) into `input/` and ask Claude Code:

```
distill
```

Naming the file works too (`distill Antifragile.epub`), but with one book waiting in `input/`
there is nothing to name. Ingest files the book away for you: it derives a slug, moves the file
into `library/<slug>/`, extracts the text, and leaves `input/` empty for the next book.

You get a directory of plain Markdown you own, plus an interactive page you can open in a browser —
all of it inside the book's own folder:

```
input/                    empty again after ingest
library/antifragile/
  Antifragile.epub        your copy, moved here
  source/                 the extracted text
  notes/  spine.md  quotes.md  critique.md  cards.md  ...
  book.json  page.html
```

**`input/` and `library/` are gitignored in full.** Books and packs stay on your machine; the repo
carries the pipeline and nothing else.

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
| `page.html` | Interactive page: nine sections from retelling to deck, same skeleton for every book |

## The retelling

The chapter retelling is written for someone who will never open the book, and it is held to a
standard rather than to taste. Every chapter gets a claim-like heading, two to four blocks instead
of one paragraph, connectives that name a cause instead of "then", a stated stake, and a line
handing a question to the next chapter. `scripts/retell_lint.py` measures all of that — word
budget, sentence length, density of names and numbers, chain openers, causal connectives, topic
chaining — and pass 3 does not start until it is clean. The reasoning and the sources are in
`.claude/skills/book-distill/reference/retelling-standard.md`.

## The page

Every book gets the same page: one scroll, a collapsible left menu, and nine sections in a fixed
order — **retelling · pillars · map · quotes · reception · critique · recall · apply · links**.
The visible labels are translated with the pack; the ids and the order never change, so the second
pack reads like the first and
you never hunt for a section. Depth changes how densely the sections are filled; it never changes
how many there are.

Two of the nine are graphs rather than prose. **Pillars** draws the thesis as a root node and
the pillars as nodes below it: solid edges run along the load-bearing chain, dashed ones lead to
the side pillars the thesis survives without, and every edge is labelled with the step it makes. A
switch dims everything off the main path. **Map** gives each pillar a node holding a solid branch
of supports and a dashed branch of objections, each objection labelled with the claim it attacks;
the dense table is still there behind a switch. Nodes are plain `<details>` elements in normal
document flow — keyboard and deep links work, and nothing can overlap at any width.

What *is* per book is the colour: the palette is taken from that edition's cover — dominant colour
becomes the accent, the second colour carries the side paths and the `[analysis]` marks, the neutrals
get biased toward the accent hue. One reserved hue: red already means *weak claim* on this page, so
a red cover gives up its accent to the cover's second colour, and `book.json` records why. Two packs
never look the same, and each looks like its book.

The skeleton lives in `.claude/skills/book-distill/reference/page-template.html` and is committed
with the pipeline; `scripts/page_lint.py` checks a built page against it — section ids and order,
every component, the menu, both themes, tag balance, and that the script parses. Pass 5 fills its placeholders and runs the
[`ui-ux-pro-max`](https://github.com/mrgoonie/ui-ux-pro-max-skill) skill, which is **required** for
that pass — it carries the contrast, focus, touch-target and typography checks the page is held to,
and its pre-delivery checklist gates publishing.

`1984` and `frankenstein` were distilled before this skeleton existed and keep the pages they have.

## Why it is built this way

Re-reading and highlighting are near-useless for retention; retrieval practice and asking
"why is this true?" are what work. So the pack does not stop at a summary — it ends with a deck
you get tested on, and a schedule for when.

The other half of the value is the part summary apps skip: an honest critique, a filler audit
(which chapters were padding), and cross-book connections once you have more than one book here.

## Commands

| Ask for | What happens |
|---------|--------------|
| `distill [file] [depth] [lang:xx]` | Full pipeline on whatever is in `input/` — see **Depth** and **Language** below |
| `quiz <book>` | Interactive retrieval session in chat; misses are logged and come first next time |
| `ask <book> <question>` | Answers grounded in the notes, cited by chapter |
| `teach <book> <pillar>` | You explain it; Claude finds where your explanation breaks |
| `sync` | Rebuild cross-book connections across the whole library |
| `page <book>` | Rebuild and republish the interactive page |

## Depth

Depth is how long *you* spend with the finished pack, on an ordinary 300–400 page book:

| Depth | You spend | Pack | Cards | What it reads |
|-------|-----------|------|-------|---------------|
| `quick` | ~30 min | 3.5–5k words | ~15 | intro, conclusion, pillar chapters |
| `standard` (default) | ~1 hour | 8–11k words | ~40 | every chapter, one pass |
| `deep` | ~2 hours | 18–24k words | ~80 | every chapter, plus a re-read per pillar |

`deep` is longer because it carries *more of the book* — chapter-by-chapter retelling at full
density, 12–16 scenes in close-up, 40–50 quotes, every pillar met with its strongest named
objection — not because it says the same things at greater length.

## Language

The pack is written **in the language of the book** by default. Override per run:

```
distill deep lang:ru
```

Both the book's own language and the pack's are recorded in `book.json`.

## Requirements

- Python 3 (stdlib only) for EPUB/FB2/TXT; Pillow only if you want the cover quantised for you.
- `pdftotext` (poppler) for PDFs. Scanned PDFs without a text layer will not work — convert first.
- The `ui-ux-pro-max` skill installed — pass 5 requires it.

## Manual script use

```bash
python .claude/skills/book-distill/scripts/extract.py "library/book-slug/Book.epub"
python .claude/skills/book-distill/scripts/make_cards.py library/book-slug/cards.md
```

## Scope, and what this tool is not

This repository contains the pipeline: Markdown instructions and Python scripts. It contains no
books, no extracted text and no generated study packs, and it never will — `input/` and `library/`
are gitignored in full, and the common ebook extensions are ignored anywhere in the tree.

- **You supply the book.** Use a copy you lawfully own. The pipeline reads files you already have;
  it does not download books, and it does not read, remove or work around DRM or any other access
  control. A DRM-protected file simply will not parse.
- **Everything it produces stays on your machine.** Packs quote books at length, which is exactly
  why they are private study material and not something this repo publishes. If you choose to
  publish a pack you built, that is your decision and your responsibility under the copyright law
  that applies to you.
- **It sends chapters to an AI assistant.** That is how the analysis is written. Check what your
  provider's terms say about the content you submit and whether your account tier trains on it —
  API and commercial tiers generally do not, consumer tiers may depend on a setting.
- **The MIT license covers this repository's code and documentation only.** It grants no rights
  whatsoever over any book the pipeline reads or any output it produces.

## License

[MIT](LICENSE). See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request and
[SECURITY.md](SECURITY.md) for reporting a vulnerability.
