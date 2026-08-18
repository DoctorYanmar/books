# The retelling standard (Pass 2.5)

The retelling is the part of the pack a reader meets first and the part they judge it by. It is
written for someone who has **not read the book** and will not read it. Everything here is a
constraint, not advice: each rule is either mechanically checkable by `scripts/retell_lint.py` or
checked by the cold read in pass 2.6.

**The test the retelling has to pass is comprehension, not compression.** A chapter that is short,
clean and unintelligible has failed. If a rule below and a reader's understanding ever pull in
opposite directions, understanding wins and the rule is wrong — say so and change it here.

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

The first version of this standard fixed those and then failed in the opposite direction: chapters
came out at 200–250 words, sentences at a flat 13–15 words, evidence reduced to bare facts with the
inference deleted. It passed the linter with zero violations and could not be understood by anyone
who had not read the book. Two more findings say why, and they set the budget rules below.

| What we did | What it is called | Source |
|---|---|---|
| Compressed until only the claim skeleton was left | our reader has **zero prior knowledge**, and low-knowledge readers comprehend measurably better from **high-cohesion, self-contained** text; only high-knowledge readers gain from terse, gappy text (the reverse cohesion effect) | McNamara & Kintsch 1996, https://eric.ed.gov/?id=EJ538963 · https://www.tandfonline.com/doi/abs/10.1207/s1532690xci1401_1 |
| Named POSCO, Кочабамба, «распылённое владение» with no gloss | broken lexical coverage: adequate comprehension needs ~98% of the words already known — roughly one unknown item per 50 words, not one per sentence | Hu & Nation 2000, https://eric.ed.gov/?id=EJ626518 · replication: https://onlinelibrary.wiley.com/doi/10.1111/lang.12622 |

## The unit is the point, not the chapter

Split each chapter into 2–4 **points** — one idea per paragraph. (The Russian tradition calls this
unit a микротема, and its compression criteria say the same thing: every point present, none
invented, and paragraph breaks that follow the sense.) A chapter that says one thing gets one
block; a chapter that says three gets three. **Never one wall per chapter.**

If two adjacent chapters carry one point between them, merge them into a single entry and say so in
the heading (`Chapters 5–6`). If a chapter runs three ways, it gets three blocks under one heading.

## The mechanism is the deliverable

A claim plus its evidence is a bibliography. What the reader cannot reconstruct on their own is the
**middle**: why the claim follows. So template A carries **at least two prose blocks between the
claim and the evidence**:

1. **the position** — what the chapter argues against, or the problem it starts from. Every term the
   chapter later leans on is introduced here, in the reader's own words, before it is used.
2. **the mechanism** — the causal chain, spelled out step by step. This is the block that gets the
   words. If it can be shortened without losing a step, shorten it; if shortening it drops a step,
   the chapter has failed.

Their labels are written fresh for each chapter and read as claims ("Где довод ломается", "Что это
меняет в споре о приватизации"), not as slot names. Only the first, the evidence, the open question
and the forward link have fixed labels.

## Template A — argumentative chapter (nonfiction)

260–380 words per chapter at `standard`, 380–560 at `deep`, 150–220 at `quick`.

```markdown
### Chapter 3 · An incentive is not a capability

**Claim.** [one sentence, ≤28 words, ≤2 named entities, the chapter's claim as a proposition]

**[a claim-like label of your own].** [the position: 50–90 words. What was taken for granted, and
every term the chapter will use, glossed on the spot]

**[a claim-like label of your own].** [the mechanism: 90–160 words. Step by step, each step joined
to the last by because / therefore / but — never by "then". This is the longest block]

**What holds it up.**
- [evidence, ≤35 words] — [what it proves, stated as a claim, ≤20 words]
- [evidence, ≤35 words] — [what it proves, stated as a claim, ≤20 words]

**Left open.** [1–2 sentences: what this chapter does not settle]

**Next.** [1 sentence: the question this hands to the next chapter]

> **analysis.** [optional, one paragraph, our own reading — always visually separated, never merged
> into the author's claims]
```

Both halves of an evidence bullet are mandatory. `POSCO was built without ore or coal` is a fact;
`— a project private finance called hopeless turned out to be viable` is what makes it evidence.

## Template B — narrative chapter (fiction)

160–260 words per chapter at `standard`, 220–340 at `deep`, 110–170 at `quick`.

```markdown
### Chapter 4 · Winston invents a man who never existed

**Where we are.** [only if it changed since the last chapter; one short sentence]

**What happens.** [90–160 words: the turn, built with "therefore" and "but", never "then".
Every character named on first appearance in this chapter — no bare pronoun]

**Stakes.** [1–2 sentences: what is lost if it goes wrong, and for whom]

**Next.** [1 sentence: the open question]
```

`Where we are` is dropped when the setting is unchanged — the given-new contract says do not
re-supply what the reader already holds.

## Every name is glossed where it first appears

A proper noun, an institution, a technical term or a foreign word gets a 2–6 word apposition the
first time the retelling uses it, even when it also stands in the cast list: *POSCO, корейский
металлургический комбинат* · *Кочабамба, третий по величине город Боливии* · *мягкий бюджет, термин
венгерского экономиста Яноша Корнаи*. The cast list is a place to look something up; the retelling
must be readable without looking anything up.

Cross-references count as unglossed: "as chapter 2 showed" is not a gloss, because the reader may
have started here.

## Numbers are written as digits

`57 %`, `35 лет`, `108 дней` — not `пятьдесят семь процентов`. Spelled-out numerals above ten are
banned outright, and the linter counts them as entities so they cannot be used to duck the density
cap. (In the first pack they were: 51 spelled-out numerals against 39 digits, which is what a
gamed metric looks like.) Numbers up to ten stay in words where Russian usage prefers it
("проверяли восемь раз").

## Hard limits

| Check | Limit | Why |
|---|---|---|
| Blocks per chapter | ≥ 4 (A), ≥ 2 (B) | claim, position, mechanism, evidence |
| Prose blocks between claim and evidence | ≥ 2, together 140–260 words at `deep` | the mechanism is the deliverable |
| Words per chapter | template A/B ranges above | proportion rule of the précis |
| Average sentence | 15–25 words | a flat 13–15 reads as a telegram; `ru-style.md` puts Russian rhythm at 25–35 |
| Sentence length spread | standard deviation ≥ 5 words | five sentences of one length in a row read as generated |
| Longest sentence | ≤ 38 words | subject–verb distance |
| Named entities + numbers | ≤ 11 per 100 words (A), ≤ 10 (B); text inside «…» is exempt; spelled-out numerals count | given-new contract |
| Spelled-out numerals above ten | 0 | they were used to game the density cap |
| Evidence bullets carrying both halves | 100% | a fact without its inference is not evidence |
| Unglossed first mentions | 0 | ~98% lexical coverage |
| First sentence of a chapter | ≤ 28 words, ≤ 2 entities, states a claim | Adler R2; answer-first |
| Chain openers ("Then", "Next", "Later", "Separately", "Also", "At the end of the chapter") | 0 | and-then chaining |
| Causal / contrastive connectives | ≥ 1 per 2 sentences | ИК3; but-therefore rule |
| Topic chaining | ≥ 35% of prose sentences open from material already in the previous sentence, or with an explicit connective; bullet lists are exempt | Gopen & Swan |
| Forward link | present in every chapter | situation model across chapters |
| `[analysis]` inside a `[book]` block | 0 | GOST 7.9-95 on abstracts: the summariser adds no interpretation |

## Localised labels

A pack is written in the book's own language, so the fixed slot labels are translated with it. The
linter carries one table per language and detects which is in use; add a language by extending
`LANGS` in `scripts/retell_lint.py`. The Russian set, as used by the packs in this library:

| English | Russian |
|---|---|
| `## Retelling` | `## Пересказ` |
| `**Claim.**` | `**Утверждение.**` |
| `**What holds it up.**` | `**Чем держится.**` |
| `**Left open.**` | `**Что осталось открытым.**` |
| `**Next.**` | `**Дальше.**` |
| `**Where we are.**` | `**Где мы.**` |
| `**What happens.**` | `**Что происходит.**` |
| `**Stakes.**` | `**Ставка.**` |
| `> **analysis.**` | `> **разбор.**` |

The position and mechanism labels are not in this table on purpose: they are written per chapter.

## Retrieval, not just reading

The research is blunt: reading someone else's summary is the weak form. The benefit lives in
generating one. So the retelling section ends with a **self-check** — questions the reader
answers from memory before moving on, phrased so the answer is a claim and not a name — 3–5 at
`quick` and `standard`, 6–10 at `deep`. These are not the flashcards from pass 4; they are the gate
out of the retelling.

## Checking

```bash
python3 .claude/skills/book-distill/scripts/retell_lint.py library/<slug>/retelling.md --depth <depth>
```

The linter reports per chapter and exits non-zero on any hard-limit violation. Fix the prose, never
the limit.

**The linter is the smaller half of the gate.** It measures mechanics; it cannot tell whether a
chapter can be understood, and the first version of this standard proved that a text can score
perfectly and still be unreadable. The comprehension check is **pass 2.6, the cold read**: a reader
who has never seen the book gets one chapter and nothing else, and has to answer what the claim is,
why it follows, and what the evidence shows — flagging every term they did not know and every
sentence they could not parse. Any flag sends the chapter back. Pass 2.6 is described in `SKILL.md`
and its result is recorded in `book.json`.

Neither check can see a lost point, so that stays a human check: list the points of the chapter from
`notes/`, then confirm each one appears.
