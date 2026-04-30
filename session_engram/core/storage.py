import os
from pathlib import Path

from .config import MEMORY_DIR, SESSION_DIR, EXPERIENCE_DIR, ARCHIVE_DIR, CATEGORIES, GLOBAL_EXPERIENCE_DIR


def get_memory_root() -> str:
    """Get the path to the .engram directory.

    Returns:
        Absolute path to the .engram directory in the current working directory

    Example:
        >>> get_memory_root()
        '/path/to/current/dir/.engram'
    """
    cwd = Path.cwd()
    mem_path = cwd / MEMORY_DIR
    return str(mem_path)


def ensure_dirs() -> tuple[str, bool]:
    """Ensure all required directories exist.

    Creates the .engram directory structure if it doesn't exist.
    Also ensures the global experience directory in user's home.

    Returns:
        Tuple of (base_path, is_new_created) where:
        - base_path: Absolute path to the .engram directory
        - is_new_created: True if the directory was just created

    Example:
        >>> base, is_new = ensure_dirs()
        >>> print(f"Directory: {base}, New: {is_new}")
        Directory: /path/to/.engram, New: True
    """
    base = get_memory_root()
    is_new = not os.path.exists(base)
    dirs = [base, SESSION_DIR, ARCHIVE_DIR, EXPERIENCE_DIR]
    for cat in CATEGORIES:
        dirs.append(os.path.join(EXPERIENCE_DIR, cat))
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # Ensure global experience directory exists in user's home
    for cat in CATEGORIES:
        os.makedirs(os.path.join(GLOBAL_EXPERIENCE_DIR, cat), exist_ok=True)

    return base, is_new
