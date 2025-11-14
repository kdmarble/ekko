# Development Scripts

This directory contains helper scripts for ekko development and release management.

## generate-changelog.sh

Automatically generates changelog entries by analyzing git commits and categorizing them.

### Usage

```bash
# Generate entry for next version (auto-incremented from latest tag)
./scripts/generate-changelog.sh

# Generate entry for specific version
./scripts/generate-changelog.sh 1.5.4
```

### Features

- **Auto-categorization**: Analyzes commit messages and categorizes changes into:
  - Security (fixes, vulnerabilities)
  - Added (new features)
  - Changed (breaking changes, modifications)
  - Fixed (bug fixes)
  - Improved (enhancements, optimizations, refactoring)
  - Tests (test additions/changes)
  - Documentation (docs updates)
  - Development (CI/CD, build changes)

- **Smart detection**: Uses commit message keywords to categorize changes
- **Interactive**: Asks before modifying CHANGELOG.md
- **Backup**: Creates CHANGELOG.md.bak before making changes
- **Preview**: Shows the generated entry before adding

### Workflow

The script will:
1. Analyze all commits since the last tag
2. Categorize them into appropriate sections
3. Generate a formatted changelog entry
4. Ask if you want to add it to CHANGELOG.md
5. Provide next steps for committing and releasing

### Best Practices

For best results, use descriptive commit messages:
- Use keywords like "add", "fix", "improve", "security" to help categorization
- Reference issues/PRs: "Fix authentication bug (#123)"
- Be clear and concise about what changed

### Example Output

```markdown
## [1.5.4] - 2025-11-14

### Fixed
- Fix authentication bug in OAuth flow
- Resolve memory leak in command processor

### Improved
- Optimize command generation performance
- Refactor provider configuration system

### Tests
- Add integration tests for new providers
```

## Automated Release Notes

As of now, the release workflow automatically handles missing changelog entries:

- ✅ **Has CHANGELOG.md entry**: Uses manual changelog content
- ⚙️ **No CHANGELOG.md entry**: Auto-generates from GitHub commits/PRs

This means releases will always have meaningful descriptions, even if you forget to update CHANGELOG.md!
