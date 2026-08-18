---
name: book-distill
description: Turn a book file (EPUB/PDF/FB2/TXT) into a layered, interactive study pack — thesis spine, primary/secondary claim ladder, verbatim quotes, adversarial critique, retrieval cards, and a published interactive page. Use when the user drops a book in this folder or asks to distill, absorb, study, summarize, or "learn without reading" a book, build flashcards or a quiz from a book, or connect several books together.
---

# book-distill

Convert a book into an owned, layered knowledge pack the user can absorb in half an hour, an
hour, or two — whichever the run's depth asks for — instead of reading it, plus a retrieval loop
so it actually sticks.

The design rests on one fact from learning research: **re-reading and highlighting are low-utility;
retrieval practice and elaborative interrogation are high-utility.** So a summary alone is a
failed deliverable. Every run must end with material the user is *tested* on, not just shown.

## Layer model (this is what "primary vs secondary points" means here)

Every claim in the book is tagged with exactly one level:

| Level | Name | Definition | Budget |
|-------|------|------------|--------|
| **L1** | Thesis | The one sentence the whole book exists to defend | 1 |
| **L2** | Pillars | Load-bearing claims — remove one and the thesis collapses | 3–7 |
| **L3** | Support | Sub-claims, mechanisms, models, frameworks that prop up an L2 | 5–15 per L2 |
| **L4** | Evidence | Studies, data, anecdotes, case studies, historical examples | cited, not retold |
| **L5** | Texture | Digressions, author biography, throat-clearing, repetition | **named and dropped** |

L5 is explicitly listed (not silently discarded) — telling the user which 40% of the book was
filler is part of the value. Roughly: business/self-help books run L5-heavy; dense theory runs
L3-heavy.

Two provenance tags, used everywhere and never blurred:

- `[book]` — the author's own claim, restated.
- `[analysis]` — your reading: inference, objection, connection, real-world example.

## Directory layout

Book files live in `library/` — the user's own copies, never committed, never edited. The pack for
each book lives in its own directory at the repo root:

```
library/<Book File>.epub   the original, local only (the whole of library/ is gitignored)

<book-slug>/
  book.json          title, author, run log, depth, artifact URL, status
  source/            manifest.json, chapters/NNN-*.md, full.txt   (generated, do not edit,
                     gitignored — it is the book's own text, so it stays local like the file it
                     came from)
  notes/NNN-*.md     per-chapter dense notes + quotes            (pass 2)
  spine.md           L1 + L2 ladder, 10-minute read              (pass 3)
  argument-map.md    claim -> evidence -> strength -> objection   (pass 3)
  quotes.md          verbatim, sourced, ranked                    (pass 3)
  critique.md        weak points, contradictions, blind spots     (pass 3)
  cards.md           retrieval deck (Q:/A:/T: format)             (pass 4)
  anki.tsv           generated from cards.md                      (pass 4)
  drills.md          free-recall prompts + "why is this true?"    (pass 4)
  apply.md           decisions/experiments this book implies      (pass 4)
  links.md           cross-book connections                       (pass 6)
```

## Pipeline

### Pass 0 — Ingest

```bash
python .claude/skills/book-distill/scripts/extract.py "library/<book file>" --out "<book-slug>/source"
```

If the user points at a book sitting somewhere else — the repo root, Downloads, an argument to
`distill` — move it into `library/` first, then extract. Books belong in one place.

Read `source/manifest.json`. Report to the user: title, author, language, chapter count, total
words, estimated tokens, and the depth and output language you propose. If `est_total_tokens` > 400k, say so and default
to `standard` depth with sampling (see Depth).

PDF caveat: chapter splitting is regex-based on flat text and can be wrong. Check the chapter
titles in the manifest; if they look like garbage, tell the user and treat the split as arbitrary
blocks rather than pretending they are chapters. Scanned PDFs with no text layer produce near-empty
files — say so instead of hallucinating content.

### Pass 1 — Recon (cheap, orients everything else)

Read only: front matter, TOC, introduction, first chapter, last chapter, conclusion.
Produce a **provisional** L1 thesis and candidate L2 pillars. Do not write files yet — hold this
in context. It makes the chapter passes classify correctly instead of summarizing blindly.

### Pass 2 — Chapter passes

For each chapter file, write `notes/NNN-<slug>.md` using the template in
`reference/layers.md`. Non-negotiables:

- **Quotes are copy-paste, never generated.** Pull the exact string from the chapter file. If you
  cannot find it verbatim, the quote does not exist — drop it. Every quote carries `— ch.N`.
- Bulleted, terms in **bold**, one idea per bullet. No paragraph prose.
- Tag every bullet L1–L5 and `[book]`/`[analysis]`.
- Record contradictions with earlier chapters as you hit them; you will need them in `critique.md`.
- Do not read the whole book into context at once. One chapter file per Read; write its notes;
  move on. Carry forward only the running thesis/pillar list.

### Pass 2.5 — Retelling (never skip this)

**The pack fails if a reader who has never opened the book cannot say what is in it.** Analysis
without content is unreadable: pillars, evidence strength and critique mean nothing to someone who
does not yet know what happens, who is who, and how it ends.

So before any synthesis, write the retelling layer — and put it **first** in every output, ahead of
the thesis:

- `retelling/overview` — what the book is, in the ordinary sense: setting, premise, shape, ending
  stated plainly. No spoiler-hiding. A reader stops here and already knows the book.
- `retelling/cast` — who is who, one line each, with their function in the story.
- `retelling/world` — for speculative or technical books: the rules of the world, the institutions,
  the vocabulary the book invents.
- `retelling/plot` — sequential retelling, part by part and chapter by chapter. Dense, concrete,
  with the scenes that actually happen — not "the protagonist struggles with the regime". This is
  the longest single piece of the pack and it is what makes the reader feel they have read the book.
- `retelling/scenes` — 6–10 key scenes in close-up, each with a verbatim quote.
- `retelling/timeline` — the order of events when the book scrambles it.

Templates in `reference/layers.md`. Only after this comes the spine, the map and the critique.

### Pass 3 — Synthesis

From the notes only (not the raw book), write `spine.md`, `argument-map.md`, `quotes.md`,
`critique.md`. Templates in `reference/layers.md`.

`critique.md` is what separates this from every summary app — be genuinely adversarial:
what would have to be true for the thesis to fail, which evidence is anecdote dressed as data,
what the author never addresses, where the book contradicts itself, who disagrees and why.

### Pass 3.5 — Reception (what the known critics said)

A pack that contains only your own reading is a closed room. Books of any standing have a documented
argument around them, and the reader wants it: contemporary reviews, the famous objections, the
writers who answered back, the book's afterlife.

**This is the one layer that must be researched, never recalled.** Attributing an invented opinion or
a misremembered quote to a real critic is the worst failure mode in the whole pack — worse than a
wrong claim of your own, because it is unfalsifiable-looking and defamatory. Rules:

1. Search the web for the reception before writing a word of it. No source, no entry.
2. Quote sparingly and briefly — a phrase, not a paragraph — always with critic, publication and date.
3. When you cannot verify a quotation, state the position in your own words and say where it is argued.
4. List the sources used at the bottom of the page.
5. If a documented critic made a point you had already written as your own analysis, **credit them and
   correct the earlier page.** Convergence is not authorship.

Organise it as: contemporary reviews → major dissenting critiques → later writers answering back →
the book's life in the reader's own language and culture → afterlife in public argument → a short
map of how the lines of dispute divide. Close with your own note on which objection actually lands
against which pillar.

### Pass 4 — Retrieval layer

Write `cards.md` and `drills.md` per `reference/layers.md` card rules, then:

```bash
python .claude/skills/book-distill/scripts/make_cards.py "<book-slug>/cards.md"
```

Card count by depth: quick ~15, standard ~40, deep ~80. Cards test *understanding and transfer*,
never trivia ("what year was the study?" is a bad card).

### Pass 5 — Interactive page

Build a single self-contained HTML page and publish it with the Artifact tool.
**Load the `artifact-design` skill before writing it.** Required behavior is specified in
`reference/interactive.md`: layered progressive disclosure (thesis → pillars → support →
evidence), quote cards, flip-cards, a self-graded quiz, and the critique panel.
Record the returned URL in `book.json`.

### Pass 6 — Cross-book links (only when ≥2 books exist)

Read the other books' `spine.md` files. Write/refresh `links.md` on both sides: agreements,
direct contradictions, and where one book answers a question another leaves open. This is the
syntopical layer — it is the main thing single-book tools cannot do.

## Output language

**The pack is written in the language of the book.** That is the default: a Russian edition of
*1984* produces a Russian pack, an English edition of *Antifragile* produces an English one. The
user overrides it per run when they want something else.

How the language is decided, in this order:

1. An explicit flag on the request — `lang:en`, `lang:ru`, "на русском", "in English". Always wins.
2. `language` in `source/manifest.json` — EPUB and FB2 carry it in their metadata.
3. When that is missing or obviously wrong (PDF and TXT usually have no metadata), judge from the
   text of `source/full.txt`.

Say which language you picked, and why, in the ingest report. Record it in `book.json` as
`output_language`, next to the book's own `language`.

The book keeps its own language regardless of the pack's: a book in English is read in English even
when the pack is written in Russian. Never write a draft in one language and translate it — the
calque survives every edit pass. Write in the target language from the first sentence.

Quotes are the one thing that cannot be written, only sourced. Pick a policy per book and state it
on the page:

1. An edition in the output language exists → run `extract.py` on it too and pull quotes verbatim
   from it, naming translator and year.
2. No such edition → quote the original verbatim and add a working gloss, marked as a gloss.
3. Book is already in the output language → normal verbatim rules.

### Russian output

Load `reference/ru-style.md` before writing a single Russian sentence — it carries the
banned-construction list, the quote policy, terminology and typography. Before publishing a Russian
page:

```bash
python .claude/skills/book-distill/scripts/ru_lint.py "<book-slug>/page.html"
```

Fix every finding, then reread the opening paragraph of each page by hand — the linter catches
mechanics, not intonation, and generated prose gives itself away in openings.

### Other languages

Same discipline, no linter. The templates in `reference/layers.md` show Russian headings in places;
translate the headings into the output language and keep the structure identical — the page builder
and the `quiz`/`ask` modes parse the structure, not the words. Reread the openings by hand there too.

## Depth

Depth is a **study-time budget for the reader**, not an effort dial for the run. The numbers below
are calibrated on an ordinary 300–400 page book — roughly 90–120k words, 25–40 chapters. For a book
far outside that range, scale the word budgets with the source length and say so in `book.json`.

| Depth | Reader spends | Pack size | Cards | Chapter passes |
|-------|---------------|-----------|-------|----------------|
| `quick` | ~30 min | 3.5–5k words | ~15 | intro, conclusion, and the chapters carrying pillars |
| `standard` (default) | ~1 hour | 8–11k words | ~40 | every chapter file, one pass each |
| `deep` | ~2 hours | 18–24k words | ~80 | every chapter, plus a re-read pass per pillar |

The word budgets come from the time: ~45 minutes of reading plus ~15 of retrieval for `standard`, at
roughly 180 words per minute on dense study prose. Count the whole pack — the page is what the
reader actually spends the hour on.

**quick** — triage. Retelling covers the overview, the cast, and the shape of the plot at part
level. Spine with thesis and pillars. 8–10 quotes. No argument map, no reception, no `apply.md`,
no `links.md`. It answers one question: is this book worth the full pack?

**standard** — the normal run. Every layer in the pipeline. Retelling covers every chapter in 2–3
sentences, 6–8 scenes in close-up, 20–25 quotes. Critique and reception both present, both compact.

**deep** — for a book the user will act on. Everything `standard` has at roughly double the volume,
and the extra volume goes into *content*, not commentary:

- retelling at 5–8 sentences per chapter, carrying the subplots, minor characters and second-order
  detail that `standard` drops;
- 12–16 scenes in close-up, each with a verbatim quote;
- 40–50 quotes, including the ones that only work in context;
- a second pass per pillar: re-read the chapters it rests on, follow the evidence chain to its
  source, note what the author never says;
- expanded critique — every pillar gets its strongest named objection, not only the weak ones;
- reception researched wider: the dissenters, the writers who answered back, the afterlife;
- `apply.md` with concrete experiments and `links.md` against every other book in the library.

The failure mode of `deep` is padding: longer restatement of the same claim, more adjectives, more
throat-clearing about method. A deep pack is longer because it carries **more of the book** — more
scenes, more names, more evidence, more objections. If a deep section says nothing `standard` did
not, cut it.

For books over ~400k estimated tokens, `standard` may sample: full passes on chapters carrying L2
pillars, one-paragraph passes on the rest. **Say in `book.json` and to the user exactly which
chapters were sampled** — never let a partial pass look complete. `deep` does not sample: if the
book is too large for full passes, say so and run `standard`.

## Modes

Invocation, with both modifiers optional and order-free:

```
distill <book> [quick|standard|deep] [lang:<code>]
```

`quick`/`standard`/`deep` set the depth (default `standard`); `lang:` overrides the output
language (default: the book's own, see **Output language**). Plain requests carry the same
meaning — "по-английски", "in Russian", "the deep one" — read them as the flags they are.

The user can ask for a single stage instead of the whole pipeline:

- **distill** (default) — passes 0–6.
- **quiz** — read `cards.md`/`drills.md`, run an interactive session in chat: ask, wait, grade
  the answer against the notes, cite the chapter, adapt difficulty. Log misses at the bottom of
  `drills.md` under `## Misses (YYYY-MM-DD)`; those come first next session.
- **ask** — Q&A grounded in `notes/` and `source/chapters/`. Always cite `ch.N`; when the notes
  do not cover it, go back to the chapter file rather than guessing.
- **page** — rebuild/republish the interactive page only.
- **sync** — pass 6 only, across all books.
- **teach** — Feynman mode: the user explains a pillar in their own words, you find exactly where
  the explanation breaks and quote the passage that fixes it.

## Rules

1. Never invent a quote, a study, a number, or a page reference.
2. Never blur `[book]` and `[analysis]`.
3. Prefer the author's own vocabulary for concept names; define jargon once, in `spine.md`.
4. If the book is bad — thin, derivative, evidence-free — say so in `critique.md` and cut the
   pack short rather than inflating it.
5. State coverage honestly in `book.json`: which chapters got full passes, which were sampled.
6. Book files live in `library/` and never leave it. `library/` and every `source/` directory are
   gitignored — the book's own text stays on the user's machine and is never committed or pushed.
