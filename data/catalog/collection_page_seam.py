"""collection_page_seam.py — doorbell for collection-page-template.

Wires the fleet capability (collection-page-template) called-not-inline.
The inline fallback (collection_page_atom.py) is byte-identical to the vault;
this seam is the app's declared call-site so enforcement-family can verify
the plugin is CALLED, not duplicated.

Fleet plugin: collection-page-template  (family: website-whisper -> site-gallery-whisper)
Inline fallback: collection_page_atom.py
"""
# called-not-inline: collection-page-template
from collection_page_atom import (  # noqa: F401  (re-exported for callers)
    emit_page,
    load_media_status,
    _compose_page,
    _build_figures,
    _stem_location,
)

__all__ = [
    "emit_page",
    "load_media_status",
    "_compose_page",
    "_build_figures",
    "_stem_location",
]
