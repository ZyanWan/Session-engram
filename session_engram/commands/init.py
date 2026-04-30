import os
from datetime import datetime
from pathlib import Path

from ..core.config import DATE_FORMAT
from ..core.storage import ensure_dirs
from .update import cmd_update
from .install import install_platform

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


def _read_template(name: str) -> str:
    path = os.path.join(TEMPLATE_DIR, name)
    return Path(path).read_text(encoding="utf-8")


def cmd_init():
    """Initialize .engram directory structure and create index.md.

    Creates the .engram directory structure if it doesn't exist, including:
    - .engram/
    - .engram/session/
    - .engram/session/archive/
    - .engram/experience/
    - .engram/experience/design/
    - .engram/experience/technical/
    - .engram/experience/business/

    Also creates index.md from template and installs AI platform integration
    (AGENTS.md / CLAUDE.md + hooks) so AI knows about the memory system.

    Example:
        $ sengram init
        ✅ Created .engram/ directory: /path/to/.engram
        ✅ Created index.md from template
        ✅ index.md updated (0 entries)
        📄 Updated AGENTS.md
        🎉 Session-Engram initialized successfully!

        # Or if already initialized:
        $ sengram init
        📁 .engram/ directory already exists: /path/to/.engram
        📄 index.md already exists
        ✅ index.md updated (5 entries)
        📄 Updated AGENTS.md
        🎉 Session-Engram initialized successfully!
    """
    base, is_new = ensure_dirs()
    if is_new:
        print(f"✅ Created .engram/ directory: {base}")
    else:
        print(f"📁 .engram/ directory already exists: {base}")

    index_path = os.path.join(base, "index.md")
    if not os.path.exists(index_path):
        today = datetime.now().strftime(DATE_FORMAT)
        content = _read_template("index-template.md")
        content = content.replace("{DATETIME}", today)
        content = content.replace("{SESSION_ENTRIES_IN_PROGRESS}", "")
        content = content.replace("{SESSION_ENTRIES_COMPLETED}", "")
        content = content.replace("{EXPERIENCE_ENTRIES_DESIGN}", "")
        content = content.replace("{EXPERIENCE_ENTRIES_TECHNICAL}", "")
        content = content.replace("{EXPERIENCE_ENTRIES_BUSINESS}", "")
        Path(index_path).write_text(content, encoding="utf-8")
        print(f"✅ Created index.md from template")
    else:
        print(f"📄 index.md already exists")

    cmd_update()

    # Auto-install AI platform integration so AI knows about the memory system
    install_platform("auto")

    print(f"🎉 Session-Engram initialized successfully!")
