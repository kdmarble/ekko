#!/usr/bin/env python3
"""
ekko - AI-powered command line assistant
Supports Anthropic API and Ollama
"""

import sys
import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, Any
from abc import ABC, abstractmethod

try:
    import requests
except ImportError:
    print("Error: requests module not found. Install with: pip install requests")
    sys.exit(1)

# ============================================================================
# Base Provider Interface
# ============================================================================

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All provider implementations must inherit from this class and implement
    the generate() method.
    """

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str) -> str:
        """
        Generate a command from a natural language prompt.

        Args:
            prompt: The user's natural language request
            system_prompt: System instructions for the model

        Returns:
            Generated shell command as a string

        Raises:
            Exception: Provider-specific errors should be caught and
                      converted to user-friendly messages with sys.exit(1)
        """
        raise NotImplementedError

    @classmethod
    def get_config_keys(cls) -> list:
        """
        Return list of configuration keys needed for this provider.

        Returns:
            List of configuration key names
        """
        return []

    @classmethod
    def validate_config(cls, config: dict) -> tuple:
        """
        Validate provider-specific configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (is_valid: bool, error_message: str or None)
        """
        return True, None

# ============================================================================
# Anthropic Provider
# ============================================================================

class AnthropicProvider(LLMProvider):
    """
    Provider for Anthropic's Claude models via their API.

    Supports all Claude models through the Anthropic API.
    """

    def __init__(self, api_key: str, model: str):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (starts with 'sk-ant-')
            model: Model identifier (e.g., 'claude-sonnet-4-5-20250929')
        """
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"

    def generate(self, prompt: str, system_prompt: str) -> str:
        """Generate command using Anthropic API."""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        data = {
            "model": self.model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=data, timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Anthropic API: {str(e)}\n"
            error_msg += "Possible fixes:\n"
            error_msg += "  - Check your API key is valid\n"
            error_msg += "  - Verify your internet connection\n"
            error_msg += "  - Run 'ekko --setup' to reconfigure\n"
            print(error_msg)
            sys.exit(1)

    @classmethod
    def get_config_keys(cls) -> list:
        """Return configuration keys needed for Anthropic."""
        return ["anthropic_api_key", "anthropic_model"]

    @classmethod
    def validate_config(cls, config: dict) -> tuple:
        """Validate Anthropic configuration."""
        api_key = config.get("anthropic_api_key", "")
        model = config.get("anthropic_model", "")

        # Validate API key
        if not api_key or len(api_key) < 10:
            return False, "Invalid or missing Anthropic API key"

        # Check for suspicious patterns
        suspicious = ["#", "\n", "echo", "$", "&&"]
        if any(pattern in api_key for pattern in suspicious):
            return False, "Invalid Anthropic API key format"

        # Validate model name
        if not model:
            return False, "Missing Anthropic model name"

        if any(pattern in model for pattern in suspicious):
            return False, f"Invalid Anthropic model name: '{model}'"

        return True, None

# ============================================================================
# Ollama Provider
# ============================================================================

class OllamaProvider(LLMProvider):
    """
    Provider for local Ollama models.

    Ollama allows running open-source LLMs locally for complete privacy.
    """

    def __init__(self, url: str, model: str):
        """
        Initialize Ollama provider.

        Args:
            url: Ollama API URL (e.g., 'http://localhost:11434')
            model: Model name (e.g., 'qwen3-coder', 'llama3.2')
        """
        self.url = url.rstrip("/")
        self.model = model

    def generate(self, prompt: str, system_prompt: str) -> str:
        """Generate command using Ollama."""
        api_url = f"{self.url}/api/generate"

        data = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
        }

        try:
            response = requests.post(api_url, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["response"]
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Ollama: {str(e)}\n"
            error_msg += "Possible fixes:\n"
            error_msg += f"  - Check Ollama is running at {self.url}\n"
            error_msg += (
                f"  - Verify the model '{self.model}' is installed: ollama list\n"
            )
            error_msg += "  - Check the Ollama URL is correct\n"
            error_msg += "  - Run 'ekko --setup' to reconfigure\n"
            print(error_msg)
            sys.exit(1)

    @classmethod
    def get_config_keys(cls) -> list:
        """Return configuration keys needed for Ollama."""
        return ["ollama_url", "ollama_model"]

    @classmethod
    def validate_config(cls, config: dict) -> tuple:
        """Validate Ollama configuration."""
        url = config.get("ollama_url", "")
        model = config.get("ollama_model", "")

        # Validate URL
        if not url:
            return False, "Missing Ollama URL"

        if not url.startswith(("http://", "https://")):
            return False, f"Invalid Ollama URL format: '{url}'"

        # Basic validation for domain/host
        without_protocol = url.split("://", 1)[1] if "://" in url else ""
        if not without_protocol:
            return False, f"Invalid Ollama URL: '{url}'"

        # Validate model name
        if not model:
            return False, "Missing Ollama model name"

        # Check for suspicious patterns
        suspicious = ["#", "$", "&&", "||", ";", "\n", "echo", "rm ", "curl"]
        if any(pattern in model for pattern in suspicious):
            return False, f"Invalid Ollama model name: '{model}'"

        return True, None

# ============================================================================
# Provider Registry
# ============================================================================

PROVIDERS = {
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
}

def get_provider(provider_name: str, **kwargs):
    """Get a provider instance by name."""
    provider_class = PROVIDERS.get(provider_name.lower())
    if not provider_class:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(
            f"Unknown provider '{provider_name}'. Available: {available}"
        )
    return provider_class(**kwargs)

# ============================================================================
# Configuration Management
# ============================================================================

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
                    print(
                        "⚠ Invalid API key format. Please enter a valid Anthropic API key."
                    )

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

# ============================================================================
# Command Generator
# ============================================================================

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
            return get_provider(
                "anthropic", api_key=api_key, model=self.config["anthropic_model"]
            )

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
            print(f"\n\033[36m{cmd}\033[0m")

            # Get user input
            try:
                user_input = input(
                    "\033[90m[enter=run, n=cancel, or describe what's wrong]: \033[0m"
                )
            except (KeyboardInterrupt, EOFError):
                print()
                return

            # Handle response
            if not user_input or user_input.lower() in ["y", "yes"]:
                # Run command
                try:
                    subprocess.run(cmd, shell=True)
                except KeyboardInterrupt:
                    print()
                return

            elif user_input.lower() in ["n", "no", "q", "quit"]:
                # Cancel
                return

            else:
                # Correction - loop with feedback
                prompt = f"Original: '{original_prompt}'. Previous: '{cmd}'. Issue: {user_input}. Generate corrected command."
                print("\033[90m↻ revising...\033[0m")

# ============================================================================
# Command Line Interface
# ============================================================================

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
            print("ekko v1.2.0")
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
