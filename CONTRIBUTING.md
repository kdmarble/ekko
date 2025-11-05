# Contributing to ekko

Thank you for your interest in contributing to ekko! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Guidelines](#coding-guidelines)
- [Testing](#testing)

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

## Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/ekko.git
cd ekko
```

2. **Install development dependencies**

```bash
pip install requests black flake8 --user
```

3. **Test locally without installing**

```bash
chmod +x ekko.py
./ekko.py --help
```

4. **Or use the demo script**

```bash
bash demo.sh
```

5. **Run the Makefile commands**

```bash
make help      # See all available commands
make test      # Run basic tests
make format    # Format code with black
make lint      # Lint code with flake8
```

## Pull Request Process

1. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Follow the [coding guidelines](#coding-guidelines)
   - Add tests if applicable
   - Update documentation as needed

3. **Test your changes**

```bash
make test
make lint
```

4. **Commit with clear messages**

```bash
git commit -m "Add feature: brief description"
```

Follow this commit message format:
- `Add feature: description` - New functionality
- `Fix: description` - Bug fixes
- `Update: description` - Changes to existing features
- `Docs: description` - Documentation only
- `Refactor: description` - Code refactoring

5. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

6. **Open a Pull Request**
   - Provide a clear title and description
   - Reference any related issues
   - Explain what changes were made and why

## Coding Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use `black` for formatting (max line length: 100)
- Use `flake8` for linting
- Write clear, descriptive variable and function names

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

### Documentation

- Add docstrings to all public functions and classes
- Update README.md for user-facing changes
- Add inline comments for complex logic

### Error Handling

- Provide clear error messages
- Handle exceptions gracefully
- Print helpful guidance to users

```python
# Good
try:
    response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error connecting to API: {e}")
    print("Check your internet connection and API key")
    return None
```

## Testing

ekko has a comprehensive automated test suite using `pexpect` for interactive testing. We encourage adding tests for all new features and bug fixes.

### Running the Test Suite

```bash
# Setup test environment (one time)
python3 -m venv .venv
source .venv/bin/activate
pip install pexpect requests

# Run all tests
python3 tests/test_setup_wizard.py      # 7 interactive setup tests
python3 tests/test_piped_installation.py # 2 installation tests

# Expected output: 9/9 tests passing (100%)
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

### Writing New Tests

When adding new features, include tests that:

1. **Test the happy path** - Verify normal operation
2. **Test edge cases** - Invalid inputs, missing data, etc.
3. **Test error handling** - Ensure helpful error messages
4. **Test user interactions** - Use `pexpect` for interactive workflows

Example test structure:

```python
def test_your_feature(self):
    """Test description"""
    config_dir = self.setup_test_env()

    env = os.environ.copy()
    env['HOME'] = self.test_dir

    # Spawn interactive process
    child = pexpect.spawn(
        'python3', ['ekko.py', '--your-flag'],
        env=env,
        timeout=10
    )

    try:
        # Test interactions
        child.expect('Expected prompt:')
        child.sendline('user input')

        # Verify behavior
        child.expect('Expected output')
        child.expect(pexpect.EOF, timeout=2)

        # Assert results
        assert config_file.exists(), "Config should exist"

    finally:
        child.close()
        self.cleanup_test_env()
```

### Manual Testing

Test your changes across different scenarios:

1. **Different AI providers**
   - Anthropic API
   - Ollama (multiple models)

2. **Different platforms**
   - Linux (various distributions)
   - macOS

3. **Different shell commands**
   - File operations
   - Network commands
   - Git operations
   - Process management

### Test Checklist

Before submitting a PR, verify:

- [ ] All automated tests pass (`tests/test_*.py`)
- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] Added tests for new features or bug fixes
- [ ] Manual testing in local environment
- [ ] Documentation updated if needed
- [ ] No breaking changes (or clearly documented)

### Why We Use `pexpect`

We use `pexpect` for testing because:
- **Interactive testing**: Tests real user interactions with the CLI
- **TTY simulation**: Validates input/output behavior in terminal environments
- **Bug prevention**: Caught the critical piped installation bug
- **Real-world scenarios**: Tests actual installation and setup workflows

### Test Coverage Goals

We aim to maintain:
- ✅ **100% of critical paths** tested (setup, config, installation)
- ✅ **All validation functions** tested with valid and invalid inputs
- ✅ **Error handling** tested with helpful error messages
- ✅ **Installation scenarios** tested (piped, interactive, etc.)

## Adding New AI Providers

Want to add support for a new AI provider? Here's the pattern:

1. **Create a new provider class** in `ekko.py`:

```python
class NewProviderProvider(LLMProvider):
    """New provider integration"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, system_prompt: str) -> str:
        # Implement API call
        pass
```

2. **Update the Config class** to support the new provider:
   - Add configuration options
   - Update `setup_wizard()`
   - Update `_get_provider()` in CommandGenerator

3. **Test thoroughly** with the new provider

4. **Update documentation**:
   - Add to README.md
   - Update QUICKSTART.md
   - Document any provider-specific setup

## Questions?

- Open an issue for questions
- Tag with `question` label
- We're happy to help!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to ekko! 🎉
