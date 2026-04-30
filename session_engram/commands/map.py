import os

from ..core.storage import ensure_dirs
from ..core.graph import build_graph_data
from ..core.visualizer import generate_vis_html


def cmd_map():
    """Generate interactive memory map.

    Creates an HTML file with an interactive vis.js visualization of all sessions and experiences.
    Features:
    - Community clustering by type
    - Summary display in info panel
    - Time range filter
    - Edge weight/type differentiation (shares_tag vs inspired)
    - Hyperedges for tag groups (3+ nodes)
    - Performance warning for large graphs
    - File path display with copy
    - Tag-based node highlighting

    Example:
        $ sengram map
        ✅ Engram map generated: /path/to/engram-map.html
           🔄 Active Session: 1 | ✅ Completed: 0 | 📦 Archived: 6
           💡 Experience: 15 | 🔗 Connections: 44
    """
    base, is_new = ensure_dirs()
    if is_new:
        print(f"✅ Created .engram/ directory: {base}")

    nodes, edges, communities, tag_groups = build_graph_data()

    if not nodes:
        print("📭 Engram is empty")
        return

    active_sessions = sum(1 for n in nodes if n.get("file_type") == "active-session")
    completed_sessions = sum(1 for n in nodes if n.get("file_type") == "completed-session")
    archived_sessions = sum(1 for n in nodes if n.get("file_type") == "archived-session")
    experiences = sum(1 for n in nodes if n.get("file_type", "").startswith("experience-"))

    output_path = os.path.join(base, "..", "engram-map.html")
    generate_vis_html(nodes, edges, communities, tag_groups, output_path)

    print(f"✅ Engram map generated: {output_path}")
    print(f"   🔄 Active Session: {active_sessions} | ✅ Completed: {completed_sessions} | 📦 Archived: {archived_sessions}")
    print(f"   💡 Experience: {experiences} | 🔗 Connections: {len(edges)}")
    if len(nodes) > 80:
        print(f"   ⚡ Large graph ({len(nodes)} nodes) — performance mode enabled")
