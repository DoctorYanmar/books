# Interactive page spec (Pass 5)

One self-contained HTML file per book, published with the Artifact tool. Load the
`artifact-design` skill first — this file specifies *behavior and information architecture*, not
visual design.

Write the file to `<book-slug>/page.html`, publish, and store the returned URL in `book.json`.
Republishing the same file path updates the same URL — always reuse the path so the link is stable.

## The one job of this page

Let the user go from "knows nothing" to "holds the argument" in a single scroll, at a depth they
choose per claim — and then be tested. It is a study instrument, not a summary poster.

## Required sections, in order

1. **Header** — title, author, year, one-line thesis, and honest stats: chapters covered, words
   in the original, estimated read time of the page, coverage caveat if sampled.

2. **Retelling — the first pages, before any analysis.** Overview, cast, world, the sequential
   plot retelling, key scenes, timeline. The plot page gets its own navigation entry and is
   readable start to finish on its own. A reader who lands on the page and reads only this section
   must come away able to describe the book. Everything here is `[book]`; no interpretation.

3. **The ladder (progressive disclosure)** — the core interaction. Each pillar renders collapsed:
   claim + evidence-strength chip (`strong` / `mixed` / `anecdotal`). Expanding reveals the L3
   mechanism bullets; expanding again reveals L4 evidence and the load-bearing quote. Three levels,
   collapsed by default, keyboard-operable. `[analysis]` content is visually distinct from
   `[book]` content everywhere it appears — one consistent marker, explained once in a legend.

4. **Argument map** — the `argument-map.md` table rendered as a dependency view: pillars as nodes,
   support as children, with the weak links marked. An inline SVG tree is enough; if the map has
   more than ~15 nodes, fall back to the table with strength chips. Must scroll inside its own
   container, never widen the page.

5. **Quote cards** — the three tiers from `quotes.md` (load-bearing / sharp / suspect), each with
   its chapter reference and a copy button. The "suspect" tier keeps its `[analysis]` note visible.

6. **Reception** — what the documented critics said: contemporary reviews, the major objections, the
   writers who answered back, the book's afterlife, and a source list. Every entry names a critic,
   a publication and a year; nothing here may be written from memory.

7. **Critique panel** — collapsible, one entry per section of `critique.md`, verdict pinned at
   the top and always visible.

8. **Retrieval** — two modes over the deck in `cards.md`:
   - *Flip*: question shown, answer hidden, self-grade got-it / missed. Track the session in
     `localStorage` keyed by book slug so progress survives a reload.
   - *Quiz*: 10 cards sampled per round, weighted toward previously missed cards, score at the end
     with the missed fronts listed and their chapter references linked back to the ladder.
   Cards are embedded as a JS array in the page — no network calls of any kind.

9. **Apply** — the checklist from `apply.md`, checkboxes persisted in `localStorage`.

10. **Cross-book links** — only rendered when `links.md` exists.

## Constraints

- Fully self-contained: inline CSS/JS, no CDN, no fonts, no external images. A strict CSP blocks
  every external request.
- Theme-aware per the Artifact rules: full light palette on bare `:root`, dark overrides in both
  `@media (prefers-color-scheme: dark)` (guarded with `:root:not([data-theme="light"])`) and
  `:root[data-theme="dark"]`, explicit token background on `body`.
- Mobile-first: the ladder must stay readable at 375px. Tables and the argument map get their own
  `overflow-x: auto` wrapper.
- No fabricated content in the page — it renders only what the Markdown files already contain.
- Keep the `<title>` short and stable across republishes: the book's short title.
