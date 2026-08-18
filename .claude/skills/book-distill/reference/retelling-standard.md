# The retelling standard (Pass 2.5)

The retelling is the part of the pack a reader meets first and the part they judge it by. It is
written for someone who has **not read the book** and will not read it. Everything here is a
constraint, not advice: each rule is mechanically checkable, and `scripts/retell_lint.py` checks it.

## Why the rules exist

The three packs built before this standard failed the same way, and the failure has a name in the
literature.

| What we did | What it is called | Source |
|---|---|---|
| One dense paragraph per chapter | "inconsiderate text"; structured, labelled text scores measurably higher on information content (9.7 vs 5.5 of 14 items) and clarity (7.4 vs 6.2) | Hartley, *Improving the Clarity of Journal Abstracts* — https://informationr.net/ir/hartley2.html |
| Chapter opens with a detail, never a claim | topic-listing instead of claim-stating; Adler's Rule 2 demands the unity be stated as a proposition | *How to Read a Book*, rules quoted at https://www.tosummarise.com/analytical-reading-from-how-to-read-a-book/ |
| Facts joined by "then / next / separately" | "and-then chaining" — the connective test: replace *and* with *but* or *therefore* | Parker & Stone, quoted at https://ncse.ngo/and-therefore-randy-olson-and-art-science-storytelling-part-1 |
| A new proper noun or number every 6–8 words | broken given-new contract: no antecedent for the reader to attach new material to | Clark & Haviland, https://web.stanford.edu/~clark/1970s/Clark,%20H.H.%20_%20Haviland,%20S.E.%20_Comprehension%20and%20the%20given-new%20contract_%201977.pdf |
| Every sentence starting a new subject | topic drift; the reader has no throughline to follow | Gopen & Swan, https://www.gatsby.ucl.ac.uk/~pel/misc/gopen_swan.pdf |
| No stakes, no consequence | incomplete retell — story-grammar scoring counts "consequence" as a required element | Story Grammar Scorer, https://conductscience.com/tools/story-grammar-scorer |
| Chapters as isolated blocks | fragmentation: no situation model is built across chapter boundaries | Kintsch, https://condor.depaul.edu/dallbrit/extra/hon207/readings/kintsch-1988-construction-integration.pdf |
| Deleting connective tissue while compressing | a logical-coherence error — the standard Russian school criterion (ИК3) penalises exactly this when compressing a text | Russian state exam criteria, https://rustutors.ru/zadanie1oge.html |
| Reader only reads, never produces | the benefit in the research comes from *generating* a summary, not consuming one | generation effect, https://link.springer.com/article/10.3758/BF03193441 |

Two more facts shaped the format. Commercial services almost never retell chapter by chapter —
Blinkist, getAbstract, Headway and Sumizeit cut the book into **claim-titled idea units**, and
Shortform, the one chapter-by-chapter exception, says it "reorganize[s] extensively for coherency"
and still gives every chapter a claim-like title. And Shortform marks its own commentary inline
with the literal string `Shortform note:` — the same job our `[book]` / `[analysis]` tags do, but
visible in the flow rather than only in the file.

## The unit is the point, not the chapter

Split each chapter into 2–4 **points** — one idea per paragraph. (The Russian tradition calls this
unit a микротема, and its compression criteria say the same thing: every point present, none
invented, and paragraph breaks that follow the sense.) A chapter that says one thing gets one
block; a chapter that says three gets three. **Never one wall per chapter.**

If two adjacent chapters carry one point between them, merge them into a single entry and say so in
the heading (`Chapters 5–6`). If a chapter runs three ways, it gets three blocks under one heading.

## Template A — argumentative chapter (nonfiction)

140–220 words per chapter at `standard`, 190–300 at `deep`, 90–140 at `quick`.

```markdown
### Chapter 3 · An incentive is not a capability

**Claim.** [one sentence, ≤25 words, ≤2 named entities, the chapter's claim as a proposition]

**How it goes.** [60–90 words: what was taken for granted, what breaks it, what the author
concludes — Situation → Complication → Answer, in the author's own order]

**What holds it up.**
- [evidence ≤25 words] — [what it proves, named]
- [evidence ≤25 words] — [what it proves, named]

**Left open.** [1–2 sentences: what this chapter does not settle]

**Next.** [1 sentence: the question this hands to the next chapter]

> **analysis.** [optional, one paragraph, our own reading — always visually separated, never merged
> into the author's claims]
```

## Template B — narrative chapter (fiction)

80–130 words per chapter at `standard`, 90–180 at `deep`, 50–80 at `quick`.

```markdown
### Chapter 4 · Winston invents a man who never existed

**Where we are.** [only if it changed since the last chapter; one short sentence]

**What happens.** [40–70 words: the turn, built with "therefore" and "but", never "then".
Every character named on first appearance in this chapter — no bare pronoun]

**Stakes.** [1 sentence: what is lost if it goes wrong]

**Next.** [1 sentence: the open question]
```

`Where we are` is dropped when the setting is unchanged — the given-new contract says do not
re-supply what the reader already holds.

## Localised labels

A pack is written in the book's own language, so the slot labels are translated with it. The
linter carries one table per language and detects which is in use; add a language by extending
`LANGS` in `scripts/retell_lint.py`. The Russian set, as used by the packs in this library:

| English | Russian |
|---|---|
| `## Retelling` | `## Пересказ` |
| `**Claim.**` | `**Утверждение.**` |
| `**How it goes.**` | `**Как получилось.**` |
| `**What holds it up.**` | `**Чем держится.**` |
| `**Left open.**` | `**Что осталось открытым.**` |
| `**Next.**` | `**Дальше.**` |
| `**Where we are.**` | `**Где мы.**` |
| `**What happens.**` | `**Что происходит.**` |
| `**Stakes.**` | `**Ставка.**` |
| `> **analysis.**` | `> **разбор.**` |

## Hard limits

| Check | Limit | Why |
|---|---|---|
| Blocks per chapter | ≥ 2 | ИК3 paragraph division; no walls |
| Words per chapter | template A/B ranges above | proportion rule of the précis |
| Average sentence | ≤ 20 words | our old retellings ran 26–34 |
| Longest sentence | ≤ 30 words | subject–verb distance |
| Named entities + numbers | ≤ 11 per 100 words (A), ≤ 10 (B); text inside «…» is exempt | old packs ran 12–19 |
| First sentence of a chapter | ≤ 25 words, ≤ 2 entities, states a claim | Adler R2; answer-first |
| Chain openers ("Then", "Next", "Later", "Separately", "Also", "At the end of the chapter") | 0 | and-then chaining |
| Causal / contrastive connectives | ≥ 1 per 3 sentences | ИК3; but-therefore rule |
| Topic chaining | ≥ 20% of prose sentences open from material already in the previous sentence, or with an explicit connective; bullet lists are exempt — parallel items are not a chain | Gopen & Swan |
| Forward link | present in every chapter | situation model across chapters |
| `[analysis]` inside a `[book]` block | 0 | GOST 7.9-95 on abstracts: the summariser adds no interpretation |

## Retrieval, not just reading

The research is blunt: reading someone else's summary is the weak form. The benefit lives in
generating one. So the retelling section ends with a **self-check** — questions the reader
answers from memory before moving on, phrased so the answer is a claim and not a name — 3–5 at
`quick` and `standard`, 6–10 at `deep`. These are not the flashcards from pass 4; they are the gate out of the retelling.

## Checking

```bash
python3 .claude/skills/book-distill/scripts/retell_lint.py library/<slug>/retelling.md
```

The linter reports per chapter and exits non-zero on any hard-limit violation. Fix the prose, never
the limit. It measures mechanics only — it cannot see whether a point was lost, so that stays a
human check: list the points of the chapter from `notes/`, then confirm each one appears.
