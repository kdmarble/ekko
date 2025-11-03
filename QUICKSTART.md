# ekko Quick Start

Get running in under 2 minutes.

## Linux / macOS / WSL

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/yourusername/ekko/main/install-ekko.sh | bash

# Reload shell
source ~/.zshrc  # or ~/.bashrc

# Use it
ekko find all files over 500MB
```

## Windows

```powershell
# Download and run installer
irm https://raw.githubusercontent.com/yourusername/ekko/main/install-ekko.ps1 | iex

# Reload PowerShell
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','User')

# Use it
ekko find all files over 500MB
```

## Configuration

During installation, you'll be asked:

### Option 1: Ollama (Free, Local)
1. Install Ollama: https://ollama.com/download
2. Run: `ollama pull llama3.2`
3. Select "1" in setup wizard

### Option 2: Anthropic API (Best Quality)
1. Get API key: https://console.anthropic.com
2. Select "2" in setup wizard
3. Paste your API key

## Usage

```bash
# Type ekko followed by what you want
ekko compress this folder to tar.gz

# Review the generated command
tar -czf folder.tar.gz folder/

# Press Enter to run, N to cancel, or type a correction
[enter=run, n=cancel, or describe what's wrong]:
```

## Examples

```bash
ekko show disk usage sorted by size
ekko kill process on port 3000
ekko git show last 5 commits
ekko find python files modified today
ekko create backup of this directory
```

## Troubleshooting

**"Command not found: ekko"**
```bash
source ~/.zshrc  # Reload your shell
```

**Ollama not connecting**
```bash
ollama serve  # Start Ollama
ollama pull llama3.2  # Pull model
```

**Want to change settings?**
```bash
ekko --setup  # Re-run setup wizard
```

## What's Next?

- Read the full [README](README-ekko.md) for advanced usage
- Try different models (see README for recommendations)
- Customize the system prompt in `~/.config/ekko/config.json`

---

**ekko** - echo back the commands you need
