"""
Tests for shell history functionality.
"""

import os
from unittest.mock import patch, MagicMock
from ekko.history import ShellHistory


def test_shell_detection():
    """Test shell detection from environment."""
    history = ShellHistory()
    # Should detect some shell or return 'unknown'
    assert history.shell in ["bash", "zsh", "fish", "unknown"]


def test_empty_command():
    """Test that empty commands are not logged."""
    history = ShellHistory()

    result = history.add_to_history("")
    assert result is False

    result = history.add_to_history("   ")
    assert result is False


def test_command_escaping():
    """Test that commands with special characters are properly escaped."""
    history = ShellHistory()

    # Test single quotes
    escaped = history._escape_command("echo 'hello'")
    assert "'\\''" in escaped or escaped == "echo '\\''hello'\\'''"

    # Test command without quotes
    escaped = history._escape_command("ls -la")
    assert escaped == "ls -la"


def test_zsh_history_interactive():
    """Test adding to zsh history using print -s in interactive mode."""
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        history = ShellHistory()
        history.shell = "zsh"
        history.shell_path = "/bin/zsh"

        result = history.add_to_history("ls -la")
        assert result is True

        # Verify subprocess.run was called with interactive flag
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "/bin/zsh"
        assert call_args[1] == "-i"  # Interactive mode
        assert call_args[2] == "-c"
        assert "print -s" in call_args[3]
        assert "ls -la" in call_args[3]


def test_bash_history_interactive():
    """Test adding to bash history using history -s in interactive mode."""
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        history = ShellHistory()
        history.shell = "bash"
        history.shell_path = "/bin/bash"

        result = history.add_to_history("echo 'test'")
        assert result is True

        # Verify subprocess.run was called with interactive flag
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "/bin/bash"
        assert call_args[1] == "-i"  # Interactive mode
        assert call_args[2] == "-c"
        assert "history -s" in call_args[3]
        assert "echo" in call_args[3]


def test_fish_history_interactive():
    """Test adding to fish history using history --save in interactive mode."""
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        history = ShellHistory()
        history.shell = "fish"
        history.shell_path = "/usr/bin/fish"

        result = history.add_to_history("git status")
        assert result is True

        # Verify subprocess.run was called with interactive flag
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "/usr/bin/fish"
        assert call_args[1] == "-i"  # Interactive mode
        assert call_args[2] == "-c"
        assert "history --save" in call_args[3]
        assert "git status" in call_args[3]


def test_shell_command_failure():
    """Test handling of shell command failures."""
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1  # Command failed
        mock_run.return_value = mock_result

        history = ShellHistory()
        history.shell = "zsh"
        history.shell_path = "/bin/zsh"

        result = history.add_to_history("some command")
        assert result is False


def test_no_shell_path():
    """Test handling when SHELL environment variable is not set."""
    history = ShellHistory()
    history.shell_path = ""

    result = history.add_to_history("test command")
    assert result is False


def test_unknown_shell():
    """Test handling of unknown shells."""
    with patch("subprocess.run") as mock_run:
        history = ShellHistory()
        history.shell = "unknown"
        history.shell_path = "/bin/unknown"

        result = history.add_to_history("test command")
        # Should return False since we don't know how to handle this shell
        assert result is False
        # Should not attempt to run subprocess for unknown shell
        mock_run.assert_not_called()


def test_subprocess_timeout():
    """Test handling of subprocess timeout."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = TimeoutError()

        history = ShellHistory()
        history.shell = "zsh"
        history.shell_path = "/bin/zsh"

        result = history.add_to_history("test command")
        assert result is False


# Tests are now run via pytest - no manual runner needed
