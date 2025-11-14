"""
Shell history management for different shell environments.
"""

import os
import time
from pathlib import Path
from typing import Optional


class ShellHistory:
    """Manage shell history across different shell environments."""

    def __init__(self):
        """Initialize shell history manager."""
        self.shell = self._detect_shell()
        self.histfile = self._get_histfile()

    def _detect_shell(self) -> str:
        """
        Detect the current shell from environment.

        Returns:
            Shell name (bash, zsh, fish, or unknown)
        """
        shell_path = os.environ.get("SHELL", "")
        shell_name = os.path.basename(shell_path).lower()

        # Handle common shells
        if "bash" in shell_name:
            return "bash"
        elif "zsh" in shell_name:
            return "zsh"
        elif "fish" in shell_name:
            return "fish"
        else:
            return "unknown"

    def _get_histfile(self) -> Optional[Path]:
        """
        Get the history file path for the current shell.

        Returns:
            Path to history file, or None if not found
        """
        # Check HISTFILE environment variable first
        histfile_env = os.environ.get("HISTFILE")
        if histfile_env:
            return Path(histfile_env).expanduser()

        # Shell-specific defaults
        home = Path.home()
        if self.shell == "bash":
            return home / ".bash_history"
        elif self.shell == "zsh":
            return home / ".zsh_history"
        elif self.shell == "fish":
            return home / ".local" / "share" / "fish" / "fish_history"

        return None

    def add_to_history(self, command: str) -> bool:
        """
        Add a command to shell history.

        Args:
            command: Command to add to history

        Returns:
            True if successful, False otherwise
        """
        if not command or not command.strip():
            return False

        try:
            if self.shell == "bash":
                return self._add_bash_history(command)
            elif self.shell == "zsh":
                return self._add_zsh_history(command)
            elif self.shell == "fish":
                return self._add_fish_history(command)
            else:
                # Fallback: try generic approach
                return self._add_generic_history(command)
        except Exception:
            # Silently fail - shell history is not critical
            return False

    def _add_bash_history(self, command: str) -> bool:
        """
        Add command to bash history.

        Uses HISTFILE append for compatibility with subprocess execution.

        Args:
            command: Command to add

        Returns:
            True if successful
        """
        if not self.histfile:
            return False

        try:
            # Ensure directory exists
            self.histfile.parent.mkdir(parents=True, exist_ok=True)

            # Append to history file
            with open(self.histfile, "a") as f:
                f.write(f"{command}\n")

            # Ensure history file has secure permissions
            self.histfile.chmod(0o600)
            return True
        except (OSError, PermissionError):
            # Silently fail - shell history is not critical
            return False

    def _add_zsh_history(self, command: str) -> bool:
        """
        Add command to zsh history.

        Zsh history format: ': timestamp:duration;command'

        Args:
            command: Command to add

        Returns:
            True if successful
        """
        if not self.histfile:
            return False

        try:
            # Ensure directory exists
            self.histfile.parent.mkdir(parents=True, exist_ok=True)

            # Zsh extended history format
            timestamp = int(time.time())
            with open(self.histfile, "a") as f:
                f.write(f": {timestamp}:0;{command}\n")

            # Ensure history file has secure permissions
            self.histfile.chmod(0o600)
            return True
        except (OSError, PermissionError):
            # Silently fail - shell history is not critical
            return False

    def _add_fish_history(self, command: str) -> bool:
        """
        Add command to fish history.

        Fish history format uses YAML-like structure.

        Args:
            command: Command to add

        Returns:
            True if successful
        """
        if not self.histfile:
            return False

        try:
            # Ensure directory exists
            self.histfile.parent.mkdir(parents=True, exist_ok=True)

            # Fish history format
            timestamp = int(time.time())
            with open(self.histfile, "a") as f:
                f.write(f"- cmd: {command}\n")
                f.write(f"  when: {timestamp}\n")

            # Ensure history file has secure permissions
            self.histfile.chmod(0o600)
            return True
        except (OSError, PermissionError):
            # Silently fail - shell history is not critical
            return False

    def _add_generic_history(self, command: str) -> bool:
        """
        Fallback method for unknown shells.

        Args:
            command: Command to add

        Returns:
            True if successful
        """
        if not self.histfile:
            return False

        try:
            # Ensure directory exists
            self.histfile.parent.mkdir(parents=True, exist_ok=True)

            # Simple append
            with open(self.histfile, "a") as f:
                f.write(f"{command}\n")

            # Ensure history file has secure permissions
            self.histfile.chmod(0o600)
            return True
        except (OSError, PermissionError):
            # Silently fail - shell history is not critical
            return False


def log_to_history(command: str) -> None:
    """
    Convenience function to log a command to shell history.

    Args:
        command: Command to log to history
    """
    history = ShellHistory()
    history.add_to_history(command)
