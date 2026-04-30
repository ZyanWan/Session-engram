"""
Session-Engram CLI Entry Point

Cross-dialogue session memory system for AI assistants.
Command: sengram <command>
"""

import sys
import traceback

from .commands.init import cmd_init
from .commands.info import cmd_info
from .commands.map import cmd_map
from .commands.export import cmd_export
from .commands.update import cmd_update
from .commands.list import cmd_list
from .commands.check import cmd_check
from .commands.archive import cmd_archive
from .commands.timeline import cmd_timeline
from .commands.index import cmd_index
from .commands.install import install_platform, uninstall_platform


def _configure_encoding():
    """Configure stdout/stderr encoding to UTF-8 on Windows."""
    if sys.platform == "win32":
        import io
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _parse_export_args():
    """Parse export command arguments."""
    import argparse

    parser = argparse.ArgumentParser(prog="sengram export")
    parser.add_argument(
        "--format", "-f",
        choices=["json", "graphml"],
        default="json",
        help="Output format (default: json)"
    )
    return parser.parse_args(sys.argv[2:])


def _cmd_install():
    """Handle sengram install/uninstall."""
    args = sys.argv[2:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: sengram install [platform]    — install AI platform integration")
        print("       sengram uninstall [platform]  — remove AI platform integration")
        print()
        print("Platforms: auto (default), claude, opencode, agents")
        return

    platform = args[0] if args[0] != "auto" else "auto"
    install_platform(platform)


def _cmd_uninstall():
    """Handle sengram uninstall."""
    args = sys.argv[2:]
    platform = args[0] if args else "auto"
    uninstall_platform(platform)


def main():
    """Main CLI entry point."""
    _configure_encoding()

    commands = {
        "init": cmd_init,
        "info": cmd_info,
        "map": cmd_map,
        "export": lambda: cmd_export(format=_parse_export_args().format),
        "update": cmd_update,
        "list": cmd_list,
        "check": cmd_check,
        "archive": cmd_archive,
        "timeline": cmd_timeline,
        "index": cmd_index,
        "install": _cmd_install,
        "uninstall": _cmd_uninstall,
    }

    if len(sys.argv) < 2:
        print("Session-Engram - Cross-dialogue session memory system")
        print(f"\nUsage: sengram <command>")
        print(f"Commands: {', '.join(commands.keys())}")
        print("\nFirst run will auto-create .engram/ directory.")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd not in commands:
        print(f"❌ Unknown command: {cmd}")
        sys.exit(1)

    try:
        commands[cmd]()
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
