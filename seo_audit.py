#!/usr/bin/env python3
"""
seo_audit.py — Full SEO gap report for ivy-wolf-site (all 16 routes).
Exit 0 = CLEAN (no gaps).  Exit 1 = gaps remain.
"""
import os
import re
import sys

ROUTES = [
    ("index.html", "/"),
    ("about/index.html", "/about"),
    ("contact/index.html", "/contact"),
    ("legal/index.html", "/legal"),
    ("services/index.html", "/services"),
    ("shop/index.html", "/shop"),
    ("shop/a-work/index.html", "/shop/a-work"),
    ("journal/index.html", "/journal"),
    ("journal/behind-the-first-canvas/index.html", "/journal/behind-the-first-canvas"),
    ("thank-you/index.html", "/thank-you"),
    ("collections/index.html", "/collections"),
    ("collections/austin-texas/index.html", "/collections/austin-texas"),
    ("collections/the-bahamas/index.html", "/collections/the-bahamas"),
    ("collections/telluride-colorado/index.html", "/collections/telluride-colorado"),
    ("collections/sedona-arizona/index.html", "/collections/sedona-arizona"),
    ("collections/panama/index.html", "/collections/panama"),
]

TITLE_MIN = 30
TITLE_MAX = 60
DESC_MIN = 50
DESC_MAX = 160


def get_meta_content(content: str, attr_name: str) -> str:
    """Extract meta content correctly, respecting the opening quote type."""
    # Match name="attr_name" content="value" (double quotes)
    m = re.search(
        rf'<meta\s+name="{re.escape(attr_name)}"\s+content="([^"]*)"',
        content, re.IGNORECASE,
    )
    if m:
        return m.group(1)
    # Try reversed attribute order
    m = re.search(
        rf'<meta\s+content="([^"]*)"\s+name="{re.escape(attr_name)}"',
        content, re.IGNORECASE,
    )
    if m:
        return m.group(1)
    # Try single quotes (less common)
    m = re.search(
        rf"<meta\s+name='{re.escape(attr_name)}'\s+content='([^']*)'",
        content, re.IGNORECASE,
    )
    if m:
        return m.group(1)
    return ""


def audit(path: str, route: str) -> list:
    gaps = []
    content = open(path, encoding="utf-8").read()

    # ── Title ──────────────────────────────────────────────────────────────
    title_m = re.search(r'<title[^>]*>(.*?)</title>', content, re.DOTALL | re.IGNORECASE)
    if not title_m:
        gaps.append("NO title tag")
    else:
        t = title_m.group(1).strip()
        if len(t) < TITLE_MIN:
            gaps.append(f"title too short ({len(t)} chars): {t!r}")
        elif len(t) > TITLE_MAX:
            gaps.append(f"title too long ({len(t)} chars): {t!r}")

    # ── Meta description ───────────────────────────────────────────────────
    desc = get_meta_content(content, "description")
    if not desc:
        gaps.append("NO meta description")
    elif len(desc) < DESC_MIN:
        gaps.append(f"description too short ({len(desc)} chars): {desc!r}")
    elif len(desc) > DESC_MAX:
        gaps.append(f"description too long ({len(desc)} chars)")

    # ── Canonical ──────────────────────────────────────────────────────────
    if 'rel="canonical"' not in content and "rel='canonical'" not in content:
        gaps.append("NO canonical link")

    # ── Open Graph ────────────────────────────────────────────────────────
    for og_prop in ("og:title", "og:description", "og:image"):
        if og_prop not in content:
            gaps.append(f"NO {og_prop}")

    # OG description content length
    og_desc_m = re.search(r'property="og:description"\s+content="([^"]*)"', content, re.IGNORECASE)
    if og_desc_m:
        od = og_desc_m.group(1).strip()
        if len(od) < DESC_MIN:
            gaps.append(f"og:description too short ({len(od)} chars): {od!r}")

    # ── H1 ────────────────────────────────────────────────────────────────
    h1s = re.findall(r'<h1[^>]*>.*?</h1>', content, re.DOTALL | re.IGNORECASE)
    if not h1s:
        gaps.append("NO h1 tag")
    elif len(h1s) > 1:
        gaps.append(f"MULTIPLE h1 tags ({len(h1s)})")

    # ── JSON-LD ───────────────────────────────────────────────────────────
    if 'application/ld+json' not in content:
        gaps.append("NO JSON-LD schema")

    # ── Image alt text ────────────────────────────────────────────────────
    imgs = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
    missing_alt = [img for img in imgs if 'alt=' not in img.lower()]
    if missing_alt:
        gaps.append(f"{len(missing_alt)} image(s) missing alt text")

    return gaps


def main():
    print("=" * 70)
    print("seo_audit.py — Ivy Wolf Art SEO gap report (all 16 routes)")
    print("=" * 70)

    total_gaps = 0
    clean = 0
    for path, route in ROUTES:
        if not os.path.exists(path):
            print(f"  ❌ {route:<45} FILE NOT FOUND")
            total_gaps += 1
            continue
        gaps = audit(path, route)
        total_gaps += len(gaps)
        if not gaps:
            clean += 1
            print(f"  ✅ {route:<45} CLEAN")
        else:
            for g in gaps:
                print(f"  ❌ {route:<45} {g}")

    print()
    print(f"Routes clean: {clean}/16  |  Total gaps: {total_gaps}")

    if total_gaps == 0:
        print("\n✅ GAP LIST EMPTY — all 16 routes pass SEO audit.")
        sys.exit(0)
    else:
        print(f"\n❌ {total_gaps} gap(s) remain — fix and re-run.")
        sys.exit(1)


if __name__ == "__main__":
    main()
