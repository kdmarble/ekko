"""
Tests for shell history functionality.
"""

import os
import tempfile
from pathlib import Path
from ekko.history import ShellHistory


def test_shell_detection():
    """Test shell detection from environment."""
    history = ShellHistory()
    # Should detect some shell or return 'unknown'
    assert history.shell in ["bash", "zsh", "fish", "unknown"]


def test_bash_history():
    """Test bash history logging."""
    with tempfile.TemporaryDirectory() as tmpdir:
        histfile = Path(tmpdir) / "test_history"

        # Create a history instance and override histfile
        history = ShellHistory()
        history.shell = "bash"
        history.histfile = histfile

        # Add a command
        result = history.add_to_history("echo 'test command'")
        assert result is True

        # Verify it was written
        assert histfile.exists()
        content = histfile.read_text()
        assert "echo 'test command'" in content


def test_zsh_history():
    """Test zsh history logging."""
    with tempfile.TemporaryDirectory() as tmpdir:
        histfile = Path(tmpdir) / "test_history"

        # Create a history instance and override histfile
        history = ShellHistory()
        history.shell = "zsh"
        history.histfile = histfile

        # Add a command
        result = history.add_to_history("ls -la")
        assert result is True

        # Verify it was written in zsh format
        assert histfile.exists()
        content = histfile.read_text()
        assert "ls -la" in content
        assert ":" in content  # Zsh format includes timestamp


def test_fish_history():
    """Test fish history logging."""
    with tempfile.TemporaryDirectory() as tmpdir:
        histfile = Path(tmpdir) / "test_history"

        # Create a history instance and override histfile
        history = ShellHistory()
        history.shell = "fish"
        history.histfile = histfile

        # Add a command
        result = history.add_to_history("git status")
        assert result is True

        # Verify it was written in fish format
        assert histfile.exists()
        content = histfile.read_text()
        assert "cmd: git status" in content
        assert "when:" in content


def test_empty_command():
    """Test that empty commands are not logged."""
    history = ShellHistory()

    result = history.add_to_history("")
    assert result is False

    result = history.add_to_history("   ")
    assert result is False


if __name__ == "__main__":
    # Run basic tests
    test_shell_detection()
    print("✓ Shell detection test passed")

    test_bash_history()
    print("✓ Bash history test passed")

    test_zsh_history()
    print("✓ Zsh history test passed")

    test_fish_history()
    print("✓ Fish history test passed")

    test_empty_command()
    print("✓ Empty command test passed")

    print("\nAll tests passed!")
