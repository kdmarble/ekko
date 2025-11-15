"""
Shell history management for different shell environments.
"""

import os
import subprocess


class ShellHistory:
    """Manage shell history across different shell environments."""

    def __init__(self):
        """Initialize shell history manager."""
        self.shell = self._detect_shell()
        self.shell_path = os.environ.get("SHELL", "")

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

    def _escape_command(self, command: str) -> str:
        """
        Escape a command string for safe shell execution.

        Args:
            command: Command to escape

        Returns:
            Escaped command string
        """
        # Escape single quotes by replacing ' with '\''
        return command.replace("'", "'\\''")

    def _add_via_interactive_shell(self, command: str) -> bool:
        """
        Add command to history using shell's built-in commands in interactive mode.

        This is a generic approach that works with any history manager (Atuin, McFly,
        Hishtory, etc.) by running the shell in interactive mode (-i flag), which:
        1. Sources the user's shell config (.zshrc, .bashrc, .config/fish/config.fish)
        2. Initializes any history managers that hook into the shell
        3. Makes built-in history commands work through those managers

        Args:
            command: Command to add

        Returns:
            True if successful
        """
        if not self.shell_path:
            return False

        escaped_cmd = self._escape_command(command)

        try:
            if self.shell == "zsh":
                # Use print -s in interactive mode to trigger history hooks
                shell_cmd = f"print -s '{escaped_cmd}'"
                result = subprocess.run(
                    [self.shell_path, "-i", "-c", shell_cmd],
                    capture_output=True,
                    timeout=5,
                    env=os.environ.copy(),
                    stdin=subprocess.DEVNULL,  # Prevent waiting for input
                )
                return result.returncode == 0

            elif self.shell == "bash":
                # Use history -s in interactive mode to trigger history hooks
                shell_cmd = f"history -s '{escaped_cmd}'"
                result = subprocess.run(
                    [self.shell_path, "-i", "-c", shell_cmd],
                    capture_output=True,
                    timeout=5,
                    env=os.environ.copy(),
                    stdin=subprocess.DEVNULL,  # Prevent waiting for input
                )
                return result.returncode == 0

            elif self.shell == "fish":
                # Use history --save in interactive mode to trigger history hooks
                shell_cmd = f"history --save '{escaped_cmd}'"
                result = subprocess.run(
                    [self.shell_path, "-i", "-c", shell_cmd],
                    capture_output=True,
                    timeout=5,
                    env=os.environ.copy(),
                    stdin=subprocess.DEVNULL,  # Prevent waiting for input
                )
                return result.returncode == 0

            return False

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # Silently fail - shell history is not critical
            return False

    def add_to_history(self, command: str) -> bool:
        """
        Add a command to shell history.

        Uses shell built-in commands in interactive mode, which works generically
        with any shell history manager (Atuin, McFly, Hishtory, etc.) by sourcing
        the user's shell config and initializing their history tools.

        Args:
            command: Command to add to history

        Returns:
            True if successful, False otherwise
        """
        if not command or not command.strip():
            return False

        try:
            return self._add_via_interactive_shell(command)
        except Exception:
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
