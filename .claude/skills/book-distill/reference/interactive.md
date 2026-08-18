# Interactive page spec (Pass 5)

One self-contained HTML file per book, published with the Artifact tool. Write it to
`library/<book-slug>/page.html`, publish, store the returned URL in `book.json`. Republishing the
same path keeps the same URL — always reuse the path so links stay stable.

## Two hard rules

**1. The structure is the same for every book.** It is not designed per book and not improvised.
It lives in `reference/page-template.html`: the same shell, the same thirteen views in the same
order, the same component classes, the same JavaScript. What changes from book to book is the
content, the depth, and the palette — nothing else. A page that invents its own section order is
a defect, however good it looks.

**2. The palette comes from the book's cover.** Every book gets its own colour identity, taken
from the cover of the edition in `library/<book-slug>/`, so two packs never look alike and each
looks like its book. Nothing else in the design is per-book.

**Load the `ui-ux-pro-max` skill before writing the page.** It is mandatory for this pass — it
carries the accessibility, contrast, touch-target and typography checks this page is held to, and
its pre-delivery checklist is the last gate before publishing. `artifact-design` stays useful for
the publishing mechanics; it does not replace the structure below.

## The template

```bash
cp .claude/skills/book-distill/reference/page-template.html /tmp/page-build.html
```

The file is plain HTML with `{{PLACEHOLDER}}` slots. Fill every one — a leftover `{{...}}` in the
published page is a bug. The slots fall into five groups:

| Group | Slots | What goes in |
|---|---|---|
| Палитра | `PALETTE_LIGHT`, `PALETTE_DARK_MEDIA`, `PALETTE_DARK_ATTR` | token values taken from the cover (see below) |
| Шапка | `TITLE`, `BRAND_*`, `SIDE_FOOT`, `KICKER`, `H1`, `H1_SUB`, `THESIS`, `METALINE` | book identity and honest stats |
| Подписи | `NAV_*`, `GROUP_*`, `H2_*`, `LEDE_*`, and the UI strings in the cards view | translated into the pack's output language |
| Разделы | `VIEW_*` | the content of each view, built from the Markdown files |
| Данные | `QUOTES_JSON`, `CARDS_JSON`, `SCHEDULE_JSON`, `POSITIONS_JSON`, `STORE_KEY`, `QUOTE_ATTRIB` | generated from `quotes.md` and `anki.tsv`, never retyped |

Section ids, their order, the class names and the JavaScript are fixed. Translate the labels for a
non-Russian pack; never rename an id, drop a view, or add one.

## The thirteen views

Grouped in the rail as **Книга → Разбор → Работа** (translate the group names, keep the grouping).

| # | id | What it holds | Source file |
|---|----|---------------|-------------|
| 1 | `about` | overview: premise, shape, what happens, how it ends, who should read the original | `retelling.md` |
| 2 | `world` | cast and the book's vocabulary | `retelling.md` |
| 3 | `plot` | sequential retelling, chapter by chapter | `retelling.md` |
| 4 | `scenes` | key scenes with verbatim quotes, then the timeline | `retelling.md` |
| 5 | `spine` | thesis + pillars as `details.pillar`, two levels deep | `spine.md` |
| 6 | `map` | the claim table with strength chips | `argument-map.md` |
| 7 | `quotes` | three tiers, rendered from `QUOTES_JSON`, each with a copy button | `quotes.md` |
| 8 | `critique` | adversarial read, verdict pinned first | `critique.md` |
| 9 | `reception` | documented critics with publication and date, sources at the end | `reception.md` |
| 10 | `cards` | flip deck + 10-card quiz, progress in `localStorage` | `cards.md` / `anki.tsv` |
| 11 | `drills` | free recall, elaboration, transfer, schedule, misses log | `drills.md` |
| 12 | `apply` | positions as checkboxes, experiments, what to stop doing | `apply.md` |
| 13 | `method` | depth, coverage, what was not read, how it was built and verified | `book.json` |

Depth changes the volume inside these views, never their number: `quick` fills them thinly and
`deep` fills them densely, but the reader finds the same thirteen entries in the same order in
every pack.

## Palette from the cover

```bash
python3 - <<'PY'
import zipfile, glob, re
z = zipfile.ZipFile(glob.glob('library/<slug>/*.epub')[0])
name = [n for n in z.namelist() if re.search(r'cover.*\.(jpe?g|png)$', n, re.I)][0]
open('/tmp/cover.jpg','wb').write(z.read(name))
PY
```

Then look at the image, and quantise it for the actual values:

```bash
python3 -c "from PIL import Image; im=Image.open('/tmp/cover.jpg').convert('RGB').resize((160,240)); \
print(sorted(im.quantize(colors=8).convert('RGB').getcolors(38400), reverse=True))"
```

Mapping, in this order:

- **`--accent`** — the cover's dominant chromatic colour, darkened for the light theme until it
  passes 4.5:1 on `--panel`, lightened for the dark theme until it passes 4.5:1 on `--ground`.
- **`--steel`** — the cover's second colour (the type colour, the illustration, the spine band).
  Used for secondary marks; must also stay readable in both themes.
- **`--ground` / `--panel` / `--side`** — near-neutral, biased a few points toward the accent hue.
  Never a pure grey and never a saturated tint: the text sits on these.
- **`--accent-wash` / `--steel-wash`** — the same hues at the far end of the scale, for chips and
  pinned cards.

If the file has no cover image, derive the palette from the physical edition's binding and say so
in `book.json`. Two books in the library must not end up with the same accent hue; check the
existing `book.json` files before settling on one.

## Verification before publishing

1. Every `{{PLACEHOLDER}}` filled.
2. `node --check` on the extracted `<script>`; open/close counts equal for `details`, `section`,
   `div`, `table`, `blockquote`.
3. Every quote on the page found verbatim in `source/chapters/` — the page renders only what the
   Markdown files already contain, and nothing here may be written from memory.
4. `python .claude/skills/book-distill/scripts/ru_lint.py library/<slug>/page.html` for a Russian
   pack; fix everything outside verbatim quotes.
5. Render both themes and look at them (`html2png` is on PATH), including one expanded pillar.
6. Run the `ui-ux-pro-max` pre-delivery checklist: contrast in both themes, visible focus, touch
   targets, no horizontal scroll at 375px, `prefers-reduced-motion` honoured.

## Constraints

- Fully self-contained: inline CSS and JS, no CDN, no external images, no network calls.
- Theme-aware exactly as the template does it: full light palette on bare `:root`, dark overrides
  in `@media (prefers-color-scheme: dark)` guarded with `:root:not([data-theme="light"])`, and
  again under `:root[data-theme="dark"]`.
- Mobile: the rail collapses behind the burger below 900px; tables scroll inside `.scroller`.
- `<title>` short and stable across republishes.
