"""
Static structured content for public pages (no Flask imports).

Guide tab payloads live in `_guide_pages_data.py`. Protocol blurbs for category
tiles live in ``protocol_details.py``. Keys must align with
``thaghrah.core.constants.PROTOCOL_NAMES``. Guide sidebar tabs additionally
allow ``"Cheat Sheet"``.

Per-tab page shape::

    {
        "title": str,
        "sections": [
            {
                "heading": str,
                "paragraphs": [str],
                "bullets": [str],
                "images": [{"src": "images/...", "alt": str, optional keys}],
                "image_after_paragraph": int | omitted,
                "video": {"title", "embed_url", "watch_url", ...},
                "links": [{"label", "url"}],
            },
            ...
        ],
    }

Presentation is shared via ``templates/guide.html``. PDFs are optional files
under ``static/pdfs/``; paths are listed in ``GUIDE_TAB_PDF_REL``.
"""

from thaghrah.content._guide_pages_data import GUIDE_PAGES, GUIDE_TAB_PDF_REL
from thaghrah.content.protocol_details import PROTOCOL_DETAILS

__all__ = ["GUIDE_PAGES", "GUIDE_TAB_PDF_REL", "PROTOCOL_DETAILS"]
