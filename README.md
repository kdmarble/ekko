# ekko

**AI-powered command line assistant** - Generate shell commands from natural language with an interactive approval workflow.

```bash
❯ ekko find all files over 500MB
find ~ -type f -size +500M
[enter=run, n=cancel, or describe what's wrong]: only in Downloads folder
↻ revising...
find ~/Downloads -type f -size +500M
[enter=run, n=cancel, or describe what's wrong]: ⏎
# executes command
```

## Features

- 🤖 **Multiple AI Providers**: Supports Anthropic API and local Ollama
- 💬 **Interactive Workflow**: Approve, deny, or request corrections before execution
- 🔄 **Iterative Corrections**: Refine commands through natural language feedback
- 🚀 **Cross-Platform**: Works on Linux, macOS, Windows, and WSL
- 🎯 **Simple Command**: Just type `ekko` followed by what you want
- 🔒 **Privacy-First**: Use local Ollama models for complete privacy

## Installation

### Linux / macOS / WSL

```bash
curl -fsSL https://raw.githubusercontent.com/kdmarble/ekko/main/install-ekko.sh | bash
```

Or manually:

```bash
# Download
curl -fsSL https://raw.githubusercontent.com/kdmarble/ekko/main/ekko.py -o ~/.local/bin/ekko
chmod +x ~/.local/bin/ekko

# Install dependencies
pip install requests --user

# Configure
ekko --setup
```

### Windows

```powershell
# Download install script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kdmarble/ekko/main/install-ekko.ps1" -OutFile "install-ekko.ps1"

# Run installer
powershell -ExecutionPolicy Bypass -File install-ekko.ps1
```

## Configuration

Run the setup wizard:

```bash
ekko --setup
```

### Option 1: Anthropic API (Recommended for Quality)

1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. Select "Anthropic API" in setup wizard
3. Enter your API key
4. Default model: `claude-sonnet-4-20250514`

**Pros**: Best quality, fast responses, no local setup  
**Cons**: Costs money (~$3 per 1M input tokens)

### Option 2: Ollama (Recommended for Privacy)

1. Install Ollama from [ollama.com](https://ollama.com)
2. Pull a model: `ollama pull llama3.2`
3. Select "Ollama" in setup wizard
4. Use default settings

**Pros**: Free, private, works offline  
**Cons**: Requires ~4GB RAM, slower on CPU

### Manual Configuration

Edit `~/.config/ekko/config.json` (Linux/macOS) or `%APPDATA%\ekko\config.json` (Windows):

```json
{
  "provider": "anthropic",
  "anthropic_api_key": "sk-ant-...",
  "anthropic_model": "claude-sonnet-4-20250514",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama3.2",
  "system_prompt": "You are a shell expert. Output ONLY the command to solve the problem. No explanation, no markdown, no backticks - just the raw shell command."
}
```

## Usage

### Basic Examples

```bash
# Find files
ekko find all files over 500MB
ekko show me disk usage sorted by size

# Git operations
ekko git reset to 3 commits ago
ekko show git log for last week

# Process management
ekko kill process using port 3000
ekko show all python processes

# Archives
ekko compress this folder to tar.gz
ekko extract this zip preserving permissions

# Network
ekko show all listening ports
ekko test if port 443 is open on example.com
```

### Interactive Workflow

1. **Type your request**: `ekko find large log files`
2. **Review command**: Command is displayed in cyan
3. **Choose action**:
   - Press **Enter** or **Y** to run
   - Type **N** to cancel
   - Type **correction** to refine (e.g., "only in /var/log")

### Example Session

```bash
❯ ekko compress this folder
tar -czf folder.tar.gz folder/
[enter=run, n=cancel, or describe what's wrong]: exclude node_modules
↻ revising...
tar --exclude='node_modules' -czf folder.tar.gz folder/
[enter=run, n=cancel, or describe what's wrong]: ⏎
# creates archive
```

## Recommended Models

### Anthropic API
- `claude-sonnet-4-20250514` - Best balance (default)
- `claude-opus-4-20250514` - Highest quality, slower
- `claude-haiku-4-20250514` - Faster, cheaper

### Ollama
- `llama3.2` - Fast, good quality (default, 2GB)
- `codellama` - Better for complex commands (4GB)
- `mistral` - Balanced option (4GB)
- `llama3.2:70b` - Best quality if you have resources (40GB)

Pull models with: `ollama pull <model-name>`

## Troubleshooting

### "Command not found: ekko"

Reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

Or check PATH:
```bash
echo $PATH | grep -o "$HOME/.local/bin"
```

### Anthropic API Errors

- **401 Unauthorized**: Check API key in config
- **429 Rate Limited**: Wait a moment or upgrade plan
- **Overloaded**: Try again

### Ollama Connection Errors

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull model if missing
ollama pull llama3.2
```

### Python Module Missing

```bash
pip install requests --user
# or
python3 -m pip install requests --user
```

## Security Considerations

- ⚠️ **Review before execution**: Always check commands before pressing Enter
- 🔐 **API keys**: Stored in `~/.config/ekko/config.json` with user-only permissions
- 🏠 **Local execution**: Commands run in your shell with your permissions
- 🔒 **Ollama privacy**: Local models never send data to external servers

## Uninstallation

```bash
# Remove binary
rm ~/.local/bin/ekko  # Linux/macOS
rm -rf "$LOCALAPPDATA/ekko"  # Windows

# Remove config
rm -rf ~/.config/ekko  # Linux/macOS
rm -rf "$APPDATA/ekko"  # Windows
```

## Requirements

- **Python**: 3.7 or later
- **Dependencies**: `requests` (auto-installed)
- **Storage**: ~10KB for the tool
- **For Ollama**: 2-40GB depending on model

## Testing

ekko includes a comprehensive test suite to ensure reliability and prevent regressions.

### Running Tests

```bash
# Setup test environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install pexpect requests

# Run all tests
python3 tests/test_setup_wizard.py         # Interactive setup tests (7 tests)
python3 tests/test_piped_installation.py   # Installation tests (2 tests)
python3 tests/test_provider_switching.py   # Provider switching tests (10 tests)
python3 tests/test_upgrade_compatibility.py # Upgrade compatibility tests (5 tests)
```

### Test Coverage

**Setup Wizard Tests** (7 tests):
- ✅ Valid Ollama and Anthropic configurations
- ✅ URL validation (rejects invalid formats)
- ✅ Model name validation (detects injection attempts)
- ✅ API key validation
- ✅ Corrupted config detection

**Installation Tests** (2 tests):
- ✅ Piped installation scenario testing (`curl ... | bash`)
- ✅ TTY input redirection for piped installations

**Provider Switching Tests** (10 tests):
- ✅ Display configuration with `--config`
- ✅ Switch between providers with `--switch`
- ✅ Change models with `--model`
- ✅ Combo switching with `--use`
- ✅ Settings persistence across provider changes
- ✅ Validation of invalid providers and models
- ✅ Error handling for unconfigured providers

**Upgrade Compatibility Tests** (5 tests):
- ✅ v1.0.1 configs work seamlessly with v1.1.0
- ✅ Config structure unchanged (no migration needed)
- ✅ Both provider settings preserved during upgrade
- ✅ New switching commands work with old configs
- ✅ Backward compatibility verified

**What's Tested**:
- Interactive setup wizard with various inputs
- Configuration file validation
- Installation script behavior in piped environments
- Provider and model switching functionality
- Settings persistence and configuration management
- Version upgrade compatibility (v1.0.1 → v1.1.0)
- Error handling and user guidance

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on adding new tests.

## License

MIT License - See LICENSE file for details

## Why ekko?

The name **ekko** is a play on the shell `echo` command - it echoes back what you need, but smarter. The double 'k' makes it unique and memorable.

---

**Get started in 60 seconds:**

```bash
curl -fsSL https://raw.githubusercontent.com/kdmarble/ekko/main/install-ekko.sh | bash
ekko find all files over 500MB
```
