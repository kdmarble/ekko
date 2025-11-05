# Provider Plugin System

This directory contains documentation and examples for extending ekko with additional AI provider integrations.

## Overview

ekko uses a provider plugin architecture that makes it easy to add support for new AI services. Providers implement a simple interface defined in the main `ekko.py` file.

## Current Providers

- **Anthropic** - Claude models via Anthropic API
- **Ollama** - Local models via Ollama

## Planned Providers

- **OpenAI** - GPT models via OpenAI API
- **Google Gemini** - Gemini models via Google AI API
- **Cohere** - Command models via Cohere API
- **Azure OpenAI** - Azure-hosted OpenAI models
- **Local Python** - Direct integration with local LLM libraries

## Provider Interface

All providers must implement the `LLMProvider` base class:

```python
class LLMProvider:
    """Base class for LLM providers"""

    def generate(self, prompt: str, system_prompt: str) -> str:
        """
        Generate a command from a natural language prompt.

        Args:
            prompt: The user's natural language request
            system_prompt: System instructions for the model

        Returns:
            Generated shell command as a string

        Raises:
            Should handle errors gracefully and exit with helpful messages
        """
        raise NotImplementedError
```

## Adding a New Provider

### 1. Create Provider Class

Add your provider class to `ekko.py`:

```python
class NewProviderProvider(LLMProvider):
    """Integration for New Provider API"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.newprovider.com/v1/generate"

    def generate(self, prompt: str, system_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "max_tokens": 1024
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["output"]
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to New Provider: {str(e)}\n"
            error_msg += "Possible fixes:\n"
            error_msg += "  - Check your API key is valid\n"
            error_msg += "  - Verify your internet connection\n"
            error_msg += "  - Run 'ekko --setup' to reconfigure\n"
            print(error_msg)
            sys.exit(1)
```

### 2. Update Config Class

Add configuration support in the `Config` class:

#### In `default_config()`:
```python
def default_config(self) -> Dict[str, Any]:
    return {
        "provider": "ollama",
        "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "anthropic_model": "claude-sonnet-4-5-20250929",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "qwen3-coder",
        "newprovider_api_key": "",  # Add this
        "newprovider_model": "default-model",  # Add this
        "system_prompt": "..."
    }
```

#### In `setup_wizard()`:
```python
print("Choose your AI provider:")
print("1. Ollama (local, free)")
print("2. Anthropic API (requires API key)")
print("3. New Provider (requires API key)")  # Add this
choice = self._get_input("Enter choice [1]: ") or "1"

# Add new provider setup
if choice == "3":
    self.config["provider"] = "newprovider"
    api_key = self._get_input("Enter New Provider API key: ")
    if self._validate_api_key(api_key):
        self.config["newprovider_api_key"] = api_key
    model = self._get_input(f"Model [{self.config['newprovider_model']}]: ")
    if model and self._validate_model_name(model):
        self.config["newprovider_model"] = model
```

#### In `_validate_config()`:
```python
elif provider == "newprovider":
    api_key = config.get("newprovider_api_key", "")
    if not self._validate_api_key(api_key):
        print(f"⚠ Invalid New Provider API key in config")
        return False
    model = config.get("newprovider_model", "")
    if not self._validate_model_name(model):
        print(f"⚠ Invalid New Provider model name in config: '{model}'")
        return False
```

#### In `switch_provider()`:
```python
valid_providers = ["ollama", "anthropic", "newprovider"]  # Add here

if provider_name == "newprovider":
    api_key = self.config.get("newprovider_api_key", "")
    if not api_key or not self._validate_api_key(api_key):
        print(f"⚠ New Provider not configured.")
        print(f"   Run: ekko --setup")
        sys.exit(1)
```

#### In `show_config()`:
```python
# Add display logic for your provider
if provider == "newprovider":
    model = self.config.get("newprovider_model", "")
    print(f"✓ Active: newprovider ({model})")
```

### 3. Update CommandGenerator

Add provider instantiation in `_get_provider()`:

```python
def _get_provider(self) -> LLMProvider:
    provider_type = self.config["provider"]

    if provider_type == "anthropic":
        # ... existing code ...
    elif provider_type == "ollama":
        # ... existing code ...
    elif provider_type == "newprovider":
        api_key = self.config.get("newprovider_api_key")
        if not api_key:
            print("Error: New Provider API key not configured. Run: ekko --setup")
            sys.exit(1)
        return NewProviderProvider(api_key, self.config["newprovider_model"])
    else:
        print(f"Error: Unknown provider '{provider_type}'")
        sys.exit(1)
```

### 4. Update Documentation

- Add provider to README.md
- Update CONTRIBUTING.md with provider info
- Document any provider-specific setup steps
- Add to CHANGELOG.md

### 5. Add Tests

Create tests for your provider:
- Configuration validation
- Provider switching
- Error handling
- API integration (if possible with mocking)

## Provider Guidelines

### Error Handling

- Always catch `requests.exceptions.RequestException`
- Provide clear, actionable error messages
- Suggest running `ekko --setup` to reconfigure
- Include relevant troubleshooting steps

### API Keys

- Store API keys in config file
- Validate API key format in `_validate_api_key()`
- Mask API keys in `show_config()` output
- Support environment variables for initial setup

### Models

- Provide sensible default model
- Validate model names to prevent injection
- Document recommended models in README
- Allow easy model switching with `--model`

### Response Parsing

- Clean up markdown formatting (backticks, code blocks)
- Extract only the command, not explanations
- Handle multi-line responses appropriately
- Use the `clean_command()` helper method

### Timeouts

- Use reasonable timeouts (30-60 seconds)
- Consider model size and response time
- Provide feedback during long operations

## Example Pull Request Checklist

When submitting a new provider:

- [ ] Provider class implements `LLMProvider` interface
- [ ] Configuration support added to `Config` class
- [ ] Setup wizard updated with new provider option
- [ ] Validation functions handle new provider
- [ ] Provider switching works correctly
- [ ] Error handling with helpful messages
- [ ] API keys masked in config display
- [ ] Documentation updated (README, CONTRIBUTING)
- [ ] Tests added for new provider
- [ ] CHANGELOG.md updated
- [ ] Works on both Linux and macOS
- [ ] Tested with actual API credentials

## Questions?

Open an issue or discussion on GitHub if you need help adding a new provider. We're happy to assist!

## Future Improvements

- Plugin loading from external files
- Provider discovery mechanism
- Provider-specific configuration validation schemas
- Shared authentication helpers
- Rate limiting and retry logic
- Response caching
- Provider health checks
