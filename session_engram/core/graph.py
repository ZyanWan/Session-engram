import os
from pathlib import Path
from typing import Any

from .config import SESSION_DIR, EXPERIENCE_DIR
from .parser import parse_front_matter, extract_summary


def build_graph_data() -> tuple[list[dict], list[dict], dict[int, list[str]], dict[str, list[str]]]:
    """Build nodes, edges, communities and tag_groups from engram data.

    Returns:
        Tuple of (nodes, edges, communities, tag_groups) where:
        - nodes: list of node dicts with id, label, file_type, source_file, summary, etc.
        - edges: list of edge dicts with source, target, relation, weight, shared_tags
        - communities: dict mapping community_id -> list of node_ids
        - tag_groups: dict mapping tag_name -> list of node_ids (for hyperedges)
    """
    nodes: list[dict] = []
    edges: list[dict] = []
    category_map = {"设计类": "design", "技术类": "technical", "业务类": "business"}

    def _read_node(fp: str, f: str, **overrides: Any) -> dict:
        raw = Path(fp).read_text(encoding="utf-8")
        fm = parse_front_matter(raw)
        summary = extract_summary(raw)
        node_id = f.replace(".md", "")
        base = {
            "id": node_id,
            "label": f.replace(".md", ""),
            "file_type": "unknown",
            "source_file": "",
            "status": fm.get("status", "unknown") if fm else "unknown",
            "tags": fm.get("tags", []) if fm else [],
            "created": fm.get("created", "") if fm else "",
            "updated": fm.get("updated", "") if fm else "",
            "summary": summary,
        }
        base.update(overrides)
        return base

    if os.path.exists(SESSION_DIR):
        for f in os.listdir(SESSION_DIR):
            if f.endswith(".md") and f != "archive":
                fp = os.path.join(SESSION_DIR, f)
                fm = parse_front_matter(Path(fp).read_text(encoding="utf-8"))
                status = fm.get("status", "unknown") if fm else "unknown"
                if status == "archived":
                    file_type = "archived-session"
                elif status == "in-progress":
                    file_type = "active-session"
                else:
                    file_type = "completed-session"
                node = _read_node(fp, f, file_type=file_type, source_file=f"session/{f}")
                node["label"] = f.replace(".md", "").replace("session-", "")
                nodes.append(node)

    archive_session_dir = os.path.join(SESSION_DIR, "archive")
    if os.path.exists(archive_session_dir):
        for f in os.listdir(archive_session_dir):
            if f.endswith(".md"):
                fp = os.path.join(archive_session_dir, f)
                node = _read_node(fp, f, file_type="archived-session",
                                  source_file=f"session/archive/{f}", status="archived")
                node["label"] = f.replace(".md", "").replace("session-", "")
                nodes.append(node)

    if os.path.exists(EXPERIENCE_DIR):
        for cat_folder in os.listdir(EXPERIENCE_DIR):
            cat_path = os.path.join(EXPERIENCE_DIR, cat_folder)
            if not os.path.isdir(cat_path):
                continue
            engram_cat = category_map.get(cat_folder, cat_folder.lower())
            for f in os.listdir(cat_path):
                if f.endswith(".md"):
                    fp = os.path.join(cat_path, f)
                    node = _read_node(fp, f, file_type=f"experience-{engram_cat}",
                                      source_file=f"experience/{cat_folder}/{f}",
                                      category=engram_cat, status="resolved")
                    node["label"] = f.replace(".md", "").replace("exp-", "")
                    nodes.append(node)

    tag_map: dict[str, list[str]] = {}
    for node in nodes:
        for tag in node.get("tags", []):
            tag_lower = tag.lower()
            if tag_lower not in tag_map:
                tag_map[tag_lower] = []
            tag_map[tag_lower].append(node["id"])

    pair_shared: dict[tuple[str, str], list[str]] = {}
    for tag, nids in tag_map.items():
        for i, nid1 in enumerate(nids):
            for nid2 in nids[i + 1:]:
                pair = (min(nid1, nid2), max(nid1, nid2))
                if pair not in pair_shared:
                    pair_shared[pair] = []
                pair_shared[pair].append(tag)

    node_type_map = {n["id"]: n.get("file_type", "") for n in nodes}
    for pair, shared_tags in pair_shared.items():
        t1 = node_type_map.get(pair[0], "")
        t2 = node_type_map.get(pair[1], "")
        is_session_xp = (t1.startswith("session") and t2.startswith("experience")) or \
                         (t1.startswith("experience") and t2.startswith("session"))
        edges.append({
            "source": pair[0],
            "target": pair[1],
            "relation": "inspired" if is_session_xp else "shares_tag",
            "confidence": "EXTRACTED",
            "weight": len(shared_tags),
            "shared_tags": shared_tags,
        })

    communities: dict[int, list[str]] = {}
    type_to_comm: dict[str, int] = {}
    for i, ft in enumerate(["active-session", "completed-session", "archived-session",
                              "experience-design", "experience-technical", "experience-business"]):
        type_to_comm[ft] = i
    for node in nodes:
        ft = node.get("file_type", "")
        cid = type_to_comm.get(ft, 0)
        if cid not in communities:
            communities[cid] = []
        communities[cid].append(node["id"])

    tag_groups: dict[str, list[str]] = {}
    for tag, nids in tag_map.items():
        if len(nids) >= 2:
            tag_groups[tag] = nids

    return nodes, edges, communities, tag_groups
