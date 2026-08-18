# Output templates

Every file below is Markdown, written to the book's directory, `library/<book-slug>/`. Paths in
`book.json` are relative to that directory. Keep the headings exactly as
shown — the interactive page builder and the `quiz`/`ask` modes parse them.

The templates are written with Russian headings in places, because that is what the first packs
used. **The pack is written in the book's own language by default** (see the skill's *Output
language* section): translate the headings into the output language and keep the structure
identical.

Volume per depth — the same templates, three sizes:

| | `quick` | `standard` | `deep` |
|---|---|---|---|
| Pack total | 3.5–5k words | 8–11k words | 18–24k words |
| Retelling | part-level shape | 2–3 sentences per chapter | 5–8 sentences per chapter, with subplots |
| Scenes | — | 6–8 | 12–16 |
| Quotes | 8–10 | 20–25 | 40–50 |
| Cards | ~15 | ~40 | ~80 |
| Skipped files | `argument-map.md`, `reception.md`, `apply.md`, `links.md` | — | — |

---

## notes/NNN-<slug>.md — chapter pass

```markdown
# ch.3 — What Fragility Actually Means

**Role in the argument:** establishes the L2 pillar "fragility is measurable before failure".
**Skip-safe:** no  <!-- yes = a reader could drop this chapter and lose nothing -->

## Claims
- **L2** `[book]` **Fragility** = harm accelerates faster than benefit as volatility rises —
  a *concave* response to variance, not a synonym for weakness.
- **L3** `[book]` Detectable **before** any failure: measure the second derivative of the
  response curve, not the failure history.
- **L3** `[book]` The opposite is not robustness but **antifragility** — gains from disorder.
- **L4** `[book]` Evidence: 2008 bank leverage ratios; the Titanic; restaurant industry
  turnover. All illustrative, none quantitative.
- **L5** two pages of Mediterranean travel anecdote — dropped.

## Concepts introduced
- **Concavity** — payoff curve bending down; small shocks hurt less than large shocks hurt more.

## Quotes
> "<a verbatim sentence copied from source/chapters/, never retyped from memory>"
> — ch.3

## Tensions
- `[analysis]` Contradicts the claim in ch.1 that the property cannot be quantified — here the
  author offers a measurement procedure.

## Open questions
- `[analysis]` How is this distinguishable from plain convexity in options pricing?
```

Rules: bullets only, one idea each, every claim tagged `L1`–`L5` and `[book]`/`[analysis]`.
Quotes copy-pasted verbatim from the chapter file, max 3 per chapter, each earning its place
(it is quotable *because* it is the compressed form of a claim — not because it sounds nice).

---

## retelling — the layer that must come first

Written before the spine and shown before it. The test: hand the retelling to someone who has never
opened the book, and they can describe the plot, name the characters, explain the ending, and hold
a conversation about it. If they cannot, the retelling failed and nothing downstream is readable.

Rules that keep it from turning into a blurb:

- **Concrete over abstract.** Not "Winston struggles against the regime" but "Winston buys a diary
  in a junk shop, writes DOWN WITH BIG BROTHER, and understands he is already dead."
- **Sequential.** Follow the book's own order, part by part, chapter by chapter. The shape of a
  chapter entry, its word budget and the checks it must pass are set by
  `reference/retelling-standard.md`; do not invent a shape here.
- **The ending is told.** A study pack is not a bookshop. Withholding the ending makes the analysis
  impossible to follow.
- **Names, objects, numbers.** The junk shop, the paperweight, room 101, the rats. Concrete nouns
  are what make a retelling feel like the book rather than a summary of it.
- **No interpretation here.** Everything on these pages is `[book]`. Meaning belongs in the spine
  and the critique; mixing the two is what makes summaries feel like they explain nothing.

```markdown
# What the book is

**Setting and premise:** <2–4 sentences: place, time, where the protagonist stands>
**Shape:** <parts, length, who narrates, whether there are embedded texts>
**How it ends:** <plainly, nothing withheld>
**If you read the original:** <for whom, and which chapters>

## Cast
- **<name>** — <who they are and what work they do in the story>

## How the world works
- **<institution / term>** — <what it is and how it works>

## Retelling
### Chapter 1 · <claim-like title>
<the slots from retelling-standard.md: Claim / How it goes / What holds it up / Left open / Next,
or Where we are / What happens / Stakes / Next for a narrative chapter>

## Key scenes
### <scene title> · ch. N
<what happens, 3–6 sentences>
> «verbatim quote»

## Timeline
- <event> — <when>

## Self-check
<3–5 questions at quick and standard, 6–10 at deep; the answer is a claim, not a name>
```

Headings and slot labels are translated with the pack — see the table in
`reference/retelling-standard.md`.

## spine.md — the 10-minute read

```markdown
# <Title> — <Author> (<year>)

**One line:** <the L1 thesis, in the author's terms, ≤30 words>
**Genre of argument:** <empirical / conceptual / polemic / manual / memoir-with-thesis>
**If true, what changes:** <2–3 concrete consequences>
**Read the original if:** <who genuinely needs the full text, and which chapters>

## The ladder

### P1 — <pillar claim, one sentence>
- Mechanism: <how the author says it works>
- Rests on: <L3 support, 2–4 bullets>
- Evidence quality: <strong / mixed / anecdotal> — <one line why>
- Strongest quote: "<verbatim>" — ch.N

### P2 — ...

## Vocabulary
- **<term>** — <definition in the author's sense, one line>

## What the book does not claim
- <common misreading it is often flattened into>

## Coverage
Full passes: ch.1–12. Sampled: ch.13–15 (appendix material).
```

---

## argument-map.md

One row per L2/L3 claim, so weak links are visible at a glance.

```markdown
| ID | Level | Claim | Rests on | Evidence | Strength | Best objection |
|----|-------|-------|----------|----------|----------|----------------|
| P1 | L2 | Fragility is measurable pre-failure | S1, S2 | 3 case studies | mixed | Cases are selected post-hoc |
| S1 | L3 | Response to variance is concave | — | conceptual | strong | — |
```

Then a short **Dependency notes** section: which pillar carries the most weight, and which
single claim, if refuted, takes the most of the book down with it.

---

## quotes.md

Ranked, sourced, and useful — not a highlight dump.

```markdown
# Quotes — <Title>

## Load-bearing (the argument in the author's own words)
> "<verbatim>"
> — ch.3 · supports **P1**
*Why it matters:* <one line>

## Sharp (memorable phrasing worth reusing)
...

## Suspect (sounds profound, asserts a lot, proves nothing)
> "<verbatim>"
> — ch.7
*`[analysis]`* <what is being smuggled in>
```

If a quote cannot be found verbatim in `source/chapters/`, it does not go in this file.

---

## critique.md

```markdown
# Critique — <Title>

## What would have to be true for the thesis to fail
- ...

## Evidence audit
- **P2** rests entirely on anecdote (`ch.5`, `ch.9`) presented in the register of data.

## Internal contradictions
- ch.1 vs ch.3 — <both quoted, one line each>

## Never addressed
- <the obvious objection the author walks past>

## Who disagrees
- `[analysis]` <named opposing position or book, and its core point>

## Verdict
<2–4 sentences: what survives, what to discard, what to steal.>
```

---

## reception.md — what the known critics said

Researched, never recalled. Every entry carries a name, a place of publication and a year; every
quotation is short and verified against a source fetched during the run. Sources listed at the end.

```markdown
# What the critics said

## Contemporaries, <year>
**<Name>** · <publication, date>
<the position in 2–4 sentences; a short quote if it was verified>
`[analysis]` <which pillar this objection hits, and whether it lands>

## The argument about what kind of book this is
<the substantial dissenters: ideological, generic, source-critical>

## Writers who answered it
<who replied with a book or an essay>

## The book in the reader's own language
<translations, editions, censorship, differences in terminology>

## Second life in the news
<when and why the book was read en masse again>

## How the lines of argument split
<3–5 lines: the argument about the mechanism / the genre / the sources / a defence from inside the text>

## Sources
<the publications actually used>
```

Hard rules: no unsourced opinion attributed to a named person; no quotation longer than a phrase;
if a critic said what you had claimed as your own analysis, credit them and fix the earlier page.

## cards.md — retrieval deck

Parsed by `scripts/make_cards.py`. Format, blank line between cards:

```
Q: Why can fragility be detected before any failure occurs?
A: Because it is a property of the response curve (concavity to variance), not of failure
   history — you measure how harm scales with shock size, not whether harm has happened yet.
T: ch3 P1 mechanism
```

Card rules — the deck is the deliverable that produces retention, so:

- **Generative, not recognition.** The answer must be produced, not recognized. No true/false,
  no multiple choice.
- **Why/how over what.** At least half the deck asks for a mechanism, a cause, or a prediction
  (elaborative interrogation). "Define X" cards: at most 20% of the deck.
- **One fact per card.** If the answer has three parts, it is three cards.
- **Transfer cards** (~15%): apply a pillar to a situation not in the book.
- **Objection cards** (~10%): "What is the strongest argument against P2?"
- **No trivia.** Dates, author biography, and study sample sizes are not cards.
- **No cards about the pack itself.** The deck tests the book, never the pipeline: extraction quirks, coverage
  decisions, and verification steps belong on the method page. A card the reader can only answer by knowing
  how the pack was built is noise in the deck, however interesting the fact is.
- Tag every card with the chapter and the pillar ID: `T: ch3 P1`.

---

## drills.md

```markdown
# Drills — <Title>

## Free recall (do these cold, before opening anything)
1. Write the thesis in one sentence, then list the pillars. Check against `spine.md`.
2. Explain **P1** to a skeptical colleague in 60 seconds.

## Elaborative interrogation
- Why would P2 be true rather than the obvious alternative? What mechanism forces it?

## Transfer
- Apply P3 to <a domain the book never mentions>. Where does it break?

## Spaced schedule
- [ ] Day 1 — full deck
- [ ] Day 3 — misses only
- [ ] Day 7 — full deck
- [ ] Day 21 — pillars + transfer only

## Misses (YYYY-MM-DD)
- <card front> — answered <what the user said>, gap: <what was missing> (ch.N)
```

---

## apply.md

```markdown
# Apply — <Title>

## Decisions this book argues you should change
- <specific, testable, with the pillar that supports it>

## Experiments (small, this week)
- <action> — expected signal if the book is right: <what you would observe>

## What this book says you should stop doing
- ...
```

---

## links.md (cross-book)

```markdown
# <Title> ↔ other books in this library

## Agrees with
- **<Other Title>** — both argue <shared claim>. <Other> gives the mechanism this one asserts.

## Contradicts
- **<Other Title>** — <claim A> vs <claim B>. Testable difference: <what would settle it>.

## Answers a question the other leaves open
- <Other Title> asks <X> and stops; this book's **P3** is a direct answer.
```

---

## book.json

```json
{
  "title": "...",
  "author": "...",
  "slug": "...",
  "source_file": "The Book.epub",
  "language": "en",
  "output_language": "en",
  "depth": "standard",
  "pack_words": 9400,
  "coverage": {"full_passes": "ch.1-12", "sampled": "ch.13-15", "skipped": []},
  "artifact_url": "https://...",
  "runs": [{"date": "2026-08-15", "mode": "distill", "depth": "standard", "cards": 41}]
}
```

`language` is the book's own; `output_language` is the pack's. They match unless the run carried a
`lang:` override — record why when they differ. `pack_words` is the measured total, so the next run
can see whether the depth budget was actually hit.
