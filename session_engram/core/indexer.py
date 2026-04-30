"""Index generator for session engram.

Generates .engram/index.md — a lightweight summary that AI reads at session start.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .config import MEMORY_DIR, SESSION_DIR, EXPERIENCE_DIR, ARCHIVE_DIR, GLOBAL_EXPERIENCE_DIR
from .parser import parse_front_matter, extract_summary


def _get_index_mtime() -> float:
    """Get the modification time of index.md, or 0 if not exists."""
    index_path = os.path.join(MEMORY_DIR, "index.md")
    if os.path.exists(index_path):
        return os.path.getmtime(index_path)
    return 0.0


def _check_freshness() -> tuple[bool, str]:
    """Check if index.md is stale compared to source files.

    Returns:
        (is_fresh, message) — is_fresh is True if index is up-to-date.
    """
    index_mtime = _get_index_mtime()
    if index_mtime == 0:
        return False, "Index missing — run `sengram index`"

    latest_mtime = 0.0
    stale_source = ""

    for d in [SESSION_DIR, ARCHIVE_DIR, EXPERIENCE_DIR]:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if not f.endswith(".md"):
                    continue
                fp = os.path.join(root, f)
                mtime = os.path.getmtime(fp)
                if mtime > latest_mtime:
                    latest_mtime = mtime
                    stale_source = os.path.relpath(fp, MEMORY_DIR)

    if latest_mtime > index_mtime:
        return False, f"Index stale ({stale_source} is newer) — run `sengram index`"
    return True, ""


def _scan_sessions() -> list[dict[str, Any]]:
    """Scan all session files and return metadata."""
    sessions: list[dict[str, Any]] = []

    for d, file_type in [
        (SESSION_DIR, "active"),
        (ARCHIVE_DIR, "archived"),
    ]:
        if not os.path.exists(d):
            continue
        for f in os.listdir(d):
            if not f.endswith(".md"):
                continue
            fp = os.path.join(d, f)
            raw = Path(fp).read_text(encoding="utf-8")
            fm = parse_front_matter(raw)
            if not fm:
                continue

            status = fm.get("status", "unknown")
            if file_type == "active" and status == "archived":
                file_type_actual = "archived"
            elif file_type == "active" and status == "in-progress":
                file_type_actual = "active"
            elif file_type == "active":
                file_type_actual = "completed"
            else:
                file_type_actual = "archived"

            summary_raw = fm.get("summary", "").strip()
            if summary_raw and summary_raw != "|":
                summary_line = summary_raw.split("\n")[0]
            else:
                summary_line = extract_summary(raw)[:120]

            sessions.append({
                "id": f.replace(".md", ""),
                "label": f.replace(".md", "").replace("session-", ""),
                "status": status,
                "file_type": file_type_actual,
                "tags": fm.get("tags", []),
                "created": fm.get("created", ""),
                "updated": fm.get("updated", ""),
                "summary_line": summary_line,
                "source_file": f"session/{f}" if file_type == "active" else f"session/archive/{f}",
            })

    sessions.sort(key=lambda s: s["created"] or "", reverse=True)
    return sessions


def _scan_experiences(base_dir: str = EXPERIENCE_DIR) -> list[dict[str, Any]]:
    """Scan experience files under a directory and return metadata."""
    category_map = {"设计类": "design", "技术类": "technical", "业务类": "business"}
    experiences: list[dict[str, Any]] = []

    if not os.path.exists(base_dir):
        return experiences

    for cat_folder in os.listdir(base_dir):
        cat_path = os.path.join(base_dir, cat_folder)
        if not os.path.isdir(cat_path):
            continue
        category = category_map.get(cat_folder, cat_folder.lower())
        for f in os.listdir(cat_path):
            if not f.endswith(".md"):
                continue
            fp = os.path.join(cat_path, f)
            raw = Path(fp).read_text(encoding="utf-8")
            fm = parse_front_matter(raw)
            if not fm:
                continue
            uses = fm.get("uses", "0")
            try:
                uses_int = int(uses)
            except (ValueError, TypeError):
                uses_int = 0
            experiences.append({
                "id": f.replace(".md", ""),
                "label": f.replace(".md", "").replace("exp-", ""),
                "category": category,
                "tags": fm.get("tags", []),
                "created": fm.get("created", ""),
                "uses": uses_int,
                "source_file": f"{os.path.relpath(cat_path, MEMORY_DIR)}/{f}",
            })

    experiences.sort(key=lambda e: (e["uses"], e["created"] or ""), reverse=True)
    return experiences


def _scan_global_experiences() -> list[dict[str, Any]]:
    """Scan global experience files from user's home directory."""
    category_map = {"设计类": "design", "技术类": "technical", "业务类": "business"}
    experiences: list[dict[str, Any]] = []

    if not os.path.exists(GLOBAL_EXPERIENCE_DIR):
        return experiences

    for cat_folder in os.listdir(GLOBAL_EXPERIENCE_DIR):
        cat_path = os.path.join(GLOBAL_EXPERIENCE_DIR, cat_folder)
        if not os.path.isdir(cat_path):
            continue
        category = category_map.get(cat_folder, cat_folder.lower())
        for f in os.listdir(cat_path):
            if not f.endswith(".md"):
                continue
            fp = os.path.join(cat_path, f)
            raw = Path(fp).read_text(encoding="utf-8")
            fm = parse_front_matter(raw)
            if not fm:
                continue
            uses = fm.get("uses", "0")
            try:
                uses_int = int(uses)
            except (ValueError, TypeError):
                uses_int = 0
            experiences.append({
                "id": f.replace(".md", ""),
                "label": f.replace(".md", "").replace("exp-", ""),
                "category": category,
                "tags": fm.get("tags", []),
                "created": fm.get("created", ""),
                "uses": uses_int,
                "source_file": f"~/.sengram/experience/{cat_folder}/{f}",
            })

    experiences.sort(key=lambda e: (e["uses"], e["created"] or ""), reverse=True)
    return experiences


def generate_index() -> str:
    """Generate the content of .engram/index.md.

    Returns:
        Markdown string of the index file.
    """
    sessions = _scan_sessions()
    experiences = _scan_experiences(EXPERIENCE_DIR)
    global_experiences = _scan_global_experiences()

    active = [s for s in sessions if s["file_type"] == "active"]
    completed = [s for s in sessions if s["file_type"] == "completed"]
    archived = [s for s in sessions if s["file_type"] == "archived"]

    lines: list[str] = []
    lines.append("# Engram Memory Index")
    lines.append("")

    # Freshness warning
    is_fresh, freshness_msg = _check_freshness()
    if not is_fresh:
        lines.append(f"> ⚠️  **{freshness_msg}**")
        lines.append("")

    lines.append(f"> Auto-generated by `sengram index`. {len(sessions)} sessions, {len(experiences)} experiences.")
    lines.append("")

    # Quick context hints
    hints: list[str] = []
    if active:
        hints.append(f"{len(active)} active session(s)")
    if experiences:
        hints.append(f"{len(experiences)} experience(s)")
    if global_experiences:
        hints.append(f"{len(global_experiences)} global experience(s)")
    if hints:
        lines.append("> 💡 " + " | ".join(hints))
        lines.append("")

    # Active sessions
    if active:
        lines.append("## Active Sessions")
        lines.append("")
        for s in active:
            tags = ", ".join(s["tags"][:5]) if s["tags"] else ""
            tag_str = f" `{tags}`" if tags else ""
            lines.append(f"- **[{s['label']}]({s['source_file']})** ({s['created']}){tag_str}")
            if s["summary_line"]:
                lines.append(f"  {s['summary_line']}")
        lines.append("")

    # Recent completed
    if completed:
        lines.append("## Recent Completed")
        lines.append("")
        for s in completed[:5]:
            tags = ", ".join(s["tags"][:3]) if s["tags"] else ""
            tag_str = f" `{tags}`" if tags else ""
            lines.append(f"- [{s['label']}]({s['source_file']}) ({s['created']}){tag_str}")
        lines.append("")

    # Recent archived
    if archived:
        lines.append("## Recent Archived")
        lines.append("")
        for s in archived[:5]:
            tags = ", ".join(s["tags"][:3]) if s["tags"] else ""
            tag_str = f" `{tags}`" if tags else ""
            lines.append(f"- [{s['label']}]({s['source_file']}) ({s['created']}){tag_str}")
        lines.append("")

    # Experiences by category
    if experiences:
        lines.append("## Experiences")
        lines.append("")
        by_cat: dict[str, list[dict]] = {}
        for e in experiences:
            cat = e["category"]
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append(e)

        cat_labels = {"design": "Design", "technical": "Technical", "business": "Business"}
        for cat, items in by_cat.items():
            label = cat_labels.get(cat, cat.title())
            lines.append(f"### {label} ({len(items)})")
            lines.append("")
            for item in items[:5]:
                tags = ", ".join(item["tags"][:3]) if item["tags"] else ""
                tag_str = f" `{tags}`" if tags else ""
                uses_badge = f" (used {item['uses']}×)" if item["uses"] > 0 else ""
                lines.append(f"- [{item['label']}]({item['source_file']}) ({item['created']}){tag_str}{uses_badge}")
            if len(items) > 5:
                lines.append(f"- ... and {len(items) - 5} more")
            lines.append("")

    # Global experiences
    if global_experiences:
        lines.append("## Global Experiences (Cross-Project)")
        lines.append("")
        by_cat: dict[str, list[dict]] = {}
        for e in global_experiences:
            cat = e["category"]
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append(e)

        for cat, items in by_cat.items():
            label = cat_labels.get(cat, cat.title())
            lines.append(f"### {label} ({len(items)})")
            lines.append("")
            for item in items[:5]:
                tags = ", ".join(item["tags"][:3]) if item["tags"] else ""
                tag_str = f" `{tags}`" if tags else ""
                uses_badge = f" (used {item['uses']}×)" if item["uses"] > 0 else ""
                lines.append(f"- [{item['label']}]({item['source_file']}) ({item['created']}){tag_str}{uses_badge}")
            if len(items) > 5:
                lines.append(f"- ... and {len(items) - 5} more")
            lines.append("")

    # Tag index
    all_tags: dict[str, int] = {}
    for s in sessions:
        for t in s["tags"]:
            all_tags[t.lower()] = all_tags.get(t.lower(), 0) + 1
    for e in experiences + global_experiences:
        for t in e["tags"]:
            all_tags[t.lower()] = all_tags.get(t.lower(), 0) + 1

    if all_tags:
        sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:20]
        lines.append("## Top Tags")
        lines.append("")
        lines.append(" ".join(f"`{t}`" for t, _ in sorted_tags))
        lines.append("")

    return "\n".join(lines)
