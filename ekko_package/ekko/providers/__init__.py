"""
Provider implementations for ekko
"""

from ekko.providers.base import LLMProvider
from ekko.providers.anthropic import AnthropicProvider
from ekko.providers.ollama import OllamaProvider

__all__ = ["LLMProvider", "AnthropicProvider", "OllamaProvider"]

# Provider registry for auto-discovery
PROVIDERS = {
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
}


def get_provider(provider_name: str, **kwargs):
    """
    Factory function to get a provider instance.

    Args:
        provider_name: Name of the provider (e.g., "anthropic", "ollama")
        **kwargs: Provider-specific configuration

    Returns:
        Provider instance

    Raises:
        ValueError: If provider is not found
    """
    provider_class = PROVIDERS.get(provider_name.lower())
    if not provider_class:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(
            f"Unknown provider '{provider_name}'. Available: {available}"
        )
    return provider_class(**kwargs)
