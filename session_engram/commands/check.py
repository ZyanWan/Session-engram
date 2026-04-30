from datetime import datetime, timedelta

from ..core.config import ARCHIVE_DAYS
from ..core.storage import ensure_dirs
from ..core.scanner import scan_all


def cmd_check():
    """Check engram status.

    Displays a summary of the current state of all engrams, including:
    - Number of in-progress sessions
    - Number of completed sessions
    - Number of experiences
    - Number of archived sessions
    - List of sessions that can be archived (inactive for 7+ days)

    Example:
        $ sengram check
        📊 Session-Engram Status
           🔄 In Progress: 2 | ✅ Completed: 3 | 💡 Experience: 5 | 📦 Archived: 1

        ⚠️  Can Archive (1):
           - session-old-project.md
    """
    base, is_new = ensure_dirs()
    if is_new:
        print(f"✅ Created .engram/ directory: {base}")
    data = scan_all()
    cutoff = datetime.now() - timedelta(days=ARCHIVE_DAYS)
    stale = [s for s in data["sessions"] if s["modified"] < cutoff and s["front_matter"].get("status") != "archived"]
    active = len([s for s in data["sessions"] if s["front_matter"].get("status") == "in-progress"])
    resolved = len([s for s in data["sessions"] if s["front_matter"].get("status") == "resolved"])
    total_exp = sum(len(v) for v in data["experiences"].values())
    print(f"📊 Session-Engram Status")
    print(f"   🔄 In Progress: {active} | ✅ Completed: {resolved} | 💡 Experience: {total_exp} | 📦 Archived: {len(data['archives'])}")
    if stale:
        print(f"\n⚠️  Can Archive ({len(stale)}):")
        for s in stale:
            print(f"   - {s['file']}")
