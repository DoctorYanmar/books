# Russian output: how to write so it does not smell of a machine

Required reading before building a pack in Russian. Explanations are in English; the word lists,
examples and terminology are in Russian, because that is the data being checked.

## The main rule: write in Russian, never translate into it

A pack is **never translated from an English draft**. An English draft is the source of calques:
English word order, chains of participles, «является», clipped English-length phrases. Write the
analysis in English first and translate it, and the traces survive any amount of editing.

So: read the chapters in the original language, think, and **write in Russian directly**. No
intermediate English text exists. Machine translation (DeepL, Google, "translate this page") is
used at no step — not for analysis, and least of all for quotes.

## Quotes: three acceptable policies, pick one and declare it on the page

1. **A Russian edition as the source** (best). The user puts the Russian file of the book in
   `library/`. Run `extract.py` a second time over it, take quotes **verbatim from the Russian
   edition**, cite the chapter of the Russian text, and name the translator and year on the page.
   For *Frankenstein* the canonical Russian text is З. Александрова's translation (1965).
2. **Bilingual** (when no Russian edition exists). The quote is the verbatim original with a
   working Russian gloss under it, marked «подстрочник, не канонический перевод». Nothing is
   passed off as a published translation.
3. **Russian original** (the book is Russian to begin with) — the usual rules: verbatim, unedited.

Forbidden: translating a quote yourself and presenting it as a quote from the book. That is the
same offence as inventing one.

## Blacklist

Remove completely:

- **Канцелярит-связки**: является, представляет собой, осуществлять, производить (в значении
  «делать»), данный/данная в значении «этот», в рамках, в части, в целях, посредством, ввиду того что.
- **Ватные вводные**: важно отметить, стоит отметить, нельзя не отметить, следует подчеркнуть,
  необходимо понимать, как мы видим, давайте разберёмся, итак, что же это значит.
- **Инфостиль-штампы 2020-х**: глубокое погружение, ключевой момент, на самом деле, по сути,
  в конечном счёте, красной нитью, не просто X, а Y; «это не просто книга — это…».
- **Триплеты-парцелляция**: «Не жалость. Не страх. Ответственность.» One such device in a whole
  document is already too many; zero is the norm.
- **Кальки**: делает смысл (имеет смысл), адресовать проблему, в конце дня, драйвер, челлендж,
  инсайт (when «наблюдение» or «вывод» will do), нарратив (when it is simply a story).
- **Мусорные усилители**: очень, крайне, поистине, буквально, действительно, просто-напросто.

## Positive rules

- **A verb instead of a verbal noun.** Not «осуществление отказа от создания подруги» but «он
  отказался её создать». Two «-ание/-ение» nouns in a row: rewrite.
- **One participial phrase per sentence.** Two is bureaucratic mush; a sentence opening with a
  gerund («Рассматривая роман…») is better not started at all.
- **Active voice.** «Существо требует договора», not «договор требуется существом». Impersonal
  constructions («считается», «можно сказать») only where the subject genuinely is unknown.
- **Russian rhythm, not English.** English prose chops into short sentences; Russian holds a period
  of 25–35 words comfortably. Vary the length: five sentences of the same length in a row read as
  generated. Over 45 words, split.
- **Use the terms the Russian tradition already has**: тезис, посылка, довод, аргументация, фабула
  и сюжет, повествовательная рамка, ненадёжный рассказчик, вставной рассказ, романтическая ирония.
  Do not invent «клейм», «эвиденс», «пиллар». The pack's layers are named
  тезис / опоры / подпорки / свидетельства / фактура (L1–L5).
- **Names and cultural references follow the translation tradition**, not transcription by ear:
  Виктор Франкенштейн, Уолтон, Клерваль, Элизабет, Жюстина, Делейси, «Потерянный рай»,
  «Страдания юного Вертера». Call the creature **существо** or **творение**; «монстр» only when a
  character says it.
- **Provenance tags are translated**: `[book]` → `[книга]`, `[analysis]` → `[разбор]`. Mixing them
  is still forbidden.
- **Retelling slot labels are translated too**, per the table in `retelling-standard.md`.

## Typography

- Guillemets «…», nested „…“. English "" never appear in Russian text.
- The dash is long (—) with spaces; the hyphen only inside words. Ranges take an en dash (гл. 10–15).
- Use `ё` consistently: everywhere or nowhere. Everywhere is recommended — in a study text it
  removes ambiguity.
- Non-breaking space before «гл.», «с.», inside initials and in «19 в.».
- Dates and numbers the Russian way: 1818 год, 78 140 слов (a space as the thousands separator,
  not a comma).
- In HTML: `<html lang="ru">` is unnecessary (the platform supplies the wrapper), but put
  `lang="ru"` on `body` or the root container, and `<span lang="en">` around English insertions.
  Hyphenation: `hyphens: auto` follows Russian rules only when `lang` is set.

## Check before publishing

```bash
python3 .claude/skills/book-distill/scripts/ru_lint.py "library/<book-slug>/page.html"
```

The linter catches mechanics: the blacklist, «-ание/-ение» chains, long sentences, English quotation
marks, a hyphen where a dash belongs. It does not catch the thing that matters — tone. So after the
linter, one pass by eye against a single rule: **if the phrase could not appear in a living Russian
review, rewrite it.** This goes double for the opening paragraphs of every page: generated text
gives itself away in introductions.

## Служебные подписи на странице

Кикеры, подписи разделов, подвал и колонтитул — часть документа, а не разговор с читателем.
Пишите их так, как пишут в справочном издании: назовите, что перед читателем и на чём оно
построено, и остановитесь.

- **Никаких оценок времени чтения и трудозатрат.** «Чтение примерно на два часа», «пак глубины
  deep», «на полчаса» — это внутренние мерки конвейера, а не сведения о книге. Глубина влияет на
  плотность разделов, но на странице не упоминается.
- **Подпись не повторяет заголовок.** Тег «Слой 7 · повторение» над заголовком «Повторение» не
  добавляет ничего. Подпись называет источник слоя: «по тексту книги», «дословно из издания»,
  «внешние источники».
- **Никаких прибауток и характеристик вместо фактов.** «Всё здесь», «чтобы осталось», «спорят по
  существу» заменяются на то, что там на самом деле: «тезис и опоры», «доводы и возражения»,
  «документальная работа, общий предмет».
- **Охват указывается, но как запись, а не как признание.** «Охват: прочитаны введение и все
  14 глав — 236 672 слова основного текста. Авторские примечания не разбирались» — так; «мы честно
  прочли всё, кроме…» — нет. Правило 5 из SKILL.md требует назвать охват, а не извиняться за него.
- **Числа больше десяти — цифрами и в подписях тоже**: «84 карточки», а не «восемьдесят четыре».
