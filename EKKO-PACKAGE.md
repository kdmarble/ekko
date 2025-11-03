# ekko - Final Package

## What Is ekko?

**ekko** is an AI-powered command line assistant that generates shell commands from natural language.

Named after the shell `echo` command (with a unique double-k spelling), ekko echoes back the exact commands you need, then lets you approve, deny, or refine them interactively.

## Quick Demo

```bash
❯ ekko find all files over 500MB
find ~ -type f -size +500M
[enter=run, n=cancel, or describe what's wrong]: only in Downloads
↻ revising...
find ~/Downloads -type f -size +500M
[enter=run, n=cancel, or describe what's wrong]: ⏎
# command executes
```

## Installation (End Users)

### One-Liner Install

**Linux/macOS/WSL:**
```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/ekko/main/install-ekko.sh | bash
```

**Windows:**
```powershell
irm https://raw.githubusercontent.com/yourusername/ekko/main/install-ekko.ps1 | iex
```

### Manual Install

1. Download `ekko.py`
2. Make it executable: `chmod +x ekko.py`
3. Move to PATH: `mv ekko.py ~/.local/bin/ekko`
4. Install requests: `pip install requests --user`
5. Configure: `ekko --setup`

## Files in This Package

### Core Files (Required)
- **ekko.py** (9KB) - Main Python script
- **install-ekko.sh** (3KB) - Unix installer
- **install-ekko.ps1** (2.7KB) - Windows installer

### Documentation
- **README-ekko.md** - Complete user documentation
- **QUICKSTART-ekko.md** - 2-minute getting started guide
- **THIS_FILE.md** - What you're reading now

### Development
- **demo-ekko.sh** - Test ekko without installing
- **LICENSE** - MIT License
- **.gitignore** - Git configuration

### Legacy Files (from aicmd)
These are the original aicmd files before rebranding. You can delete them:
- aicmd.py, install.sh, install.ps1, README.md, etc.

## Features

✅ **Interactive workflow** - Approve/deny/correct commands before execution  
✅ **Dual AI support** - Anthropic API or local Ollama  
✅ **Cross-platform** - Linux, macOS, Windows, WSL  
✅ **Privacy-first** - Use local models for complete privacy  
✅ **Zero config needed** - Setup wizard on first run  
✅ **Simple command** - Just `ekko <what you want>`

## Configuration Options

ekko supports two AI providers:

### Anthropic API
- Best quality responses
- Fast (< 1 second)
- Costs ~$3 per 1M tokens
- Get key at: console.anthropic.com

### Ollama (Local)
- Completely free
- Runs offline
- Private (data never leaves your machine)
- Requires 2-40GB depending on model
- Install at: ollama.com

## Usage Examples

```bash
# File operations
ekko find all files over 500MB
ekko compress this folder excluding node_modules

# Git commands
ekko git show last 5 commits with diffs
ekko git reset to 3 commits ago

# System administration
ekko show disk usage sorted by size
ekko kill process using port 3000

# Network
ekko test if port 443 is open on example.com
ekko show all listening ports
```

## Publishing to GitHub

### Step 1: Create Repository

1. Go to github.com/new
2. Name: `ekko`
3. Description: "AI-powered command line assistant - ekko back the commands you need"
4. Public
5. Don't initialize with README
6. Create

### Step 2: Push Code

```bash
git init
git add ekko.py install-ekko.sh install-ekko.ps1 README-ekko.md QUICKSTART-ekko.md LICENSE
git commit -m "Initial release: ekko v1.0.0"
git remote add origin https://github.com/YOUR_USERNAME/ekko.git
git branch -M main
git push -u origin main
```

### Step 3: Update URLs

Replace `yourusername` with your GitHub username in:
- install-ekko.sh (line with REPO_URL)
- install-ekko.ps1 (line with $url)
- README-ekko.md (all GitHub links)
- QUICKSTART-ekko.md (installation commands)

```bash
# Find and replace
find . -name "*ekko*" -type f -exec sed -i 's/yourusername/YOUR_USERNAME/g' {} \;
```

### Step 4: Create Release

1. Go to repository → Releases → "Create a new release"
2. Tag: `v1.0.0`
3. Title: `ekko v1.0.0 - Initial Release`
4. Description: See example in old PUBLISHING.md
5. Publish

### Step 5: Test

```bash
# In a fresh environment
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/ekko/main/install-ekko.sh | bash
```

## Customization

Users can customize ekko by editing `~/.config/ekko/config.json`:

```json
{
  "provider": "ollama",
  "anthropic_api_key": "",
  "anthropic_model": "claude-sonnet-4-20250514",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama3.2",
  "system_prompt": "You are a shell expert. Output ONLY the command..."
}
```

## Taglines & Marketing

**One-liner:**
"ekko - AI-powered command line assistant that generates shell commands from natural language"

**Taglines:**
- "ekko back the commands you need"
- "When you forgot the command, just ekko"
- "Natural language → Shell commands"
- "AI commands, instant approval"

**SEO keywords:**
AI, CLI, command line, shell, terminal, assistant, code generation, developer tools

## Support & Community

After launch:
- Enable GitHub Discussions
- Add issue templates
- Monitor r/commandline, r/programming
- Share on HackerNews, Twitter, Dev.to

## Next Steps

1. **Test locally**: `bash demo-ekko.sh`
2. **Create GitHub repo**: Follow steps above
3. **Share it**: Reddit, HN, Twitter
4. **Gather feedback**: Listen to early users
5. **Iterate**: Add features based on requests

## File Checklist

Ready to publish:
- [x] ekko.py - Core tool
- [x] install-ekko.sh - Unix installer
- [x] install-ekko.ps1 - Windows installer
- [x] README-ekko.md - Full documentation
- [x] QUICKSTART-ekko.md - Quick start
- [x] LICENSE - MIT license
- [x] demo-ekko.sh - Local demo

Before publishing:
- [ ] Update URLs with your GitHub username
- [ ] Test on Linux
- [ ] Test on macOS
- [ ] Test on Windows
- [ ] Create GitHub repository
- [ ] Create v1.0.0 release
- [ ] Share on social media

## Why ekko Works

Unlike other tools:
- **Focused**: Only does command generation (no code editing, no IDE bloat)
- **Interactive**: Built-in approve/deny/correct workflow
- **Flexible**: Works with Anthropic or Ollama
- **Cross-platform**: Native installers for all OSes
- **Simple**: One command, clear purpose
- **Your exact UX**: Built for the workflow you designed

Total project size: ~15KB compressed
Lines of code: ~350 Python
Dependencies: Just `requests`

---

**Ready to launch ekko?** 🚀

Start with: `bash demo-ekko.sh`
