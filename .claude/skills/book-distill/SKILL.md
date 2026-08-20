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

Books arrive in `input/` — that is the drop zone and the only place the user has to think about.
Everything about a book, once ingested, lives in one directory: `library/<book-slug>/`. The book
file, the extracted text, the pack, the page. **`input/` and `library/` are both gitignored in
full** — the books are the user's own copies and the packs quote them at length, so none of it is
ever committed or pushed. Only the skill and the repo docs live in git.

```
input/                 the drop zone: a new book file waits here, and only until pass 0 runs

library/<book-slug>/
  <Book File>.epub   the original, exactly as the user has it — never edited, never renamed
  book.json          title, author, language, run log, depth, artifact URL, status
  source/            manifest.json, chapters/NNN-*.md, full.txt   (generated, do not edit)
  notes/NNN-*.md     per-chapter dense notes + quotes            (pass 2)
  state/             the run's working memory, kept on disk and not in context
    recon.md         provisional thesis + pillar candidates       (pass 1)
    digest.md        every chapter's L1-L3 claims, generated      (pass 2)
    retelling/       front.md, NNN-*.md blocks, tail.md           (pass 2.5)
    cold-read.md     one line per chapter: pass, or what failed   (pass 2.6)
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

Slugs are lowercase-hyphenated short titles: `library/antifragile/`, not
`library/antifragile-things-that-gain-from-disorder/`.

The interactive page is built from a shared template, not written from scratch:

```
.claude/skills/book-distill/reference/
  page-template.html   the page skeleton every new book uses: same sections, same components, same JS
  interactive.md       what each view holds, how the palette is derived, how to verify
```

## Context budget — why the passes are shaped the way they are

A 400-page book does not fit in the run's context, and the pipeline breaks in a specific way when
you pretend it does: the chapter passes fill the main context with book text, and everything after
them — retelling, synthesis, cards, page — runs on a context that is already full and starts
degrading or compacting. The pack gets thinner exactly where the book is longest.

So the run is split in two roles, and the split is not optional.

**The orchestrator (this context) never reads book text.** Not `source/chapters/*`, not
`source/full.txt`, not a whole file under `notes/`, not `retelling.md` end to end. What it may read:
`source/manifest.json`, `state/*`, linter output, `book.json`, and single chapter blocks when it is
repairing one flagged sentence.

**Subagents read book text and write files.** Every chapter-sized piece of work is one subagent with
one chapter's worth of input. It writes its output to disk and returns a receipt — never the text it
just wrote. A subagent that returns its file has defeated the entire arrangement, so say so in the
prompt: *write the file, then reply with at most N lines.*

Between the two sits the working memory on disk, `state/`, which is small on purpose: `recon.md`
carries the provisional thesis into every chapter agent, `digest.md` carries every chapter's claims
back out. The orchestrator holds those two files; the book stays on disk.

Three practical rules that come out of this:

- **Fan out in waves of 4–6.** Every agent's receipt lands in this context, and so does every tool
  call's own overhead. Waves keep that bounded and keep a bad prompt from being paid for forty times.
- **Never put a linter loop inside a writing agent.** One write, then the caller runs the linter once,
  then the caller sends back only what failed. The first version of this pipeline let each writer
  iterate against the linter on its own: 3.2M tokens across 44 agents for eleven chapters.
- **Nothing is written twice.** Chapter blocks are assembled by script, the page's chapter articles
  are generated from the retelling, the digest is generated from the notes. Regenerate, never retype.

## Pipeline

### Pass 0 — Ingest

Ingest is what turns a loose file into a library entry. It always runs first, even when the user
names the book, and it always ends with the file inside `library/<book-slug>/`.

1. **Find the book.** With no filename in the request, list `input/` — that is where books are
   dropped. One file there is the book; several means asking which, unless the user said "all of
   them". A path in the request wins over `input/`; a book found loose in the repo root or handed
   over from anywhere else on disk is handled exactly the same way from step 2 on.
2. **Derive the slug.** Read the title and author out of the file's metadata rather than its
   filename — download names are mangled and often truncated mid-word. The slug is a short,
   lowercase-hyphenated title, transliterated into ASCII for non-Latin scripts
   (`злые-самаритяне` → `zlye-samaritiane`), and it is the short title only:
   `library/antifragile/`, not `library/antifragile-things-that-gain/`. Tell the user the slug you
   picked. If `library/<slug>/` already exists and holds a pack, stop and ask — never overwrite an
   existing pack, and never silently distil the same book twice under two slugs.
3. **Move, do not copy.** `mkdir -p library/<book-slug>/` and `mv` the file in, keeping its
   original filename intact — the user has one copy of the book and it stays one copy. `input/`
   is left empty (bar `.gitkeep`) so the next drop is unambiguous. Never extract or distil a book
   in place in `input/`.
4. **Extract.**

```bash
python .claude/skills/book-distill/scripts/extract.py "library/<book-slug>/<book file>"
```

The default output is `source/` beside the book file, which is where it belongs — no `--out`
needed. One book, one directory, everything in it.

Read `source/manifest.json`. Report to the user: title, author, language, chapter count, total
words, estimated tokens, and the depth and output language you propose. If `est_total_tokens` > 400k, say so and default
to `standard` depth with sampling (see Depth).

PDF caveat: chapter splitting is regex-based on flat text and can be wrong. Check the chapter
titles in the manifest; if they look like garbage, tell the user and treat the split as arbitrary
blocks rather than pretending they are chapters. Scanned PDFs with no text layer produce near-empty
files — say so instead of hallucinating content.

### Pass 1 — Recon (cheap, orients everything else)

One subagent, not the orchestrator. It reads front matter, TOC, introduction, first chapter, last
chapter and conclusion — five or six chapter files, which is already more book text than the main
context should ever hold — and writes `state/recon.md`:

- the **provisional** L1 thesis, one sentence;
- 3–7 candidate L2 pillars, one line each, with the chapters each is expected to live in;
- the book's own vocabulary: the terms it coins or redefines, one line each;
- the shape: parts, narrator, whether chapters are argumentative (template A) or narrative (B).

Cap it at 500 words — it is pasted into every chapter agent that follows, so every word is paid for
once per chapter. The agent returns the thesis line and the pillar list, nothing else.

Read `state/recon.md` yourself; it is the one piece of book-derived text the orchestrator carries.
It makes the chapter passes classify correctly instead of summarizing blindly.

### Pass 2 — Chapter passes (one agent per chapter)

**One subagent per chapter file, in waves of 4–6.** The orchestrator never opens a chapter. Each
agent gets: the path to its own chapter file, the path where its notes go, `state/recon.md` inline,
the depth, the output language, and the notes template from `reference/layers.md`. It gets no other
chapter, no other notes file, and no page.

It writes `notes/NNN-<slug>.md` and returns a receipt of at most 6 lines: the chapter's role in the
argument, which candidate pillar it feeds (or that it feeds none), whether it is skip-safe, and any
contradiction it noticed with the thesis it was handed. Not the notes.

Non-negotiables inside the agent's prompt:

- **Quotes are copy-paste, never generated.** Pull the exact string from the chapter file. If you
  cannot find it verbatim, the quote does not exist — drop it. Every quote carries `— ch.N`.
- Bulleted, terms in **bold**, one idea per bullet. No paragraph prose.
- Tag every bullet L1–L5 and `[book]`/`[analysis]`.
- Record contradictions with the thesis in `state/recon.md`, and with any earlier chapter it can see
  named there; the cross-chapter contradictions the agent cannot see are found later, in the digest.
- The chapter file is read once. Do not re-read it to polish.

Two things a chapter agent cannot do, because it only sees one chapter: it cannot know a name was
already glossed elsewhere, and it cannot see a contradiction with a chapter it never read. Both are
handled after the fan-out, not by widening the agent's input.

When every wave is done, roll the notes up into the digest:

```bash
python3 .claude/skills/book-distill/scripts/notes_digest.py library/<slug>
```

It writes `state/digest.md` — every chapter's L1–L3 claims, concepts, tensions and quote count, and
nothing else, with the source note named on each entry. **That file, not `notes/`, is what passes 3
and 4 read.** It warns when it passes 6k words; at that size drop to `--levels L1,L2` rather than
letting synthesis start on a full context.

Read the digest once and settle the argument on it: which candidates survive as L2 pillars, which
chapters carry each, which tensions are real contradictions. Rewrite `state/recon.md` into the
confirmed spine sketch — that is what pass 2.5 hands to the retelling agents.

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
- `retelling/plot` — the chapter-by-chapter retelling, written to the standard below. This is the
  longest single piece of the pack and the part the reader judges everything else by.
- `retelling/scenes` — 6–10 key scenes in close-up, each with a verbatim quote.
- `retelling/timeline` — the order of events when the book scrambles it.
- `retelling/self-check` — 3–5 questions the reader answers from memory before leaving the section,
  one per point. The research is blunt: the gain comes from *producing* a summary, not reading
  one, so the retelling must end by making the reader produce something.

**The chapter retelling follows `reference/retelling-standard.md`, and it is not optional.** Two
templates, chosen by what the chapter is:

- **Template A, argumentative chapter** — `Claim` (the chapter's claim as a proposition, not its
  topic) → **the position** (what the chapter argues against, every term glossed as it appears) →
  **the mechanism** (why the claim follows, step by step, joined by because/therefore/but) →
  `What holds it up` (evidence bullets, each carrying both halves: the fact, then what it proves)
  → `Left open` → `Next` (the question handed to the next chapter). The two middle blocks get
  labels written fresh for that chapter, and they carry 140–260 words at `deep` — that middle is
  the part the reader cannot reconstruct alone, and cutting it is how the first version of this
  pipeline produced retellings nobody could read.
- **Template B, narrative chapter** — `Where we are` (only if the setting changed) →
  `What happens` (the turn, built with "therefore" and "but") → `Stakes` (what is lost if it
  fails) → `Next`. Labels are translated with the pack; the mapping lives in the standard.

The unit is the point, not the chapter: split a chapter into 2–4 blocks, merge two thin
chapters into one entry. Chapter headings are claim-like — the book's own chapter title is not
enough, because a title names a topic and the reader needs the point.

**It is written one block per agent, and assembled by script.** The retelling is the longest file in
the pack — at `deep` it is the book's length problem all over again — so no context writes it whole:

1. **Blocks.** One subagent per chapter, waves of 4–6, writing `state/retelling/NNN-<slug>.md`. Each
   gets its own chapter file, its own `notes/NNN-*.md`, the confirmed spine sketch, the depth, the
   language, and `reference/retelling-standard.md`. The file starts with `### ` and contains that
   entry only. The agent returns three lines: heading, word count, template A or B.
2. **Front and tail.** Two more agents, off `state/digest.md` and the spine sketch — never off the
   chapters. One writes `state/retelling/front.md` (what the book is, cast, how the world works),
   one writes `state/retelling/tail.md` (key scenes, timeline, self-check). The scenes agent needs
   verbatim quotes, so it gets the chapter files its scenes come from, named by the digest.
3. **Assemble.**

```bash
python3 .claude/skills/book-distill/scripts/build_retelling.py library/<slug>
```

It stitches front matter, the numbered blocks in order and the tail into `library/<slug>/retelling.md`,
and refuses to write a file the linter would reject outright: a block that does not open with `### `,
a duplicated number, an empty front matter. It warns on gaps in the numbering. Rerun it after every
block edit — `retelling.md` is generated, so edit the block file, never the assembled file.

Because the block agents run blind to each other, expect two artefacts and fix them here: a name may
be glossed in more than one chapter (harmless, thin it out where it reads as repetition), and two
chapters may open the same way (rewrite one). A term that is glossed **nowhere** is a linter finding,
below.

Run the linter on the assembled file; it exits non-zero on any violation:

```bash
python3 .claude/skills/book-distill/scripts/retell_lint.py library/<slug>/retelling.md --depth <depth>
```

It checks blocks per chapter, word budget, the words spent on position and mechanism, sentence
length and its spread, density of names and numbers, spelled-out numerals, both halves of every
evidence bullet, unglossed first mentions, chain openers ("then", "next", "separately"…), causal
connectives, topic chaining, the forward link, and that `[analysis]` never sits inside a `[book]`
block. It cannot see a lost point — check the points against `state/digest.md`, which lists them
per chapter, and send a repair agent at any block that dropped one.

The linter runs **once, here, in the orchestrator** — never inside the block agents. Its findings are
per chapter, so route each chapter's findings back to one repair agent holding that block file and
those lines. That is one write, one lint, one repair; the loop-inside-the-agent version cost 3.2M
tokens for eleven chapters.

### Pass 2.6 — Cold read (the comprehension gate)

The linter measures mechanics and nothing else. A retelling can score zero violations and still be
unreadable — that is not hypothetical, it is what the first version of this pipeline shipped. So
every chapter is read by someone who has never seen the book.

Spawn one subagent per chapter with **no access to `source/`, `notes/`, or the rest of the pack** —
it gets the chapter block from `retelling.md` and nothing else.

**Set the reader's baseline explicitly, or the gate is unfalsifiable.** The cold reader is an
educated adult with ordinary general knowledge: everyday vocabulary, school history and geography,
and the common words of public life — inflation, shares, bonds, subsidy, monopoly, a veto, a
president's name, a blast furnace. What they do **not** have is anything specific to this book: its
author, its argument, its cases, its coinages, and the jargon of its field. A reader told to disown
all knowledge flags «инфляция» and «Рейган», nothing can ever pass, and the loop burns budget
forever — that happened on the first run of this gate.

It answers, in the pack's language:

1. What is this chapter claiming? (one sentence, in its own words)
2. Why does that follow? Give the steps.
3. Name one piece of evidence and say what it is supposed to prove.
4. List every term, name or institution **specific to this book or its field** that the chapter
   uses without explaining — not words an educated adult already knows.
5. Quote every sentence whose meaning you could not get on one reading.

A chapter passes when 1–3 are answered correctly and 4–5 come back empty. Anything in 4 or 5 is a
defect in the text, never in the reader: gloss the term, split the sentence, restore the missing
step, and send the chapter back through — as a repair agent on that block file, not as an edit made
here.

**The reader returns a verdict, not a transcript**: `pass`, or the flagged terms and the quoted
sentences, capped at ten lines. Answers 1–3 are how it convinces itself; they do not come back
unless the verdict is `fail`, and then only the one that went wrong. Append the verdicts to
`state/cold-read.md`, one line per chapter — that file is the pass's record and the thing you
reread, not forty agent replies. Record the totals in `book.json` under `verification.cold_read`:
chapters passed, chapters revised, and what the readers flagged.

Repairs change `state/retelling/NNN-*.md`, so rerun `build_retelling.py` and `retell_lint.py` after
the round, and cold-read only the chapters that were rewritten.

Do not skip this pass because the linter is green. Green mechanics with a failed cold read is the
exact failure mode this gate exists for.

Two practical rules learned the expensive way. **Read the flags before acting on them** — a flag on
a book-specific coinage is a defect, a flag on ordinary vocabulary is a miscalibrated reader, and
only the first kind gets fixed. And **do not put the linter loop inside the writing agent**: one
write, then the linter run once by the caller, then one cold read, then the caller fixes the flagged
sentences. The first run of this pipeline let each writer iterate against the linter on its own and
spent 3.2M tokens across 44 agents for eleven chapters.

Templates for the other layers are in `reference/layers.md`. Only after all this comes the spine,
the map and the critique.

### Pass 3 — Synthesis

From `state/digest.md` and `state/recon.md` — not the raw book, and not the notes files themselves —
write `spine.md`, `argument-map.md`, `quotes.md`, `critique.md`. Templates in `reference/layers.md`.
The digest names the source note for every claim, so when one claim needs its full context, open that
one note; opening all of them is how this pass ends up holding the book again.

`quotes.md` is the exception that still needs the book: the quotes already exist verbatim in
`notes/`, so build it with a script or a subagent that greps the note files for quote blocks, ranks
them and writes the file — never by rereading `source/`.

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
python .claude/skills/book-distill/scripts/make_cards.py "library/<book-slug>/cards.md"
```

Card count by depth: quick ~15, standard ~40, deep ~80. Cards test *understanding and transfer*,
never trivia ("what year was the study?" is a bad card).

At `deep` this is eighty cards and it fans out too: one agent per pillar, each holding `spine.md`,
the digest entries for that pillar's chapters and its share of the count, each writing
`state/cards/PN.md`. Concatenate into `cards.md`, then dedupe by hand — sibling agents produce near
twins around a shared concept — and only then run `make_cards.py`.

### Pass 5 — Interactive page

**The page has one skeleton, shared by every book distilled from now on.** It lives in
`reference/page-template.html`: a single scroll with a collapsible left menu and nine sections in
a fixed order — `retelling`, `pillars`, `map`, `quotes`, `reception`, `critique`, `recall`,
`apply`, `links`. Fill its `{{PLACEHOLDER}}` slots; never invent a section order, rename an
id or drop a section. Depth changes how densely the sections are filled, not how many there are.

`library/1984/` and `library/frankenstein/` were built before this skeleton and keep the pages
they already have. Do not rebuild them unless the user asks.

**The chapter articles are generated from `retelling.md`, never typed twice.** The retelling is the
source of truth for that block; the page is a rendering of it:

```bash
python3 .claude/skills/book-distill/scripts/build_chaps.py library/<slug>/retelling.md library/<slug>/page.html
```

It rewrites everything inside `<div class="chaps">` and maps the markdown onto the template's
components: the claim becomes `p.lead`, the fixed slots keep the mono `span.lbl` chip, the
per-chapter labels of the position and mechanism blocks become `span.say` (sentence case, serif —
a claim is not a slot name), evidence becomes a `ul`, and `> **разбор.**` becomes `p.an-block`.
Run it again after any edit to the retelling, so the two never drift apart.

**The claim map is generated too, like the chapter articles.** `argument-map.md` already carries one
block per pillar with the same five fields, so the graph and the table behind it are derived from it
rather than typed:

```bash
python3 .claude/skills/book-distill/scripts/build_map.py library/<slug>
```

It writes `state/slots-map.json` with `FLOW_MAP`, `FLOW_NOTE_MAP`, `MAP_TABLE` and `MAP_NOTES`, and
reads which pillars are load-bearing out of the file's own closing section, so the map cannot drift
from the pack or from the pillars graph. Rerun it after any edit to `argument-map.md`.

**Keep one numbering.** `spine.md` is the ladder of record: `argument-map.md`, `critique.md`, the
cards and both graphs use its `P1…Pn` identifiers and its wording. A pack whose map numbers pillars
its own way shows the reader two different sets under the same names — check this before publishing,
because neither linter can see it.

The rest of the page is filled the same way the retelling was: **the orchestrator never holds the
whole page.** Copy the template, run `build_chaps.py` for the chapter block, and fill the remaining
`{{PLACEHOLDER}}` slots one at a time — each from the pack file that backs it (`spine.md`,
`argument-map.md`, `quotes.md`, `reception.md`, `critique.md`, `cards.md`, `apply.md`, `links.md`),
written straight into the file with a small script or an agent that returns only which slot it
filled. Read the page back only through `page_lint.py` and a screenshot.

**Two of the nine sections are graphs, not prose.** They are what makes the argument readable at a
glance, so they are built the same way in every pack:

- **The pillars graph** — one node per pillar, chained from a root node holding the thesis. Solid
  edges run along the load-bearing chain; dashed edges lead to the side pillars, the ones the
  thesis survives without. Every edge carries a short label saying what the step is. A switch
  above the graph dims the side pillars ("main path only"), and one button opens or closes every
  node. Which pillars are load-bearing is an `[analysis]` call and is marked as one on the page.
- **The claim map** — one node per pillar; inside it a solid branch of supports and a
  dashed branch of objections, each objection labelled with the claim it attacks. The dense table
  stays available behind a graph/table switch.

Nodes are `<details>` elements: keyboard support, `Esc`, and deep linking come for free, and no
absolute positioning means nothing can overlap at any width.

**Two skills are mandatory before writing it**, in this order:

1. `ui-ux-pro-max` — the design and accessibility authority for this pass. Its pre-delivery
   checklist (contrast in both themes, focus states, touch targets, no horizontal scroll at 375px,
   reduced motion) is the last gate before publishing.
2. `artifact-design` — for the publishing mechanics of the Artifact itself.

**The palette is the one thing designed per book, and it is taken from the book's cover** — pull
the cover image out of the file, read its dominant colours, map them onto `--stamp` and `--ochre`,
and bias the neutrals a few points toward the accent hue. One exception, and it must be recorded
in `book.json`: the skeleton already spends red on weak claims and objections, so a cover whose
dominant colour is a red or crimson cannot supply the accent — take the cover's second colour, or
a neighbour of it, and say in `book.json` why. Two books in the library must not share an accent
hue.

Before publishing, run the structural check:

```bash
python3 .claude/skills/book-distill/scripts/page_lint.py library/<slug>/page.html
```

It verifies the nine section ids and their order, every component the skeleton is built from, one
menu link per section, both theme blocks, that nothing but Google Fonts is loaded, tag balance and
that the script parses. A page that does not pass is not published.

`reference/interactive.md` carries the slot list, the section-to-file mapping, the graph markup,
the palette procedure and the verification steps. Record the returned URL in `book.json`.

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
python .claude/skills/book-distill/scripts/ru_lint.py "library/<book-slug>/page.html"
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
distill [<book>] [quick|standard|deep] [lang:<code>]
```

The book argument is optional: with none, the book is whatever is sitting in `input/` (see
**Pass 0**). `quick`/`standard`/`deep` set the depth (default `standard`); `lang:` overrides the
output language (default: the book's own, see **Output language**). Plain requests carry the same
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
6. A book and everything made from it live in `library/<book-slug>/`, and `input/` and `library/`
   are both gitignored in full. Nothing about any book — file, extracted text, notes, page — is
   ever committed or pushed. Never work around the ignore rules to "back up" a pack.
7. `input/` holds books that have not been ingested yet, nothing else. Pass 0 empties it by moving
   the file, never by copying or deleting it.
8. Every page built from now on has the same nine sections in the same order, the same collapsible
   left menu, and the same node graphs in the pillars and map sections. Per book only the content,
   the depth and the palette change — and the palette comes from that book's cover. The two packs
   that predate the skeleton, `1984` and `frankenstein`, keep their pages.
9. The orchestrator does not read book text. Chapters, notes and retelling blocks are read by
   subagents that write files and return receipts; the orchestrator lives on `state/`, the manifest
   and linter output. A pass that needs the whole book in one context is a pass that needs splitting.
10. The chapter retelling follows `reference/retelling-standard.md` and passes `retell_lint.py`
   before pass 3 starts. A chapter written as one dense paragraph, opening on a detail instead of a
   claim and chained with "then", is a defect however accurate it is.
11. Pass 5 runs with the `ui-ux-pro-max` skill loaded. It is not optional and not a remedy applied
   after the page turns out wrong.
