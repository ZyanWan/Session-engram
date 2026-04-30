import os
from pathlib import Path

from ..core.storage import ensure_dirs
from ..core.indexer import generate_index


def cmd_index():
    """Generate .engram/index.md — lightweight memory summary for AI.

    Creates a compact index file that AI reads at session start to understand
    the project's session history, active work, and available experiences.

    Example:
        $ sengram index
        ✅ Engram index generated: /path/to/.engram/index.md
           🔄 Active: 1 | 📦 Archived: 6 | 💡 Experience: 15
    """
    base, is_new = ensure_dirs()
    if is_new:
        print(f"✅ Created .engram/ directory: {base}")

    index_content = generate_index()
    output_path = os.path.join(base, "index.md")

    Path(output_path).write_text(index_content, encoding="utf-8")

    print(f"✅ Engram index generated: {output_path}")
