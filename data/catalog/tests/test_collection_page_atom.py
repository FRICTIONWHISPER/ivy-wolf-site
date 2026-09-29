"""Tests for data/catalog/collection_page_atom.py — collection page emitter.

All tests use injected loaders (no filesystem I/O) except the integration tests
that read the real catalog.json / media-map.json.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from collection_page_atom import (
    _build_figures,
    _compose_page,
    _stem_location,
    emit_page,
    load_media_status,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

MINIMAL_CATALOG = {
    "schema_version": "1.0.0",
    "site": "IWA",
    "collections": [
        {
            "slug": "test-place",
            "title": "Test Place",
            "status": "live",
            "product_type": "collection-limited-edition",
            "credit": "The Wolf Life",
            "hero_stem": "img-0001",
            "place_image_stems": ["img-0001", "img-0002"],
            "_place_notes": {
                "img-0001": "Test Location A — PIC note",
                "img-0002": "Test Location B — PIC note",
            },
            "commission_cta": True,
            "works": [],
        }
    ],
}

MINIMAL_MEDIA = {"media": [{"id": "img-0001", "status": "SELECT-KEEP"}]}

NO_CTA_CATALOG = {
    "schema_version": "1.0.0",
    "site": "IWA",
    "collections": [
        {
            "slug": "paintings-coll",
            "title": "Mind, Body and Spirit",
            "status": "live",
            "product_type": "collection-limited-edition",
            "credit": "The Wolf Life",
            "hero_stem": "img-8204",
            "place_image_stems": ["img-8204"],
            "_place_notes": {"img-8204": "Abstract, blue"},
            "commission_cta": False,
            "works": [],
        }
    ],
}


# ── Unit: pure helpers ────────────────────────────────────────────────────────

def test_stem_location_with_note():
    notes = {"img-0001": "Laguna Beach, California — sunset over rocks"}
    assert _stem_location("img-0001", notes) == "Laguna Beach, California"


def test_stem_location_missing():
    assert _stem_location("img-9999", {}) == ""


def test_stem_location_no_dash():
    notes = {"img-0001": "San Salvador, Bahamas"}
    assert _stem_location("img-0001", notes) == "San Salvador, Bahamas"


def test_build_figures_credit_always_wolf_life():
    notes = {"img-0001": "Some Place — note"}
    html = _build_figures(["img-0001"], notes)
    assert "The Wolf Life" in html, "figcaption must always include 'The Wolf Life'"


def test_build_figures_no_price():
    notes = {"img-0001": "Some Place — note"}
    html = _build_figures(["img-0001"], notes)
    assert "$" not in html, "figures must not contain any price"
    assert "HELD" not in html, "figures must not contain 'HELD'"


def test_build_figures_gallery_markers_absent():
    notes = {"img-0001": "Test — note"}
    html = _build_figures(["img-0001"], notes)
    # markers are in the section, not the figure itself
    assert "GALLERY_REGION" not in html


def test_build_figures_uses_stem_in_src():
    notes = {"img-abc": "Place — note"}
    html = _build_figures(["img-abc"], notes)
    assert "img-abc-800w.jpg" in html
    assert "img-abc-400w.jpg" in html
    assert "img-abc-1200w.jpg" in html
    assert "img-abc-1600w.jpg" in html


def test_build_figures_lazy_load():
    html = _build_figures(["img-x"], {"img-x": "Loc — note"})
    assert 'loading="lazy"' in html


def test_compose_page_collection_number():
    html = _compose_page(
        slug="test-place",
        title="Test Place",
        position=3,
        hero_stem="img-0001",
        place_stems=["img-0001"],
        place_notes={"img-0001": "A — B"},
        description="Original expressionist paintings.",
        schema_desc="The Test Place collection.",
        commission_cta=True,
    )
    assert "Collection 03" in html


def test_compose_page_no_price():
    html = _compose_page(
        slug="test-place",
        title="Test Place",
        position=1,
        hero_stem="img-0001",
        place_stems=["img-0001"],
        place_notes={"img-0001": "A — B"},
        description="Desc.",
        schema_desc="Schema.",
        commission_cta=True,
    )
    assert "$" not in html
    assert "HELD" not in html
    assert "prices-table" not in html


def test_compose_page_credit_wolf_life():
    html = _compose_page(
        slug="test-place",
        title="Test Place",
        position=1,
        hero_stem="img-0001",
        place_stems=["img-0001"],
        place_notes={"img-0001": "Test Location — note"},
        description="Desc.",
        schema_desc="Schema.",
        commission_cta=True,
    )
    assert "The Wolf Life" in html


def test_compose_page_limited_edition_block():
    html = _compose_page(
        slug="test-place",
        title="Test Place",
        position=1,
        hero_stem="img-0001",
        place_stems=["img-0001"],
        place_notes={"img-0001": "A — B"},
        description="Desc.",
        schema_desc="Schema.",
        commission_cta=True,
    )
    assert "A limited collection" in html
    assert "never reproduced" in html


def test_compose_page_gallery_markers():
    html = _compose_page(
        slug="test-place",
        title="Test Place",
        position=1,
        hero_stem="img-0001",
        place_stems=["img-0001"],
        place_notes={"img-0001": "A — B"},
        description="Desc.",
        schema_desc="Schema.",
        commission_cta=True,
    )
    assert "<!-- GALLERY_REGION_START -->" in html
    assert "<!-- GALLERY_REGION_END -->" in html


def test_compose_page_footer_credit():
    html = _compose_page(
        slug="test-place",
        title="Test Place",
        position=1,
        hero_stem="img-0001",
        place_stems=["img-0001"],
        place_notes={},
        description="Desc.",
        schema_desc="Schema.",
        commission_cta=False,
    )
    assert "Built by Uplift Technology Services, LLC" in html


def test_compose_page_seo_canonical():
    html = _compose_page(
        slug="the-bahamas",
        title="The Bahamas",
        position=2,
        hero_stem="img-2122",
        place_stems=["img-2122"],
        place_notes={"img-2122": "San Salvador, Bahamas — hero"},
        description="Desc.",
        schema_desc="Schema.",
        commission_cta=True,
    )
    assert 'href="https://ivy-wolf.com/collections/the-bahamas"' in html
    assert "og:url" in html
    assert "CollectionPage" in html
    assert "twitter:card" in html


def test_compose_page_commission_cta_true():
    html = _compose_page(
        slug="test-place",
        title="Test Place",
        position=1,
        hero_stem="img-0001",
        place_stems=["img-0001"],
        place_notes={},
        description="Desc.",
        schema_desc="Schema.",
        commission_cta=True,
    )
    assert 'class="commission-cta"' in html
    assert "Commission a work from this collection" in html


def test_compose_page_commission_cta_false():
    html = _compose_page(
        slug="mind-body-spirit",
        title="Mind, Body and Spirit",
        position=7,
        hero_stem="img-8204",
        place_stems=["img-8204"],
        place_notes={},
        description="Desc.",
        schema_desc="Schema.",
        commission_cta=False,
    )
    assert 'class="commission-cta"' not in html


def test_compose_page_no_photographer_name():
    html = _compose_page(
        slug="test-place",
        title="Test Place",
        position=1,
        hero_stem="img-0001",
        place_stems=["img-0001"],
        place_notes={},
        description="Desc.",
        schema_desc="Schema.",
        commission_cta=False,
    )
    assert "Justin" not in html
    assert "Smith" not in html


def test_compose_page_no_red_gold():
    html = _compose_page(
        slug="test-place",
        title="Test Place",
        position=1,
        hero_stem="img-0001",
        place_stems=["img-0001"],
        place_notes={},
        description="Desc.",
        schema_desc="Schema.",
        commission_cta=False,
    )
    for forbidden in ["#ff0000", "#cc0000", "gold", "#D4AF37", "oxblood", "brass"]:
        assert forbidden.lower() not in html.lower(), f"forbidden color/word: {forbidden}"


def test_compose_page_accent_purple_ok():
    html = _compose_page(
        slug="test-place",
        title="Test Place",
        position=1,
        hero_stem="img-0001",
        place_stems=["img-0001"],
        place_notes={},
        description="Desc.",
        schema_desc="Schema.",
        commission_cta=False,
    )
    assert "#7C5CFF" in html


# ── Unit: load_media_status ───────────────────────────────────────────────────

def test_load_media_status_injected():
    status = load_media_status(loader=lambda: MINIMAL_MEDIA)
    assert "img-0001" in status
    assert status["img-0001"]["status"] == "SELECT-KEEP"


def test_load_media_status_missing_stem():
    status = load_media_status(loader=lambda: MINIMAL_MEDIA)
    assert "img-9999" not in status


# ── Unit: emit_page (injected loaders, no filesystem) ────────────────────────

def test_emit_page_dry_run_returns_html():
    html = emit_page(
        slug="test-place",
        dry_run=True,
        catalog_loader=lambda: MINIMAL_CATALOG,
        media_loader=lambda: MINIMAL_MEDIA,
    )
    assert "Test Place" in html
    assert "<!DOCTYPE html>" in html


def test_emit_page_slug_not_found():
    with pytest.raises(ValueError, match="slug not found"):
        emit_page(
            slug="nonexistent",
            dry_run=True,
            catalog_loader=lambda: MINIMAL_CATALOG,
            media_loader=lambda: MINIMAL_MEDIA,
        )


def test_emit_page_position_encoding():
    html = emit_page(
        slug="test-place",
        dry_run=True,
        catalog_loader=lambda: MINIMAL_CATALOG,
        media_loader=lambda: MINIMAL_MEDIA,
    )
    assert "Collection 01" in html


def test_emit_page_commission_cta_false_from_catalog():
    html = emit_page(
        slug="paintings-coll",
        dry_run=True,
        catalog_loader=lambda: NO_CTA_CATALOG,
        media_loader=lambda: MINIMAL_MEDIA,
    )
    assert 'class="commission-cta"' not in html


# ── Integration: real catalog.json ────────────────────────────────────────────

SEVEN_SLUGS = {
    "austin-texas",
    "the-bahamas",
    "telluride-colorado",
    "sedona-arizona",
    "panama",
    "laguna",
    "mind-body-spirit",
}


def test_all_seven_slugs_present():
    """Integration: real catalog.json must have all 7 live collection slugs."""
    import json as _json
    from pathlib import Path as _Path
    here = _Path(__file__).resolve().parents[1]
    with open(here / "catalog.json", encoding="utf-8") as fh:
        cat = _json.load(fh)
    slugs = {c["slug"] for c in cat["collections"]}
    assert SEVEN_SLUGS == slugs, (
        f"Missing or extra slugs: {SEVEN_SLUGS.symmetric_difference(slugs)}"
    )


def test_emit_page_the_bahamas_integration():
    html = emit_page(slug="the-bahamas", dry_run=True)
    assert "The Bahamas" in html
    assert "The Wolf Life" in html
    assert "A limited collection" in html
    assert "$" not in html
    assert "HELD" not in html
    assert "Collection 02" in html


def test_emit_page_laguna_integration():
    html = emit_page(slug="laguna", dry_run=True)
    assert "Laguna, California" in html
    assert "Collection 06" in html
    assert "The Wolf Life" in html
    assert 'class="commission-cta"' not in html


def test_emit_page_mind_body_spirit_integration():
    html = emit_page(slug="mind-body-spirit", dry_run=True)
    # catalog title is "Mind, Body & Spirit" — HTML-encoded in the page
    assert "Mind, Body" in html
    assert "Spirit" in html
    assert "Collection 07" in html
    assert "The Wolf Life" in html
    # commission_cta not set in catalog — defaults True (MBS is also commissioned art BLG-02)
    assert 'class="commission-cta"' in html
    assert "$" not in html
