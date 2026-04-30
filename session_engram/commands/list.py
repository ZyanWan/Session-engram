import os

from ..core.config import CATEGORIES, DATE_FORMAT
from ..core.storage import ensure_dirs
from ..core.scanner import scan_all


def cmd_list():
    """List all engrams.

    Displays a formatted list of all sessions and experiences in the .engram directory.
    Sessions are sorted by modification date (newest first).
    Experiences are grouped by category.

    Example:
        $ sengram list
        📁 Session-Engram List

        Session (3):
          [in-progress] 2026-04-29 10:30  session-auth-system.md  — authentication
          [resolved] 2026-04-28 15:45  session-api-design.md  — api-design
          [in-progress] 2026-04-27 09:15  session-database.md  — database

        Experience:
          technical (2):
            2026-04-28 14:20  jwt-refresh-token.md  — jwt
            2026-04-26 11:30  database-optimization.md  — performance
          design (1):
            2026-04-25 16:45  responsive-layout.md  — css

        Archive (1):
          📦 session-old-project.md
    """
    base, is_new = ensure_dirs()
    if is_new:
        print(f"✅ Created .engram/ directory: {base}")
    data = scan_all()
    print(f"📁 Session-Engram List\n")
    print(f"Session ({len(data['sessions'])}):")
    for s in sorted(data["sessions"], key=lambda x: x["modified"], reverse=True):
        tags = s["front_matter"].get("tags", [])
        desc = tags[0] if tags else "?"
        print(f"  [{s['front_matter'].get('status', '?'):>12}] {s['modified'].strftime(DATE_FORMAT)}  {s['file']}  — {desc}")
    print(f"\nExperience:")
    for cat in CATEGORIES:
        entries = data["experiences"].get(cat, [])
        if entries:
            print(f"  {cat} ({len(entries)}):")
            for e in entries:
                tags = e["front_matter"].get("tags", [])
                desc = tags[0] if tags else "?"
                print(f"    {e['front_matter'].get('created', '?')}  {e['file']}  — {desc}")
    if data["archives"]:
        print(f"\nArchive ({len(data['archives'])}):")
        for a in data["archives"]:
            print(f"  📦 {a['file']}")
