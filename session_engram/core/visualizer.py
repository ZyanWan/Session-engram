import json
import os
from pathlib import Path
from typing import Any

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


def _read_template(name: str) -> str:
    path = os.path.join(TEMPLATE_DIR, name)
    return Path(path).read_text(encoding="utf-8")


def generate_vis_html(nodes: list[dict], edges: list[dict],
                      communities: dict[int, list[str]],
                      tag_groups: dict[str, list[str]],
                      output_path: str) -> None:
    """Generate vis.js interactive HTML map with enhanced features.

    Features:
    - Summary display in info panel
    - Time range filter
    - Edge weight/type differentiation
    - Hyperedges for tag groups
    - Performance warning for large graphs
    - File path display
    """
    community_labels: dict[int, str] = {
        0: "Session Active",
        1: "Session Completed",
        2: "Session Archived",
        3: "Experience Design",
        4: "Experience Technical",
        5: "Experience Business",
    }
    community_colors = [
        "#0891b2", "#6366f1", "#374151",
        "#d97706", "#dc2626", "#9333ea",
    ]

    node_community: dict[str, int] = {}
    for cid, nids in communities.items():
        for nid in nids:
            node_community[nid] = cid

    degree: dict[str, int] = {}
    for e in edges:
        degree[e["source"]] = degree.get(e["source"], 0) + 1
        degree[e["target"]] = degree.get(e["target"], 0) + 1
    max_deg = max(degree.values(), default=1) or 1

    def sanitize(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    vis_nodes = []
    for n in nodes:
        nid = n["id"]
        cid = node_community.get(nid, 0)
        color = community_colors[cid % len(community_colors)]
        label = n.get("label", nid)
        deg = degree.get(nid, 1)
        size = 12 + 16 * (deg / max_deg)
        font_size = 11 if deg >= max_deg * 0.2 else 0
        short_label = label[:28] + "..." if len(label) > 30 else label
        vis_nodes.append({
            "id": nid,
            "label": short_label,
            "color": {"background": color, "border": color, "highlight": {"background": "#f0fdf4", "border": color}, "hover": {"background": "#f8fafc", "border": color}},
            "size": round(size, 1),
            "font": {"size": font_size, "color": "#1e293b", "face": "-apple-system, sans-serif"},
            "title": sanitize(label),
            "shadow": {"enabled": True, "color": color, "size": 8, "x": 0, "y": 0},
            "community": cid,
            "community_name": community_labels.get(cid, f"Community {cid}"),
            "source_file": n.get("source_file", ""),
            "file_type": n.get("file_type", ""),
            "degree": deg,
            "summary": sanitize(n.get("summary", "")),
            "created": n.get("created", ""),
            "updated": n.get("updated", ""),
            "tags": n.get("tags", []),
        })

    max_weight = max((e.get("weight", 1) for e in edges), default=1) or 1
    vis_edges = []
    for i, e in enumerate(edges):
        w = e.get("weight", 1)
        rel = e.get("relation", "shares_tag")
        is_inspired = rel == "inspired"
        width = 1 + 2 * (w / max_weight)
        shared_tags_str = ", ".join(e.get("shared_tags", []))
        vis_edges.append({
            "from": e["source"],
            "to": e["target"],
            "label": "",
            "title": sanitize(f"{rel} ({w} shared: {shared_tags_str})" if w > 1 else rel),
            "dashes": is_inspired,
            "width": round(width, 1),
            "color": {"color": "#d97706" if is_inspired else "#475569", "opacity": 0.3 + 0.4 * (w / max_weight), "hover": "#1e293b"},
            "arrows": {"to": {"enabled": is_inspired, "scaleFactor": 0.3}},
            "smooth": {"enabled": True, "type": "continuous", "roundness": 0.15},
        })

    hyperedge_data = []
    for tag, nids in tag_groups.items():
        if len(nids) >= 3:
            hyperedge_data.append({"tag": tag, "nodes": nids, "count": len(nids)})

    legend_data = []
    for cid in sorted(community_labels.keys()):
        color = community_colors[cid % len(community_colors)]
        n = len(communities.get(cid, []))
        legend_data.append({"cid": cid, "color": color, "label": community_labels[cid], "count": n})

    all_dates = sorted(set(n.get("created", "") or n.get("updated", "") for n in nodes))
    all_dates = [d for d in all_dates if d]
    date_min = all_dates[0] if all_dates else ""
    date_max = all_dates[-1] if all_dates else ""

    nodes_json = json.dumps(vis_nodes).replace("</", "<\\/")
    edges_json = json.dumps(vis_edges).replace("</", "<\\/")
    legend_json = json.dumps(legend_data).replace("</", "<\\/")
    hyperedge_json = json.dumps(hyperedge_data).replace("</", "<\\/")
    perf_warning = "true" if len(nodes) > 80 else "false"
    stats = f"{len(nodes)} nodes · {len(edges)} edges · {len(communities)} communities"

    html = _read_template("engram-map.html")
    html = html.replace("/*__NODES__*/[]", nodes_json)
    html = html.replace("/*__EDGES__*/[]", edges_json)
    html = html.replace("/*__LEGEND__*/[]", legend_json)
    html = html.replace("/*__HYPEREDGES__*/[]", hyperedge_json)
    html = html.replace("__PERF_WARNING__", perf_warning)
    html = html.replace("__DATE_MIN__", date_min)
    html = html.replace("__DATE_MAX__", date_max)
    html = html.replace("__STATS__", stats)

    Path(output_path).write_text(html, encoding="utf-8")
