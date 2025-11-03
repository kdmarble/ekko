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

- **1.0.1** - Bug fixes for installation and configuration validation
- **1.0.0** - Initial public release

## Links

- [Repository](https://github.com/kdmarble/ekko)
- [Issues](https://github.com/kdmarble/ekko/issues)
- [Discussions](https://github.com/kdmarble/ekko/discussions)
