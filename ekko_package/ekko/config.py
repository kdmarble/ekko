"""
Configuration management for ekko
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any
from ekko.providers import PROVIDERS


class Config:
    """Manage ekko configuration file and settings."""

    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / ".config" / "ekko"
        self.config_file = self.config_dir / "config.json"
        self.config = self.load_config()

    def _get_input(self, prompt: str) -> str:
        """
        Get input from TTY instead of stdin to handle piped installation scripts.

        Args:
            prompt: Prompt to display to user

        Returns:
            User input as string
        """
        try:
            # Open TTY directly to avoid reading from piped stdin
            with open("/dev/tty", "r") as tty:
                # Print to stdout so user sees the prompt
                print(prompt, end="", flush=True)
                return tty.readline().strip()
        except (IOError, OSError, FileNotFoundError):
            # Fall back to regular input if TTY is not available
            return input(prompt).strip()

    def _validate_url(self, url: str) -> bool:
        """
        Validate URL format.

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise
        """
        if not url:
            return False
        # Check if it starts with http:// or https://
        if not url.startswith(("http://", "https://")):
            return False
        # Basic validation that it has a domain/host
        without_protocol = url.split("://", 1)[1] if "://" in url else ""
        return bool(without_protocol and len(without_protocol) > 0)

    def _validate_model_name(self, model: str) -> bool:
        """
        Validate model name is reasonable.

        Args:
            model: Model name to validate

        Returns:
            True if valid, False otherwise
        """
        if not model:
            return False
        # Check for suspicious content (like bash commands or comments)
        suspicious_patterns = ["#", "$", "&&", "||", ";", "\n", "echo", "rm ", "curl"]
        return not any(pattern in model for pattern in suspicious_patterns)

    def _validate_api_key(self, api_key: str) -> bool:
        """
        Validate API key format.

        Args:
            api_key: API key to validate

        Returns:
            True if valid, False otherwise
        """
        if not api_key:
            return False
        # Check for reasonable length and no suspicious content
        suspicious_patterns = ["#", "\n", "echo", "$", "&&"]
        return len(api_key) > 10 and not any(
            pattern in api_key for pattern in suspicious_patterns
        )

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Configuration dictionary
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)

                # Validate the loaded config
                if not self._validate_config(config):
                    print(
                        "⚠ Warning: Configuration file appears to be corrupted or invalid."
                    )
                    print(f"   Config file: {self.config_file}")
                    print("   Please run 'ekko --setup' to reconfigure.\n")
                    sys.exit(1)

                return config
            except json.JSONDecodeError:
                print("⚠ Error: Configuration file is not valid JSON.")
                print(f"   Config file: {self.config_file}")
                print("   Please run 'ekko --setup' to reconfigure.\n")
                sys.exit(1)
        return self.default_config()

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration structure and content.

        Args:
            config: Configuration dictionary

        Returns:
            True if valid, False otherwise
        """
        # Check for required keys
        required_keys = [
            "provider",
            "ollama_url",
            "ollama_model",
            "anthropic_model",
            "system_prompt",
        ]
        if not all(key in config for key in required_keys):
            return False

        # Validate provider-specific settings
        provider = config.get("provider", "")
        if provider not in PROVIDERS:
            print(f"⚠ Invalid provider in config: '{provider}'")
            return False

        # Get provider class and validate
        provider_class = PROVIDERS[provider]
        is_valid, error_msg = provider_class.validate_config(config)
        if not is_valid:
            print(f"⚠ {error_msg}")
            return False

        return True

    def default_config(self) -> Dict[str, Any]:
        """
        Return default configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            "provider": "ollama",  # "anthropic" or "ollama"
            "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "anthropic_model": "claude-sonnet-4-5-20250929",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "qwen3-coder",
            "system_prompt": "You are a shell expert. Output ONLY the command to solve the problem. No explanation, no markdown, no backticks - just the raw shell command.",
        }

    def save_config(self):
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def setup_wizard(self):
        """Run interactive setup wizard."""
        print("🔧 ekko setup wizard\n")

        # Provider selection - use explicit ordering
        print("Choose your AI provider:")
        print("1. Ollama (local, free)")
        print("2. Anthropic API (requires API key)")
        choice = self._get_input("Enter choice [1]: ") or "1"

        if choice == "2":
            self.config["provider"] = "anthropic"

            # Get and validate API key
            while True:
                api_key = self._get_input("Enter Anthropic API key: ")
                if self._validate_api_key(api_key):
                    self.config["anthropic_api_key"] = api_key
                    break
                else:
                    print("⚠ Invalid API key format. Please enter a valid Anthropic API key.")

            # Get model name (with validation)
            model = self._get_input(f"Model [{self.config['anthropic_model']}]: ")
            if model:
                if self._validate_model_name(model):
                    self.config["anthropic_model"] = model
                else:
                    print(
                        f"⚠ Invalid model name, using default: {self.config['anthropic_model']}"
                    )
        else:
            self.config["provider"] = "ollama"

            # Get and validate Ollama URL
            while True:
                url = self._get_input(f"Ollama URL [{self.config['ollama_url']}]: ")
                if not url:
                    # User pressed enter, use default
                    break
                if self._validate_url(url):
                    self.config["ollama_url"] = url
                    break
                else:
                    print(
                        "⚠ Invalid URL format. Please enter a valid URL (e.g., http://localhost:11434)"
                    )

            # Get and validate model name
            model = self._get_input(f"Model [{self.config['ollama_model']}]: ")
            if model:
                if self._validate_model_name(model):
                    self.config["ollama_model"] = model
                else:
                    print(
                        f"⚠ Invalid model name, using default: {self.config['ollama_model']}"
                    )

        self.save_config()
        print(f"\n✓ Configuration saved to {self.config_file}")
        print("\nTo use: ekko find all files over 500MB")

    def switch_provider(self, provider_name: str):
        """
        Switch to a different provider.

        Args:
            provider_name: Name of provider to switch to
        """
        # Normalize provider name
        provider_name = provider_name.lower()

        # Validate provider name
        if provider_name not in PROVIDERS:
            available = ", ".join(PROVIDERS.keys())
            print(f"⚠ Invalid provider: '{provider_name}'")
            print(f"   Valid providers: {available}")
            sys.exit(1)

        # Check if provider is configured
        provider_class = PROVIDERS[provider_name]
        is_valid, error_msg = provider_class.validate_config(self.config)
        if not is_valid:
            print(f"⚠ {provider_name.capitalize()} not configured.")
            print("   Run: ekko --setup")
            sys.exit(1)

        # Switch provider
        self.config["provider"] = provider_name
        self.save_config()

        # Show confirmation
        model = self.config.get(f"{provider_name}_model", "")
        print(f"✓ Switched to {provider_name} ({model})")

    def switch_model(self, model_name: str):
        """
        Switch model for the current provider.

        Args:
            model_name: Name of model to switch to
        """
        # Validate model name
        if not self._validate_model_name(model_name):
            print(f"⚠ Invalid model name: '{model_name}'")
            sys.exit(1)

        # Get current provider
        provider = self.config.get("provider", "ollama")

        # Update the appropriate model field
        model_key = f"{provider}_model"
        self.config[model_key] = model_name
        self.save_config()

        print(f"✓ Changed {provider} model to {model_name}")

    def show_config(self):
        """Display current configuration with masked sensitive data."""
        provider = self.config.get("provider", "ollama")

        print("\n🔧 ekko configuration\n")
        print(f"Config file: {self.config_file}\n")

        # Show active provider
        if provider == "anthropic":
            model = self.config.get("anthropic_model", "")
            print(f"✓ Active: anthropic ({model})")
        else:
            model = self.config.get("ollama_model", "")
            url = self.config.get("ollama_url", "")
            print(f"✓ Active: ollama ({model})")
            print(f"  URL: {url}")

        print()

        # Show other configured providers
        if provider == "anthropic":
            # Show Ollama if configured
            ollama_url = self.config.get("ollama_url", "")
            ollama_model = self.config.get("ollama_model", "")
            if ollama_url and self._validate_url(ollama_url):
                print(f"○ Available: ollama ({ollama_model})")
                print(f"  URL: {ollama_url}")
            else:
                print("○ Not configured: ollama")
                print("  Run: ekko --setup")
        else:
            # Show Anthropic if configured
            api_key = self.config.get("anthropic_api_key", "")
            anthropic_model = self.config.get("anthropic_model", "")
            if api_key and self._validate_api_key(api_key):
                # Mask API key - show only last 4 characters
                masked_key = "sk-ant-..." + api_key[-4:] if len(api_key) > 4 else "***"
                print(f"○ Available: anthropic ({anthropic_model})")
                print(f"  API Key: {masked_key}")
            else:
                print("○ Not configured: anthropic")
                print("  Run: ekko --setup")

        print()
