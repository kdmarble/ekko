#!/usr/bin/env python3
"""
Comprehensive tests for ekko setup wizard using pexpect
Tests the interactive setup process, validation, and configuration
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pexpect


class TestSetupWizard:
    """Test suite for ekko setup wizard"""

    def __init__(self):
        self.test_dir = None
        self.original_config_dir = None
        self.passed = 0
        self.failed = 0

    def setup_test_env(self):
        """Create a temporary test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="ekko_test_")
        self.original_config_dir = os.environ.get('HOME', '')

        # Create a temporary config directory
        config_dir = Path(self.test_dir) / ".config" / "ekko"
        config_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 Test directory: {self.test_dir}")
        return config_dir

    def get_test_env(self):
        """Get environment with test HOME and preserved Python paths"""
        env = os.environ.copy()
        env['HOME'] = self.test_dir
        # Preserve Python path so subprocess can find installed modules
        if 'PYTHONPATH' not in env:
            env['PYTHONPATH'] = ':'.join(sys.path)
        return env

    def cleanup_test_env(self):
        """Clean up test environment"""
        if self.test_dir and Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up test directory")

    def run_test(self, name, test_func):
        """Run a single test and track results"""
        print(f"\n🧪 Testing: {name}")
        try:
            test_func()
            print(f"   ✅ PASSED")
            self.passed += 1
            return True
        except AssertionError as e:
            print(f"   ❌ FAILED: {e}")
            self.failed += 1
            return False
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            self.failed += 1
            return False

    def test_ollama_setup_valid_inputs(self):
        """Test setup wizard with valid Ollama inputs"""
        config_dir = self.setup_test_env()

        # Get test environment with preserved Python paths
        env = self.get_test_env()

        # Run setup wizard
        child = pexpect.spawn(
            'python3', ['-m', 'ekko.cli', '--setup'],
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )

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
            config_file = config_dir / "config.json"
            assert config_file.exists(), "Config file should exist"

            # Verify config contents
            with open(config_file, 'r') as f:
                config = json.load(f)

            assert config['provider'] == 'ollama', "Provider should be ollama"
            assert config['ollama_url'] == 'http://localhost:11434', "Should use default URL"
            assert config['ollama_model'] == 'qwen3-coder', "Should use specified model"

        finally:
            child.close()
            self.cleanup_test_env()

    def test_ollama_setup_custom_url(self):
        """Test setup wizard with custom Ollama URL"""
        config_dir = self.setup_test_env()

        env = self.get_test_env()

        child = pexpect.spawn(
            'python3', ['-m', 'ekko.cli', '--setup'],
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )

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
            config_file = config_dir / "config.json"
            with open(config_file, 'r') as f:
                config = json.load(f)

            assert config['ollama_url'] == 'http://192.168.1.100:11434', "Should use custom URL"
            assert config['ollama_model'] == 'mistral', "Should use specified model"

        finally:
            child.close()
            self.cleanup_test_env()

    def test_invalid_url_validation(self):
        """Test that invalid URLs are rejected"""
        config_dir = self.setup_test_env()

        env = self.get_test_env()

        child = pexpect.spawn(
            'python3', ['-m', 'ekko.cli', '--setup'],
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )

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
            config_file = config_dir / "config.json"
            with open(config_file, 'r') as f:
                config = json.load(f)

            assert config['ollama_url'] == 'http://localhost:11434', "Should save valid URL"

        finally:
            child.close()
            self.cleanup_test_env()

    def test_invalid_model_name_validation(self):
        """Test that suspicious model names are rejected"""
        config_dir = self.setup_test_env()

        env = self.get_test_env()

        child = pexpect.spawn(
            'python3', ['-m', 'ekko.cli', '--setup'],
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )

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
            config_file = config_dir / "config.json"
            with open(config_file, 'r') as f:
                config = json.load(f)

            assert config['ollama_model'] == 'qwen3-coder', "Should use default for invalid model"

        finally:
            child.close()
            self.cleanup_test_env()

    def test_corrupted_config_detection(self):
        """Test that corrupted config files are detected"""
        config_dir = self.setup_test_env()

        # Create a corrupted config (like the bug we fixed)
        config_file = config_dir / "config.json"
        corrupted_config = {
            "provider": "ollama",
            "ollama_url": "# Final instructions",
            "ollama_model": "echo -e \"Installation complete!\"",
            "anthropic_api_key": "",
            "anthropic_model": "claude-sonnet-4-5-20250929",
            "system_prompt": "You are a shell expert."
        }

        with open(config_file, 'w') as f:
            json.dump(corrupted_config, f)

        env = self.get_test_env()

        # Try to run ekko with corrupted config
        child = pexpect.spawn(
            'python3', ['-m', 'ekko.cli', '--help'],
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )

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
            self.cleanup_test_env()

    def test_anthropic_setup_valid_inputs(self):
        """Test setup wizard with valid Anthropic inputs"""
        config_dir = self.setup_test_env()

        env = self.get_test_env()

        child = pexpect.spawn(
            'python3', ['-m', 'ekko.cli', '--setup'],
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )

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
            config_file = config_dir / "config.json"
            with open(config_file, 'r') as f:
                config = json.load(f)

            assert config['provider'] == 'anthropic', "Provider should be anthropic"
            assert config['anthropic_api_key'] == 'sk-ant-test1234567890abcdefghij', "Should save API key"
            assert config['anthropic_model'] == 'claude-sonnet-4-5-20250929', "Should use default model"

        finally:
            child.close()
            self.cleanup_test_env()

    def test_invalid_api_key_validation(self):
        """Test that invalid API keys are rejected"""
        config_dir = self.setup_test_env()

        env = self.get_test_env()

        child = pexpect.spawn(
            'python3', ['-m', 'ekko.cli', '--setup'],
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )

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
            self.cleanup_test_env()

    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success rate: {(self.passed/total*100):.1f}%")
        print(f"{'='*60}\n")

        return self.failed == 0


def main():
    """Run all tests"""
    print("="*60)
    print("EKKO SETUP WIZARD TEST SUITE")
    print("="*60)

    tester = TestSetupWizard()

    # Run all tests
    tester.run_test("Ollama setup with valid inputs",
                   tester.test_ollama_setup_valid_inputs)

    tester.run_test("Ollama setup with custom URL",
                   tester.test_ollama_setup_custom_url)

    tester.run_test("Invalid URL validation",
                   tester.test_invalid_url_validation)

    tester.run_test("Invalid model name validation",
                   tester.test_invalid_model_name_validation)

    tester.run_test("Corrupted config detection",
                   tester.test_corrupted_config_detection)

    tester.run_test("Anthropic setup with valid inputs",
                   tester.test_anthropic_setup_valid_inputs)

    tester.run_test("Invalid API key validation",
                   tester.test_invalid_api_key_validation)

    # Print summary
    success = tester.print_summary()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
