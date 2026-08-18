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
| Facts joined by "затем / дальше / отдельно" | "and-then chaining" — the connective test: replace *and* with *but* or *therefore* | Parker & Stone, quoted at https://ncse.ngo/and-therefore-randy-olson-and-art-science-storytelling-part-1 |
| A new proper noun or number every 6–8 words | broken given-new contract: no antecedent for the reader to attach new material to | Clark & Haviland, https://web.stanford.edu/~clark/1970s/Clark,%20H.H.%20_%20Haviland,%20S.E.%20_Comprehension%20and%20the%20given-new%20contract_%201977.pdf |
| Every sentence starting a new subject | topic drift; the reader has no throughline to follow | Gopen & Swan, https://www.gatsby.ucl.ac.uk/~pel/misc/gopen_swan.pdf |
| No stakes, no consequence | incomplete retell — story-grammar scoring counts "consequence" as a required element | Story Grammar Scorer, https://conductscience.com/tools/story-grammar-scorer |
| Chapters as isolated blocks | fragmentation: no situation model is built across chapter boundaries | Kintsch, https://condor.depaul.edu/dallbrit/extra/hon207/readings/kintsch-1988-construction-integration.pdf |
| Deleting connective tissue while compressing | ИК3 logical error — the standard Russian marking penalty for losing links when cutting | ОГЭ criteria, https://rustutors.ru/zadanie1oge.html |
| Reader only reads, never produces | the benefit in the research comes from *generating* a summary, not consuming one | generation effect, https://link.springer.com/article/10.3758/BF03193441 |

Two more facts shaped the format. Commercial services almost never retell chapter by chapter —
Blinkist, getAbstract, Headway and Sumizeit cut the book into **claim-titled idea units**, and
Shortform, the one chapter-by-chapter exception, says it "reorganize[s] extensively for coherency"
and still gives every chapter a claim-like title. And Shortform marks its own commentary inline
with the literal string `Shortform note:` — the same job our `[книга]` / `[разбор]` tags do, but
visible in the flow rather than only in the file.

## The unit is the микротема, not the chapter

Split each chapter into 2–4 микротемы — one идея per paragraph, which is what the Russian
compression criteria require (ИК1: every микротема present, none invented; ИК3: paragraph breaks
follow the sense). A chapter that says one thing gets one block; a chapter that says three gets
three. **Never one wall per chapter.**

If two adjacent chapters carry one микротема between them, merge them into a single entry and say
so in the heading (`Главы 5–6`). If a chapter runs three ways, it gets three blocks under one
heading.

## Template A — argumentative chapter (nonfiction)

140–220 words per chapter at `standard`, 190–300 at `deep`, 90–140 at `quick`.

```markdown
### Глава 3 · Стимулы не заменяют возможностей

**Утверждение.** [one sentence, ≤25 words, ≤2 named entities, the chapter's claim as a proposition]

**Как получилось.** [60–90 words: what was taken for granted, what breaks it, what the author
concludes — Situation → Complication → Answer, in the author's own order]

**Чем держится.**
- [evidence ≤25 words] — [what it proves, named]
- [evidence ≤25 words] — [what it proves, named]

**Что осталось открытым.** [1–2 sentences: what this chapter does not settle]

**Дальше.** [1 sentence: the question this hands to the next chapter]

> **разбор.** [optional, one paragraph, our own reading — always visually separated, never merged
> into the author's claims]
```

## Template B — narrative chapter (fiction)

80–130 words per chapter at `standard`, 90–180 at `deep`, 50–80 at `quick`.

```markdown
### Глава 4 · Уинстон изобретает человека, которого не было

**Где мы.** [only if it changed since the last chapter; one short sentence]

**Что происходит.** [40–70 words: the turn, built with «поэтому» and «но», never «затем».
Every character named on first appearance in this chapter — no bare pronoun]

**Ставка.** [1 sentence: what is lost if it goes wrong]

**Дальше.** [1 sentence: the open question]
```

`Где мы` is dropped when the setting is unchanged — the given-new contract says do not re-supply
what the reader already holds.

## Hard limits

| Check | Limit | Why |
|---|---|---|
| Blocks per chapter | ≥ 2 | ИК3 paragraph division; no walls |
| Words per chapter | template A/B ranges above | proportion rule of the précis |
| Average sentence | ≤ 20 words | our old retellings ran 26–34 |
| Longest sentence | ≤ 30 words | subject–verb distance |
| Named entities + numbers | ≤ 11 per 100 words (A), ≤ 10 (B); text inside «…» is exempt | old packs ran 12–19 |
| First sentence of a chapter | ≤ 25 words, ≤ 2 entities, states a claim | Adler R2; answer-first |
| Chain openers («Затем», «Дальше», «Далее», «Потом», «Отдельно», «В конце главы», «Также») | 0 | and-then chaining |
| Causal / contrastive connectives | ≥ 1 per 3 sentences | ИК3; but-therefore rule |
| Topic chaining | ≥ 20% of sentences open from material already in the previous sentence, or with an explicit connective | Gopen & Swan |
| Forward link | present in every chapter | situation model across chapters |
| `[разбор]` inside a `[книга]` block | 0 | ГОСТ 7.9-95: the referent adds no interpretation |

## Retrieval, not just reading

The research is blunt: reading someone else's summary is the weak form. The benefit lives in
generating one. So the retelling section ends with **«Проверьте себя»** — 3–5 questions the reader
answers from memory before moving on, one per микротема, phrased so the answer is a claim and not
a name. These are not the flashcards from pass 4; they are the gate out of the retelling.

## Checking

```bash
python3 .claude/skills/book-distill/scripts/retell_lint.py library/<slug>/retelling.md
```

The linter reports per chapter and exits non-zero on any hard-limit violation. Fix the prose, never
the limit. It measures mechanics only — it cannot see whether a микротема was lost, so ИК1 stays a
human check: list the микротемы of the chapter from `notes/`, then confirm each one appears.
