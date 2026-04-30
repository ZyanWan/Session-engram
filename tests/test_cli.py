"""Tests for Session-Engram CLI."""

import os
import tempfile
import pytest
from pathlib import Path
from datetime import datetime

# Import from parent package
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session_engram.core.parser import parse_front_matter
from session_engram.core.storage import ensure_dirs, get_memory_root
from session_engram.core.config import CATEGORIES, MEMORY_DIR, SESSION_DIR, EXPERIENCE_DIR
from session_engram.commands.init import cmd_init
from session_engram.commands.info import cmd_info
from session_engram.commands.list import cmd_list
from session_engram.commands.check import cmd_check
from session_engram.commands.update import cmd_update
from session_engram.commands.map import cmd_map
from session_engram.commands.archive import cmd_archive


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_dir)


class TestParseFrontMatter:
    """Tests for front matter parsing."""

    def test_valid_front_matter(self):
        """Test parsing valid front matter."""
        content = """---
type: session
status: in-progress
tags: [test, example]
created: 2026-04-29
---
# Test Content
"""
        result = parse_front_matter(content)
        assert result is not None
        assert result["type"] == "session"
        assert result["status"] == "in-progress"
        assert "test" in result["tags"]

    def test_no_front_matter(self):
        """Test content without front matter."""
        content = """# Just a heading

Some content here.
"""
        result = parse_front_matter(content)
        assert result is None

    def test_empty_front_matter(self):
        """Test empty front matter."""
        content = """---
---
# Content
"""
        result = parse_front_matter(content)
        assert result is not None

    def test_front_matter_with_multiple_tags(self):
        """Test front matter with multiple tags."""
        content = """---
type: experience
status: resolved
tags: [jwt, authentication, mobile, security]
created: 2026-04-29
---
# Content
"""
        result = parse_front_matter(content)
        assert result is not None
        assert len(result["tags"]) == 4
        assert "jwt" in result["tags"]
        assert "security" in result["tags"]

    def test_front_matter_with_special_characters(self):
        """Test front matter with special characters in values."""
        content = """---
type: session
status: in-progress
summary: Build authentication system with JWT tokens
created: 2026-04-29
---
# Content
"""
        result = parse_front_matter(content)
        assert result is not None
        assert "Build authentication system" in result["summary"]


class TestDirectoryOperations:
    """Tests for directory operations."""

    def test_get_memory_root(self, temp_dir):
        """Test getting memory root path."""
        root = get_memory_root()
        assert root.endswith(MEMORY_DIR)

    def test_ensure_dirs(self, temp_dir):
        """Test directory creation."""
        base, is_new = ensure_dirs()
        assert os.path.exists(base)
        assert is_new is True
        assert os.path.exists(os.path.join(base, "session"))
        assert os.path.exists(os.path.join(base, "session", "archive"))
        assert os.path.exists(os.path.join(base, "experience"))
        for cat in CATEGORIES:
            assert os.path.exists(os.path.join(base, "experience", cat))

    def test_ensure_dirs_existing(self, temp_dir):
        """Test ensure_dirs with existing directory."""
        # First run creates
        base1, is_new1 = ensure_dirs()
        assert is_new1 is True
        
        # Second run detects existing
        base2, is_new2 = ensure_dirs()
        assert is_new2 is False
        assert base1 == base2


class TestInitCommand:
    """Tests for init command."""

    def test_init_new_directory(self, temp_dir):
        """Test init command creates directory structure."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            cmd_init()

        output = f.getvalue()
        assert "created" in output.lower()
        assert os.path.exists(MEMORY_DIR)
        assert os.path.exists(os.path.join(MEMORY_DIR, "index.md"))

    def test_init_existing_directory(self, temp_dir):
        """Test init command with existing directory."""
        import io
        from contextlib import redirect_stdout

        # First run creates
        f = io.StringIO()
        with redirect_stdout(f):
            cmd_init()

        # Second run shows existing
        f = io.StringIO()
        with redirect_stdout(f):
            cmd_init()

        output = f.getvalue()
        assert "already exists" in output.lower()

    def test_init_creates_index_md(self, temp_dir):
        """Test init command creates index.md file."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            cmd_init()

        index_path = os.path.join(MEMORY_DIR, "index.md")
        assert os.path.exists(index_path)
        
        content = Path(index_path).read_text(encoding="utf-8")
        assert "Session-Engram Index" in content
        assert "In Progress" in content
        assert "Completed" in content

    def test_init_with_template(self, temp_dir):
        """Test init command uses template if available."""
        import io
        from contextlib import redirect_stdout

        template_dir = os.path.join(os.path.dirname(__file__), "..", "session_engram", "templates")
        template_path = os.path.join(template_dir, "index-template.md")

        original_existed = os.path.exists(template_path)
        original_content = Path(template_path).read_text(encoding="utf-8") if original_existed else None

        test_template_content = """# Session-Engram Index

> Last Updated: {DATETIME}
> Global index for .engram folder.

---

## Session

### In Progress

| File | Task | Last Updated |
|------|------|--------------|
| {SESSION_ENTRIES_IN_PROGRESS}
"""
        try:
            Path(template_path).write_text(test_template_content, encoding="utf-8")

            f = io.StringIO()
            with redirect_stdout(f):
                cmd_init()

            output = f.getvalue()
            assert "template" in output.lower()

            index_path = os.path.join(MEMORY_DIR, "index.md")
            content = Path(index_path).read_text(encoding="utf-8")
            assert "Session-Engram Index" in content
        finally:
            if original_existed and original_content is not None:
                Path(template_path).write_text(original_content, encoding="utf-8")
            elif os.path.exists(template_path):
                os.remove(template_path)


class TestInfoCommand:
    """Tests for info command."""

    def test_info_command_new_dir(self, temp_dir):
        """Test info command creates directory on first run."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            cmd_info()

        output = f.getvalue()
        assert "created" in output.lower()
        assert os.path.exists(MEMORY_DIR)

    def test_info_command_existing_dir(self, temp_dir):
        """Test info command with existing directory."""
        import io
        from contextlib import redirect_stdout

        # First run creates
        f = io.StringIO()
        with redirect_stdout(f):
            cmd_info()

        # Second run shows info
        f = io.StringIO()
        with redirect_stdout(f):
            cmd_info()

        output = f.getvalue()
        assert "directory" in output.lower()
        assert "content" in output.lower()

    def test_info_shows_counts(self, temp_dir):
        """Test info command shows correct counts."""
        import io
        from contextlib import redirect_stdout

        # Create a test session file
        base, _ = ensure_dirs()
        session_path = os.path.join(SESSION_DIR, "test-session.md")
        Path(session_path).write_text("""---
type: session
status: in-progress
tags: [test]
---
# Test Session
""", encoding="utf-8")

        f = io.StringIO()
        with redirect_stdout(f):
            cmd_info()

        output = f.getvalue()
        assert "sessions: 1" in output.lower()


class TestListCommand:
    """Tests for list command."""

    def test_list_empty(self, temp_dir):
        """Test list command with empty engram."""
        import io
        from contextlib import redirect_stdout

        ensure_dirs()
        
        f = io.StringIO()
        with redirect_stdout(f):
            cmd_list()

        output = f.getvalue()
        assert "session (0)" in output.lower()

    def test_list_with_sessions(self, temp_dir):
        """Test list command with sessions."""
        import io
        from contextlib import redirect_stdout

        base, _ = ensure_dirs()
        
        # Create test session files
        for i in range(3):
            session_path = os.path.join(SESSION_DIR, f"test-session-{i}.md")
            Path(session_path).write_text(f"""---
type: session
status: {'in-progress' if i % 2 == 0 else 'resolved'}
tags: [test, example]
created: 2026-04-29
---
# Test Session {i}
""", encoding="utf-8")

        f = io.StringIO()
        with redirect_stdout(f):
            cmd_list()

        output = f.getvalue()
        assert "session (3)" in output.lower()


class TestCheckCommand:
    """Tests for check command."""

    def test_check_empty(self, temp_dir):
        """Test check command with empty engram."""
        import io
        from contextlib import redirect_stdout

        ensure_dirs()
        
        f = io.StringIO()
        with redirect_stdout(f):
            cmd_check()

        output = f.getvalue()
        assert "in progress: 0" in output.lower()

    def test_check_with_sessions(self, temp_dir):
        """Test check command with sessions."""
        import io
        from contextlib import redirect_stdout

        base, _ = ensure_dirs()
        
        # Create test session files
        session_path = os.path.join(SESSION_DIR, "test-session.md")
        Path(session_path).write_text("""---
type: session
status: in-progress
tags: [test]
---
# Test Session
""", encoding="utf-8")

        f = io.StringIO()
        with redirect_stdout(f):
            cmd_check()

        output = f.getvalue()
        assert "in progress: 1" in output.lower()


class TestUpdateCommand:
    """Tests for update command."""

    def test_update_creates_index(self, temp_dir):
        """Test update command creates index.md."""
        import io
        from contextlib import redirect_stdout

        base, _ = ensure_dirs()
        
        f = io.StringIO()
        with redirect_stdout(f):
            cmd_update()

        output = f.getvalue()
        assert "index.md updated" in output.lower()
        
        index_path = os.path.join(MEMORY_DIR, "index.md")
        assert os.path.exists(index_path)

    def test_update_with_sessions(self, temp_dir):
        """Test update command with sessions."""
        import io
        from contextlib import redirect_stdout

        base, _ = ensure_dirs()
        
        # Create test session files
        session_path = os.path.join(SESSION_DIR, "test-session.md")
        Path(session_path).write_text("""---
type: session
status: in-progress
tags: [test]
---
# Test Session
""", encoding="utf-8")

        f = io.StringIO()
        with redirect_stdout(f):
            cmd_update()

        output = f.getvalue()
        assert "1 entries" in output.lower()


class TestMapCommand:
    """Tests for map command."""

    def test_map_empty(self, temp_dir):
        """Test map command with empty engram."""
        import io
        from contextlib import redirect_stdout

        ensure_dirs()
        
        f = io.StringIO()
        with redirect_stdout(f):
            cmd_map()

        output = f.getvalue()
        assert "engram is empty" in output.lower()

    def test_map_with_sessions(self, temp_dir):
        """Test map command with sessions."""
        import io
        from contextlib import redirect_stdout

        base, _ = ensure_dirs()
        
        # Create test session files
        session_path = os.path.join(SESSION_DIR, "test-session.md")
        Path(session_path).write_text("""---
type: session
status: in-progress
tags: [test]
---
# Test Session
""", encoding="utf-8")

        f = io.StringIO()
        with redirect_stdout(f):
            cmd_map()

        output = f.getvalue()
        assert "engram map generated" in output.lower()


class TestArchiveCommand:
    """Tests for archive command."""

    def test_archive_empty(self, temp_dir):
        """Test archive command with empty engram."""
        import io
        from contextlib import redirect_stdout

        ensure_dirs()
        
        f = io.StringIO()
        with redirect_stdout(f):
            cmd_archive()

        output = f.getvalue()
        assert "no sessions to archive" in output.lower()

    def test_archive_old_sessions(self, temp_dir):
        """Test archive command with old sessions."""
        import io
        from contextlib import redirect_stdout
        from datetime import datetime, timedelta

        base, _ = ensure_dirs()
        
        # Create an old session file
        session_path = os.path.join(SESSION_DIR, "old-session.md")
        Path(session_path).write_text("""---
type: session
status: in-progress
tags: [test]
---
# Old Session
""", encoding="utf-8")
        
        # Set file modification time to 10 days ago
        old_time = datetime.now() - timedelta(days=10)
        os.utime(session_path, (old_time.timestamp(), old_time.timestamp()))

        f = io.StringIO()
        with redirect_stdout(f):
            cmd_archive()

        output = f.getvalue()
        assert "archived" in output.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
