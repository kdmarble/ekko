# Contributing to ekko

Thank you for your interest in contributing to ekko! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Architecture Overview](#architecture-overview)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [CLI Development with Typer](#cli-development-with-typer)
- [Rich Terminal Output](#rich-terminal-output)
- [Adding New AI Providers](#adding-new-ai-providers)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Coding Guidelines](#coding-guidelines)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, AI provider)
- **Error messages** or logs if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Clear use case** - Why is this enhancement needed?
- **Proposed solution** - How would it work?
- **Alternatives considered** - What other approaches did you think about?

### Pull Requests

We actively welcome your pull requests! Areas we'd love help with:

- Additional AI provider integrations (OpenAI, Google Gemini, etc.)
- Enhanced command parsing and validation
- Platform compatibility improvements (Linux, macOS)
- Documentation improvements
- Bug fixes
- Test coverage
- Shell completion support

## Architecture Overview

ekko is distributed as a **Python package** with a modular, well-organized structure.

### Directory Structure

```
ekko/
├── ekko_package/          # Python package source
│   ├── ekko/
│   │   ├── __init__.py
│   │   ├── cli.py          # Typer-based CLI interface
│   │   ├── config.py       # Configuration management
│   │   ├── generator.py    # Command generation logic
│   │   └── providers/      # Provider implementations
│   │       ├── __init__.py # Provider registry
│   │       ├── base.py     # Base provider interface
│   │       ├── anthropic.py
│   │       └── ollama.py
│   ├── setup.py            # Package setup
│   └── pyproject.toml      # Modern packaging config
├── install-ekko.sh         # pipx-based installer
├── tests/                  # Test suite
├── Makefile                # Development commands
└── providers/              # Provider documentation
```

### Key Technologies

- **Typer**: Modern CLI framework with automatic help generation
- **Rich**: Beautiful terminal output with tables, panels, and colors
- **Provider System**: Pluggable architecture for AI providers

### Architecture Decisions

**Why Typer?**
- Automatic help generation
- Type hints for validation
- Built-in Rich support
- Less boilerplate than argparse
- Better developer experience

**Why Package-Only Distribution?**
- **Simplified**: One distribution method
- **Dependencies**: Typer and Rich require proper package management
- **Portability**: pipx provides isolated, portable installs
- **Standards**: Follows Python packaging best practices
- **Maintenance**: Easier to maintain

**Why Flag-Based Commands?**

The main use case is natural language prompts:
```bash
ekko find all files over 500MB
```

Using subcommands would conflict:
```bash
ekko find setup  # Ambiguous - is "find" a command or part of prompt?
```

Flags make it clear:
```bash
ekko --setup  # Unambiguous special command
ekko find files named setup  # Natural language prompt
```

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/ekko.git
cd ekko
```

### 2. Install in Editable Mode

```bash
# Using make
make install

# Or manually
cd ekko_package && pip install -e .
```

This installs ekko with all dependencies (typer, rich, requests) in development mode.

### 3. Verify Installation

```bash
ekko --version  # Should show v1.3.0
ekko --help     # Should show help with Rich formatting
```

## Development Workflow

### 1. Making Changes

Work in the package source:

```bash
cd ekko_package/ekko/
# Edit files
vim cli.py
vim config.py
vim providers/anthropic.py
```

### 2. Testing Changes

```bash
# Run all tests
make test

# Or run individual test files
python3 tests/test_setup_wizard.py
python3 tests/test_piped_installation.py
python3 tests/test_provider_switching.py
python3 tests/test_upgrade_compatibility.py
```

### 3. Code Quality

```bash
make format  # Format with black
make lint    # Lint with flake8
```

### 4. Building Package

```bash
make package  # Creates distributable package in ekko_package/dist/
```

## CLI Development with Typer

ekko uses Typer for the command-line interface. Here's how to work with it:

### Basic Structure (cli.py)

```python
import typer
from rich.console import Console

app = typer.Typer(
    name="ekko",
    help="AI-powered command line assistant",
    add_completion=False,
)

console = Console()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    prompt: Optional[List[str]] = typer.Argument(None),
    setup: bool = typer.Option(False, "--setup", help="Run setup wizard"),
):
    """Main ekko command."""
    # Implementation
    pass
```

### Adding New Options

```python
@app.callback(invoke_without_command=True)
def main(
    # ... existing parameters ...
    new_option: str = typer.Option(None, "--new", help="New option description"),
):
    if new_option:
        # Handle new option
        console.print(f"New option value: {new_option}")
        return
```

### Typer Resources

- [Typer Documentation](https://typer.tiangolo.com/)
- [Typer Tutorial](https://typer.tiangolo.com/tutorial/)
- [Click Documentation](https://click.palletsprojects.com/) (Typer is built on Click)

## Rich Terminal Output

ekko uses Rich for beautiful terminal output. Key patterns:

### Console Output

```python
from rich.console import Console

console = Console()

# Colored output
console.print("[cyan]Command[/cyan]")
console.print("[green]✓[/green] Success")
console.print("[red]Error:[/red] Something went wrong")

# Dimmed text
console.print("[dim]Additional info[/dim]")
```

### Tables

```python
from rich.table import Table

table = Table(
    title="Configuration",
    show_header=True,
    header_style="bold cyan",
    border_style="dim"
)

table.add_column("Provider", style="cyan")
table.add_column("Status", style="green")
table.add_row("anthropic", "✓ Active")

console.print(table)
```

### Panels

```python
from rich.panel import Panel

panel = Panel(
    "Important message",
    title="Title",
    border_style="blue"
)

console.print(panel)
```

### Input

```python
# Simple input with styling
user_input = console.input("[dim]Prompt: [/dim]")

# Or use Rich's Prompt
from rich.prompt import Prompt

value = Prompt.ask("Enter value")
confirmed = Prompt.ask("Continue?", choices=["y", "n"])
```

### Rich Resources

- [Rich Documentation](https://rich.readthedocs.io/)
- [Rich Examples](https://github.com/Textualize/rich#rich-library)

## Adding New AI Providers

Adding a new AI provider is straightforward thanks to our modular architecture.

### Step 1: Create Provider Module

Create `ekko_package/ekko/providers/newprovider.py`:

```python
"""
New Provider integration
"""

import sys
import requests
from ekko.providers.base import LLMProvider


class NewProviderProvider(LLMProvider):
    """New Provider API integration."""

    def __init__(self, api_key: str, model: str = "default-model"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.newprovider.com/v1/generate"

    def generate(self, prompt: str, system_prompt: str) -> str:
        """
        Generate command using New Provider API.

        Args:
            prompt: User's natural language request
            system_prompt: System context/instructions

        Returns:
            Generated shell command as string

        Raises:
            SystemExit: If API call fails
        """
        try:
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            print(f"Error calling New Provider API: {e}")
            sys.exit(1)

    def validate(self) -> bool:
        """
        Validate provider configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        # Test API connectivity
        try:
            response = requests.get(
                "https://api.newprovider.com/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
```

### Step 2: Register Provider

Add to `ekko_package/ekko/providers/__init__.py`:

```python
from ekko.providers.base import LLMProvider
from ekko.providers.anthropic import AnthropicProvider
from ekko.providers.ollama import OllamaProvider
from ekko.providers.newprovider import NewProviderProvider  # Add this

PROVIDERS = {
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
    "newprovider": NewProviderProvider,  # Add this
}
```

### Step 3: Update Configuration

Add setup wizard support in `ekko_package/ekko/config.py`:

```python
def setup_wizard(self):
    """Interactive configuration wizard."""
    # ... existing code ...

    # Add new provider option
    print("\nAvailable providers:")
    print("1. Anthropic API (Best quality)")
    print("2. Ollama (Best privacy)")
    print("3. New Provider (Your description)")  # Add this
```

### Step 4: Test Your Provider

```python
# Test provider import and initialization
python3 -c "from ekko.providers import get_provider; \
    p = get_provider('newprovider', api_key='test-key'); \
    print(p.generate('list files', 'Generate shell commands'))"
```

### Step 5: Documentation

Add provider documentation in `providers/newprovider.md` with:
- Setup instructions
- Model options
- API key acquisition
- Example usage
- Troubleshooting

## Testing

ekko has a comprehensive automated test suite using `pexpect` for interactive testing.

### Running the Test Suite

```bash
# Run all tests
make test

# Or run individual tests
python3 tests/test_setup_wizard.py
python3 tests/test_piped_installation.py
python3 tests/test_provider_switching.py
python3 tests/test_upgrade_compatibility.py
```

### Test Structure

**`tests/test_setup_wizard.py`** - Interactive setup wizard tests:
- Valid configurations (Ollama and Anthropic)
- Input validation (URLs, models, API keys)
- Corrupted config detection
- Error handling and user feedback

**`tests/test_piped_installation.py`** - Installation scenario tests:
- Piped installation (`curl ... | bash`)
- TTY input redirection
- End-to-end installation workflow

**`tests/test_provider_switching.py`** - Provider switching tests:
- `--switch` command functionality
- `--model` command functionality
- `--use` command functionality
- Configuration persistence

**`tests/test_upgrade_compatibility.py`** - Upgrade tests:
- Config migration from older versions
- Backward compatibility

### Writing New Tests

When adding new features, include tests that:

1. **Test the happy path** - Verify normal operation
2. **Test edge cases** - Invalid inputs, missing data, etc.
3. **Test error handling** - Ensure helpful error messages
4. **Test user interactions** - Use `pexpect` for interactive workflows

Example test structure:

```python
import pexpect
import sys

def test_new_feature():
    """Test description."""
    child = pexpect.spawn(
        "ekko --new-flag",
        encoding="utf-8",
        timeout=5
    )

    try:
        # Expect output
        child.expect("Expected prompt")

        # Send input
        child.sendline("user input")

        # Verify result
        child.expect("Expected output")
        child.expect(pexpect.EOF)

        print("✓ Test passed")
    finally:
        child.close()

if __name__ == "__main__":
    test_new_feature()
```

### Why We Use `pexpect`

We use `pexpect` for testing because:
- **Interactive testing**: Tests real user interactions with the CLI
- **TTY simulation**: Validates input/output behavior in terminal environments
- **Bug prevention**: Catches edge cases in interactive workflows
- **Real-world scenarios**: Tests actual installation and setup workflows

### Test Coverage Goals

We aim to maintain:
- ✅ **100% of critical paths** tested (setup, config, installation)
- ✅ **All validation functions** tested with valid and invalid inputs
- ✅ **Error handling** tested with helpful error messages
- ✅ **Installation scenarios** tested (piped, interactive, etc.)

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Follow the [coding guidelines](#coding-guidelines)
- Add tests for new features or bug fixes
- Update documentation as needed
- Use Rich for any terminal output
- Use Typer for CLI changes

### 3. Test Your Changes

```bash
make test    # Run all tests
make lint    # Check code style
make format  # Format code
```

### 4. Commit with Clear Messages

```bash
git commit -m "Add feature: brief description"
```

Follow this commit message format:
- `Add feature: description` - New functionality
- `Fix: description` - Bug fixes
- `Update: description` - Changes to existing features
- `Docs: description` - Documentation only
- `Refactor: description` - Code refactoring

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Open a Pull Request

- Provide a clear title and description
- Reference any related issues
- Explain what changes were made and why
- Include screenshots for UI changes (Rich output)

### Test Checklist

Before submitting a PR, verify:

- [ ] All automated tests pass (`make test`)
- [ ] Code formatting passes (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Added tests for new features or bug fixes
- [ ] Manual testing in local environment
- [ ] Documentation updated if needed
- [ ] No breaking changes (or clearly documented)
- [ ] Rich output looks good in terminal
- [ ] Typer help text is clear and helpful

## Coding Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use `black` for formatting (max line length: 100)
- Use `flake8` for linting
- Write clear, descriptive variable and function names
- Add type hints where appropriate

### Code Organization

```python
# Good
def clean_command(self, cmd: str) -> str:
    """Strip markdown and formatting artifacts from command output."""
    # Remove markdown code blocks
    cmd = re.sub(r'```[a-z]*\n?', '', cmd)
    return cmd.strip()

# Avoid
def cc(self, c):  # Unclear names, no docstring
    return c.strip()
```

### Imports

Group imports in this order:
1. Standard library
2. Third-party packages
3. Local modules

```python
import os
import sys
from typing import Optional, Dict

import typer
from rich.console import Console

from ekko.config import Config
from ekko.providers import get_provider
```

### Documentation

- Add docstrings to all public functions and classes (Google style)
- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update CHANGELOG.md for all changes

Example docstring:

```python
def my_function(param: str, optional: Optional[int] = None) -> Dict[str, str]:
    """
    Short description of function.

    Args:
        param: Description of param
        optional: Description of optional param

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

### Error Handling

- Provide clear error messages
- Handle exceptions gracefully
- Print helpful guidance to users
- Use Rich for formatted error output

```python
# Good
from rich.console import Console

console = Console()

try:
    response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    console.print(f"[red]Error connecting to API:[/red] {e}")
    console.print("[yellow]Check your internet connection and API key[/yellow]")
    sys.exit(1)
```

### Terminal Output

- Use Rich Console for all output
- Use appropriate colors and styles
- Keep output concise and readable
- Use tables for structured data
- Use panels for important messages

```python
from rich.console import Console
from rich.table import Table

console = Console()

# Good
console.print("[green]✓[/green] Configuration saved")
console.print(f"[cyan]{command}[/cyan]")

# Avoid raw print
print("Configuration saved")  # No formatting
print(f"\033[36m{command}\033[0m")  # Raw ANSI codes
```

## Questions?

- Open an issue for questions
- Tag with `question` label
- Check existing issues and discussions
- We're happy to help!

## Resources

- **Typer**: https://typer.tiangolo.com/
- **Rich**: https://rich.readthedocs.io/
- **pexpect**: https://pexpect.readthedocs.io/

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to ekko! 🎉
