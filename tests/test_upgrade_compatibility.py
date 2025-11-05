#!/usr/bin/env python3
"""
Tests for ekko version upgrade compatibility
Ensures v1.3.0 works seamlessly with v1.0.1 configs
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


class TestUpgradeCompatibility:
    """Test suite for version upgrade compatibility"""

    def __init__(self):
        self.test_dir = None
        self.passed = 0
        self.failed = 0
        self.ekko_package = Path(__file__).parent.parent / "ekko_package"

    def setup_test_env(self, config_data):
        """Create a test environment with a specific config version"""
        self.test_dir = tempfile.mkdtemp(prefix="ekko_upgrade_test_")

        # Create config directory
        config_dir = Path(self.test_dir) / ".config" / "ekko"
        config_dir.mkdir(parents=True, exist_ok=True)

        # Create config file
        config_file = config_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

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
            # Add package to Python path
            env['PYTHONPATH'] = str(self.ekko_package)

        result = subprocess.run(
            ['python3', '-m', 'ekko.cli'] + args,
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

    def test_v101_ollama_only_config(self):
        """Test v1.0.1 config with only Ollama configured"""
        # Typical v1.0.1 config from a user who chose Ollama
        v101_config = {
            "provider": "ollama",
            "anthropic_api_key": "",
            "anthropic_model": "claude-sonnet-4-5-20250929",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "qwen3-coder",
            "system_prompt": "You are a shell expert. Output ONLY the command to solve the problem. No explanation, no markdown, no backticks - just the raw shell command."
        }

        self.setup_test_env(v101_config)

        try:
            # Test that v1.3.0 can load v1.0.1 config
            result = self.run_ekko(['--version'])
            assert result.returncode == 0, "Should load v1.0.1 config successfully"
            assert "v1.3.0" in result.stdout, "Should report v1.3.0"

            # Test new --config command works
            result = self.run_ekko(['--config'])
            assert result.returncode == 0, "Should display config"
            assert "ollama" in result.stdout and "qwen3-coder" in result.stdout, "Should show old settings"

            # Test new --model command works
            result = self.run_ekko(['--model', 'llama3'])
            assert result.returncode == 0, "Should update model"

            # Verify config structure preserved
            config = self.get_config()
            assert config['ollama_model'] == 'llama3', "Should update model"
            assert config['provider'] == 'ollama', "Provider should remain"
            assert all(key in config for key in v101_config.keys()), "All keys preserved"

        finally:
            self.cleanup_test_env()

    def test_v101_anthropic_only_config(self):
        """Test v1.0.1 config with only Anthropic configured"""
        # Typical v1.0.1 config from a user who chose Anthropic
        v101_config = {
            "provider": "anthropic",
            "anthropic_api_key": "sk-ant-test123456789",
            "anthropic_model": "claude-sonnet-4-5-20250929",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "qwen3-coder",
            "system_prompt": "You are a shell expert. Output ONLY the command to solve the problem. No explanation, no markdown, no backticks - just the raw shell command."
        }

        self.setup_test_env(v101_config)

        try:
            # Test that v1.3.0 can load and display Anthropic config
            result = self.run_ekko(['--config'])
            assert result.returncode == 0, "Should load config"
            assert "anthropic" in result.stdout, "Should show Anthropic"
            assert "claude-sonnet-4-5-20250929" in result.stdout, "Should show model"

            # Test new switching works
            result = self.run_ekko(['--model', 'claude-opus-4'])
            assert result.returncode == 0, "Should update Anthropic model"

            config = self.get_config()
            assert config['anthropic_model'] == 'claude-opus-4', "Should update model"
            assert config['anthropic_api_key'] == 'sk-ant-test123456789', "API key preserved"

        finally:
            self.cleanup_test_env()

    def test_v101_both_providers_config(self):
        """Test v1.0.1 config with both providers configured"""
        # User who set up both providers in v1.0.1
        v101_config = {
            "provider": "ollama",
            "anthropic_api_key": "sk-ant-original-key-123",
            "anthropic_model": "claude-3-opus-20240229",
            "ollama_url": "http://192.168.1.100:11434",
            "ollama_model": "mistral",
            "system_prompt": "You are a shell expert. Output ONLY the command to solve the problem. No explanation, no markdown, no backticks - just the raw shell command."
        }

        self.setup_test_env(v101_config)

        try:
            # Test switching preserves old settings
            result = self.run_ekko(['--switch', 'anthropic'])
            assert result.returncode == 0, "Should switch successfully"

            config = self.get_config()
            assert config['provider'] == 'anthropic', "Provider switched"
            assert config['ollama_model'] == 'mistral', "Ollama settings preserved"
            assert config['ollama_url'] == 'http://192.168.1.100:11434', "Custom URL preserved"

            # Switch back
            result = self.run_ekko(['--switch', 'ollama'])
            assert result.returncode == 0, "Should switch back"

            config = self.get_config()
            assert config['provider'] == 'ollama', "Provider switched back"
            assert config['anthropic_model'] == 'claude-3-opus-20240229', "Anthropic settings preserved"
            assert config['anthropic_api_key'] == 'sk-ant-original-key-123', "API key preserved"

        finally:
            self.cleanup_test_env()

    def test_config_structure_unchanged(self):
        """Verify config JSON structure is identical between versions"""
        v101_config = {
            "provider": "ollama",
            "anthropic_api_key": "",
            "anthropic_model": "claude-sonnet-4-5-20250929",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "qwen3-coder",
            "system_prompt": "You are a shell expert."
        }

        self.setup_test_env(v101_config)

        try:
            # Run any v1.3.0 operation
            self.run_ekko(['--version'])

            # Verify structure hasn't changed
            config = self.get_config()
            assert set(config.keys()) == set(v101_config.keys()), "Config keys unchanged"
            assert isinstance(config['provider'], str), "provider is string"
            assert isinstance(config['anthropic_api_key'], str), "API key is string"
            assert isinstance(config['ollama_url'], str), "URL is string"

        finally:
            self.cleanup_test_env()

    def test_no_migration_needed(self):
        """Verify v1.3.0 requires no migration or config updates"""
        v101_config = {
            "provider": "anthropic",
            "anthropic_api_key": "sk-ant-test-key",
            "anthropic_model": "claude-sonnet-4-5-20250929",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "qwen3-coder",
            "system_prompt": "Custom prompt"
        }

        self.setup_test_env(v101_config)

        try:
            # Read original config
            original_config = self.get_config()

            # Just load it (don't run any commands that modify)
            result = self.run_ekko(['--help'])
            assert result.returncode == 0, "Should run successfully"

            # Verify config unchanged
            current_config = self.get_config()
            assert current_config == original_config, "Config should be unchanged after load"

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
    print("EKKO UPGRADE COMPATIBILITY TEST SUITE")
    print("Testing v1.0.1 → v1.3.0 upgrade")
    print("="*60)

    tester = TestUpgradeCompatibility()

    # Run all tests
    tester.run_test("v1.0.1 config with Ollama only",
                   tester.test_v101_ollama_only_config)

    tester.run_test("v1.0.1 config with Anthropic only",
                   tester.test_v101_anthropic_only_config)

    tester.run_test("v1.0.1 config with both providers",
                   tester.test_v101_both_providers_config)

    tester.run_test("Config structure unchanged",
                   tester.test_config_structure_unchanged)

    tester.run_test("No migration needed",
                   tester.test_no_migration_needed)

    # Print summary
    success = tester.print_summary()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
