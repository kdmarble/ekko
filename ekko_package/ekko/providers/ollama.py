"""
Ollama local provider integration
"""

import sys

import requests

from ekko.providers.base import LLMProvider


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
            error_msg += f"  - Verify the model '{self.model}' is installed: ollama list\n"
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
