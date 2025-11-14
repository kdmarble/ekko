"""
Tests for ekko provider and model switching functionality.
Tests --switch, --model, --use, and --config commands.
"""

import pytest


class TestProviderSwitching:
    """Test suite for provider switching functionality"""

    def test_config_display(self, preconfigured_env, ekko_runner):
        """Test --config command displays configuration"""
        result = ekko_runner(['--config'])

        assert result.returncode == 0, "Should exit successfully"
        assert "ekko Configuration" in result.stdout, "Should show config header"
        assert "ollama" in result.stdout, "Should show ollama provider"
        assert "Active" in result.stdout, "Should show active status"
        assert "qwen3-coder" in result.stdout, "Should show current model"
        assert "anthropic" in result.stdout, "Should show anthropic provider"
        assert "sk-ant-..." in result.stdout, "Should mask API key"

    def test_switch_provider(self, preconfigured_env, ekko_runner, read_config):
        """Test --switch command changes provider"""
        # Switch to Anthropic
        result = ekko_runner(['--switch', 'anthropic'])

        assert result.returncode == 0, "Should exit successfully"
        assert "Switched to anthropic" in result.stdout, "Should confirm switch"

        # Verify config was updated
        config = read_config()
        assert config['provider'] == 'anthropic', "Provider should be anthropic"
        assert config['ollama_model'] == 'qwen3-coder', "Ollama settings should persist"

    def test_switch_invalid_provider(self, preconfigured_env, ekko_runner, read_config):
        """Test --switch rejects invalid provider"""
        result = ekko_runner(['--switch', 'openai'])

        assert result.returncode != 0, "Should exit with error"
        output = result.stdout + result.stderr
        assert "Invalid provider" in output, "Should show error message"
        assert "Valid providers:" in output, "Should show valid options"

        # Verify config was not changed
        config = read_config()
        assert config['provider'] == 'ollama', "Provider should remain ollama"

    def test_switch_unconfigured_provider(self, write_config, ekko_runner):
        """Test --switch rejects unconfigured provider"""
        # Create config with only Ollama configured
        config = {
            "provider": "ollama",
            "anthropic_api_key": "",  # Empty = unconfigured
            "anthropic_model": "claude-sonnet-4-5-20250929",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "qwen3-coder",
            "system_prompt": "You are a shell expert."
        }
        write_config(config)

        # Try to switch to unconfigured Anthropic
        result = ekko_runner(['--switch', 'anthropic'])

        assert result.returncode != 0, "Should exit with error"
        output = result.stdout + result.stderr
        assert "not configured" in output, "Should show not configured error"
        assert "ekko --setup" in output, "Should suggest running setup"

    def test_switch_model(self, preconfigured_env, ekko_runner, read_config):
        """Test --model command changes model for current provider"""
        # Change Ollama model
        result = ekko_runner(['--model', 'llama3'])

        assert result.returncode == 0, "Should exit successfully"
        assert "Changed ollama model to llama3" in result.stdout, "Should confirm change"

        # Verify config was updated
        config = read_config()
        assert config['ollama_model'] == 'llama3', "Model should be updated"
        assert config['provider'] == 'ollama', "Provider should remain same"

    def test_switch_model_invalid(self, preconfigured_env, ekko_runner):
        """Test --model rejects suspicious model names"""
        # Try to use suspicious model name
        result = ekko_runner(['--model', 'echo "malicious"'])

        assert result.returncode != 0, "Should exit with error"
        output = result.stdout + result.stderr
        assert "Invalid model name" in output, "Should show validation error"

    def test_use_command_with_both(self, preconfigured_env, ekko_runner, read_config):
        """Test --use command with provider:model"""
        # Use combo command
        result = ekko_runner(['--use', 'anthropic:claude-opus-4'])

        assert result.returncode == 0, "Should exit successfully"
        assert "Switched to anthropic" in result.stdout, "Should show provider switch"
        assert "Changed anthropic model" in result.stdout, "Should show model change"

        # Verify config was updated
        config = read_config()
        assert config['provider'] == 'anthropic', "Provider should be anthropic"
        assert config['anthropic_model'] == 'claude-opus-4', "Model should be updated"

    def test_use_command_provider_only(self, preconfigured_env, ekko_runner, read_config):
        """Test --use command with just provider name"""
        # Use command with just provider
        result = ekko_runner(['--use', 'anthropic'])

        assert result.returncode == 0, "Should exit successfully"
        assert "Switched to anthropic" in result.stdout, "Should show provider switch"

        # Verify config was updated
        config = read_config()
        assert config['provider'] == 'anthropic', "Provider should be anthropic"
        assert config['anthropic_model'] == 'claude-sonnet-4-5-20250929', "Model should remain default"

    def test_settings_persistence(self, preconfigured_env, ekko_runner, read_config):
        """Test that settings persist when switching between providers"""
        # Change Ollama model
        ekko_runner(['--model', 'llama3'])

        # Switch to Anthropic and change its model
        ekko_runner(['--switch', 'anthropic'])
        ekko_runner(['--model', 'claude-opus-4'])

        # Switch back to Ollama
        result = ekko_runner(['--switch', 'ollama'])

        # Verify Ollama still has llama3
        assert "llama3" in result.stdout, "Should show llama3 model"

        config = read_config()
        assert config['ollama_model'] == 'llama3', "Ollama model should persist"
        assert config['anthropic_model'] == 'claude-opus-4', "Anthropic model should persist"

    def test_help_shows_new_commands(self, preconfigured_env, ekko_runner):
        """Test that --help shows new switching commands"""
        result = ekko_runner(['--help'])

        assert result.returncode == 0, "Should exit successfully"
        assert "--config" in result.stdout, "Should document --config"
        assert "--switch" in result.stdout, "Should document --switch"
        assert "--model" in result.stdout, "Should document --model"
        assert "--use" in result.stdout, "Should document --use"
        assert "Provider Management:" in result.stdout, "Should have examples section"
