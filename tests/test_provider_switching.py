#!/usr/bin/env python3
"""
Tests for ekko provider and model switching functionality
Tests --switch, --model, --use, and --config commands
"""

import os
import sys
import json
import tempfile
import shutil
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestProviderSwitching:
    """Test suite for provider switching functionality"""

    def __init__(self):
        self.test_dir = None
        self.passed = 0
        self.failed = 0
        self.ekko_script = Path(__file__).parent.parent / "ekko.py"

    def setup_test_env(self):
        """Create a temporary test environment with pre-configured ekko"""
        self.test_dir = tempfile.mkdtemp(prefix="ekko_test_")

        # Create config directory
        config_dir = Path(self.test_dir) / ".config" / "ekko"
        config_dir.mkdir(parents=True, exist_ok=True)

        # Create a valid config with both providers configured
        config_file = config_dir / "config.json"
        config = {
            "provider": "ollama",
            "anthropic_api_key": "sk-ant-test1234567890abcdefghij",
            "anthropic_model": "claude-sonnet-4-5-20250929",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "qwen3-coder",
            "system_prompt": "You are a shell expert. Output ONLY the command."
        }

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"📁 Test directory: {self.test_dir}")
        return config_dir

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

    def run_ekko(self, args, env=None):
        """Helper to run ekko command and return output"""
        if env is None:
            env = os.environ.copy()
            env['HOME'] = self.test_dir

        result = subprocess.run(
            ['python3', str(self.ekko_script)] + args,
            env=env,
            capture_output=True,
            text=True
        )
        return result

    def get_config(self):
        """Helper to read current config"""
        config_file = Path(self.test_dir) / ".config" / "ekko" / "config.json"
        with open(config_file, 'r') as f:
            return json.load(f)

    def test_config_display(self):
        """Test --config command displays configuration"""
        self.setup_test_env()

        try:
            result = self.run_ekko(['--config'])

            assert result.returncode == 0, "Should exit successfully"
            assert "ekko configuration" in result.stdout, "Should show config header"
            assert "Active: ollama" in result.stdout, "Should show active provider"
            assert "qwen3-coder" in result.stdout, "Should show current model"
            assert "Available: anthropic" in result.stdout, "Should show other provider"
            assert "sk-ant-..." in result.stdout, "Should mask API key"

        finally:
            self.cleanup_test_env()

    def test_switch_provider(self):
        """Test --switch command changes provider"""
        self.setup_test_env()

        try:
            # Switch to Anthropic
            result = self.run_ekko(['--switch', 'anthropic'])

            assert result.returncode == 0, "Should exit successfully"
            assert "Switched to anthropic" in result.stdout, "Should confirm switch"

            # Verify config was updated
            config = self.get_config()
            assert config['provider'] == 'anthropic', "Provider should be anthropic"
            assert config['ollama_model'] == 'qwen3-coder', "Ollama settings should persist"

        finally:
            self.cleanup_test_env()

    def test_switch_invalid_provider(self):
        """Test --switch rejects invalid provider"""
        self.setup_test_env()

        try:
            result = self.run_ekko(['--switch', 'openai'])

            assert result.returncode != 0, "Should exit with error"
            output = result.stdout + result.stderr
            assert "Invalid provider" in output, "Should show error message"
            assert "Valid providers:" in output, "Should show valid options"

            # Verify config was not changed
            config = self.get_config()
            assert config['provider'] == 'ollama', "Provider should remain ollama"

        finally:
            self.cleanup_test_env()

    def test_switch_unconfigured_provider(self):
        """Test --switch rejects unconfigured provider"""
        config_dir = self.setup_test_env()

        try:
            # Remove Anthropic API key to make it unconfigured
            config_file = config_dir / "config.json"
            config = self.get_config()
            config['anthropic_api_key'] = ""
            with open(config_file, 'w') as f:
                json.dump(config, f)

            # Try to switch to unconfigured Anthropic
            result = self.run_ekko(['--switch', 'anthropic'])

            assert result.returncode != 0, "Should exit with error"
            output = result.stdout + result.stderr
            assert "not configured" in output, "Should show not configured error"
            assert "ekko --setup" in output, "Should suggest running setup"

        finally:
            self.cleanup_test_env()

    def test_switch_model(self):
        """Test --model command changes model for current provider"""
        self.setup_test_env()

        try:
            # Change Ollama model
            result = self.run_ekko(['--model', 'llama3'])

            assert result.returncode == 0, "Should exit successfully"
            assert "Changed ollama model to llama3" in result.stdout, "Should confirm change"

            # Verify config was updated
            config = self.get_config()
            assert config['ollama_model'] == 'llama3', "Model should be updated"
            assert config['provider'] == 'ollama', "Provider should remain same"

        finally:
            self.cleanup_test_env()

    def test_switch_model_invalid(self):
        """Test --model rejects suspicious model names"""
        self.setup_test_env()

        try:
            # Try to use suspicious model name
            result = self.run_ekko(['--model', 'echo "malicious"'])

            assert result.returncode != 0, "Should exit with error"
            output = result.stdout + result.stderr
            assert "Invalid model name" in output, "Should show validation error"

        finally:
            self.cleanup_test_env()

    def test_use_command_with_both(self):
        """Test --use command with provider:model"""
        self.setup_test_env()

        try:
            # Use combo command
            result = self.run_ekko(['--use', 'anthropic:claude-opus-4'])

            assert result.returncode == 0, "Should exit successfully"
            assert "Switched to anthropic" in result.stdout, "Should show provider switch"
            assert "Changed anthropic model" in result.stdout, "Should show model change"

            # Verify config was updated
            config = self.get_config()
            assert config['provider'] == 'anthropic', "Provider should be anthropic"
            assert config['anthropic_model'] == 'claude-opus-4', "Model should be updated"

        finally:
            self.cleanup_test_env()

    def test_use_command_provider_only(self):
        """Test --use command with just provider name"""
        self.setup_test_env()

        try:
            # Use command with just provider
            result = self.run_ekko(['--use', 'anthropic'])

            assert result.returncode == 0, "Should exit successfully"
            assert "Switched to anthropic" in result.stdout, "Should show provider switch"

            # Verify config was updated
            config = self.get_config()
            assert config['provider'] == 'anthropic', "Provider should be anthropic"
            assert config['anthropic_model'] == 'claude-sonnet-4-5-20250929', "Model should remain default"

        finally:
            self.cleanup_test_env()

    def test_settings_persistence(self):
        """Test that settings persist when switching between providers"""
        self.setup_test_env()

        try:
            # Change Ollama model
            self.run_ekko(['--model', 'llama3'])

            # Switch to Anthropic and change its model
            self.run_ekko(['--switch', 'anthropic'])
            self.run_ekko(['--model', 'claude-opus-4'])

            # Switch back to Ollama
            result = self.run_ekko(['--switch', 'ollama'])

            # Verify Ollama still has llama3
            assert "llama3" in result.stdout, "Should show llama3 model"

            config = self.get_config()
            assert config['ollama_model'] == 'llama3', "Ollama model should persist"
            assert config['anthropic_model'] == 'claude-opus-4', "Anthropic model should persist"

        finally:
            self.cleanup_test_env()

    def test_help_shows_new_commands(self):
        """Test that --help shows new switching commands"""
        self.setup_test_env()

        try:
            result = self.run_ekko(['--help'])

            assert result.returncode == 0, "Should exit successfully"
            assert "--config" in result.stdout, "Should document --config"
            assert "--switch" in result.stdout, "Should document --switch"
            assert "--model" in result.stdout, "Should document --model"
            assert "--use" in result.stdout, "Should document --use"
            assert "Provider Management:" in result.stdout, "Should have examples section"

        finally:
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
    print("EKKO PROVIDER SWITCHING TEST SUITE")
    print("="*60)

    tester = TestProviderSwitching()

    # Run all tests
    tester.run_test("Display configuration with --config",
                   tester.test_config_display)

    tester.run_test("Switch provider with --switch",
                   tester.test_switch_provider)

    tester.run_test("Reject invalid provider",
                   tester.test_switch_invalid_provider)

    tester.run_test("Reject unconfigured provider",
                   tester.test_switch_unconfigured_provider)

    tester.run_test("Change model with --model",
                   tester.test_switch_model)

    tester.run_test("Reject invalid model name",
                   tester.test_switch_model_invalid)

    tester.run_test("Use command with provider:model",
                   tester.test_use_command_with_both)

    tester.run_test("Use command with provider only",
                   tester.test_use_command_provider_only)

    tester.run_test("Settings persist across switches",
                   tester.test_settings_persistence)

    tester.run_test("Help shows new commands",
                   tester.test_help_shows_new_commands)

    # Print summary
    success = tester.print_summary()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
