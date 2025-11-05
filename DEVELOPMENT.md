# ekko Development Guide

This guide explains the ekko architecture, development workflow, and how to contribute.

## Architecture Overview

ekko uses a **modular development structure** but **distributes as a single file** for easy installation. This gives us the best of both worlds:

- **Development**: Clean, maintainable, modular code
- **Distribution**: Single-file for `curl | bash` installation
- **Package**: Proper Python package for `pip install`

### Directory Structure

```
ekko/
├── ekko_package/          # Modular source code
│   ├── ekko/
│   │   ├── __init__.py
│   │   ├── cli.py          # Command-line interface
│   │   ├── config.py       # Configuration management
│   │   ├── generator.py    # Command generation logic
│   │   └── providers/      # Provider implementations
│   │       ├── __init__.py # Provider registry
│   │       ├── base.py     # Base provider interface
│   │       ├── anthropic.py
│   │       └── ollama.py
│   ├── setup.py            # Package setup
│   └── pyproject.toml      # Modern packaging config
├── build.py                # Builds single-file ekko.py
├── ekko.py                 # Generated single-file distribution
├── install-ekko.sh         # Installation script
├── tests/                  # Test suite
└── providers/              # Provider documentation
```

## Development Workflow

### 1. Making Changes

**Work in the modular source:**

```bash
cd ekko_package/ekko/
# Edit files in this directory
vim config.py
vim providers/anthropic.py
```

### 2. Building Single-File Distribution

After making changes, rebuild the single-file distribution:

```bash
python3 build.py
```

This combines all modules into `ekko.py` for distribution.

### 3. Testing

Run the test suite against the built single file:

```bash
# Run all tests
python3 tests/test_setup_wizard.py
python3 tests/test_piped_installation.py
python3 tests/test_provider_switching.py
python3 tests/test_upgrade_compatibility.py

# Or use make
make test
```

### 4. Code Formatting

```bash
make format  # Format with black
make lint    # Lint with flake8
```

## Adding a New Provider

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
    """Provider for New Provider API."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.newprovider.com/v1/generate"

    def generate(self, prompt: str, system_prompt: str) -> str:
        """Generate command using New Provider API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "max_tokens": 1024,
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=data, timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["output"]
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to New Provider: {str(e)}")
            print("Possible fixes:")
            print("  - Check your API key is valid")
            print("  - Verify your internet connection")
            print("  - Run 'ekko --setup' to reconfigure")
            sys.exit(1)

    @classmethod
    def get_config_keys(cls) -> list:
        """Return configuration keys needed."""
        return ["newprovider_api_key", "newprovider_model"]

    @classmethod
    def validate_config(cls, config: dict) -> tuple:
        """Validate provider-specific configuration."""
        api_key = config.get("newprovider_api_key", "")
        model = config.get("newprovider_model", "")

        if not api_key or len(api_key) < 10:
            return False, "Invalid or missing New Provider API key"

        if not model:
            return False, "Missing New Provider model name"

        return True, None
```

### Step 2: Register Provider

Update `ekko_package/ekko/providers/__init__.py`:

```python
from ekko.providers.newprovider import NewProviderProvider

PROVIDERS = {
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
    "newprovider": NewProviderProvider,  # Add this
}
```

### Step 3: Update Config

Update `ekko_package/ekko/config.py`:

1. Add defaults in `default_config()`:
```python
"newprovider_api_key": "",
"newprovider_model": "default-model",
```

2. Update `setup_wizard()` to include the new provider option.

### Step 4: Update Build Script

The build script automatically discovers providers from the `providers/` directory. You just need to make sure it's included in the build.

Edit `build.py` to add your provider:

```python
# Add New Provider provider
output.append("# " + "=" * 76)
output.append("# New Provider Provider")
output.append("# " + "=" * 76)
output.append("")
newprovider_content = read_module(package_dir / "providers" / "newprovider.py")
newprovider_content = re.sub(
    r"^from ekko\.providers\.base import LLMProvider\s*$",
    "",
    newprovider_content,
    flags=re.MULTILINE,
)
output.append(newprovider_content.strip())
```

And update the registry:

```python
output.append("PROVIDERS = {")
output.append('    "anthropic": AnthropicProvider,')
output.append('    "ollama": OllamaProvider,')
output.append('    "newprovider": NewProviderProvider,')  # Add this
output.append("}")
```

### Step 5: Rebuild and Test

```bash
python3 build.py
python3 ekko.py --setup  # Test the setup wizard
```

### Step 6: Add Tests

Create tests for your provider in `tests/`.

### Step 7: Update Documentation

- Update `README.md` with the new provider
- Update `providers/README.md` with provider-specific documentation
- Update `CHANGELOG.md`

## Build System Details

### How `build.py` Works

The build script:

1. Reads all module files from `ekko_package/ekko/`
2. Removes internal `from ekko.*` imports
3. Combines everything into a single file
4. Removes module docstrings (keeps main docstring)
5. Adds proper header and imports
6. Creates executable `ekko.py`

### What Gets Built

| Source | Purpose |
|--------|---------|
| `ekko_package/ekko/*.py` | Modular source code |
| `ekko.py` | Single-file distribution (generated) |
| `ekko_package/dist/*.whl` | Python package wheel |

## Distribution Methods

ekko can be installed three ways:

### 1. Single-File (Recommended for Users)

```bash
curl -fsSL https://raw.githubusercontent.com/kdmarble/ekko/main/install-ekko.sh | bash
```

Uses the generated `ekko.py` file.

### 2. pip Install (Future)

```bash
pip install ekko
```

Installs from the `ekko_package/` as a proper Python package.

### 3. From Source (For Developers)

```bash
git clone https://github.com/kdmarble/ekko.git
cd ekko
python3 build.py
./ekko.py --setup
```

## CI/CD Pipeline

### On Pull Request

1. **Lint** - Check code formatting
2. **Build** - Create single-file distribution
3. **Test** - Run all test suites on Linux and macOS
4. **Security** - Scan with Trivy

### On Release Tag

1. **Build** - Create both single-file and package distributions
2. **Test** - Run full test suite
3. **Package** - Create wheels and source distributions
4. **Release** - Publish to GitHub Releases with:
   - `ekko.py` (single file)
   - `install-ekko.sh` (installer)
   - `ekko-vX.Y.Z.tar.gz` (source archive)
   - `ekko-X.Y.Z-py3-none-any.whl` (Python wheel)
   - `checksums.txt` (SHA256 checksums)

## Code Style

- **Format**: black (max line length 100)
- **Lint**: flake8
- **Type hints**: Optional but encouraged
- **Docstrings**: Required for public functions and classes

### Example

```python
def my_function(param: str) -> bool:
    """
    Brief description.

    Args:
        param: Parameter description

    Returns:
        Return value description

    Raises:
        ValueError: When param is invalid
    """
    # Implementation
    pass
```

## Testing Guidelines

### Test Structure

- **Unit tests**: Test individual components
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test full user workflows

### Running Tests

```bash
# Individual test suites
python3 tests/test_setup_wizard.py
python3 tests/test_provider_switching.py

# All tests
for test in tests/test_*.py; do python3 "$test"; done
```

### Writing Tests

Use `pexpect` for interactive testing:

```python
def test_my_feature(self):
    """Test my feature."""
    config_dir = self.setup_test_env()
    env = self.get_test_env()

    child = pexpect.spawn(
        'python3', ['ekko.py', '--my-flag'],
        cwd=Path(__file__).parent.parent,
        env=env,
        timeout=10
    )

    try:
        child.expect('Expected output')
        child.sendline('user input')
        child.expect('Next expected output')
        child.expect(pexpect.EOF, timeout=2)

        # Assert results
        assert condition, "Error message"
    finally:
        child.close()
        self.cleanup_test_env()
```

## Release Process

1. **Update version** in `ekko_package/ekko/__init__.py`
2. **Update CHANGELOG.md** with changes
3. **Build and test**:
   ```bash
   python3 build.py
   python3 tests/test_*.py
   ```
4. **Commit changes**
5. **Create tag**: `git tag v1.2.0`
6. **Push tag**: `git push origin v1.2.0`
7. **CI/CD automatically creates release**

## Troubleshooting

### Build Issues

**Problem**: `build.py` fails
- Check all source files have proper structure
- Ensure no syntax errors in modules
- Verify imports are correct

**Problem**: Tests fail after build
- Rebuild: `python3 build.py`
- Check for duplicate `if __name__ == "__main__"` blocks
- Verify all imports are properly handled

### Development Issues

**Problem**: Changes not reflected
- Remember to rebuild: `python3 build.py`
- Clear any cached `.pyc` files
- Restart Python if testing in REPL

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct
- How to submit issues
- Pull request process
- Community guidelines

## Questions?

- **Issues**: https://github.com/kdmarble/ekko/issues
- **Discussions**: https://github.com/kdmarble/ekko/discussions
- **Documentation**: https://github.com/kdmarble/ekko

---

Happy coding! 🚀
