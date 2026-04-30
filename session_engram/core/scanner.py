import os
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import SESSION_DIR, EXPERIENCE_DIR, ARCHIVE_DIR, CATEGORIES
from .storage import get_memory_root
from .parser import parse_front_matter


def scan_all() -> dict[str, Any]:
    """Scan all engram files.

    Scans the .engram directory structure and returns a dictionary containing
    all sessions, experiences, and archives with their metadata.

    Returns:
        Dictionary with the following structure:
        {
            "sessions": [
                {
                    "file": str,
                    "path": str,
                    "front_matter": dict,
                    "modified": datetime
                },
                ...
            ],
            "experiences": {
                "design": [...],
                "technical": [...],
                "business": [...]
            },
            "archives": [
                {
                    "file": str,
                    "path": str
                },
                ...
            ]
        }

    Example:
        >>> data = scan_all()
        >>> print(f"Sessions: {len(data['sessions'])}")
        Sessions: 3
    """
    base = get_memory_root()
    result: dict[str, Any] = {"sessions": [], "experiences": {}, "archives": []}
    for cat in CATEGORIES:
        result["experiences"][cat] = []

    if os.path.exists(SESSION_DIR):
        for f in os.listdir(SESSION_DIR):
            if f.endswith(".md") and f != "archive":
                fp = os.path.join(SESSION_DIR, f)
                fm = parse_front_matter(Path(fp).read_text(encoding="utf-8"))
                result["sessions"].append({
                    "file": f, "path": fp, "front_matter": fm or {},
                    "modified": datetime.fromtimestamp(os.path.getmtime(fp))
                })

    archive_session_dir = os.path.join(SESSION_DIR, "archive")
    if os.path.exists(archive_session_dir):
        for f in os.listdir(archive_session_dir):
            if f.endswith(".md"):
                result["archives"].append({"file": f, "path": os.path.join(archive_session_dir, f)})

    if os.path.exists(EXPERIENCE_DIR):
        for cat in CATEGORIES:
            cat_dir = os.path.join(EXPERIENCE_DIR, cat)
            if os.path.exists(cat_dir):
                for f in os.listdir(cat_dir):
                    if f.endswith(".md"):
                        fp = os.path.join(cat_dir, f)
                        fm = parse_front_matter(Path(fp).read_text(encoding="utf-8"))
                        result["experiences"][cat].append({
                            "file": f, "path": fp, "front_matter": fm or {}
                        })
    return result
