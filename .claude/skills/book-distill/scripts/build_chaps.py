#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the `Глава за главой` block of page.html from retelling.md.

    python3 build_chaps.py library/<slug>/retelling.md library/<slug>/page.html

The page skeleton is shared across books, so the chapter articles are generated, never
hand-written: markdown blocks map onto the components the template already defines.
"""
import re
import sys

MD, PAGE = sys.argv[1], sys.argv[2]

md = open(MD, encoding="utf-8").read()

# Slot labels are translated with the pack, so pick the set the retelling was written in.
SLOTS = {
    "ru": {"heading": "## Пересказ", "claim": "Утверждение", "evidence": "Чем держится",
           "open": "Что осталось открытым", "next": "Дальше"},
    "en": {"heading": "## Retelling", "claim": "Claim", "evidence": "What holds it up",
           "open": "Left open", "next": "Next"},
}
lang = "ru" if SLOTS["ru"]["heading"] in md else "en"
if SLOTS[lang]["heading"] not in md:
    sys.exit(f"no retelling heading in {MD} — expected one of "
             + ", ".join(repr(s["heading"]) for s in SLOTS.values()))
body = re.split(r"\n## ", md.split(SLOTS[lang]["heading"], 1)[1])[0]

EVIDENCE = SLOTS[lang]["evidence"]
OPEN = SLOTS[lang]["open"]
NEXT = SLOTS[lang]["next"]
CLAIM = SLOTS[lang]["claim"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s):
    s = esc(s.strip())
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


articles = []
for chunk in re.split(r"\n### ", body)[1:]:
    lines = chunk.split("\n")
    head = lines[0].strip()
    cnum, title = head.split(" · ", 1) if " · " in head else ("", head)
    raw = "\n".join(lines[1:]).strip()

    out = ['      <article class="chap">',
           '      <span class="cnum">%s</span>' % esc(cnum),
           '      <h4>%s</h4>' % esc(title)]

    for block in re.split(r"\n\s*\n", raw):
        block = block.strip()
        if not block:
            continue
        if block.startswith(">"):
            text = re.sub(r"^>\s*", "", block, flags=re.M).replace("\n", " ")
            text = re.sub(r"^\*\*разбор\.\*\*\s*", "", text.strip())
            out.append('      <p class="an-block"><span class="mark an">разбор</span> %s</p>'
                       % inline(text))
            continue
        m = re.match(r"\*\*(.+?)\.\*\*\s*(.*)", block, flags=re.S)
        if not m:
            out.append("      <p>%s</p>" % inline(block.replace("\n", " ")))
            continue
        label, rest = m.group(1), m.group(2).strip()
        if label == CLAIM:
            out.append('      <p class="lead">%s</p>' % inline(rest.replace("\n", " ")))
        elif label == EVIDENCE:
            items = [ln.strip()[2:].strip() for ln in rest.split("\n")
                     if ln.strip().startswith("- ")]
            lis = "".join("<li>%s</li>" % inline(i) for i in items)
            out.append('      <div><span class="lbl">%s</span><ul>%s</ul></div>'
                       % (esc(label), lis))
        elif label == OPEN:
            out.append('      <div><span class="lbl">%s</span><p class="open">%s</p></div>'
                       % (esc(label), inline(rest.replace("\n", " "))))
        elif label == NEXT:
            out.append('      <div><span class="lbl">%s</span><p class="fwd">%s</p></div>'
                       % (esc(label), inline(rest.replace("\n", " "))))
        else:
            out.append('      <div><span class="say">%s.</span><p>%s</p></div>'
                       % (esc(label), inline(rest.replace("\n", " "))))

    out.append("      </article>")
    articles.append("\n".join(out))

html = open(PAGE, encoding="utf-8").read()
if '<div class="chaps">' not in html and "{{VIEW_PERESKAZ}}" in html:
    # a page straight off the template: open the container the articles live in
    html = html.replace("{{VIEW_PERESKAZ}}", '    <div class="chaps">\n    </div>')
if '<div class="chaps">' not in html:
    sys.exit(f'{PAGE} has neither <div class="chaps"> nor the {{{{VIEW_PERESKAZ}}}} slot')
start = html.index('<div class="chaps">')
open_tag_end = start + len('<div class="chaps">')
end = html.index("\n    </div>", open_tag_end)
new = html[:open_tag_end] + "\n" + "\n".join(articles) + html[end:]
open(PAGE, "w", encoding="utf-8").write(new)
print("chapters written: %d" % len(articles))
