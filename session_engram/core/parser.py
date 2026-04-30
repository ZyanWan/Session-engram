import re
from typing import Optional, Any


def parse_front_matter(content: str) -> Optional[dict[str, Any]]:
    """Parse YAML front matter from markdown content.

    Args:
        content: Raw markdown file content

    Returns:
        Parsed front matter dictionary, or None if not found

    Example:
        >>> content = '''---
        ... type: session
        ... status: in-progress
        ... tags: [test, example]
        ... ---
        ... # Content
        ... '''
        >>> parse_front_matter(content)
        {'type': 'session', 'status': 'in-progress', 'tags': ['test', 'example']}
    """
    content = content.lstrip("\ufeff")
    pattern = r"^---[^\S\n]*\n(.*?)\n?---[^\S\n]*\n"
    match = re.match(pattern, content, re.DOTALL)
    if not match:
        return None
    yaml_text = match.group(1)
    result: dict[str, Any] = {}
    for line in yaml_text.split("\n"):
        line = line.strip()
        if ": " in line and not line.startswith("#"):
            key, _, value = line.partition(": ")
            key = key.strip()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip("'\"") for v in value[1:-1].split(",")]
            result[key] = value
    return result


def extract_summary(content: str, max_len: int = 200) -> str:
    """Extract first meaningful paragraph after front matter as summary.

    Safely extracts the first non-heading, non-empty paragraph from
    markdown content. Returns empty string if nothing useful is found.
    Does NOT modify parse_front_matter — operates on raw file content.
    """
    content = content.lstrip("\ufeff")
    body = re.sub(r"^---[^\S\n]*\n.*?\n?---[^\S\n]*\n", "", content, flags=re.DOTALL).strip()
    if not body:
        return ""
    lines = body.split("\n")
    summary_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if summary_lines:
                break
            continue
        if stripped.startswith("#"):
            if summary_lines:
                break
            continue
        if stripped.startswith("```") or stripped.startswith("|") or stripped.startswith(">"):
            if summary_lines:
                break
            continue
        summary_lines.append(stripped)
    summary = " ".join(summary_lines)
    if len(summary) > max_len:
        summary = summary[:max_len - 3] + "..."
    return summary
