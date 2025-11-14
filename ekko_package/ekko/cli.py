"""
Command-line interface for ekko
"""

from typing import Optional, List
import typer
from ekko import __version__
from ekko.config import Config
from ekko.generator import CommandGenerator

app = typer.Typer(
    name="ekko",
    help="AI-powered command line assistant",
    add_completion=False,
    rich_markup_mode="rich",
)


def version_callback(value: bool):
    """Handle --version flag."""
    if value:
        typer.echo(f"ekko v{__version__}")
        raise typer.Exit()


def help_callback(ctx: typer.Context, value: bool):
    """Handle --help flag with custom help message."""
    if value:
        typer.echo("""ekko - AI-powered command line assistant

Usage:
  ekko <prompt>           Generate and run command
  ekko --setup            Run configuration wizard
  ekko --config           Show current configuration
  ekko --switch <provider>   Switch AI provider
  ekko --model <name>     Change model for current provider
  ekko --use <provider>:<model>  Switch provider and model
  ekko --help             Show this help
  ekko --version          Show version

Examples:
  ekko find all files over 500MB
  ekko compress this folder to tar.gz
  ekko show disk usage sorted by size

Provider Management:
  ekko --config                          # Show what's configured
  ekko --switch ollama                   # Switch to Ollama
  ekko --switch anthropic                # Switch to Anthropic
  ekko --model llama3                    # Change model
  ekko --use ollama:qwen3-coder          # Switch both at once

Configuration: ~/.config/ekko/config.json""")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def callback(
    prompt: Optional[List[str]] = typer.Argument(
        None, help="Natural language prompt for command generation"
    ),
    setup: bool = typer.Option(False, "--setup", help="Run configuration wizard"),
    config_show: bool = typer.Option(False, "--config", help="Show current configuration"),
    switch: Optional[str] = typer.Option(
        None, "--switch", help="Switch AI provider (ollama/anthropic)"
    ),
    model: Optional[str] = typer.Option(None, "--model", help="Change model for current provider"),
    use: Optional[str] = typer.Option(
        None, "--use", help="Switch provider and model (format: provider:model)"
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version",
    ),
    help_flag: bool = typer.Option(
        False,
        "--help",
        "-h",
        callback=help_callback,
        is_eager=True,
        help="Show help message",
    ),
):
    """
    ekko - AI-powered command line assistant

    Generate shell commands from natural language prompts.
    """
    config = Config()

    # Handle special commands
    if setup:
        config.setup_wizard()
        return

    if config_show:
        config.show_config()
        return

    if switch:
        config.switch_provider(switch)
        return

    if model:
        config.switch_model(model)
        return

    if use:
        if ":" in use:
            provider, model_name = use.split(":", 1)
            config.switch_provider(provider)
            config.switch_model(model_name)
        else:
            # Just switch provider, keep current model
            config.switch_provider(use)
        return

    # Check if configured
    if not config.config.get("anthropic_api_key") and config.config["provider"] == "anthropic":
        typer.echo("Not configured. Run: ekko --setup")
        return

    # Get prompt from arguments
    if not prompt:
        typer.echo("Usage: ekko <prompt>")
        typer.echo("Run 'ekko --help' for more information")
        raise typer.Exit(1)

    prompt_text = " ".join(prompt)

    # Generate and run
    generator = CommandGenerator(config.config)
    generator.run(prompt_text)


def main():
    """Entry point for console script."""
    app()


if __name__ == "__main__":
    app()
