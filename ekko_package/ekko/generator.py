"""
Command generation logic for ekko
"""

import re
import subprocess
import sys

from rich.console import Console

from ekko.history import log_to_history
from ekko.providers import get_provider

console = Console()


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

        if provider_type == "anthropic":
            api_key = self.config.get("anthropic_api_key")
            if not api_key:
                print("Error: Anthropic API key not configured. Run: ekko --setup")
                import sys

                sys.exit(1)
            return get_provider("anthropic", api_key=api_key, model=self.config["anthropic_model"])

        elif provider_type == "ollama":
            return get_provider(
                "ollama",
                url=self.config["ollama_url"],
                model=self.config["ollama_model"],
            )

        else:
            print(f"Error: Unknown provider '{provider_type}'")
            import sys

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
        except Exception:
            pass
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

                # Run command
                try:
                    subprocess.run(cmd, shell=True)
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
