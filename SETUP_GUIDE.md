# ekko - Repository Setup Guide

This guide is for maintainers setting up the ekko repository for initial publication and ongoing development.

## Quick Start for Maintainers

### 1. Update Placeholder URLs

Before publishing, replace `kdmarble` with your actual GitHub username in these files:

```bash
# Find all instances
grep -r "kdmarble" .

# Replace all at once (Linux)
find . -type f \( -name "*.sh" -o -name "*.ps1" -o -name "*.md" \) \
  -exec sed -i 's/kdmarble/your-actual-username/g' {} +

# Replace all at once (macOS)
find . -type f \( -name "*.sh" -o -name "*.ps1" -o -name "*.md" \) \
  -exec sed -i '' 's/kdmarble/your-actual-username/g' {} +
```

**Files to update:**
- `README.md`
- `QUICKSTART.md`
- `CHANGELOG.md`
- `install-ekko.sh`
- `install-ekko.ps1`

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ekko`
3. Description: "AI-powered command line assistant - ekko back the commands you need"
4. Choose **Public**
5. **Do NOT** initialize with README (we have our own)
6. Click "Create repository"

### 3. Push Code to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial release: ekko v1.0.0"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ekko.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 4. Configure Repository Settings

#### Enable Discussions

1. Go to repository **Settings** → **General**
2. Scroll to **Features**
3. Enable **Discussions**

#### Add Topics/Tags

1. Go to your repository main page
2. Click the gear icon next to "About"
3. Add topics: `cli`, `ai`, `shell`, `command-line`, `anthropic`, `ollama`, `python`, `terminal`, `developer-tools`
4. Save changes

#### Set Repository Description

Use: "AI-powered command line assistant - ekko back the commands you need"

### 5. Create First Release

1. Go to your repository → **Releases** → "Create a new release"
2. Click "Choose a tag" → Type `v1.0.0` → "Create new tag"
3. Release title: `ekko v1.0.0 - Initial Release`
4. Description:

```markdown
## 🎉 ekko v1.0.0 - Initial Release

ekko is an AI-powered command line assistant that generates shell commands from natural language.

### ✨ Features

- 🤖 **Multiple AI Providers**: Supports Anthropic API and local Ollama
- 💬 **Interactive Workflow**: Approve, deny, or request corrections before execution
- 🔄 **Iterative Corrections**: Refine commands through natural language feedback
- 🚀 **Cross-Platform**: Works on Linux, macOS, Windows, and WSL
- 🎯 **Simple Command**: Just type `ekko` followed by what you want
- 🔒 **Privacy-First**: Use local Ollama models for complete privacy

### 📦 Installation

**Linux/macOS/WSL:**
```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/ekko/main/install-ekko.sh | bash
```

**Windows:**
```powershell
irm https://raw.githubusercontent.com/YOUR_USERNAME/ekko/main/install-ekko.ps1 | iex
```

### 📚 Documentation

- [README](README.md) - Complete documentation
- [QUICKSTART](QUICKSTART.md) - Get started in 2 minutes
- [CONTRIBUTING](CONTRIBUTING.md) - Help improve ekko

### 🙏 Thank You

Thank you for trying ekko! We welcome feedback and contributions.

---

**What is ekko?** The name is a play on the shell `echo` command - it echoes back what you need, but smarter.
```

5. Click **Publish release**

### 6. Test Installation

Test that the public installation URLs work:

```bash
# In a clean environment (VM, container, or test machine)
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/ekko/main/install-ekko.sh | bash

# Or test the Windows installer in PowerShell
irm https://raw.githubusercontent.com/YOUR_USERNAME/ekko/main/install-ekko.ps1 | iex
```

### 7. Add Badges to README (Optional)

Add these at the top of `README.md`:

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/release/YOUR_USERNAME/ekko.svg)](https://github.com/YOUR_USERNAME/ekko/releases)
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/ekko.svg)](https://github.com/YOUR_USERNAME/ekko/stargazers)
```

## Development Workflow

### Local Testing

```bash
# Test without installing
make demo

# Or run directly
chmod +x ekko.py
./ekko.py --help

# Run tests
make test

# Format code
make format

# Lint code
make lint
```

### Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make changes and test**
   ```bash
   make test
   make lint
   ```

3. **Commit changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/your-feature
   ```

### Release Process

When ready to release a new version:

1. **Update version** in `ekko.py`:
   ```python
   if sys.argv[1] in ['--version', '-v']:
       print("ekko v1.1.0")  # Update this
   ```

2. **Update CHANGELOG.md**:
   ```markdown
   ## [1.1.0] - 2025-XX-XX
   ### Added
   - New feature description
   ### Fixed
   - Bug fix description
   ```

3. **Commit and tag**:
   ```bash
   git add .
   git commit -m "Release v1.1.0"
   git tag v1.1.0
   git push && git push --tags
   ```

4. **Create GitHub Release**
   - Go to Releases → "Create a new release"
   - Choose tag: v1.1.0
   - Generate release notes
   - Publish

## Maintenance Tasks

### Responding to Issues

- Label issues appropriately: `bug`, `enhancement`, `question`, `good first issue`
- Respond within 48 hours when possible
- Close stale issues after 30 days of inactivity

### Reviewing Pull Requests

Checklist for PR reviews:

- [ ] Code follows style guidelines
- [ ] Tests pass (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] Documentation updated if needed
- [ ] No breaking changes (or properly documented)
- [ ] Commit messages are clear

### Community Engagement

- Enable and monitor GitHub Discussions
- Respond to community questions
- Highlight good contributions
- Tag issues as `good first issue` for newcomers

## Promotion

### Initial Launch

Share on:

- **Reddit**:
  - r/commandline
  - r/programming
  - r/Python
  - r/linux
  - r/opensource

- **Hacker News**: news.ycombinator.com/submit

- **Twitter/X**: Use hashtags `#CLI #AI #DevTools #OpenSource`

- **Dev.to**: Write a blog post about ekko

- **Product Hunt**: Wait until you have some traction

### Launch Post Template

```
🎉 Introducing ekko - AI-powered command line assistant

Ever forgot a bash command? Just type what you want in natural language:

  ekko find all files over 500MB
  ekko compress this folder excluding node_modules
  ekko kill process on port 3000

ekko generates the command, you review and approve it, then it runs. Simple!

✨ Features:
- Works with Claude (Anthropic) or local Ollama
- Interactive approve/deny/correct workflow
- Cross-platform (Linux, macOS, Windows)
- Privacy-first with local models

🚀 Get started: [link to repo]

Open source (MIT) | Contributions welcome!
```

## Monitoring

### Metrics to Track

- GitHub stars
- Fork count
- Issues opened/closed
- Pull requests
- Download counts (via release assets)
- Discussions activity

### Success Indicators

First week:
- 50+ GitHub stars
- 5+ issues/discussions
- 2-3 meaningful conversations

First month:
- 200+ stars
- 500+ installations
- 10+ issues resolved
- First external contributor

## Support

### Getting Help

If you need help with maintenance:

1. Check existing issues and discussions
2. Refer to `CONTRIBUTING.md` for contribution guidelines
3. Use the issue templates for consistency
4. Engage with the community in Discussions

## Future Enhancements

Ideas for future versions:

- [ ] Additional AI providers (OpenAI, Google Gemini)
- [ ] Command history and favorites
- [ ] Shell completion scripts (bash, zsh, fish)
- [ ] Web UI for configuration
- [ ] Plugin system for extensibility
- [ ] Multi-language support
- [ ] Command explanations (what does this command do?)
- [ ] Dry-run mode (show what would run without executing)

## Security

### API Keys

- Never commit API keys to the repository
- Remind users to keep their config files private
- Configuration files have user-only permissions (600)

### Code Review

- Review all PRs for security issues
- Watch for command injection vulnerabilities
- Validate all user inputs
- Keep dependencies updated

## License

This project is MIT licensed. All contributors agree to license their contributions under MIT.

---

## Questions?

If you have questions about repository maintenance, open an issue with the `question` label.

**Happy maintaining! 🎉**
