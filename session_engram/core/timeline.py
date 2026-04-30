"""Timeline data builder for session engram.

Builds chronological timeline data from engram nodes.
"""

from __future__ import annotations

from typing import Any

from .graph import build_graph_data


def build_timeline_data() -> list[dict[str, Any]]:
    """Build timeline entries from engram data.

    Returns:
        List of timeline entries sorted by created date (newest first),
        each containing: id, label, file_type, source_file, status,
        tags, created, updated, summary.
    """
    nodes, _edges, _communities, _tag_groups = build_graph_data()

    entries: list[dict[str, Any]] = []
    for n in nodes:
        entries.append({
            "id": n["id"],
            "label": n.get("label", n["id"]),
            "file_type": n.get("file_type", "unknown"),
            "source_file": n.get("source_file", ""),
            "status": n.get("status", "unknown"),
            "tags": n.get("tags", []),
            "created": n.get("created", ""),
            "updated": n.get("updated", ""),
            "summary": n.get("summary", ""),
        })

    entries.sort(key=lambda e: e["created"] or "", reverse=True)
    return entries
