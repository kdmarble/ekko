"""
Tests for backwards compatibility with legacy config formats.
Ensures current version works seamlessly with historical config formats.
"""

import pytest
from conftest import REQUIRED_CONFIG_KEYS, VALID_PROVIDERS


class TestBackwardsCompatibility:
    """Test suite for backwards compatibility with legacy configs"""

    @pytest.mark.parametrize("config_fixture", [
        "v101_ollama_config",
        "v101_anthropic_config",
        "v101_both_providers_config",
    ])
    def test_legacy_config_loads_successfully(
        self, config_fixture, request, write_config, ekko_runner, current_version
    ):
        """
        Test that legacy config formats load without errors.
        This ensures users can upgrade without manual migration.
        """
        # Get the config fixture by name
        legacy_config = request.getfixturevalue(config_fixture)
        write_config(legacy_config)

        # Test that version command works (validates config loads)
        result = ekko_runner(['--version'])
        assert result.returncode == 0, f"Failed to load {config_fixture}"
        assert current_version in result.stdout, "Should display current version"

    def test_v101_ollama_only_config_operations(
        self, v101_ollama_config, write_config, ekko_runner, read_config
    ):
        """Test v1.0.1 Ollama-only config with various operations"""
        write_config(v101_ollama_config)

        # Test --config command displays settings
        result = ekko_runner(['--config'])
        assert result.returncode == 0
        assert "ollama" in result.stdout.lower()
        assert "qwen3-coder" in result.stdout

        # Test --model command updates model
        result = ekko_runner(['--model', 'llama3'])
        assert result.returncode == 0

        # Verify config structure preserved
        config = read_config()
        assert config['ollama_model'] == 'llama3'
        assert config['provider'] == 'ollama'
        assert all(key in config for key in REQUIRED_CONFIG_KEYS)

    def test_v101_anthropic_only_config_operations(
        self, v101_anthropic_config, write_config, ekko_runner, read_config
    ):
        """Test v1.0.1 Anthropic-only config with various operations"""
        write_config(v101_anthropic_config)

        # Test config displays correctly
        result = ekko_runner(['--config'])
        assert result.returncode == 0
        assert "anthropic" in result.stdout.lower()

        # Test model switching
        result = ekko_runner(['--model', 'claude-opus-4'])
        assert result.returncode == 0

        config = read_config()
        assert config['anthropic_model'] == 'claude-opus-4'
        assert config['anthropic_api_key'] == 'sk-ant-test123456789'
        assert all(key in config for key in REQUIRED_CONFIG_KEYS)

    def test_v101_both_providers_switching(
        self, v101_both_providers_config, write_config, ekko_runner, read_config
    ):
        """Test provider switching preserves settings for both providers"""
        write_config(v101_both_providers_config)

        # Switch to Anthropic
        result = ekko_runner(['--switch', 'anthropic'])
        assert result.returncode == 0

        config = read_config()
        assert config['provider'] == 'anthropic'
        # Ollama settings should be preserved
        assert config['ollama_model'] == 'mistral'
        assert config['ollama_url'] == 'http://192.168.1.100:11434'

        # Switch back to Ollama
        result = ekko_runner(['--switch', 'ollama'])
        assert result.returncode == 0

        config = read_config()
        assert config['provider'] == 'ollama'
        # Anthropic settings should be preserved
        assert config['anthropic_model'] == 'claude-3-opus-20240229'
        assert config['anthropic_api_key'] == 'sk-ant-original-key-123'

    def test_config_schema_preserved(
        self, v101_ollama_config, write_config, ekko_runner, read_config
    ):
        """Verify config JSON schema remains unchanged after operations"""
        write_config(v101_ollama_config)
        original_keys = set(v101_ollama_config.keys())

        # Run operation that reads config
        result = ekko_runner(['--version'])
        assert result.returncode == 0

        # Verify structure hasn't changed
        config = read_config()
        assert set(config.keys()) == original_keys
        assert isinstance(config['provider'], str)
        assert isinstance(config['anthropic_api_key'], str)
        assert isinstance(config['ollama_url'], str)
        assert config['provider'] in VALID_PROVIDERS

    def test_no_migration_required(
        self, v101_anthropic_config, write_config, ekko_runner, read_config
    ):
        """Verify that loading legacy config doesn't modify it"""
        write_config(v101_anthropic_config)
        original_config = read_config()

        # Just load config (don't modify)
        result = ekko_runner(['--help'])
        assert result.returncode == 0

        # Verify config is completely unchanged
        current_config = read_config()
        assert current_config == original_config

    @pytest.mark.parametrize("operation,args", [
        ("config_display", ['--config']),
        ("help", ['--help']),
        ("version", ['--version']),
    ])
    def test_readonly_operations_preserve_config(
        self, v101_ollama_config, write_config, ekko_runner, read_config, operation, args
    ):
        """Test that read-only operations never modify config"""
        write_config(v101_ollama_config)
        original_config = read_config()

        result = ekko_runner(args)
        assert result.returncode == 0

        current_config = read_config()
        assert current_config == original_config, f"{operation} should not modify config"

    def test_custom_ollama_url_preserved(
        self, write_config, ekko_runner, read_config
    ):
        """Test that custom Ollama URLs are preserved across operations"""
        custom_config = {
            "provider": "ollama",
            "anthropic_api_key": "",
            "anthropic_model": "claude-sonnet-4-5-20250929",
            "ollama_url": "http://custom-host.local:8080",
            "ollama_model": "qwen3-coder",
            "system_prompt": "You are a shell expert."
        }
        write_config(custom_config)

        # Switch provider and back
        ekko_runner(['--switch', 'anthropic'])
        ekko_runner(['--switch', 'ollama'])

        config = read_config()
        assert config['ollama_url'] == 'http://custom-host.local:8080'

    def test_empty_api_key_preserved(
        self, v101_ollama_config, write_config, ekko_runner, read_config
    ):
        """Test that empty API keys remain empty (not replaced with defaults)"""
        write_config(v101_ollama_config)
        assert v101_ollama_config['anthropic_api_key'] == ""

        # Run various operations
        ekko_runner(['--config'])
        ekko_runner(['--model', 'llama3'])

        config = read_config()
        assert config['anthropic_api_key'] == ""
