"""
Base provider interface for LLM integrations
"""

from abc import ABC, abstractmethod


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
