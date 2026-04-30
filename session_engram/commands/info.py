import os

from ..core.storage import ensure_dirs
from ..core.scanner import scan_all


def cmd_info():
    """Show Session-Engram status and directory info.

    Displays the current status of the .engram directory, including:
    - Whether the directory was just created or already exists
    - Presence of index.md file
    - Count of sessions, experiences, and archives

    Example:
        $ sengram info
        📁 Session-Engram directory: /path/to/.engram
           index.md: exists

        📊 Content:
           Sessions: 3 | Experiences: 5 | Archives: 2
    """
    base, is_new = ensure_dirs()
    if is_new:
        print(f"✅ Created .engram/ directory: {base}")
    else:
        print(f"📁 Session-Engram directory: {base}")

    index_path = os.path.join(base, "index.md")
    if os.path.exists(index_path):
        print(f"   index.md: exists")
    else:
        print(f"   index.md: not found (will be created on first update)")

    data = scan_all()
    sessions = len(data["sessions"])
    experiences = sum(len(v) for v in data["experiences"].values())
    archives = len(data["archives"])
    print(f"\n📊 Content:")
    print(f"   Sessions: {sessions} | Experiences: {experiences} | Archives: {archives}")
