#!/usr/bin/env python3
"""
seo_inject.py — Bounded SEO injector for ivy-wolf-site.
Adds canonical, OG, Twitter-card, and JSON-LD to all 16 routes.

Safety contract (bounded_region_editor pattern):
  - Every find/replace must match EXACTLY ONCE or the script HALTS (exits non-zero).
  - No file is written unless the match count is exactly 1.
  - Logs every match count so the record is auditable.
"""

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
BASE_URL = "https://ivy-wolf.com"
DEFAULT_OG_IMAGE = "assets/photo-library/img-7235-1200w.jpg"

ORG_SCHEMA = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Organization",
            "@id": f"{BASE_URL}/#organization",
            "name": "Ivy Wolf Art",
            "url": BASE_URL,
            "logo": f"{BASE_URL}/brand/kit/logos/ivy-wolf-art_primary_on-light.svg",
            "description": "Original expressionist paintings by Ivy Wolf. Commissioned works and five collections.",
            "legalName": "Wolf Co.",
        },
        {
            "@type": "WebSite",
            "@id": f"{BASE_URL}/#website",
            "url": BASE_URL,
            "name": "Ivy Wolf Art",
            "publisher": {"@id": f"{BASE_URL}/#organization"},
        },
    ],
}


def schema_webpage(url, name, description=""):
    s = {"@context": "https://schema.org", "@type": "WebPage",
         "url": url, "name": name, "isPartOf": {"@id": f"{BASE_URL}/#website"}}
    if description:
        s["description"] = description
    return s


def schema_collection(url, name, description):
    return {"@context": "https://schema.org", "@type": "CollectionPage",
            "url": url, "name": name, "description": description,
            "isPartOf": {"@id": f"{BASE_URL}/#website"}}


# ── Per-page config ────────────────────────────────────────────────────────────
PAGES = [
    {
        "file": "index.html",
        "route": "/",
        "og_type": "website",
        "og_image": DEFAULT_OG_IMAGE,
        "schema": ORG_SCHEMA,
        # title and description already good — no fix needed
    },
    {
        "file": "about/index.html",
        "route": "/about",
        "og_type": "website",
        "og_image": DEFAULT_OG_IMAGE,
        "title_old": "About — Ivy Wolf Art",
        "title_new": "About the Artist — Ivy Wolf Art | Expressionist Painter",
        "schema": schema_webpage(
            f"{BASE_URL}/about",
            "About Ivy Wolf — Expressionist Painter",
            "About Ivy Wolf — 21 years of practice, expressionist painting, and the commission process.",
        ),
    },
    {
        "file": "contact/index.html",
        "route": "/contact",
        "og_type": "website",
        "og_image": DEFAULT_OG_IMAGE,
        "title_old": "Contact — Ivy Wolf Art",
        "title_new": "Contact Ivy Wolf Art — Begin a Vision Session",
        "schema": {"@context": "https://schema.org", "@type": "ContactPage",
                   "url": f"{BASE_URL}/contact",
                   "name": "Contact Ivy Wolf Art — Begin a Vision Session",
                   "description": "Begin a Vision Session or enquire about a collection work. Contact Ivy Wolf Art."},
    },
    {
        "file": "legal/index.html",
        "route": "/legal",
        "og_type": "website",
        "og_image": DEFAULT_OG_IMAGE,
        "title_old": "Legal — Ivy Wolf Art",
        "title_new": "Legal Information — Ivy Wolf Art | Wolf Co.",
        "schema": schema_webpage(
            f"{BASE_URL}/legal",
            "Legal Information — Ivy Wolf Art",
            "Legal information for Ivy Wolf Art, a brand of Wolf Co.",
        ),
    },
    {
        "file": "services/index.html",
        "route": "/services",
        "og_type": "website",
        "og_image": DEFAULT_OG_IMAGE,
        "schema": {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": "Custom Painting Commission — Ivy Wolf Art",
            "provider": {"@id": f"{BASE_URL}/#organization"},
            "serviceType": "Custom Painting Commission",
            "description": "Commission an original expressionist painting. Free Vision Session → written proposal → 50% deposit → 2–6 weeks → one revision → delivery with a signed Certificate of Authenticity.",
            "url": f"{BASE_URL}/services",
        },
    },
    {
        "file": "shop/index.html",
        "route": "/shop",
        "og_type": "website",
        "og_image": DEFAULT_OG_IMAGE,
        "title_old": "Shop — Ivy Wolf Art",
        "title_new": "Shop Original Paintings — Ivy Wolf Art | Opening Soon",
        "desc_old": "Ivy Wolf Art shop — opening soon.",
        "desc_new": "Ivy Wolf Art original expressionist paintings — shop opening soon. Browse the collections while you wait.",
        "schema": schema_collection(
            f"{BASE_URL}/shop",
            "Shop — Ivy Wolf Art",
            "Ivy Wolf Art original expressionist paintings, opening soon.",
        ),
    },
    {
        "file": "shop/a-work/index.html",
        "route": "/shop/a-work",
        "og_type": "website",
        "og_image": DEFAULT_OG_IMAGE,
        "title_old": "Shop — Ivy Wolf Art",
        "title_new": "A-Work — Original Paintings by Ivy Wolf Art | Opening Soon",
        "desc_old": "Ivy Wolf Art shop — opening soon.",
        "desc_new": "Browse A-Work original expressionist paintings by Ivy Wolf Art. Shop opening soon. See the collections in the meantime.",
        "schema": schema_collection(
            f"{BASE_URL}/shop/a-work",
            "A-Work — Ivy Wolf Art",
            "A-Work original expressionist paintings by Ivy Wolf Art, shop opening soon.",
        ),
    },
    {
        "file": "journal/index.html",
        "route": "/journal",
        "og_type": "website",
        "og_image": DEFAULT_OG_IMAGE,
        "title_old": "The Ivy Wolf Life — Journal",
        "title_new": "The Ivy Wolf Life — Art Journal by Ivy Wolf",
        # desc already 89 chars in the file (apostrophe foiled the audit regex) — no change needed
        "schema": {"@context": "https://schema.org", "@type": "Blog",
                   "url": f"{BASE_URL}/journal",
                   "name": "The Ivy Wolf Life",
                   "description": "A journal about art, process, and place by Ivy Wolf Art.",
                   "publisher": {"@id": f"{BASE_URL}/#organization"}},
    },
    {
        "file": "journal/behind-the-first-canvas/index.html",
        "route": "/journal/behind-the-first-canvas",
        "og_type": "article",
        "og_image": "assets/photo-library/img-2122-1200w.jpg",
        "schema": {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "url": f"{BASE_URL}/journal/behind-the-first-canvas",
            "headline": "Behind the First Canvas",
            "description": "Every painting begins before the brush touches canvas. On process, place, and what a commissioned work really asks of the painter.",
            "author": {"@id": f"{BASE_URL}/#organization"},
            "publisher": {"@id": f"{BASE_URL}/#organization"},
            "isPartOf": {"@id": f"{BASE_URL}/#website"},
        },
    },
    {
        "file": "thank-you/index.html",
        "route": "/thank-you",
        "og_type": "website",
        "og_image": DEFAULT_OG_IMAGE,
        "title_old": "Thank you — Ivy Wolf Art",
        "title_new": "Thank You — Your Message Was Received | Ivy Wolf Art",
        "noindex": True,
        "schema": schema_webpage(
            f"{BASE_URL}/thank-you",
            "Thank You — Ivy Wolf Art",
            "Your message has been received. Ivy Wolf Art will be in touch.",
        ),
    },
    {
        "file": "collections/index.html",
        "route": "/collections",
        "og_type": "website",
        "og_image": DEFAULT_OG_IMAGE,
        "title_old": "Collections — Ivy Wolf Art",
        "title_new": "Collections — Ivy Wolf Art Original Expressionist Paintings",
        "schema": schema_collection(
            f"{BASE_URL}/collections",
            "Collections — Ivy Wolf Art",
            "Five collections of original expressionist paintings: Austin Texas, The Bahamas, Telluride Colorado, Sedona Arizona, and Panama.",
        ),
    },
    {
        "file": "collections/austin-texas/index.html",
        "route": "/collections/austin-texas",
        "og_type": "website",
        "og_image": "assets/photo-library/8d37fd7b-a390-447c-8246-9540122912e4-1200w.jpg",
        "title_old": "Austin, Texas — Ivy Wolf Art",
        "title_new": "Austin, Texas — Ivy Wolf Art | Expressionist Paintings",
        "schema": schema_collection(
            f"{BASE_URL}/collections/austin-texas",
            "Austin, Texas Collection — Ivy Wolf Art",
            "The Austin, Texas collection — original expressionist paintings by Ivy Wolf.",
        ),
    },
    {
        "file": "collections/the-bahamas/index.html",
        "route": "/collections/the-bahamas",
        "og_type": "website",
        "og_image": "assets/photo-library/img-2122-1200w.jpg",
        "title_old": "The Bahamas — Ivy Wolf Art",
        "title_new": "The Bahamas — Ivy Wolf Art | Expressionist Paintings",
        "schema": schema_collection(
            f"{BASE_URL}/collections/the-bahamas",
            "The Bahamas Collection — Ivy Wolf Art",
            "The Bahamas collection — original expressionist paintings by Ivy Wolf.",
        ),
    },
    {
        "file": "collections/telluride-colorado/index.html",
        "route": "/collections/telluride-colorado",
        "og_type": "website",
        "og_image": "assets/photo-library/img-5921-1200w.jpg",
        "schema": schema_collection(
            f"{BASE_URL}/collections/telluride-colorado",
            "Telluride, Colorado Collection — Ivy Wolf Art",
            "The Telluride, Colorado collection — original expressionist paintings by Ivy Wolf.",
        ),
    },
    {
        "file": "collections/sedona-arizona/index.html",
        "route": "/collections/sedona-arizona",
        "og_type": "website",
        "og_image": "assets/photo-library/img-3216-1200w.jpg",
        "schema": schema_collection(
            f"{BASE_URL}/collections/sedona-arizona",
            "Sedona, Arizona Collection — Ivy Wolf Art",
            "The Sedona, Arizona collection — original expressionist paintings by Ivy Wolf.",
        ),
    },
    {
        "file": "collections/panama/index.html",
        "route": "/collections/panama",
        "og_type": "website",
        "og_image": "assets/photo-library/img-4740-1200w.jpg",
        "title_old": "Panama — Ivy Wolf Art",
        "title_new": "Panama — Ivy Wolf Art | Expressionist Paintings",
        "schema": schema_collection(
            f"{BASE_URL}/collections/panama",
            "Panama Collection — Ivy Wolf Art",
            "The Panama collection — original expressionist paintings by Ivy Wolf.",
        ),
    },
]


def bounded_replace(content: str, old: str, new: str, label: str) -> str:
    """Replace old with new. Asserts exactly one match or raises."""
    count = content.count(old)
    if count != 1:
        raise RuntimeError(
            f"BOUNDED HALT: '{label}' expected 1 match, found {count}. "
            f"No file was written."
        )
    print(f"    bounded_replace '{label}': matched exactly 1 ✓")
    return content.replace(old, new, 1)


def build_seo_block(page: dict, title: str, desc: str) -> str:
    route = page["route"]
    canonical_url = BASE_URL + route
    og_image_url = f"{BASE_URL}/{page['og_image']}"
    og_type = page.get("og_type", "website")
    schema_json = json.dumps(page["schema"], indent=2, ensure_ascii=False)

    noindex_line = ""
    if page.get("noindex"):
        noindex_line = '  <meta name="robots" content="noindex, nofollow">\n'

    return (
        f'\n  <!-- SEO: canonical · open-graph · schema ──────────────────────────────── -->\n'
        f'{noindex_line}'
        f'  <link rel="canonical" href="{canonical_url}">\n'
        f'  <meta property="og:type" content="{og_type}">\n'
        f'  <meta property="og:url" content="{canonical_url}">\n'
        f'  <meta property="og:title" content="{title}">\n'
        f'  <meta property="og:description" content="{desc}">\n'
        f'  <meta property="og:image" content="{og_image_url}">\n'
        f'  <meta property="og:image:width" content="1200">\n'
        f'  <meta property="og:image:height" content="800">\n'
        f'  <meta property="og:site_name" content="Ivy Wolf Art">\n'
        f'  <meta name="twitter:card" content="summary_large_image">\n'
        f'  <meta name="twitter:title" content="{title}">\n'
        f'  <meta name="twitter:description" content="{desc}">\n'
        f'  <meta name="twitter:image" content="{og_image_url}">\n'
        f'  <script type="application/ld+json">\n'
        f'  {schema_json}\n'
        f'  </script>\n'
        f'  <!-- /SEO ─────────────────────────────────────────────────────────────── -->\n'
    )


def process_page(page: dict) -> dict:
    path = BASE / page["file"]
    if not path.exists():
        return {"file": page["file"], "status": "ERROR: file not found", "ops": []}

    content = path.read_text(encoding="utf-8")
    ops = []
    errors = []

    print(f"\n  [{page['route']}] → {page['file']}")

    # 1. Fix title if needed (idempotent: skip if new title already in place)
    if "title_old" in page:
        new_title_tag = f"<title>{page['title_new']}</title>"
        old_title_tag = f"<title>{page['title_old']}</title>"
        if new_title_tag in content:
            print(f"    title already updated — skipping (idempotent) ✓")
            ops.append("title already correct — no-op")
        else:
            try:
                content = bounded_replace(content, old_title_tag, new_title_tag, "title fix")
                ops.append(f"title: {page['title_old']!r} → {page['title_new']!r}")
            except RuntimeError as e:
                errors.append(str(e))

    # 2. Fix description if needed (idempotent: skip if new desc already in place)
    if "desc_old" in page:
        new_attr = f'content="{page["desc_new"]}"'
        old_attr = f'content="{page["desc_old"]}"'
        if new_attr in content:
            print(f"    description already updated — skipping (idempotent) ✓")
            ops.append("description already correct — no-op")
        else:
            try:
                content = bounded_replace(content, old_attr, new_attr, "description fix")
                ops.append("desc updated")
            except RuntimeError as e:
                errors.append(str(e))

    # 3. Resolve current title and desc for OG tags
    title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.DOTALL | re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else ""

    desc_match = re.search(
        r'<meta\s+name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
        content, re.IGNORECASE
    )
    desc = desc_match.group(1).strip() if desc_match else ""

    # 4. Inject SEO block before </head> (idempotent: skip if already injected)
    if "<!-- SEO: canonical · open-graph · schema" in content:
        print("    seo block already injected — skipping (idempotent) ✓")
        ops.append("seo block already present — no-op")
    else:
        seo_block = build_seo_block(page, title, desc)
        try:
            content = bounded_replace(content, "</head>", seo_block + "</head>", "seo block inject")
            ops.append("injected canonical + OG + JSON-LD")
        except RuntimeError as e:
            errors.append(str(e))

    if errors:
        print(f"    ERRORS: {errors}")
        return {"file": page["file"], "status": "ERROR", "ops": ops, "errors": errors}

    # 5. Write back
    path.write_text(content, encoding="utf-8")
    print(f"    Written ✓  ({len(ops)} ops)")
    return {"file": page["file"], "status": "OK", "ops": ops}


def main():
    print("=" * 70)
    print("seo_inject.py — Ivy Wolf Art SEO injector (bounded_region_editor)")
    print("=" * 70)

    results = []
    halt = False
    for page in PAGES:
        result = process_page(page)
        results.append(result)
        if result["status"] != "OK":
            halt = True

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    ok = sum(1 for r in results if r["status"] == "OK")
    print(f"  Pages processed: {len(results)} / 16")
    print(f"  OK: {ok}   ERRORS: {len(results) - ok}")

    for r in results:
        status = "✅" if r["status"] == "OK" else "❌"
        print(f"  {status} {r['file']}")
        if r.get("errors"):
            for e in r["errors"]:
                print(f"       ERROR: {e}")

    if halt:
        print("\n⛔ HALT: one or more pages had errors. Fix above and re-run.")
        sys.exit(1)
    else:
        print("\n✅ All 16 pages injected cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()
