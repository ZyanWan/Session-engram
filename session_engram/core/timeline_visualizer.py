"""Timeline HTML generator for session engram.

Generates a standalone HTML timeline page from timeline data.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


def generate_timeline_html(entries: list[dict[str, Any]], output_path: str) -> None:
    """Generate standalone timeline HTML page.

    Args:
        entries: Timeline entries from build_timeline_data()
        output_path: Path to write the HTML file
    """
    template_path = os.path.join(TEMPLATE_DIR, "engram-timeline.html")
    template = Path(template_path).read_text(encoding="utf-8")

    entries_json = json.dumps(entries, ensure_ascii=False).replace("</", "<\\/")

    html = template.replace("/*__ENTRIES__*/ []", entries_json)

    Path(output_path).write_text(html, encoding="utf-8")
