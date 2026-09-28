"""collection_page_atom.py — emits one collection page from catalog + media-map.

TrueCore shape:
  _stem_location()    — PURE: extract display location from _place_notes entry
  _build_figures()    — PURE: HTML <figure> blocks for all place_image_stems
  _compose_page()     — PURE: full page HTML string (no I/O)
  load_media_status() — I/O seam: read media-map.json → stem→status dict
  main()              — I/O: parse args, load catalog, load media-map, write page

Rules:
  - PRICES NEVER RENDERED (works[].price is HELD; works section is PHASE-5.0)
  - Credit always 'The Wolf Life' in every figcaption
  - Limited-edition block always present
  - GALLERY_REGION_START/END markers always present (for bounded_region_editor)
  - Footer stays 'Built by Uplift Technology Services, LLC'
  - No hardcoded prices anywhere in this file
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from safe_io import safe_write

HERE = Path(__file__).parent
CATALOG_PATH = HERE / "catalog.json"
MEDIA_MAP_PATH = HERE / "media-map.json"
SITE_ROOT = HERE.parent.parent  # ivy-wolf-site/

# ── CSS is the same on every collection page (house-grammar v1.1) ────────────
_CSS = """\
    /* ── BRAND TOKENS — house-grammar v1.1 ─────────────────────────────────── */
    :root {
      --ink:         #111111;
      --paper:       #FFFFFF;
      --accent:      #7C5CFF;  /* small accent only — never on buttons */
      --muted-dark:  #757575;
      --muted-light: #555555;
      --band:        #F1F1F1;
      --rule:        #DADADA;
      --wrap:        1120px;
      --gutter:      24px;
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body {
      font-family: 'Archivo', system-ui, sans-serif;
      background: var(--paper);
      color: var(--ink);
      -webkit-font-smoothing: antialiased;
    }
    img { display: block; width: 100%; height: auto; }
    a { color: inherit; text-decoration: none; }

    .display {
      font-family: 'Instrument Serif', Georgia, serif;
      font-weight: 400;
    }

    /* ── BUTTONS ─────────────────────────────────────────────────────────────── */
    .pill-black {
      display: inline-block;
      padding: .75rem 1.75rem;
      background: var(--ink);
      color: var(--paper);
      border-radius: 2rem;
      font-size: .8125rem;
      font-weight: 500;
      letter-spacing: .04em;
      transition: opacity .15s;
    }
    .pill-black:hover { opacity: .82; }
    .pill-ghost {
      display: inline-block;
      padding: .75rem 1.75rem;
      background: transparent;
      color: var(--ink);
      border: 1px solid var(--ink);
      border-radius: 2rem;
      font-size: .8125rem;
      font-weight: 500;
      letter-spacing: .04em;
      transition: background .15s;
    }
    .pill-ghost:hover { background: var(--band); }

    /* ── NAV ─────────────────────────────────────────────────────────────────── */
    .site-nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1.25rem 2.5rem;
      border-bottom: 1px solid var(--rule);
    }
    .nav-wordmark {
      font-family: 'Instrument Serif', Georgia, serif;
      font-size: 1.5625rem;
      letter-spacing: .01em;
      color: var(--ink);
    }
    .nav-wordmark .wm-second { color: var(--muted-dark); }
    .nav-links { display: flex; align-items: center; gap: 2rem; }
    .nav-menu { display: none; }
    .nav-links a {
      font-size: .8125rem;
      font-weight: 500;
      letter-spacing: .06em;
      text-transform: uppercase;
      color: var(--muted-light);
    }
    .nav-links a:hover { color: var(--ink); }

    /* ── PAGE HEAD ───────────────────────────────────────────────────────────── */
    .page-head {
      padding: clamp(64px, 9vw, 118px) 2.5rem clamp(48px, 6vw, 72px);
      max-width: var(--wrap);
      margin: 0 auto;
    }
    .page-head .eyebrow {
      font-size: .6875rem;
      letter-spacing: .14em;
      text-transform: uppercase;
      color: var(--muted-dark);
      margin-bottom: 1.25rem;
    }
    .page-head h1 {
      font-size: clamp(2rem, 5vw, 3.5rem);
      line-height: 1.1;
      margin-bottom: 1.25rem;
    }
    .page-head p {
      font-size: 1rem;
      line-height: 1.7;
      color: var(--muted-light);
      max-width: 540px;
    }
    .page-rule { display: block; width: 100%; height: 1px; background: var(--rule); }

    /* ── LAYOUT WRAP ─────────────────────────────────────────────────────────── */
    .wrap {
      max-width: var(--wrap);
      margin: 0 auto;
      padding: 0 var(--gutter);
    }
    .section {
      padding: clamp(64px, 9vw, 118px) var(--gutter);
    }

    /* ── COMMISSION CTA ───────────────────────────────────────────────────────── */
    .commission-cta {
      text-align: center;
      padding: clamp(64px, 9vw, 118px) var(--gutter);
      background: var(--band);
    }
    .commission-cta h2 { font-size: clamp(1.5rem, 4vw, 2.5rem); margin-bottom: 1rem; }
    .commission-cta p { font-size: .9375rem; color: var(--muted-light); max-width: 480px; margin: 0 auto 2rem; line-height: 1.7; }
    .commission-cta .pills { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }

    /* ── FOOTER ──────────────────────────────────────────────────────────────── */
    .site-footer {
      border-top: 1px solid var(--rule);
      padding: 1.125rem 2.5rem;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .footer-legal { font-size: .6875rem; color: var(--muted-dark); line-height: 1.5; margin: 0; }
    .footer-legal a { color: var(--muted-dark); }
    .footer-credit { font-size: .625rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted-dark); margin: 0; }

    /* ── RESPONSIVE ──────────────────────────────────────────────────────────── */
    @media (max-width: 800px) {
      .site-nav { padding: 1rem 1.25rem; }
      .nav-links { display: none; }
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
      .nav-menu-panel a:hover { color: var(--ink); }
      .site-footer { flex-direction: column; align-items: flex-start; }
    }"""


# ── Pure helpers ─────────────────────────────────────────────────────────────

def _stem_location(stem: str, place_notes: dict) -> str:
    """PURE: return display location string from _place_notes (before ' — '), or ''."""
    note = place_notes.get(stem, "")
    return note.split(" — ")[0].strip() if note else ""


def _esc(s: str) -> str:
    """PURE: escape < > & for HTML attribute/text."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _build_figures(stems: list, place_notes: dict) -> str:
    """PURE: build HTML <figure> blocks for all place_image_stems.

    Every figcaption ends with '· The Wolf Life'.
    No status filtering — stems in place_image_stems are PIC-approved.
    """
    parts = []
    for stem in stems:
        loc = _stem_location(stem, place_notes)
        alt = _esc(loc) if loc else "Ivy Wolf Art"
        caption = f"{_esc(loc)} &middot; The Wolf Life" if loc else "The Wolf Life"
        parts.append(
            f"      <figure style=\"margin:0 0 3rem;\">\n"
            f"        <img src=\"/assets/photo-library/{stem}-800w.jpg\"\n"
            f"             srcset=\"/assets/photo-library/{stem}-400w.jpg 400w,"
            f" /assets/photo-library/{stem}-800w.jpg 800w,"
            f" /assets/photo-library/{stem}-1200w.jpg 1200w,"
            f" /assets/photo-library/{stem}-1600w.jpg 1600w\"\n"
            f"             sizes=\"(max-width:768px) 100vw, 1120px\"\n"
            f"             alt=\"{alt}\"\n"
            f"             loading=\"lazy\"\n"
            f"             style=\"aspect-ratio:4/3;object-fit:cover;\">\n"
            f"        <figcaption"
            f" style=\"font-size:.6875rem;letter-spacing:.08em;"
            f"text-transform:uppercase;color:var(--muted-dark);margin-top:1rem;\">\n"
            f"          {caption}\n"
            f"        </figcaption>\n"
            f"      </figure>"
        )
    return "\n".join(parts)


def _compose_page(
    slug: str,
    title: str,
    position: int,
    hero_stem: str,
    place_stems: list,
    place_notes: dict,
    description: str,
    schema_desc: str,
    commission_cta: bool,
) -> str:
    """PURE: compose complete collection page HTML.

    No prices rendered. No I/O. Returns the full HTML string.
    """
    coll_number = f"Collection {position:02d}"
    safe_title = _esc(title)
    page_title = f"{safe_title} — Ivy Wolf Art | Expressionist Paintings"
    og_image = f"https://ivy-wolf.com/assets/photo-library/{hero_stem}-1200w.jpg"
    figures_html = _build_figures(place_stems, place_notes)

    schema = (
        "{\n"
        f'  "@context": "https://schema.org",\n'
        f'  "@type": "CollectionPage",\n'
        f'  "url": "https://ivy-wolf.com/collections/{slug}",\n'
        f'  "name": "{safe_title} Collection — Ivy Wolf Art",\n'
        f'  "description": "{_esc(schema_desc)}",\n'
        '  "isPartOf": {\n'
        '    "@id": "https://ivy-wolf.com/#website"\n'
        "  }\n"
        "}"
    )

    commission_html = ""
    if commission_cta:
        commission_html = (
            f'  <div class="commission-cta">\n'
            f'    <h2 class="display">Commission a work from this collection</h2>\n'
            f'    <p>For a work inspired by {safe_title}'
            f" — a place that means something to you."
            f" The Vision Session is free.</p>\n"
            f'    <div class="pills">\n'
            f'      <a href="/contact" class="pill-black">Begin a Vision Session</a>\n'
            f'      <a href="/collections" class="pill-ghost">All collections</a>\n'
            f"    </div>\n"
            f"  </div>\n"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
  <meta name="description" content="The {safe_title} collection — original expressionist paintings by Ivy Wolf.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Archivo:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&display=swap" rel="stylesheet">
  <style>
{_CSS}
  </style>

  <!-- SEO: canonical · open-graph · schema ──────────────────────────────── -->
  <link rel="canonical" href="https://ivy-wolf.com/collections/{slug}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://ivy-wolf.com/collections/{slug}">
  <meta property="og:title" content="{page_title}">
  <meta property="og:description" content="The {safe_title} collection — original expressionist paintings by Ivy Wolf.">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="800">
  <meta property="og:site_name" content="Ivy Wolf Art">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{page_title}">
  <meta name="twitter:description" content="The {safe_title} collection — original expressionist paintings by Ivy Wolf.">
  <meta name="twitter:image" content="{og_image}">
  <script type="application/ld+json">
  {schema}
  </script>
  <!-- /SEO ─────────────────────────────────────────────────────────────── -->
</head>
<body>
  <nav class="site-nav">
    <a href="/" class="nav-wordmark">IVY WOLF <span class="wm-second">ART</span></a>
    <details class="nav-menu">
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
    <div class="nav-links">
      <a href="/collections">Collections</a>
      <a href="/journal">Journal</a>
      <a href="/about">About</a>
      <a href="/services">Services</a>
      <a href="/contact" class="pill-black">Commission a work</a>
    </div>
  </nav>
  <div class="page-head">
    <p class="eyebrow">{coll_number}</p>
    <h1 class="display">{safe_title}</h1>
    <p>{_esc(description)}</p>
  </div>
  <span class="page-rule"></span>

  <!-- GALLERY — photographs fold in at PHASE-5.0 via bounded_region_editor -->
  <!-- GALLERY_REGION_START -->
  <section class="section">
    <div class="wrap">
{figures_html}
      <p style="font-size:.9375rem;line-height:1.7;color:var(--muted-light);max-width:540px;margin-top:2rem;">
        A limited collection. A set number of original works from this place are released &mdash; then never reproduced. Each is singular; when the edition is gone, it is gone.
      </p>
    </div>
  </section>
  <!-- GALLERY_REGION_END -->

  <span class="page-rule"></span>

{commission_html}  <footer class="site-footer">
    <p class="footer-legal">&copy; 2026 Ivy Wolf Art &middot; a brand of Wolf Co. &middot; <a href="/contact">Contact</a></p>
    <p class="footer-credit">Built by Uplift Technology Services, LLC</p>
  </footer>
</body>
</html>"""


# ── I/O seam ─────────────────────────────────────────────────────────────────

def load_media_status(
    path: Optional[Path] = None,
    loader=None,
) -> dict:
    """I/O seam: read media-map.json → {stem: {"status": str, "location": str}} dict."""
    if loader is not None:
        raw = loader()
    else:
        with open(path or MEDIA_MAP_PATH, encoding="utf-8") as fh:
            raw = json.load(fh)
    return {
        m["id"]: {
            "status": m.get("status", ""),
            "location": m.get("location", ""),
        }
        for m in raw.get("media", [])
    }


def emit_page(
    slug: str,
    catalog_path: Optional[Path] = None,
    media_map_path: Optional[Path] = None,
    out_dir: Optional[Path] = None,
    dry_run: bool = False,
    catalog_loader=None,
    media_loader=None,
) -> str:
    """Load catalog + media-map, compose the page for slug, write to disk.

    Returns the rendered HTML string (useful for tests).
    Raises ValueError if slug is not found in catalog.
    """
    # --- load catalog ---
    if catalog_loader is not None:
        raw_catalog = catalog_loader()
    else:
        with open(catalog_path or CATALOG_PATH, encoding="utf-8") as fh:
            raw_catalog = json.load(fh)

    collections = raw_catalog.get("collections", [])
    coll = None
    position = 0
    for i, c in enumerate(collections):
        if c["slug"] == slug:
            coll = c
            position = i + 1
            break
    if coll is None:
        raise ValueError(f"slug not found in catalog: {slug!r}")

    # --- load media status (for future use / extension) ---
    load_media_status(
        path=media_map_path,
        loader=media_loader,
    )

    # --- compose page ---
    title = coll["title"]
    hero_stem = coll.get("hero_stem", "")
    place_stems = coll.get("place_image_stems", [])
    place_notes = coll.get("_place_notes", {})
    commission_cta = coll.get("commission_cta", True)
    description = (
        f"Original expressionist paintings. "
        f"Every work is singular — painted once and never reproduced."
    )
    schema_desc = (
        f"The {title} collection — original expressionist paintings by Ivy Wolf."
    )

    html = _compose_page(
        slug=slug,
        title=title,
        position=position,
        hero_stem=hero_stem,
        place_stems=place_stems,
        place_notes=place_notes,
        description=description,
        schema_desc=schema_desc,
        commission_cta=commission_cta,
    )

    if not dry_run:
        dest = (out_dir or (SITE_ROOT / "collections" / slug)) / "index.html"
        safe_write(str(dest), html)
        print(f"EMITTED  {dest}", file=sys.stderr)

    return html


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Emit a collection page from catalog.json + media-map.json."
    )
    parser.add_argument("slug", help="collection slug, e.g. the-bahamas")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="override output directory (default: collections/<slug>/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print HTML to stdout; do not write files",
    )
    args = parser.parse_args()

    html = emit_page(
        slug=args.slug,
        out_dir=args.out_dir,
        dry_run=args.dry_run,
    )
    if args.dry_run:
        print(html)


if __name__ == "__main__":
    main()
