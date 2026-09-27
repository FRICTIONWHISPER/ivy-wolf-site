#!/usr/bin/env python3
"""Fix the mobile nav squawk on all 16 ivy-wolf.com routes.

AV-2's CHECKRIDE, 2026-09-26: "mobile nav is gone - at 390px there is no
hamburger menu, so a phone visitor can read the home page and go nowhere
else on the site."

Confirmed on the LIVE site by the Director:
    @media (max-width: 800px) { .nav-links { display: none; } }
and no toggle button anywhere in the markup. Under 800px the six links
vanish with nothing in their place. Every phone visitor is trapped on
whatever page they land on.

THE FIX - no JavaScript, no new routes, no structural change:
  1. Add a <details> disclosure holding the same links. It is a native
     HTML control: it opens and closes with no script, it is keyboard
     accessible, and it cannot break if JS fails.
  2. Show it only under 800px - exactly where .nav-links is hidden.
  3. Desktop is untouched above 800px.

Runs through bounded_region_editor: every find must match EXACTLY ONCE in
a file or that file HALTS and is reported. Dry-run unless --execute.
"""
from __future__ import annotations
import os
import sys

CODE = "/Users/theaviator/AV-0/business/_wt/bkw-guard/website-whisper/03_ATOMIC/00_CODE"
sys.path.insert(0, CODE)
import bounded_region_editor as BRE  # noqa: E402

REPO = os.path.dirname(os.path.abspath(__file__))

ROUTES = [
    "index.html",
    "about/index.html", "contact/index.html", "legal/index.html",
    "services/index.html", "shop/index.html", "shop/a-work/index.html",
    "journal/index.html", "journal/behind-the-first-canvas/index.html",
    "thank-you/index.html", "collections/index.html",
    "collections/austin-texas/index.html", "collections/the-bahamas/index.html",
    "collections/telluride-colorado/index.html",
    "collections/sedona-arizona/index.html", "collections/panama/index.html",
]

# ---- 1. the CSS. Anchored on the existing mobile rule so it lands in the
#         same media query that hides the desktop links.
CSS_FIND = "      .nav-links { display: none; }"
CSS_REPL = """      .nav-links { display: none; }
      .nav-menu { display: block; position: relative; }
      .nav-menu > summary {
        list-style: none; cursor: pointer; padding: .5rem .25rem;
        font-size: .6875rem; letter-spacing: .14em; text-transform: uppercase;
        color: var(--muted-dark); user-select: none;
      }
      .nav-menu > summary::-webkit-details-marker { display: none; }
      .nav-menu[open] > summary { color: var(--ink); }
      .nav-menu-panel {
        position: absolute; right: 0; top: 2.25rem; z-index: 40;
        min-width: 13rem; background: var(--paper);
        border: 1px solid var(--rule); padding: .5rem 0;
      }
      .nav-menu-panel a {
        display: block; padding: .6rem 1.1rem; text-decoration: none;
        font-size: .8125rem; color: var(--muted-light);
      }
      .nav-menu-panel a:hover { color: var(--ink); }"""

# ---- 2. the markup. The same six destinations the desktop nav carries.
NAV_FIND = '    <div class="nav-links">'
NAV_REPL = """    <details class="nav-menu">
      <summary>Menu</summary>
      <div class="nav-menu-panel">
        <a href="/">Home</a>
        <a href="/collections">Collections</a>
        <a href="/journal">Journal</a>
        <a href="/about">About</a>
        <a href="/services">Services</a>
        <a href="/contact">Commission a work</a>
      </div>
    </details>
    <div class="nav-links">"""

# ---- 3. desktop must NOT see the disclosure.
BASE_FIND = "    .nav-links { display: flex; align-items: center; gap: 2rem; }"
BASE_REPL = """    .nav-links { display: flex; align-items: center; gap: 2rem; }
    .nav-menu { display: none; }"""

EDITS = [
    (BASE_FIND, BASE_REPL, "desktop: hide the disclosure"),
    (CSS_FIND, CSS_REPL, "mobile: style the disclosure"),
    (NAV_FIND, NAV_REPL, "markup: add the disclosure"),
]


def main(argv):
    execute = "--execute" in argv
    print(("EXECUTE" if execute else "DRY-RUN") + " - mobile nav fix, %d routes" % len(ROUTES))
    print()
    ok = halted = 0
    for rel in ROUTES:
        path = os.path.join(REPO, rel)
        if not os.path.exists(path):
            print("  MISSING  " + rel)
            halted += 1
            continue
        src = open(path, encoding="utf-8").read()
        if 'class="nav-menu"' in src:
            print("  SKIP     " + rel + "  (already fixed - idempotent)")
            ok += 1
            continue
        bad = [lab for find, _, lab in EDITS if src.count(find) != 1]
        if bad:
            print("  HALT     %s  -> %s did not match exactly once" % (rel, "; ".join(bad)))
            halted += 1
            continue
        out = src
        for find, repl, _ in EDITS:
            out = out.replace(find, repl, 1)
        if execute:
            BRE.safe_write(path, out) if hasattr(BRE, "safe_write") else open(
                path, "w", encoding="utf-8").write(out)
        print("  OK       " + rel)
        ok += 1
    print()
    print("  ready: %d   halted: %d" % (ok, halted))
    if not execute:
        print("\n  re-run with --execute to write")
    return 1 if halted else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
