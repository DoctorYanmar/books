#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Structural check for a book page built from reference/page-template.html.

Every pack in the library renders the same skeleton. This script turns that from a
promise into a check: it verifies the section list and order, the components the
skeleton is made of, the navigation, the theme tokens, tag balance and the script.

    python3 page_lint.py library/<slug>/page.html

Exit code 0 when the page matches the skeleton, 1 when it does not. The check is
structural only — it says nothing about whether the prose or the quotes are any good.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

SECTIONS = ["retelling", "pillars", "map", "quotes", "reception",
            "critique", "recall", "apply", "links"]

# component -> (selector fragment, minimum occurrences, what it is)
COMPONENTS = {
    "topbar":       (r'class="topbar"', 1, "fixed top bar with the menu button"),
    "sidenav":      (r'class="sidenav"', 1, "collapsible left menu"),
    "scrim":        (r'class="scrim"', 1, "overlay behind the drawer on narrow screens"),
    "menu button":  (r'id="menuBtn"', 1, "menu toggle"),
    "theme button": (r'id="themeBtn"', 1, "theme toggle"),
    "skip link":    (r'class="skip"', 1, "skip-to-content link"),
    "flow box":     (r'class="flowbox"', 2, "graph wrapper in pillars and map"),
    "flow node":    (r'class="fnode"', 4, "argument nodes"),
    "flow edge":    (r'class="fedge', 3, "labelled edges between nodes"),
    "branch":       (r'class="fbranch', 2, "support and objection branches"),
    "leaf":         (r'class="fleaf"', 4, "support and objection cards"),
    "chapter cards": (r'class="chap"', 3, "retelling cards, one per chapter"),
    "self-check":   (r'class="selfcheck"', 1, "recall questions closing the retelling"),
    "quote grid":   (r'id="qgrid"', 1, "quote tiers"),
    "deck":         (r'class="deck"', 1, "flashcard deck"),
    "progress":     (r'class="progress"', 1, "quiz progress bar"),
    "table wrap":   (r'class="tablewrap"', 1, "scroll container for the claim table"),
}

TAGS = ["div", "section", "details", "article", "table", "blockquote",
        "ol", "ul", "li", "nav", "summary", "button", "svg", "header", "footer", "p"]

ALLOWED_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")


def fail(problems, msg):
    problems.append(msg)


def check(path):
    s = open(path, encoding="utf-8").read()
    problems = []

    left = sorted(set(re.findall(r"\{\{[A-Z_0-9]+\}\}", s)))
    if left:
        fail(problems, "unfilled placeholders: %s" % ", ".join(left))

    found = re.findall(r'<section id="([a-z-]+)"', s)
    if found != SECTIONS:
        fail(problems, "sections are %s, expected %s" % (found, SECTIONS))

    for name, (pattern, minimum, what) in COMPONENTS.items():
        n = len(re.findall(pattern, s))
        if n < minimum:
            fail(problems, "%s: found %d, expected at least %d (%s)" % (name, n, minimum, what))

    nav = re.findall(r'<li><a href="#([a-z-]+)"', s)
    if nav != SECTIONS:
        fail(problems, "menu links are %s, expected one per section in order" % nav)

    if "<title>" not in s[:8192]:
        fail(problems, "no <title> in the first 8KB — the artifact would be named by its filename")

    if "--accent" in s and "--stamp" not in s:
        fail(problems, "palette uses --accent; this skeleton names its tokens --stamp and --ochre")
    for token in ("--paper", "--ink", "--rule", "--wire", "--stamp", "--ochre", "--alarm"):
        if token + ":" not in s:
            fail(problems, "palette token %s is never defined" % token)
    if "prefers-color-scheme: dark" not in s:
        fail(problems, "no dark palette behind prefers-color-scheme")
    if '[data-theme="dark"]' not in s:
        fail(problems, "no dark palette behind [data-theme=dark] — the toggle would not win")
    if ':root:not([data-theme="light"])' not in s:
        fail(problems, "dark media block is not guarded with :root:not([data-theme=\"light\"])")
    if "prefers-reduced-motion" not in s:
        fail(problems, "prefers-reduced-motion is not honoured")

    loaded = re.findall(r'(?:src|<link[^>]*href)\s*=\s*"https?://([A-Za-z0-9.\-]+)', s)
    loaded += re.findall(r'url\(\s*[\'"]?https?://([A-Za-z0-9.\-]+)', s)
    loaded += re.findall(r'@import\s+url\(\s*[\'"]?https?://([A-Za-z0-9.\-]+)', s)
    loaded += re.findall(r'fetch\(\s*[\'"]https?://([A-Za-z0-9.\-]+)', s)
    for host in sorted(set(loaded)):
        if host not in ALLOWED_HOSTS:
            fail(problems, "page loads a resource from %s; only Google Fonts is allowed "
                           "(links in the text to sources are fine)" % host)

    for tag in TAGS:
        opened = len(re.findall(r"<%s[ >]" % tag, s))
        closed = s.count("</%s>" % tag)
        if opened != closed:
            fail(problems, "tag <%s>: %d opened, %d closed" % (tag, opened, closed))

    scripts = re.findall(r"<script>(.*?)</script>", s, re.S)
    if not scripts:
        fail(problems, "no inline script — the page would not be interactive")
    elif shutil.which("node"):
        for i, js in enumerate(scripts):
            tmp = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8")
            tmp.write(js)
            tmp.close()
            r = subprocess.run(["node", "--check", tmp.name], capture_output=True, text=True)
            os.unlink(tmp.name)
            if r.returncode:
                fail(problems, "script %d does not parse: %s" % (i + 1, r.stderr.strip().splitlines()[-1]))
    else:
        problems.append("note: node is not on PATH, the inline script was not parsed")

    if "localStorage" not in s:
        fail(problems, "no localStorage — deck progress and menu state would not survive a reload")

    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    args = ap.parse_args()

    problems = check(args.path)
    if problems:
        print("%s does not match the skeleton:\n" % args.path)
        for p in problems:
            print("  · " + p)
        print("\n%d problem(s)." % len(problems))
        return 1

    print("%s matches the skeleton: %d sections in order, every component present, "
          "both themes defined, script parses." % (args.path, len(SECTIONS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
