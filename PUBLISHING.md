# Publishing Guide

How to publish aicmd to GitHub and make it available for users.

## Prerequisites

- GitHub account
- Git installed
- Project files ready

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `aicmd`
3. Description: "AI-powered command line assistant - Generate shell commands from natural language"
4. Choose Public
5. Don't initialize with README (we have our own)
6. Create repository

## Step 2: Push Code

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: aicmd v1.0.0"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/aicmd.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Update URLs in Files

Replace placeholder URLs with your actual GitHub username:

**Files to update:**
- `install.sh` - Line with `REPO_URL=`
- `install.ps1` - Line with `$url =`
- `README.md` - All GitHub links
- `QUICKSTART.md` - All installation URLs

**Find and replace:**
```bash
# Find all instances
grep -r "yourusername" .

# Replace (macOS)
find . -type f -name "*.sh" -o -name "*.ps1" -o -name "*.md" | xargs sed -i '' 's/yourusername/YOUR_USERNAME/g'

# Replace (Linux)
find . -type f -name "*.sh" -o -name "*.ps1" -o -name "*.md" | xargs sed -i 's/yourusername/YOUR_USERNAME/g'
```

Commit the changes:
```bash
git add .
git commit -m "Update URLs with correct username"
git push
```

## Step 4: Create First Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Title: `aicmd v1.0.0 - Initial Release`
5. Description:
   ```markdown
   ## aicmd v1.0.0
   
   First stable release of aicmd - AI-powered command line assistant.
   
   ### Features
   - ✨ Interactive command generation from natural language
   - 🤖 Support for Anthropic API and Ollama
   - 🔄 Iterative correction workflow
   - 🚀 Cross-platform (Linux, macOS, Windows, WSL)
   - 🎯 Simple ?? alias for quick access
   
   ### Installation
   
   **Linux/macOS/WSL:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/aicmd/main/install.sh | bash
   ```
   
   **Windows:**
   ```powershell
   irm https://raw.githubusercontent.com/YOUR_USERNAME/aicmd/main/install.ps1 | iex
   ```
   
   See [QUICKSTART.md](QUICKSTART.md) for more details.
   ```
6. Click "Publish release"

## Step 5: Set Up GitHub Pages (Optional)

For a nice documentation site:

1. Go to repository Settings → Pages
2. Source: Deploy from branch
3. Branch: main, folder: / (root)
4. Save
5. Your docs will be at: `https://YOUR_USERNAME.github.io/aicmd/`

## Step 6: Add Topics/Tags

1. Go to your repository
2. Click the gear icon next to "About"
3. Add topics: `cli`, `ai`, `shell`, `command-line`, `anthropic`, `ollama`, `python`
4. Save

## Step 7: Test Installation

Test the public installation URLs work:

```bash
# Create a test VM or container
docker run -it --rm ubuntu:latest bash

# Test installation
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/aicmd/main/install.sh | bash
```

## Step 8: Promote Your Project

### Add Badges to README

Add these to the top of `README.md`:

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/release/YOUR_USERNAME/aicmd.svg)](https://github.com/YOUR_USERNAME/aicmd/releases)
[![CI](https://github.com/YOUR_USERNAME/aicmd/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/aicmd/actions)
```

### Share On

- Reddit: r/commandline, r/programming, r/Python
- Hacker News: news.ycombinator.com
- Twitter/X with #CLI #AI #DevTools
- Dev.to blog post
- Product Hunt (after some traction)

## Maintenance

### Version Updates

When releasing a new version:

1. Update version in `aicmd.py` (`__version__` variable)
2. Update CHANGELOG.md (create one if needed)
3. Commit changes
4. Create new release on GitHub
5. Tag format: `v1.x.x`

### Handle Issues

- Enable GitHub Discussions for Q&A
- Use issue templates (bug report, feature request)
- Be responsive to early users
- Tag good first issues for contributors

### CI/CD

The included GitHub Actions workflow will:
- Run tests on all platforms
- Check code quality
- Create release artifacts automatically

## Marketing Copy

**One-liner:**
"AI-powered command line assistant that generates shell commands from natural language"

**Elevator pitch:**
"Forgot a command syntax? Just type `?? what you want` and get the exact shell command. Review it, refine it with natural language, then run it. Works with Anthropic's Claude or local Ollama models. Zero context switching."

**Use cases:**
- DevOps engineers managing servers
- Developers who work across multiple languages/tools
- System administrators automating tasks
- Anyone who googles "bash command for..." regularly

## Success Metrics

Track these to measure adoption:
- GitHub stars
- Download counts (from releases)
- Installation script hits
- Issues/discussions activity
- Mentions on social media

## Next Steps After Launch

1. Gather feedback from initial users
2. Add most requested features
3. Improve documentation based on questions
4. Consider adding:
   - Bash completion scripts
   - More AI providers (OpenAI, local models)
   - Command history and favorites
   - Web UI for configuration
   - Plugin system

Good luck! 🚀
