"""
Anthropic API provider integration
"""

import sys

import requests

from ekko.providers.base import LLMProvider


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
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
        except requests.exceptions.RequestException as e:
            # Don't log the full exception as it may contain sensitive request details
            error_type = type(e).__name__
            error_msg = f"Error connecting to Anthropic API: {error_type}\n"
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
