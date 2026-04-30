import os
from datetime import datetime
from pathlib import Path

from ..core.config import CATEGORIES, DATE_FORMAT
from ..core.storage import ensure_dirs, get_memory_root
from ..core.scanner import scan_all


def cmd_update():
    """Rebuild the index.md file.

    Regenerates the index.md file with the current state of all sessions and experiences.
    The index includes:
    - In-progress sessions
    - Completed sessions
    - Experiences grouped by category
    - Archived sessions

    Example:
        $ sengram update
        ✅ index.md updated (10 entries)
    """
    base, is_new = ensure_dirs()
    if is_new:
        print(f"✅ Created .engram/ directory: {base}")
    data = scan_all()
    today = datetime.now().strftime(DATE_FORMAT)
    lines = [f"# Session-Engram Index\n> Last Updated: {today}\n---\n"]

    lines.append("## Session\n### In Progress\n| File | Task | Last Updated |\n|------|------|--------------|\n")
    in_progress = sorted([s for s in data["sessions"] if s["front_matter"].get("status") == "in-progress"], key=lambda x: x["modified"], reverse=True)
    for s in in_progress:
        tags = s["front_matter"].get("tags", [])
        lines.append(f"| `session/{s['file']}` | {tags[0] if tags else s['file']} | {s['modified'].strftime(DATE_FORMAT)} |\n")
    if not in_progress:
        lines.append("| (None) | | |\n")

    lines.append("\n### Completed\n| File | Task | Completed At |\n|------|------|--------------|\n")
    resolved = sorted([s for s in data["sessions"] if s["front_matter"].get("status") == "resolved"], key=lambda x: x["modified"], reverse=True)
    for s in resolved:
        tags = s["front_matter"].get("tags", [])
        lines.append(f"| `session/{s['file']}` | {tags[0] if tags else s['file']} | {s['modified'].strftime(DATE_FORMAT)} |\n")
    if not resolved:
        lines.append("| (None) | | |\n")

    lines.append("\n---\n\n## Experience\n")
    for cat in CATEGORIES:
        lines.append(f"### {cat}\n| File | Problem | Date |\n|------|---------|------|\n")
        for e in data["experiences"].get(cat, []):
            tags = e["front_matter"].get("tags", [])
            lines.append(f"| `experience/{cat}/{e['file']}` | {tags[0] if tags else e['file']} | {e['front_matter'].get('created', '?')} |\n")
        if not data["experiences"].get(cat):
            lines.append("| (None) | | |\n")

    lines.append("\n---\n\n## Archive\n")
    if data["archives"]:
        lines.append(f"\n**Archived ({len(data['archives'])}):**\n")
        for a in data["archives"]:
            lines.append(f"- `{a['file']}`\n")
    else:
        lines.append("\nNo archived files.\n")

    Path(os.path.join(base, "index.md")).write_text("".join(lines), encoding="utf-8")
    total = len(data["sessions"]) + sum(len(v) for v in data["experiences"].values())
    print(f"✅ index.md updated ({total} entries)")
