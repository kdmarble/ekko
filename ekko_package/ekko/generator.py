"""
Command generation logic for ekko
"""

import re
import shlex
import subprocess  # nosec B404 - subprocess needed for command execution
import sys

from rich.console import Console

from ekko.history import log_to_history
from ekko.providers import get_provider

console = Console()

# Dangerous command patterns that should trigger warnings
DANGEROUS_PATTERNS = [
    r'\brm\s+-rf\s+/',  # rm -rf /
    r'\bdd\s+if=/dev/(?:zero|random)\s+of=/dev/(?:sda|hda)',  # Disk wiping
    r':\(\)\{.*:\|:.*\};:',  # Fork bomb
    r'\bchmod\s+-R\s+777\s+/',  # Dangerous chmod
    r'\bmkfs\.',  # Filesystem formatting
    r'\b(?:wget|curl).*\|\s*(?:bash|sh)',  # Pipe to shell
]


class CommandGenerator:
    """Generate and execute shell commands from natural language."""

    def __init__(self, config: dict):
        """
        Initialize command generator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.provider = self._get_provider()

    def _get_provider(self):
        """
        Get the configured LLM provider instance.

        Returns:
            Provider instance

        Raises:
            SystemExit: If provider is not configured
        """
        provider_type = self.config["provider"]

        try:
            if provider_type == "anthropic":
                api_key = self.config.get("anthropic_api_key")
                if not api_key:
                    print("Error: Anthropic API key not configured. Run: ekko --setup")
                    sys.exit(1)
                # Initialize provider - sensitive data not logged in errors
                model_name = self.config.get("anthropic_model")
                return get_provider("anthropic", api_key=api_key, model=model_name)

            elif provider_type == "ollama":
                url = self.config.get("ollama_url")
                model_name = self.config.get("ollama_model")
                return get_provider("ollama", url=url, model=model_name)

            else:
                print(f"Error: Unknown provider '{provider_type}'")
                sys.exit(1)

        except Exception as e:
            # Catch and sanitize any errors to prevent logging sensitive data
            print(f"Error initializing provider: {type(e).__name__}")
            print("Run: ekko --setup to reconfigure")
            sys.exit(1)

    def _get_original_command(self) -> str:
        """
        Get the original ekko command from sys.argv.

        Returns:
            Original ekko command string
        """
        try:
            # Reconstruct the original command
            # sys.argv[0] is the script name, rest are arguments
            argv = sys.argv
            if argv:
                # Get base command (ekko)
                cmd_parts = ["ekko"]
                # Add all arguments after the command
                if len(argv) > 1:
                    cmd_parts.extend(argv[1:])
                return " ".join(cmd_parts)
        except (IndexError, AttributeError, TypeError) as e:
            # Fallback if argv is not accessible or malformed
            # This is not critical - just return default
            return "ekko"
        return "ekko"

    def clean_command(self, cmd: str) -> str:
        """
        Strip markdown and formatting artifacts from command.

        Args:
            cmd: Raw command output from LLM

        Returns:
            Cleaned command string
        """
        # Remove markdown code blocks
        cmd = re.sub(r"```[a-z]*\n?", "", cmd)
        cmd = re.sub(r"```\n?", "", cmd)
        # Remove backticks
        cmd = cmd.strip("`").strip()
        # Get first non-empty line
        lines = [line.strip() for line in cmd.split("\n") if line.strip()]
        return lines[0] if lines else ""

    def validate_command(self, cmd: str) -> tuple[bool, str]:
        """
        Validate command for obvious security issues.

        Args:
            cmd: Command to validate

        Returns:
            Tuple of (is_valid, warning_message)
        """
        # Check for empty command
        if not cmd or not cmd.strip():
            return False, "Empty command"

        # Check for extremely dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                return False, f"Potentially dangerous command detected. Please review carefully."

        # Check command length (extremely long commands might be suspicious)
        if len(cmd) > 10000:
            return False, "Command is suspiciously long"

        return True, ""

    def run(self, original_prompt: str):
        """
        Main interactive loop for command generation and execution.

        Args:
            original_prompt: User's natural language request
        """
        prompt = original_prompt
        system_prompt = self.config["system_prompt"]

        while True:
            # Generate command
            response = self.provider.generate(prompt, system_prompt)
            cmd = self.clean_command(response)

            if not cmd:
                print("Error: Could not generate valid command")
                return

            # Validate command for security issues
            is_valid, warning = self.validate_command(cmd)
            if not is_valid:
                console.print(f"[red]⚠ {warning}[/red]")
                console.print("[yellow]Command generation cancelled for safety.[/yellow]")
                return

            # Display command
            console.print()
            console.print(f"[cyan]{cmd}[/cyan]")

            # Get user input
            try:
                user_input = console.input(
                    "[dim]\\[enter=run, n=cancel, or describe what's wrong]: [/dim]"
                )
            except (KeyboardInterrupt, EOFError):
                console.print()
                return

            # Handle response
            if not user_input or user_input.lower() in ["y", "yes"]:
                # Log to shell history
                original_cmd = self._get_original_command()
                log_to_history(original_cmd)  # Log the ekko command
                log_to_history(cmd)  # Log the generated command

                # Run command with shell=True (required for shell features like pipes, redirects)
                # nosec B602 - shell=True is intentional as this tool executes user-approved shell commands
                try:
                    subprocess.run(cmd, shell=True, check=False)  # nosec B602
                except KeyboardInterrupt:
                    console.print()
                return

            elif user_input.lower() in ["n", "no", "q", "quit"]:
                # Cancel
                return

            else:
                # Correction - loop with feedback
                prompt = f"Original: '{original_prompt}'. Previous: '{cmd}'. Issue: {user_input}. Generate corrected command."
                console.print("[dim]↻ revising...[/dim]")
