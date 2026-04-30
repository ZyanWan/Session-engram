import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from ..core.config import ARCHIVE_DAYS, ARCHIVE_DIR
from ..core.storage import ensure_dirs
from ..core.scanner import scan_all
from .update import cmd_update


def cmd_archive():
    """Archive sessions inactive for 7+ days.

    Moves sessions that have been inactive for 7 or more days to the archive directory.
    Updates the status of archived sessions to "archived" and rebuilds the index.

    Example:
        $ sengram archive
        📦 Archived: session-old-project.md
        📦 Archived: session-legacy-code.md
        ✅ index.md updated (8 entries)

        # Or if no sessions to archive:
        $ sengram archive
        ✅ No sessions to archive
    """
    base, is_new = ensure_dirs()
    if is_new:
        print(f"✅ Created .engram/ directory: {base}")
    data = scan_all()
    cutoff = datetime.now() - timedelta(days=ARCHIVE_DAYS)
    archived = []
    for s in data["sessions"]:
        if s["modified"] < cutoff and s["front_matter"].get("status") != "archived":
            src = s["path"]
            dst = os.path.join(ARCHIVE_DIR, s["file"])
            shutil.move(src, dst)
            content = Path(dst).read_text(encoding="utf-8")
            content = content.replace("status: in-progress", "status: archived").replace("status: resolved", "status: archived")
            Path(dst).write_text(content, encoding="utf-8")
            archived.append(s["file"])
            print(f"📦 Archived: {s['file']}")
    if not archived:
        print("✅ No sessions to archive")
    else:
        cmd_update()
