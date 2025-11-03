# aicmd - Project Summary

## What We Built

A **complete, production-ready, cross-platform CLI tool** that replicates your exact workflow:

```bash
❯ ?? find all files over 500MB
find ~ -type f -size +500M
[enter=run, n=cancel, or describe what's wrong]: only in Downloads
↻ revising...
find ~/Downloads -type f -size +500M
[enter=run, n=cancel, or describe what's wrong]: ⏎
# executes the command
```

## Key Features

✅ **Exact workflow you wanted** - Interactive approve/deny/correct loop
✅ **No Claude Code dependency** - Standalone Python tool
✅ **Dual AI support** - Both Anthropic API and Ollama
✅ **Cross-platform** - Linux, macOS, Windows, WSL
✅ **Easy installation** - One-line curl/PowerShell installers
✅ **Production ready** - Error handling, config management, testing

## What's Included

### Core Tool
- **`aicmd.py`** (9KB) - Main Python script
  - Anthropic API integration
  - Ollama local integration
  - Interactive command loop
  - Config management
  - Command cleaning and formatting

### Installers
- **`install.sh`** (3.4KB) - Unix/Linux/macOS/WSL installer
  - Auto-detects shell (bash/zsh/fish)
  - Installs dependencies
  - Sets up PATH and alias
  - Runs setup wizard

- **`install.ps1`** (3.1KB) - Windows PowerShell installer
  - Windows-native installation
  - PowerShell profile integration
  - PATH configuration

### Documentation
- **`README.md`** (7.9KB) - Complete documentation
  - Installation instructions
  - Configuration guide
  - Usage examples
  - Troubleshooting
  - Model recommendations

- **`QUICKSTART.md`** (1.8KB) - 2-minute getting started
- **`PUBLISHING.md`** (5.4KB) - GitHub publishing guide

### Development Tools
- **`demo.sh`** (1.3KB) - Test without installing
- **`Makefile`** (1KB) - Development tasks
- **`.github/workflows/ci.yml`** - Automated testing
- **`.gitignore`** - Git configuration
- **`LICENSE`** - MIT License

## Installation (For End Users)

### Unix-like Systems
```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/aicmd/main/install.sh | bash
source ~/.zshrc
?? find all files over 500MB
```

### Windows
```powershell
irm https://raw.githubusercontent.com/YOUR_USERNAME/aicmd/main/install.ps1 | iex
. $PROFILE
?? find all files over 500MB
```

## How It Works

1. **User types**: `?? compress this folder`
2. **Tool calls LLM**: Sends prompt to Anthropic or Ollama
3. **Displays command**: Shows generated shell command
4. **Gets feedback**: 
   - Enter/Y = execute
   - N = cancel
   - Text = correction (loops back to step 2)
5. **Executes**: Runs approved command in user's shell

## Configuration

Users run `aicmd --setup` and choose:

### Anthropic API
- Best quality
- Fast responses
- Costs ~$3 per 1M tokens
- Requires API key from console.anthropic.com

### Ollama (Local)
- Completely free
- Private, offline capable
- Requires 2-40GB depending on model
- Runs on localhost

Config stored in `~/.config/aicmd/config.json`:
```json
{
  "provider": "ollama",
  "anthropic_api_key": "",
  "anthropic_model": "claude-sonnet-4-20250514",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama3.2",
  "system_prompt": "You are a shell expert..."
}
```

## Architecture

```
User Input
    ↓
aicmd.py
    ↓
[Config Loader] → reads ~/.config/aicmd/config.json
    ↓
[Provider Selection] → Anthropic or Ollama
    ↓
[LLM Request] → API call with system prompt
    ↓
[Command Cleaner] → strips markdown, formatting
    ↓
[Display] → shows command in cyan
    ↓
[User Input] → enter/n/correction
    ↓
[Loop or Execute] → subprocess.run() or back to LLM
```

## Comparison to Claude Code

| Feature | aicmd | Claude Code |
|---------|-------|-------------|
| **Dependency** | None | Claude subscription |
| **AI Provider** | Anthropic or Ollama | Claude only |
| **Local Models** | ✅ Ollama | ❌ No |
| **Cross-platform** | ✅ Full | ✅ Full |
| **Installation** | One-liner | npm install |
| **Size** | 9KB + deps | ~50MB |
| **Focus** | Command generation | Full coding agent |
| **Workflow** | Optimized for your use case | General purpose |

## Next Steps for Publishing

1. **Create GitHub repo** named `aicmd`
2. **Push all files** from this archive
3. **Update URLs** - Replace `YOUR_USERNAME` with your GitHub username in:
   - install.sh
   - install.ps1
   - README.md
   - QUICKSTART.md
4. **Create v1.0.0 release**
5. **Test installation** with the public URLs
6. **Share** on Reddit, HN, Twitter

See `PUBLISHING.md` for detailed instructions.

## Testing Locally (Before Publishing)

```bash
# Extract the archive
tar -xzf aicmd-complete.tar.gz
cd aicmd

# Test without installing
bash demo.sh

# Or install locally
bash install.sh
```

## Customization Ideas

Users can modify:

1. **System prompt** - Change AI behavior in config
2. **Alias** - Use `ai` or any other name instead of `??`
3. **Models** - Try different Ollama models or Claude versions
4. **Providers** - Easy to add OpenAI, Google, etc.

## Support & Maintenance

After publishing:
- Enable GitHub Discussions for community Q&A
- Watch for issues from early adopters
- Key pain points will likely be:
  - Python dependency issues
  - Ollama connectivity
  - Shell integration on exotic shells
  - API key confusion

## Success Metrics

If this becomes popular, you'll see:
- 100+ GitHub stars in first week
- 1000+ installations in first month
- Issues/discussions with real use cases
- Community contributions (alternative providers, etc.)

## What Makes This Different

Unlike Shell-GPT, aichat, or other tools:
1. **Interactive workflow** - Approve/correct/deny built-in
2. **True cross-platform** - Native installers for all OSes
3. **Dual provider** - Not locked to one LLM
4. **Simple focus** - Just command generation, nothing more
5. **Your exact UX** - Built specifically for your workflow

## Files Reference

```
aicmd-complete.tar.gz (13KB)
├── aicmd.py              # Main tool (346 lines)
├── install.sh            # Unix installer
├── install.ps1           # Windows installer
├── demo.sh               # Local demo script
├── README.md             # Full documentation
├── QUICKSTART.md         # Fast start guide
├── PUBLISHING.md         # GitHub publishing guide
├── Makefile              # Dev commands
├── LICENSE               # MIT license
├── .gitignore            # Git config
└── .github/
    └── workflows/
        └── ci.yml        # Automated testing
```

## Total Project Size

- **Source code**: 9KB
- **All files**: 13KB compressed
- **Dependencies**: `requests` module only
- **Lines of code**: ~350 Python

Simple, focused, and exactly what you asked for.

---

**Ready to publish?** Follow the steps in `PUBLISHING.md`

**Want to test first?** Run `bash demo.sh`

**Questions?** All docs are in the archive
