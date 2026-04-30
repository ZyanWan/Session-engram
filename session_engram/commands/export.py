import json
import os
import sys
from datetime import datetime
from pathlib import Path

from ..core.config import DATE_FORMAT
from ..core.storage import ensure_dirs
from ..core.graph import build_graph_data


def cmd_export(format: str = "json"):
    """Export engram graph data to various formats.

    Args:
        format: Output format, either "json" or "graphml". Defaults to "json".

    Supports:
    - json: graph.json compatible with graphify and D3.js visualizations
    - graphml: GraphML format for Gephi, yEd, and other graph analysis tools

    Usage:
        sengram export              # Export as graph.json (default)
        sengram export --format json    # Explicit JSON format
        sengram export --format graphml # GraphML format (requires networkx)

    Example:
        $ sengram export
        ✅ Exported graph.json (22 nodes, 44 edges)

        $ sengram export --format graphml
        ✅ Exported graph.graphml (22 nodes, 44 edges)
    """
    fmt = format

    if fmt not in ("json", "graphml"):
        print(f"❌ Unsupported format: {fmt}. Supported: json, graphml")
        sys.exit(1)

    base, is_new = ensure_dirs()
    if is_new:
        print(f"✅ Created .engram/ directory: {base}")

    nodes, edges, communities, tag_groups = build_graph_data()

    if not nodes:
        print("📭 Engram is empty")
        return

    if fmt == "json":
        graph_data = {
            "metadata": {
                "generator": "session-engram",
                "generated_at": datetime.now().strftime(DATE_FORMAT),
                "node_count": len(nodes),
                "edge_count": len(edges),
                "community_count": len(communities),
            },
            "nodes": [
                {
                    "id": n["id"],
                    "label": n.get("label", n["id"]),
                    "type": n.get("file_type", "unknown"),
                    "status": n.get("status", "unknown"),
                    "tags": n.get("tags", []),
                    "created": n.get("created", ""),
                    "updated": n.get("updated", ""),
                    "summary": n.get("summary", ""),
                    "source_file": n.get("source_file", ""),
                    "community": next((cid for cid, nids in communities.items() if n["id"] in nids), 0),
                }
                for n in nodes
            ],
            "edges": [
                {
                    "source": e["source"],
                    "target": e["target"],
                    "relation": e.get("relation", "shares_tag"),
                    "weight": e.get("weight", 1),
                    "shared_tags": e.get("shared_tags", []),
                }
                for e in edges
            ],
            "communities": {
                str(cid): {"label": lbl, "nodes": nids}
                for cid, nids in communities.items()
                for lbl in [
                    {0: "Session Active", 1: "Session Completed", 2: "Session Archived",
                     3: "Experience Design", 4: "Experience Technical", 5: "Experience Business"}.get(cid, f"Community {cid}")
                ]
            },
            "tag_groups": tag_groups,
        }
        output_path = os.path.join(base, "..", "graph.json")
        Path(output_path).write_text(
            json.dumps(graph_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"✅ Exported graph.json ({len(nodes)} nodes, {len(edges)} edges)")

    elif fmt == "graphml":
        try:
            import networkx as nx
        except ImportError:
            print("❌ GraphML export requires networkx. Install with: pip install networkx")
            sys.exit(1)

        G = nx.DiGraph()
        for n in nodes:
            G.add_node(
                n["id"],
                label=n.get("label", n["id"]),
                type=n.get("file_type", "unknown"),
                status=n.get("status", "unknown"),
                tags="|".join(n.get("tags", [])),
                created=n.get("created", ""),
                updated=n.get("updated", ""),
                summary=n.get("summary", ""),
            )
        for e in edges:
            G.add_edge(
                e["source"],
                e["target"],
                relation=e.get("relation", "shares_tag"),
                weight=e.get("weight", 1),
                shared_tags="|".join(e.get("shared_tags", [])),
            )
        output_path = os.path.join(base, "..", "graph.graphml")
        nx.write_graphml(G, output_path)
        print(f"✅ Exported graph.graphml ({len(nodes)} nodes, {len(edges)} edges)")
