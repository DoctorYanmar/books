#!/usr/bin/env python3
"""Generate the claim-map slots of page.html from argument-map.md.

    python3 build_map.py library/<slug> [--out slots-map.json]

Writes {"FLOW_MAP", "FLOW_NOTE_MAP", "MAP_TABLE", "MAP_NOTES"} — the graph nodes, the
table behind the graph/table switch and the two notes. The markup is derived from the
file's own structure (one `## P<n>` block per pillar, with **Утверждение**, **На чём
держится**, **Сила**, **Возражение**, **Что уцелеет**), so the map on the page can never
drift from the map in the pack: regenerate instead of editing the HTML.

Which pillars are load-bearing is read from the closing section of argument-map.md, the
one that names them — the same `[analysis]` call the pillars graph uses.
"""
import argparse, json, re, html, pathlib, sys

ap = argparse.ArgumentParser()
ap.add_argument("book", help="library/<slug>")
ap.add_argument("--out", default=None, help="output JSON (default <book>/state/slots-map.json)")
args = ap.parse_args()

BOOK = pathlib.Path(args.book)
src = (BOOK / "argument-map.md").read_text(encoding="utf-8")

tail = src.rsplit("\n## ", 1)[-1]
MAIN = set(re.findall(r"\*\*(P\d)\*\*", tail.split("Боковые")[0])) or {"P1"}

blocks = re.split(r"\n## (?=P\d)", src)[1:]
pillars = []
for b in blocks:
    head, body = b.split("\n", 1)
    pid, title = head.split(" — ", 1)
    def field(name):
        m = re.search(r"\*\*%s\.\*\*\s*(?:`\[[^`]+\]`)?\s*(.+?)(?=\n\n\*\*|\n\n`|\Z)" % name, body, re.S)
        return m.group(1).strip() if m else ""
    leaves = re.findall(r"^- (.+)$", body, re.M)
    obj = re.findall(r"\*\*Возражение\.\*\*\s*`\[разбор\]`\s*(.+?)(?=\n\n)", body, re.S)
    extra = re.findall(r"^`\[разбор\]` (Второй удар.+?)(?=\n\n)", body, re.S | re.M)
    pillars.append(dict(pid=pid.strip(), title=title.strip(), claim=field("Утверждение"),
                        leaves=leaves, strength=field("Сила"),
                        objections=[o.strip() for o in obj + extra],
                        survives=field("Что уцелеет")))

def esc(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`\[(книга|разбор)\]`", "", s)
    return s.strip()

def chapref(text):
    m = re.search(r"\((введение|гл\. [^)]+)\)", text)
    return m.group(1) if m else "гл."

def strength_chip(s):
    low = s.lower()
    if low.startswith("сильн"): return "s-strong", "доказательства сильные"
    if low.startswith("анекдот"): return "s-weak", "доказательства анекдотические"
    return "s-mixed", "доказательства смешанные"

def strip_ref(text):
    """The chapter already sits in the leaf's label — repeating it in the claim reads as a stutter."""
    return re.sub(r"\s*\((введение|гл\.[^)]*)\)", "", text).strip()


def short(text, n=190):
    """Trim to the last full sentence that fits — a cut mid-word reads as a bug."""
    text = re.sub(r"\s*\((введение|гл\.[^)]*)\)", "", text).strip()
    if len(text) <= n:
        return text
    head = text[:n]
    cut = max(head.rfind(". "), head.rfind("! "), head.rfind("? "))
    if cut > n * 0.5:
        return head[:cut + 1]
    cut = head.rfind(" ")
    return head[:cut].rstrip(" ,;:—-") + "…"


def chapter_range(refs):
    """Fold «гл. 5–6», «гл. 8», «введение» into one span list: «введение, гл. 5–6, 8»."""
    nums, words = set(), []
    for r in refs:
        found = re.findall(r"(\d+)\s*[–-]\s*(\d+)|(\d+)", r)
        if not found:
            words.append(r)
            continue
        for a, b, single in found:
            if single:
                nums.add(int(single))
            else:
                nums.update(range(int(a), int(b) + 1))
    spans, ordered, i = [], sorted(nums), 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and ordered[j + 1] == ordered[j] + 1:
            j += 1
        spans.append(str(ordered[i]) if i == j else "%d\u2013%d" % (ordered[i], ordered[j]))
        i = j + 1
    parts = sorted(set(words)) + (["гл. " + ", ".join(spans)] if spans else [])
    return ", ".join(parts)


def strength_chip(s):
    low = s.lower()
    if low.startswith("сильн"): return "s-strong", "доказательства сильные"
    if low.startswith("анекдот"): return "s-weak", "доказательства анекдотические"
    return "s-mixed", "доказательства смешанные"

def strip_ref(text):
    """The chapter already sits in the leaf's label — repeating it in the claim reads as a stutter."""
    return re.sub(r"\s*\((введение|гл\.[^)]*)\)", "", text).strip()


def short(text, n=190):
    """Trim to the last full sentence that fits — a cut mid-word reads as a bug."""
    text = re.sub(r"\s*\((введение|гл\.[^)]*)\)", "", text).strip()
    if len(text) <= n:
        return text
    head = text[:n]
    cut = max(head.rfind(". "), head.rfind("! "), head.rfind("? "))
    if cut > n * 0.5:
        return head[:cut + 1]
    cut = head.rfind(" ")
    return head[:cut].rstrip(" ,;:—-") + "…"



nodes = []
for p in pillars:
    cls, chip = strength_chip(p["strength"])
    path = "main" if p["pid"] in MAIN else "side"
    label = "Опора %s · %s" % (p["pid"], chapter_range({chapref(l) for l in p["leaves"]}))
    sup = "\n".join(
        '        <div class="fleaf"><span class="lid">%s</span><span class="lclaim">%s</span></div>'
        % (html.escape(chapref(l)), esc(html.escape(strip_ref(l))))
        for l in p["leaves"])
    contra = "\n".join(
        '        <div class="fleaf"><span class="lid">против %s</span><span class="lclaim">%s</span></div>'
        % (p["pid"], esc(html.escape(strip_ref(o))))
        for o in p["objections"])
    nodes.append(
'    <details class="fnode" data-path="%s" data-node="%s"><summary>\n'
'      <span class="col1">\n'
'        <span class="pid">%s</span>\n'
'        <span class="claim">%s</span>\n'
'        <span class="chips"><span class="chip %s">%s</span></span>\n'
'      </span><span class="chev" aria-hidden="true">▾</span>\n'
'    </summary><div class="body">\n'
'      <div class="fbranch">\n%s\n      </div>\n'
'      <div class="fbranch contra">\n%s\n      </div>\n'
'      <p class="note">Что уцелеет: %s</p>\n'
'    </div></details>'
        % (path, p["pid"], html.escape(label), esc(html.escape(p["claim"])), cls, chip,
           sup, contra, esc(html.escape(p["survives"]))))

flow_map = "\n".join(nodes)

rows = "\n".join(
'        <tr><th scope="row">%s<br><span class="lbl">%s</span></th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
 % (p["pid"], html.escape(p["title"]),
    "<br>".join(esc(html.escape(short(l, 170))) for l in p["leaves"]),
    strength_chip(p["strength"])[1].replace("доказательства ", ""),
    esc(html.escape(short(p["objections"][0] if p["objections"] else "", 260))),
    esc(html.escape(short(p["survives"], 300))))
 for p in pillars)

map_table = (
'      <table>\n        <thead><tr><th scope="col">Опора</th><th scope="col">На чём держится</th>'
'<th scope="col">Сила</th><th scope="col">Возражение</th><th scope="col">Что уцелеет</th></tr></thead>\n'
'        <tbody>\n%s\n        </tbody>\n      </table>' % rows)

data = {
 "FLOW_MAP": flow_map,
 "FLOW_NOTE_MAP": ("Сплошная ветка ведёт к тому, на чём утверждение стоит, пунктирная — к тому, что по нему бьёт. "
                   "Возражения здесь наши, а не авторские; часть из них до нас высказали названные историки — "
                   "их имена и ссылки в разделе «Что сказали критики»."),
 "MAP_TABLE": map_table,
 "MAP_NOTES": ('<p class="note">Столбец «Сила» читается так: <b>сильные</b> — довод держится на документе или на '
               'признании участника; <b>смешанные</b> — факты проверяемы, а мотив выведен из совпадения интересов; '
               '<b>анекдотические</b> — довод держится на позднем воспоминании. Оценка наша.</p>'),
}
out = pathlib.Path(args.out) if args.out else (BOOK / "state" / "slots-map.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

print("pillars   :", len(pillars), "(load-bearing: %s)" % ", ".join(sorted(MAIN)))
print("leaves    :", sum(len(p["leaves"]) for p in pillars),
      "| objections:", sum(len(p["objections"]) for p in pillars))
print("slots     :", out, "(%d KB of markup)" % (len(flow_map) // 1024))
