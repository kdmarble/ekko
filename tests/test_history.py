"""
Tests for shell history functionality.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
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


def test_atuin_detection():
    """Test Atuin detection."""
    with patch("shutil.which") as mock_which:
        # Test when Atuin is available
        mock_which.return_value = "/usr/bin/atuin"
        history = ShellHistory()
        assert history.has_atuin is True

        # Test when Atuin is not available
        mock_which.return_value = None
        history = ShellHistory()
        assert history.has_atuin is False


def test_atuin_history_success():
    """Test adding command to Atuin history successfully."""
    with patch("shutil.which") as mock_which, \
         patch("subprocess.run") as mock_run:
        # Atuin is available
        mock_which.return_value = "/usr/bin/atuin"

        # Mock successful atuin history start (returns ID)
        start_result = MagicMock()
        start_result.returncode = 0
        start_result.stdout = "test-history-id-123\n"

        # Mock successful atuin history end
        end_result = MagicMock()
        end_result.returncode = 0

        mock_run.side_effect = [start_result, end_result]

        history = ShellHistory()
        result = history.add_to_history("echo 'test'")

        assert result is True
        assert mock_run.call_count == 2

        # Verify the commands were called correctly
        first_call = mock_run.call_args_list[0]
        assert first_call[0][0] == ["atuin", "history", "start", "--", "echo 'test'"]

        second_call = mock_run.call_args_list[1]
        assert second_call[0][0] == ["atuin", "history", "end", "--exit", "0", "test-history-id-123"]


def test_atuin_history_failure_fallback():
    """Test fallback to traditional history when Atuin fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        histfile = Path(tmpdir) / "test_history"

        with patch("shutil.which") as mock_which, \
             patch("subprocess.run") as mock_run:
            # Atuin is available but fails
            mock_which.return_value = "/usr/bin/atuin"

            # Mock failed atuin history start
            start_result = MagicMock()
            start_result.returncode = 1
            mock_run.return_value = start_result

            history = ShellHistory()
            history.shell = "zsh"
            history.histfile = histfile

            # Should fall back to zsh history
            result = history.add_to_history("ls -la")
            assert result is True

            # Verify fallback to file-based history worked
            assert histfile.exists()
            content = histfile.read_text()
            assert "ls -la" in content


# Tests are now run via pytest - no manual runner needed
