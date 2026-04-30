"""Platform installer for session-engram.

Injects rules and hooks into AI coding assistants so they automatically
read .engram/index.md at session start.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from ..core.indexer import generate_index

SENGRAM_RULES_SECTION = """\
## session-engram

This project has a session memory system at .engram/.

Rules:
- At the start of every session, read .engram/index.md to understand the project's session history, active work, and available experiences
- When working on a task that may relate to past sessions, check .engram/index.md for relevant context
- If .engram/experience/ contains entries related to your current task, read them — they contain reusable solutions and lessons learned
- If index.md shows a freshness warning ("Index stale"), run `sengram index` immediately before proceeding
- After completing a session, run `sengram index` to update the memory index
- When reading an experience file, increment its `uses` counter in front matter if it helped solve the current problem
"""

SENGRAM_HOOK_CONTEXT = (
    "session-engram: This project has a memory system. "
    "Read .engram/index.md for session history, active work, and reusable experiences."
)


def _get_project_root() -> str:
    """Get the current working directory as project root."""
    return os.getcwd()


def _ensure_index(base: str) -> None:
    """Generate index.md if it doesn't exist."""
    index_path = os.path.join(base, "index.md")
    if not os.path.exists(index_path):
        content = generate_index()
        Path(index_path).write_text(content, encoding="utf-8")
        print(f"  📝 Generated .engram/index.md")


def _install_claude(project_root: str) -> None:
    """Install for Claude Code: CLAUDE.md + PreToolUse hook."""
    # 1. Write/update CLAUDE.md
    claude_md_path = os.path.join(project_root, "CLAUDE.md")
    _inject_section(claude_md_path, SENGRAM_RULES_SECTION)

    # 2. Install PreToolUse hook
    settings_dir = os.path.join(project_root, ".claude")
    os.makedirs(settings_dir, exist_ok=True)
    settings_path = os.path.join(settings_dir, "settings.json")

    settings = {}
    if os.path.exists(settings_path):
        try:
            settings = json.loads(Path(settings_path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            settings = {}

    hooks = settings.get("hooks", {})
    pre_bash = hooks.get("PreToolUse", [])

    hook_command = (
        '[ -f .engram/index.md ] && '
        '\'{"hookSpecificOutput":{"hookEventName":"PreToolUse",'
        f'"additionalContext":"{SENGRAM_HOOK_CONTEXT}"}}\' || true'
    )

    hook_entry = {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": hook_command}],
    }

    read_hook_entry = {
        "matcher": "Read",
        "hooks": [{"type": "command", "command": hook_command}],
    }

    # Remove existing sengram hooks before adding
    pre_bash = [h for h in pre_bash if "engram" not in json.dumps(h).lower()]
    pre_bash.append(hook_entry)
    pre_bash.append(read_hook_entry)
    hooks["PreToolUse"] = pre_bash
    settings["hooks"] = hooks

    Path(settings_path).write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  🪝 Installed PreToolUse hook → .claude/settings.json")


def _install_opencode(project_root: str) -> None:
    """Install for OpenCode: AGENTS.md + plugin."""
    # 1. Write/update AGENTS.md
    agents_md_path = os.path.join(project_root, "AGENTS.md")
    _inject_section(agents_md_path, SENGRAM_RULES_SECTION)

    # 2. Install plugin
    plugin_dir = os.path.join(project_root, ".opencode", "plugins")
    os.makedirs(plugin_dir, exist_ok=True)

    plugin_js = f"""\
// session-engram OpenCode plugin
import {{ existsSync }} from "fs";
import {{ join }} from "path";

export const SengramPlugin = async ({{ directory }}) => {{
  let reminded = false;
  return {{
    "tool.execute.before": async (input, output) => {{
      if (reminded) return;
      const index = join(directory, ".engram", "index.md");
      if (!existsSync(index)) return;
      if (input.tool === "bash" || input.tool === "read") {{
        output.args.command =
          'echo "[sengram] Read .engram/index.md for session history and experiences" && ' +
          output.args.command;
        reminded = true;
      }}
    }},
  }};
}};
"""
    plugin_path = os.path.join(plugin_dir, "sengram.js")
    Path(plugin_path).write_text(plugin_js, encoding="utf-8")

    # Register plugin in opencode.json
    config_path = os.path.join(project_root, ".opencode", "opencode.json")
    config = {}
    if os.path.exists(config_path):
        try:
            config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            config = {}

    plugins = config.get("plugin", [])
    plugin_ref = ".opencode/plugins/sengram.js"
    if plugin_ref not in plugins:
        plugins.append(plugin_ref)
    config["plugin"] = plugins

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    Path(config_path).write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  🔌 Installed plugin → .opencode/plugins/sengram.js")


def _install_agents(project_root: str) -> None:
    """Install for generic platforms: AGENTS.md only."""
    agents_md_path = os.path.join(project_root, "AGENTS.md")
    _inject_section(agents_md_path, SENGRAM_RULES_SECTION)


def _inject_section(file_path: str, section: str) -> None:
    """Inject a section into a markdown file, avoiding duplicates."""
    marker_start = "## session-engram"
    content = ""

    if os.path.exists(file_path):
        content = Path(file_path).read_text(encoding="utf-8")
        # Remove existing section
        lines = content.split("\n")
        new_lines: list[str] = []
        in_section = False
        for line in lines:
            if line.strip() == marker_start:
                in_section = True
                continue
            if in_section and line.startswith("## ") and line.strip() != marker_start:
                in_section = False
            if not in_section:
                new_lines.append(line)
        content = "\n".join(new_lines).rstrip()

    if content and not content.endswith("\n"):
        content += "\n"
    content += "\n" + section

    Path(file_path).write_text(content, encoding="utf-8")
    print(f"  📄 Updated {os.path.basename(file_path)}")


def install_platform(platform: str = "auto") -> None:
    """Install session-engram rules and hooks for the specified AI platform.

    Args:
        platform: One of "claude", "opencode", "agents", or "auto".
                  "auto" detects based on existing config directories.
    """
    project_root = _get_project_root()
    base = os.path.join(project_root, ".engram")

    print(f"🔧 Installing session-engram for AI platform...")
    print(f"   Project: {project_root}")
    print()

    # Ensure .engram and index exist
    _ensure_index(base)

    if platform == "auto":
        if os.path.exists(os.path.join(project_root, ".claude")):
            platform = "claude"
        elif os.path.exists(os.path.join(project_root, ".opencode")):
            platform = "opencode"
        else:
            platform = "agents"

    if platform == "claude":
        _install_claude(project_root)
    elif platform == "opencode":
        _install_opencode(project_root)
    elif platform == "agents":
        _install_agents(project_root)
    else:
        print(f"❌ Unknown platform: {platform}")
        print("   Supported: claude, opencode, agents, auto")
        return

    print()
    print(f"✅ Done! AI will now read .engram/index.md at session start.")
    print(f"   Run `sengram index` to refresh the memory index.")


def uninstall_platform(platform: str = "auto") -> None:
    """Remove session-engram rules and hooks from the project.

    Args:
        platform: One of "claude", "opencode", "agents", or "auto".
    """
    project_root = _get_project_root()

    if platform == "auto":
        if os.path.exists(os.path.join(project_root, ".claude", "settings.json")):
            platform = "claude"
        elif os.path.exists(os.path.join(project_root, ".opencode", "plugins", "sengram.js")):
            platform = "opencode"
        else:
            platform = "agents"

    print(f"🔧 Uninstalling session-engram ({platform})...")

    # Remove section from the markdown file associated with this platform
    md_file_map = {
        "claude": "CLAUDE.md",
        "opencode": "AGENTS.md",
        "agents": "AGENTS.md",
    }
    target_md = md_file_map.get(platform)
    if target_md:
        md_path = os.path.join(project_root, target_md)
        if os.path.exists(md_path):
            content = Path(md_path).read_text(encoding="utf-8")
            lines = content.split("\n")
            new_lines: list[str] = []
            in_section = False
            for line in lines:
                if line.strip() == "## session-engram":
                    in_section = True
                    continue
                if in_section and line.startswith("## "):
                    in_section = False
                if not in_section:
                    new_lines.append(line)
            new_content = "\n".join(new_lines).rstrip()
            if new_content:
                Path(md_path).write_text(new_content + "\n", encoding="utf-8")
                print(f"  🗑️  Removed section from {target_md}")
            else:
                os.remove(md_path)
                print(f"  🗑️  Removed {target_md} (empty after cleanup)")

    # Remove Claude hook
    if platform == "claude":
        settings_path = os.path.join(project_root, ".claude", "settings.json")
        if os.path.exists(settings_path):
            try:
                settings = json.loads(Path(settings_path).read_text(encoding="utf-8"))
                hooks = settings.get("hooks", {})
                pre_bash = hooks.get("PreToolUse", [])
                pre_bash = [h for h in pre_bash if "engram" not in json.dumps(h).lower()]
                if pre_bash:
                    hooks["PreToolUse"] = pre_bash
                else:
                    hooks.pop("PreToolUse", None)
                if hooks:
                    settings["hooks"] = hooks
                else:
                    settings.pop("hooks", None)
                Path(settings_path).write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"  🗑️  Removed hook from .claude/settings.json")
            except (json.JSONDecodeError, OSError):
                pass

    # Remove OpenCode plugin
    if platform == "opencode":
        plugin_path = os.path.join(project_root, ".opencode", "plugins", "sengram.js")
        if os.path.exists(plugin_path):
            os.remove(plugin_path)
            print(f"  🗑️  Removed .opencode/plugins/sengram.js")

        config_path = os.path.join(project_root, ".opencode", "opencode.json")
        if os.path.exists(config_path):
            try:
                config = json.loads(Path(config_path).read_text(encoding="utf-8"))
                plugins = config.get("plugin", [])
                plugins = [p for p in plugins if "sengram" not in p]
                if plugins:
                    config["plugin"] = plugins
                else:
                    config.pop("plugin", None)
                Path(config_path).write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"  🗑️  Updated .opencode/opencode.json")
            except (json.JSONDecodeError, OSError):
                pass

    print()
    print("✅ Uninstalled. .engram/ data is preserved.")
