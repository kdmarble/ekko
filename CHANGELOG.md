# Changelog

All notable changes to ekko will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Additional AI provider support (OpenAI, Google Gemini)
- Command history and favorites
- Bash/Zsh completion scripts
- Configuration profiles for different use cases

## [1.1.1] - 2025-11-03

### Fixed
- **Critical installer bug**: Installers now preserve existing configuration files
  - Previously, re-running the installer would overwrite existing configs
  - Both `install-ekko.sh` and `install-ekko.ps1` now check for existing `config.json`
  - If config exists, installation skips setup wizard and preserves all settings
  - New installs still run the setup wizard as expected
  - Prevents accidental loss of API keys, custom models, and other settings

### Changed
- Installers now display helpful message when config is preserved
- Users informed they can run `ekko --setup` manually to reconfigure if needed

## [1.1.0] - 2025-11-02

### Added
- **Provider switching system**: Easy switching between AI providers without re-running setup
  - `ekko --config` - Show current configuration with masked API keys
  - `ekko --switch <provider>` - Switch to a different AI provider (ollama, anthropic)
  - `ekko --model <name>` - Change model for the currently active provider
  - `ekko --use <provider>:<model>` - Combo command to switch both provider and model at once
- **Settings persistence**: All provider configurations persist when switching
  - Ollama settings remain saved when using Anthropic
  - Anthropic settings remain saved when using Ollama
  - No need to reconfigure each time you switch
- **Enhanced help**: Updated `--help` output with provider management examples

### Changed
- Configuration structure already supports multiple providers simultaneously
- Setup wizard only modifies the active provider's settings, preserving others
- Help text now includes "Provider Management" section with examples

### Tests
- Added `test_provider_switching.py` with 10 comprehensive tests
- Added `test_upgrade_compatibility.py` with 5 upgrade tests
- All 24 tests passing (7 setup + 2 installation + 10 switching + 5 upgrade)
- Test coverage for: switching providers, changing models, settings persistence, error handling, upgrade compatibility

### Upgrade from v1.0.1
- **No migration required** - v1.1.0 is fully backward compatible with v1.0.1 configs
- Existing configs work seamlessly without any changes
- New switching commands work immediately with old configs
- Both provider settings are preserved during upgrade
- Simply update ekko and start using the new features!

### Benefits
- **Scalable design**: Easy to add new providers (OpenAI, Gemini, etc.) in the future
- **Better UX**: No need to run `ekko --setup` just to switch providers
- **Transparent**: `--config` command shows what's configured and what's active
- **Fast**: One-command switching between your favorite setups

## [1.0.1] - 2025-11-02

### Fixed
- **Critical installation bug**: Fixed setup wizard reading from piped script instead of user terminal
  - When installing via `curl ... | bash`, the wizard would read bash script content instead of user input
  - This caused "# Final instructions" to be saved as the Ollama URL
  - Solution: Added `/dev/tty` redirection in install-ekko.sh and TTY input handling in Python
- **Input validation**: Added comprehensive validation for all configuration inputs
  - URL validation ensures proper http:// or https:// format
  - Model name validation detects suspicious patterns (bash commands, injection attempts)
  - API key validation checks format and length
- **Config file validation**: Added validation when loading configuration
  - Detects corrupted or invalid config files on startup
  - Provides clear error messages with instructions to reconfigure
  - Prevents cryptic errors from invalid configuration
- **Error messages**: Improved error messages in LLM providers
  - Added helpful troubleshooting steps for connection failures
  - Suggests running `ekko --setup` to reconfigure
  - Provides specific guidance based on error type

### Changed
- Setup wizard now reads from TTY/console instead of stdin for better piped installation support
- Configuration loading now includes validation and fails fast with helpful messages
- Both Windows (install-ekko.ps1) and Unix (install-ekko.sh) installers updated for consistency

## [1.0.0] - 2025-01-XX

### Added
- Initial release of ekko
- Interactive command generation from natural language
- Anthropic API integration (Claude Sonnet, Opus, Haiku)
- Ollama local model integration
- Interactive approve/deny/correct workflow
- Cross-platform support (Linux, macOS, Windows, WSL)
- Automatic installers for all platforms
- Setup wizard for easy configuration
- Configuration management via JSON file
- Command cleaning and formatting
- Comprehensive documentation
- MIT License

### Features
- Multiple AI provider support
- Iterative command refinement
- Error handling and user guidance
- Shell integration (bash, zsh, fish, PowerShell)
- Model selection for both Anthropic and Ollama
- Customizable system prompts

### Documentation
- Complete README with installation and usage
- QUICKSTART guide for fast setup
- CONTRIBUTING guidelines for open-source contributors
- CODE_OF_CONDUCT for community standards
- Comprehensive inline code documentation

---

## Version History

- **1.1.1** - Hotfix for installer config preservation
- **1.1.0** - Provider switching system and enhanced configuration management
- **1.0.1** - Bug fixes for installation and configuration validation
- **1.0.0** - Initial public release

## Links

- [Repository](https://github.com/kdmarble/ekko)
- [Issues](https://github.com/kdmarble/ekko/issues)
- [Discussions](https://github.com/kdmarble/ekko/discussions)
