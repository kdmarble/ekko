"""
Command-line interface for ekko
"""

import sys
from ekko import __version__
from ekko.config import Config
from ekko.generator import CommandGenerator


def main():
    """Main entry point for ekko CLI."""
    config = Config()

    # Handle special commands
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--setup", "setup"]:
            config.setup_wizard()
            return

        if sys.argv[1] in ["--config", "config"]:
            config.show_config()
            return

        if sys.argv[1] in ["--switch"]:
            if len(sys.argv) < 3:
                print("Usage: ekko --switch <provider>")
                print("Providers: ollama, anthropic")
                sys.exit(1)
            config.switch_provider(sys.argv[2])
            return

        if sys.argv[1] in ["--model"]:
            if len(sys.argv) < 3:
                print("Usage: ekko --model <model_name>")
                sys.exit(1)
            config.switch_model(sys.argv[2])
            return

        if sys.argv[1] in ["--use"]:
            if len(sys.argv) < 3:
                print("Usage: ekko --use <provider>:<model>")
                print("Example: ekko --use anthropic:claude-sonnet-4-5-20250929")
                print("Example: ekko --use ollama:llama3")
                sys.exit(1)

            use_arg = sys.argv[2]
            if ":" in use_arg:
                provider, model = use_arg.split(":", 1)
                config.switch_provider(provider)
                config.switch_model(model)
            else:
                # Just switch provider, keep current model
                config.switch_provider(use_arg)
            return

        if sys.argv[1] in ["--help", "-h", "help"]:
            print(
                """ekko - AI-powered command line assistant

Usage:
  ekko <prompt>           Generate and run command
  ekko --setup            Run configuration wizard
  ekko --config           Show current configuration
  ekko --switch <provider>   Switch AI provider
  ekko --model <name>     Change model for current provider
  ekko --use <provider>:<model>  Switch provider and model
  ekko --help             Show this help

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

Configuration: ~/.config/ekko/config.json"""
            )
            return

        if sys.argv[1] in ["--version", "-v"]:
            print(f"ekko v{__version__}")
            return

    # Check if configured
    if (
        not config.config.get("anthropic_api_key")
        and config.config["provider"] == "anthropic"
    ):
        print("Not configured. Run: ekko --setup")
        return

    # Get prompt from arguments
    if len(sys.argv) < 2:
        print("Usage: ekko <prompt>")
        print("Run 'ekko --help' for more information")
        return

    prompt = " ".join(sys.argv[1:])

    # Generate and run
    generator = CommandGenerator(config.config)
    generator.run(prompt)


if __name__ == "__main__":
    main()
