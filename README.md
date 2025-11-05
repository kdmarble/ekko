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

## Why ekko?

- 🤖 **Multiple AI Providers**: Anthropic API and local Ollama
- 💬 **Interactive Workflow**: Approve, deny, or request corrections
- 🔄 **Iterative Refinement**: Refine commands through natural language
- 🔒 **Privacy-First**: Use local Ollama models for complete privacy
- 🚀 **Simple**: Just type `ekko` followed by what you want

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/kdmarble/ekko/main/install-ekko.sh | bash

# Try it
ekko find all files over 500MB
```

## Installation

```bash
# Download and install
curl -fsSL https://raw.githubusercontent.com/kdmarble/ekko/main/install-ekko.sh | bash

# Or manually
curl -fsSL https://raw.githubusercontent.com/kdmarble/ekko/main/ekko.py -o ~/.local/bin/ekko
chmod +x ~/.local/bin/ekko
pip install requests --user
ekko --setup
```

**Requirements**: Python 3.7+, Linux or macOS

## Configuration

Run the setup wizard:

```bash
ekko --setup
```

### Anthropic API (Best Quality)

1. Get API key from [console.anthropic.com](https://console.anthropic.com)
2. Select "Anthropic API" in setup
3. Default model: `claude-sonnet-4-5-20250929`

**Pros**: Best quality, fast
**Cons**: Costs ~$3 per 1M tokens

### Ollama (Best Privacy)

1. Install from [ollama.com](https://ollama.com)
2. Pull a model: `ollama pull qwen3-coder`
3. Select "Ollama" in setup

**Pros**: Free, private, offline
**Cons**: Requires ~2-4GB RAM

### Switch Providers Anytime

```bash
ekko --config                    # Show current config
ekko --switch ollama             # Switch to Ollama
ekko --switch anthropic          # Switch to Anthropic
ekko --model qwen3-coder         # Change model
ekko --use ollama:qwen3-coder    # Switch both at once
```

## Usage Examples

```bash
# Find files
ekko find all files over 500MB

# Git operations
ekko git reset to 3 commits ago

# Process management
ekko kill process using port 3000

# Archives
ekko compress this folder to tar.gz

# Network
ekko show all listening ports
```

## Recommended Models

**Anthropic API**:
- `claude-sonnet-4-5-20250929` - Best balance (default)
- `claude-opus-4-20250514` - Highest quality
- `claude-haiku-4-20250514` - Faster, cheaper

**Ollama**:
- `qwen3-coder` - Fast, code-focused (default)
- `llama3.2` - Good general purpose
- `codellama` - Complex commands
- `mistral` - Balanced option

Pull models: `ollama pull <model-name>`

## Security

- ⚠️ **Always review commands** before pressing Enter
- 🔐 API keys stored in `~/.config/ekko/config.json` (user-only permissions)
- 🏠 Commands run with your shell permissions
- 🔒 Ollama models never send data externally

## Troubleshooting

**Command not found**:
```bash
source ~/.bashrc  # or ~/.zshrc
```

**Anthropic API errors**:
- Check API key: `ekko --config`
- Reconfigure: `ekko --setup`

**Ollama connection errors**:
```bash
curl http://localhost:11434/api/tags  # Check if running
ollama serve                           # Start Ollama
ollama pull qwen3-coder                # Install model
```

## Contributing

We welcome contributions! ekko uses a **modular development structure** but distributes as a single file for easy installation.

**Development docs**: [DEVELOPMENT.md](DEVELOPMENT.md)

**Quick start for contributors**:
```bash
git clone https://github.com/kdmarble/ekko.git
cd ekko
# Edit files in ekko_package/ekko/
python3 build.py  # Build single-file distribution
python3 tests/test_*.py  # Run tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Adding new AI providers
- Code style guidelines
- Testing requirements
- Pull request process

**Current priorities**:
- Expanded provider support (OpenAI, Google Gemini, Cohere)
- Enhanced command parsing
- Bash/Zsh completions

## Uninstall

```bash
rm ~/.local/bin/ekko
rm -rf ~/.config/ekko
```

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**The name?** A play on `echo` - it echoes back what you need, but smarter.
