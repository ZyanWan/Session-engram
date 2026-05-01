import os

from ..core.storage import ensure_dirs
from ..core.timeline import build_timeline_data
from ..core.timeline_visualizer import generate_timeline_html


def cmd_timeline():
    """Generate interactive timeline view.

    Creates an HTML file with a chronological view of all sessions and experiences.
    Features:
    - Month-based grouping
    - Type and tag filtering
    - Expandable detail cards
    - Status badges and color coding

    Example:
        $ sengram timeline
        ✅ Engram timeline generated: /path/to/engram-timeline.html
           🔄 Active: 1 | ✅ Completed: 0 | 📦 Archived: 6 | 💡 Experience: 15
    """
    base, is_new = ensure_dirs()
    if is_new:
        print(f"✅ Created .engram/ directory: {base}")

    entries = build_timeline_data()

    if not entries:
        print("📭 Engram is empty")
        return

    active = sum(1 for e in entries if e["file_type"] == "active-session")
    completed = sum(1 for e in entries if e["file_type"] == "completed-session")
    archived = sum(1 for e in entries if e["file_type"] == "archived-session")
    experience = sum(1 for e in entries if e["file_type"].startswith("experience-"))

    output_path = os.path.join(base, "engram-timeline.html")
    generate_timeline_html(entries, output_path)

    print(f"✅ Engram timeline generated: {output_path}")
    print(f"   🔄 Active: {active} | ✅ Completed: {completed} | 📦 Archived: {archived} | 💡 Experience: {experience}")
