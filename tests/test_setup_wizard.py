"""
Comprehensive tests for ekko setup wizard using pexpect.
Tests the interactive setup process, validation, and configuration.
"""

import json

import pexpect
import pytest


class TestSetupWizard:
    """Test suite for ekko setup wizard"""

    def test_ollama_setup_valid_inputs(self, pexpect_runner, config_path):
        """Test setup wizard with valid Ollama inputs"""
        child = pexpect_runner(['--setup'])

        try:
            # Expect provider choice
            child.expect('Enter choice .*:')
            child.sendline('1')  # Ollama

            # Expect Ollama URL prompt with default
            child.expect('Ollama URL .*:')
            child.sendline('')  # Use default

            # Expect model prompt
            child.expect('Model .*:')
            child.sendline('qwen3-coder')

            # Wait for completion
            child.expect('Configuration saved')
            child.expect(pexpect.EOF, timeout=2)

            # Verify config file was created
            assert config_path.exists(), "Config file should exist"

            # Verify config contents
            with open(config_path, 'r') as f:
                config = json.load(f)

            assert config['provider'] == 'ollama', "Provider should be ollama"
            assert config['ollama_url'] == 'http://localhost:11434', "Should use default URL"
            assert config['ollama_model'] == 'qwen3-coder', "Should use specified model"

        finally:
            child.close()

    def test_ollama_setup_custom_url(self, pexpect_runner, config_path):
        """Test setup wizard with custom Ollama URL"""
        child = pexpect_runner(['--setup'])

        try:
            child.expect('Enter choice .*:')
            child.sendline('1')  # Ollama

            child.expect('Ollama URL .*:')
            child.sendline('http://192.168.1.100:11434')  # Custom URL

            child.expect('Model .*:')
            child.sendline('mistral')

            child.expect('Configuration saved')
            child.expect(pexpect.EOF, timeout=2)

            # Verify config
            with open(config_path, 'r') as f:
                config = json.load(f)

            assert config['ollama_url'] == 'http://192.168.1.100:11434', "Should use custom URL"
            assert config['ollama_model'] == 'mistral', "Should use specified model"

        finally:
            child.close()

    def test_invalid_url_validation(self, pexpect_runner, config_path):
        """Test that invalid URLs are rejected"""
        child = pexpect_runner(['--setup'])

        try:
            child.expect('Enter choice .*:')
            child.sendline('1')  # Ollama

            child.expect('Ollama URL .*:')
            child.sendline('localhost:11434')  # Invalid - no protocol

            # Should see validation error
            child.expect('Invalid URL format')

            # Try again with valid URL
            child.expect('Ollama URL .*:')
            child.sendline('http://localhost:11434')  # Valid

            child.expect('Model .*:')
            child.sendline('qwen3-coder')

            child.expect('Configuration saved')
            child.expect(pexpect.EOF, timeout=2)

            # Verify valid config was saved
            with open(config_path, 'r') as f:
                config = json.load(f)

            assert config['ollama_url'] == 'http://localhost:11434', "Should save valid URL"

        finally:
            child.close()

    def test_invalid_model_name_validation(self, pexpect_runner, config_path):
        """Test that suspicious model names are rejected"""
        child = pexpect_runner(['--setup'])

        try:
            child.expect('Enter choice .*:')
            child.sendline('1')  # Ollama

            child.expect('Ollama URL .*:')
            child.sendline('')  # Default

            child.expect('Model .*:')
            child.sendline('echo "malicious" && rm -rf /')  # Suspicious

            # Should see validation warning and use default
            child.expect('Invalid model name')

            child.expect('Configuration saved')
            child.expect(pexpect.EOF, timeout=2)

            # Verify default model was used
            with open(config_path, 'r') as f:
                config = json.load(f)

            assert config['ollama_model'] == 'qwen3-coder', "Should use default for invalid model"

        finally:
            child.close()

    def test_corrupted_config_detection(self, write_config, pexpect_runner):
        """Test that corrupted config files are detected"""
        # Create a corrupted config (like the bug we fixed)
        corrupted_config = {
            "provider": "ollama",
            "ollama_url": "# Final instructions",
            "ollama_model": "echo -e \"Installation complete!\"",
            "anthropic_api_key": "",
            "anthropic_model": "claude-sonnet-4-5-20250929",
            "system_prompt": "You are a shell expert."
        }

        write_config(corrupted_config)

        # Try to run ekko with corrupted config
        child = pexpect_runner(['--config'])

        try:
            # Should detect invalid config
            child.expect('Invalid Ollama URL')
            child.expect('Configuration file appears to be corrupted')
            child.expect('ekko --setup')

            # Should exit with error
            child.expect(pexpect.EOF, timeout=2)
            assert child.exitstatus != 0, "Should exit with error for corrupted config"

        finally:
            child.close()

    def test_anthropic_setup_valid_inputs(self, pexpect_runner, config_path):
        """Test setup wizard with valid Anthropic inputs"""
        child = pexpect_runner(['--setup'])

        try:
            child.expect('Enter choice .*:')
            child.sendline('2')  # Anthropic

            child.expect('Enter Anthropic API key:')
            child.sendline('sk-ant-test1234567890abcdefghij')  # Valid format

            child.expect('Model .*:')
            child.sendline('')  # Use default

            child.expect('Configuration saved')
            child.expect(pexpect.EOF, timeout=2)

            # Verify config
            with open(config_path, 'r') as f:
                config = json.load(f)

            assert config['provider'] == 'anthropic', "Provider should be anthropic"
            assert config['anthropic_api_key'] == 'sk-ant-test1234567890abcdefghij', "Should save API key"
            assert config['anthropic_model'] == 'claude-sonnet-4-5-20250929', "Should use default model"

        finally:
            child.close()

    def test_invalid_api_key_validation(self, pexpect_runner, config_path):
        """Test that invalid API keys are rejected"""
        child = pexpect_runner(['--setup'])

        try:
            child.expect('Enter choice .*:')
            child.sendline('2')  # Anthropic

            child.expect('Enter Anthropic API key:')
            child.sendline('short')  # Too short

            # Should see validation error
            child.expect('Invalid API key format')

            # Try again with valid key
            child.expect('Enter Anthropic API key:')
            child.sendline('sk-ant-valid-key-1234567890')

            child.expect('Model .*:')
            child.sendline('')

            child.expect('Configuration saved')
            child.expect(pexpect.EOF, timeout=2)

        finally:
            child.close()
