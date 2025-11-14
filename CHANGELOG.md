# Changelog

All notable changes to ekko will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-11-14

### Added
- **Shell history logging** for executed commands
  - Automatically logs both the `ekko` command and generated command to shell history
  - Supports multiple shell environments: bash, zsh, and fish
  - Respects `$HISTFILE` environment variable for custom history locations
  - Uses shell-specific history formats:
    - Bash: Simple line-by-line format
    - Zsh: Extended history with timestamps
    - Fish: YAML-like format with metadata
  - Enables searching and recalling past ekko queries with Ctrl+R or arrow keys
  - Commands appear in history exactly as if typed manually

### Improved
- Command execution now integrates seamlessly with shell history
- Users can easily re-run previously generated commands from history
- Better workflow integration with native shell features

### Tests
- Added comprehensive test suite for shell history functionality
- Tests cover all supported shell formats and edge cases

## [1.3.0] - 2025-11-05

### Added
- **Typer CLI framework** for modern command-line interface
  - Maintained flag-based interface (--setup, --config, etc.) for natural language compatibility
  - Better help formatting and error handling
  - Improved command-line parsing and validation
- **Rich terminal output** for enhanced visual experience
  - Beautiful tables for configuration display
  - Colored and styled command output
  - Consistent formatting throughout the application
  - Replaced raw ANSI escape codes with Rich styling

### Changed
- **BREAKING**: Simplified to package-only distribution
  - Removed single-file distribution (build.py and ekko.py)
  - Installation now uses pipx for isolated, portable installation
  - Updated install-ekko.sh to automatically install and use pipx
  - Streamlined build process focuses on Python package
- **Dependencies**:
  - Added typer>=0.9.0 (includes Rich automatically)
  - Updated requirements for better terminal experience
- **Installation**:
  - pipx-based installation for better isolation and cross-platform portability
  - Simpler, more reliable installation process
  - Automatic pipx installation if not present

### Improved
- Configuration display now shows providers in a formatted table
- Command output uses Rich console for better readability
- Error messages and prompts are more visually distinct
- Help text is cleaner and better organized
- Development workflow simplified with package-only focus

### Documentation
- Updated README.md with new installation methods
- Updated DEVELOPMENT.md with Typer patterns and simplified build docs
- Updated CONTRIBUTING.md with Rich usage guidelines
- Updated all examples to reflect new installation process
- Removed single-file build documentation

### Development
- Makefile updated to remove build target
- Test suite updated for new output formats
- Simplified development setup with editable installs
- Package building uses python -m build

## [1.2.0] - 2025-11-05

### Changed
- **BREAKING**: Windows support deprecated - ekko now only supports Linux and macOS
  - Removed Windows-specific code paths and CON console handling
  - Simplified TTY input handling for Unix-like systems
  - Removed Windows installation instructions and references
  - README streamlined and made more concise for better project visibility

### Added
- **Modular architecture** with clean separation of concerns
  - Provider system: Extensible plugin architecture for AI providers
  - Base provider interface for easy third-party provider integration
  - Separate modules: cli.py, config.py, generator.py, providers/
  - Build system: Combines modular code into single-file distribution
- **Dual distribution model**:
  - Development: Modular package structure in `ekko_package/`
  - Distribution: Single-file `ekko.py` for easy installation
  - Package: Proper Python package with setup.py and pyproject.toml
- **Build infrastructure**:
  - `build.py`: Automated single-file builder
  - Generates standalone ekko.py from modular source
  - CI/CD integration for automated builds and releases
- **Enhanced documentation**:
  - DEVELOPMENT.md: Complete architecture and contribution guide
  - Provider documentation in providers/README.md
  - Build process documentation
- **Improved provider system**:
  - Provider registry for auto-discovery
  - Validation methods in base provider class
  - Consistent error handling across providers
- GitHub Actions CI/CD workflow for automated testing and releases

### Planned
- Additional AI provider support (OpenAI, Google Gemini, Cohere)
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
