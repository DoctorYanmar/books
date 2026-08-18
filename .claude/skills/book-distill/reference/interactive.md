# Interactive page spec (Pass 5)

One self-contained HTML file per book, published with the Artifact tool. Write it to
`library/<book-slug>/page.html`, publish, store the returned URL in `book.json`. Republishing the
same path keeps the same URL — always reuse the path so links stay stable.

## Three hard rules

**1. The skeleton is the same for every book.** It is not designed per book and not improvised.
It lives in `reference/page-template.html`: the same shell, the same nine sections in the same
order, the same component classes, the same JavaScript. What changes from book to book is the
content, the depth, and the palette — nothing else. A page that invents its own section order is
a defect, however good it looks.

**2. The palette comes from the book's cover.** Every book gets its own colour identity, taken
from the cover of the edition in `library/<book-slug>/`, so two packs never look alike and each
looks like its book. One exception, recorded in `book.json` when it applies: the skeleton already
uses red for weak claims and objections, so a red or crimson cover colour cannot be the accent —
take the cover's second colour, or a neighbour of it, and say why.

**3. `1984` and `frankenstein` predate this skeleton** and keep the pages they have. The skeleton
applies to every book distilled from now on; do not rebuild the old two unless asked.

**Load the `ui-ux-pro-max` skill before writing the page.** It is mandatory for this pass — it
carries the accessibility, contrast, touch-target and typography checks this page is held to, and
its pre-delivery checklist is the last gate before publishing. `artifact-design` stays useful for
the publishing mechanics; it does not replace the structure below.

## The template

```bash
cp .claude/skills/book-distill/reference/page-template.html /tmp/page-build.html
```

The file is plain HTML with `{{PLACEHOLDER}}` slots. Fill every one — a leftover `{{...}}` in the
published page is a bug. The slots fall into six groups:

| Group | Slots | What goes in |
|---|---|---|
| Палитра | `PALETTE_LIGHT`, `PALETTE_DARK` | token values taken from the cover (see below) |
| Шапка | `TITLE`, `TOPBAR_*`, `SIDE_*`, `NAV_ITEMS`, `KICKER`, `H1`, `SUBTITLE`, `BYLINE`, `THESIS`, `LEDGER`, `METALINE` | book identity and honest stats |
| Подписи | every `UI_*` slot and `UI_JSON` | interface strings, translated into the pack's output language |
| Разделы | `SECHEAD_1…9`, `VIEW_*` | the content of each section, built from the Markdown files |
| Графы | `FLOW_SPINE`, `FLOW_MAP`, `FLOW_NOTE_SPINE`, `FLOW_NOTE_MAP`, `MAP_TABLE`, `MAP_NOTES` | the two node graphs and the table behind the map |
| Данные | `QUOTES`, `CARDS_JSON`, `STORE_KEY`, `FOOTER` | generated from `quotes.md` and `anki.tsv`, never retyped |

Section ids, their order, the class names and the JavaScript are fixed. Translate the labels for a
non-Russian pack; never rename an id, drop a section, or add one.

## The nine sections

| # | id | What it holds | Source file |
|---|----|---------------|-------------|
| 1 | `pereskaz` | overview, cast, book vocabulary, chapter-by-chapter retelling, key scenes with verbatim quotes, timeline | `retelling.md` |
| 2 | `lestnica` | thesis + pillars as a node graph, each pillar opening in two steps | `spine.md` |
| 3 | `karta` | the claim graph — supports and objections per pillar — with the table behind a switch | `argument-map.md` |
| 4 | `citaty` | three tiers with a copy button each | `quotes.md` |
| 5 | `kritiki` | documented critics with publication and date, sources at the end | `reception.md` |
| 6 | `razbor` | adversarial read, verdict pinned first | `critique.md` |
| 7 | `povtorenie` | flip deck + 10-card quiz, progress in `localStorage` | `cards.md` / `anki.tsv` |
| 8 | `primenenie` | positions as checkboxes, experiments, what to stop doing | `apply.md` |
| 9 | `svyazi` | agreements and contradictions with the other packs | `links.md` |

Depth changes the volume inside these sections, never their number: `quick` fills them thinly and
`deep` fills them densely, but the reader finds the same nine entries in the same order in every
pack.

## The left menu

Fixed top bar, fixed drawer under it. The burger toggles the drawer at any width and swaps to a
close icon while it is open; the state is remembered in `localStorage` on desktop and always
starts closed on phones. Below 1120px the drawer floats over the page with a scrim, closes on
`Esc`, on scrim click and on picking a section; from 1120px it pushes the content instead. An
`IntersectionObserver` marks the current section with `aria-current`. None of this is per book —
only the nine labels are.

## The two graphs

Both are built out of the same four pieces, and both must stay inside normal document flow — no
absolute positioning of nodes, so nothing can overlap at any width.

```html
<!-- узел -->
<details class="fnode" data-path="main|side" data-node="P1"><summary>
  <span class="col1">
    <span class="pid">Опора P1 · гл. 0–2</span>
    <span class="claim">…утверждение…</span>
    <span class="chips"><span class="chip s-strong">факты — сильные</span></span>
  </span><span class="chev">…svg…</span>
</summary><div class="body">…</div></details>

<!-- ребро между узлами: sec = пунктир, боковой путь -->
<div class="fedge sec" aria-hidden="true"><span class="elabel">боковые опоры</span></div>

<!-- ветка внутри узла: без contra — подпорки, с contra — возражения -->
<div class="fbranch contra">
  <div class="fleaf"><span class="lid">против P1</span><span class="lclaim">…</span></div>
</div>
```

- **`lestnica`** — a `.fnode.root` holding the thesis, then the pillars. Solid edges along the
  load-bearing chain, dashed edges to the side pillars. Every edge carries a label naming the step
  («несущая опора», «перенос в сегодня»). The chain/side split is `[analysis]`; say so in
  `FLOW_NOTE_SPINE`.
- **`karta`** — one node per pillar in numeric order, each holding a solid `.fbranch` of supports
  and a dashed `.fbranch.contra` of objections, every objection labelled with the claim it attacks.
  The table goes in `MAP_TABLE` behind the «схема / таблица» switch.

The switches, the «раскрыть все» button and the legends are part of the template — do not rebuild
them per book. Both graphs stay readable without colour: paths are labelled in words as well as
drawn.

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

- **`--stamp`** — the cover's dominant chromatic colour, darkened for the light theme until it
  passes 4.5:1 on `--card`, lightened for the dark theme until it passes 4.5:1 on `--paper`.
  If that colour is a red or crimson it collides with `--alarm`, which marks weak claims and
  objections: take the second colour instead and record the swap in `book.json`.
- **`--ochre`** — the cover's second colour. Carries `[разбор]` marks and the side paths in the
  graphs, so it must also clear 4.5:1 on `--paper`, `--paper-2` and `--card`.
- **`--alarm`** — stays a warning red, distinct from both of the above.
- **`--paper` / `--paper-2` / `--card`** — near-neutral, biased a few points toward the accent hue.
  Never a pure grey and never a saturated tint: the text sits on these.
- **`--rule` / `--wire`** — hairlines and graph wires. `--wire` is the darker of the two and must
  clear 3:1 on every surface it is drawn on, or the graph stops reading.

If the file has no cover image, derive the palette from the physical edition's binding and say so
in `book.json`. Two books in the library must not end up with the same accent hue; check the
existing `book.json` files before settling on one.

## Verification before publishing

1. Every `{{PLACEHOLDER}}` filled.
2. `node --check` on the extracted `<script>`; open/close counts equal for `div`, `section`,
   `details`, `article`, `ul`, `li`, `table`, `blockquote`, `button`, `svg`.
3. Every quote on the page found verbatim in `source/chapters/` — the page renders only what the
   Markdown files already contain, and nothing here may be written from memory.
4. `python .claude/skills/book-distill/scripts/ru_lint.py library/<slug>/page.html` for a Russian
   pack; fix everything outside verbatim quotes.
5. Contrast computed, not eyeballed: text tokens ≥4.5:1 and `--wire` ≥3:1 on every surface, in
   both themes.
6. Render 390, 768, 1024 and 1440px in both themes (`html2png` is on PATH), including one open
   node in each graph and the drawer open on the phone width.
7. Run the `ui-ux-pro-max` pre-delivery checklist: contrast in both themes, visible focus, touch
   targets, no horizontal scroll at 375px, `prefers-reduced-motion` honoured.

Rendering a single section is easier than scrolling a screenshot to it: append a script that drops
the masthead and every section but one, then shoot that file.

## Constraints

- Fully self-contained: inline CSS and JS, no CDN, no external images, no network calls.
- Theme-aware exactly as the template does it: full light palette on bare `:root`, dark overrides
  in `@media (prefers-color-scheme: dark)` guarded with `:root:not([data-theme="light"])`, and
  again under `:root[data-theme="dark"]`.
- Mobile: the drawer floats over the page below 1120px; tables scroll inside `.tablewrap`.
- `<title>` short and stable across republishes.
