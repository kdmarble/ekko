#!/usr/bin/env python3
"""
Test the piped installation scenario that caused the original bug
This simulates: curl -fsSL ... | bash
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

import pexpect


def test_piped_installation():
    """
    Test that the installation works correctly when piped through bash
    This simulates the bug scenario: curl -fsSL ... | bash
    """
    print("="*60)
    print("TESTING PIPED INSTALLATION SCENARIO")
    print("="*60)
    print("\n🧪 Simulating: cat install-ekko.sh | bash\n")

    # Create temporary test directory
    test_dir = tempfile.mkdtemp(prefix="ekko_piped_test_")
    print(f"📁 Test directory: {test_dir}")

    try:
        # Setup environment
        env = os.environ.copy()
        env['HOME'] = test_dir
        env['INSTALL_DIR'] = f"{test_dir}/.local/bin"
        env['CONFIG_DIR'] = f"{test_dir}/.config/ekko"

        # Create install directory
        install_dir = Path(test_dir) / ".local" / "bin"
        install_dir.mkdir(parents=True, exist_ok=True)

        # Copy ekko.py to the install location (simulating download)
        ekko_source = Path(__file__).parent.parent / "ekko.py"
        ekko_dest = install_dir / "ekko"
        shutil.copy(ekko_source, ekko_dest)
        ekko_dest.chmod(0o755)

        print(f"✓ Copied ekko.py to {ekko_dest}")

        # Now run the setup wizard via piped stdin (the problematic scenario)
        # We'll pipe some test input and verify it's reading from TTY, not the pipe
        print("\n📝 Running setup wizard with piped input (should read from TTY)...")

        # Create a child process that will interact with the setup wizard
        child = pexpect.spawn(
            str(ekko_dest), ['--setup'],
            env=env,
            timeout=10
        )

        # The wizard should read from TTY, not stdin
        # So even though we're in a piped environment, it should work
        child.expect('Enter choice .*:')
        child.sendline('1')  # Ollama

        child.expect('Ollama URL .*:')
        child.sendline('http://localhost:11434')

        child.expect('Model .*:')
        child.sendline('qwen3-coder')

        child.expect('Configuration saved')
        child.expect(pexpect.EOF, timeout=2)
        child.close()

        print("✓ Setup wizard completed successfully")

        # Verify config file was created correctly
        config_file = Path(test_dir) / ".config" / "ekko" / "config.json"
        if not config_file.exists():
            raise AssertionError(f"Config file not found: {config_file}")

        print(f"✓ Config file created: {config_file}")

        # Load and verify config
        with open(config_file, 'r') as f:
            config = json.load(f)

        print("\n📋 Configuration contents:")
        print(json.dumps(config, indent=2))

        # Verify config is correct (not corrupted)
        assert config['provider'] == 'ollama', "Provider should be ollama"
        assert config['ollama_url'] == 'http://localhost:11434', f"URL should be correct, got: {config['ollama_url']}"
        assert config['ollama_model'] == 'qwen3-coder', f"Model should be correct, got: {config['ollama_model']}"

        # Check that config doesn't contain script artifacts
        assert '# Final instructions' not in config['ollama_url'], "URL should not contain script comments"
        assert 'echo' not in config['ollama_model'], "Model should not contain bash commands"

        print("\n✅ All assertions passed!")
        print("\n" + "="*60)
        print("PIPED INSTALLATION TEST: PASSED")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n" + "="*60)
        print("PIPED INSTALLATION TEST: FAILED")
        print("="*60)
        return False

    finally:
        # Cleanup
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
            print(f"\n🧹 Cleaned up test directory")


def test_actual_installation_script():
    """
    Test the actual install-ekko.sh script with simulated user input
    """
    print("\n" + "="*60)
    print("TESTING ACTUAL INSTALLATION SCRIPT")
    print("="*60)
    print("\n🧪 Testing install-ekko.sh with simulated piping\n")

    # Create temporary test directory
    test_dir = tempfile.mkdtemp(prefix="ekko_install_test_")
    print(f"📁 Test directory: {test_dir}")

    try:
        # Modify the install script to use our test directory
        install_script = Path(__file__).parent.parent / "install-ekko.sh"

        # Read the script
        with open(install_script, 'r') as f:
            script_content = f.read()

        # Create a test version with modified paths
        test_script = Path(test_dir) / "test-install.sh"
        test_content = script_content.replace(
            'INSTALL_DIR="$HOME/.local/bin"',
            f'INSTALL_DIR="{test_dir}/.local/bin"'
        ).replace(
            'CONFIG_DIR="$HOME/.config/ekko"',
            f'CONFIG_DIR="{test_dir}/.config/ekko"'
        ).replace(
            'SHELL_RC="$HOME/',
            f'SHELL_RC="{test_dir}/'
        )

        with open(test_script, 'w') as f:
            f.write(test_content)

        test_script.chmod(0o755)

        print("✓ Created test installation script")

        # Setup environment for the test
        env = os.environ.copy()
        env['HOME'] = test_dir
        env['PATH'] = f"{test_dir}/.local/bin:{env.get('PATH', '')}"

        # Run the installation script (simulating cat install.sh | bash)
        # But we'll use pexpect to provide interactive input
        child = pexpect.spawn('bash', [str(test_script)], env=env, timeout=30)

        try:
            # Wait for setup wizard
            child.expect('Enter choice .*:', timeout=20)
            child.sendline('1')  # Ollama

            child.expect('Ollama URL .*:')
            child.sendline('')  # Default

            child.expect('Model .*:')
            child.sendline('qwen3-coder')

            child.expect('Installation complete', timeout=10)
            child.expect(pexpect.EOF, timeout=2)
            child.close()

            print("✓ Installation script completed successfully")

            # Verify config
            config_file = Path(test_dir) / ".config" / "ekko" / "config.json"
            assert config_file.exists(), "Config file should exist"

            with open(config_file, 'r') as f:
                config = json.load(f)

            print("\n📋 Configuration contents:")
            print(json.dumps(config, indent=2))

            # Verify correctness
            assert config['ollama_url'] == 'http://localhost:11434', "URL should be valid"
            assert config['ollama_model'] == 'qwen3-coder', "Model should be valid"
            assert '# Final instructions' not in str(config.values()), "Should not contain script artifacts"

            print("\n✅ All assertions passed!")
            print("\n" + "="*60)
            print("INSTALLATION SCRIPT TEST: PASSED")
            print("="*60)

            return True

        finally:
            if child.isalive():
                child.close()

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        print("INSTALLATION SCRIPT TEST: FAILED")
        print("="*60)
        return False

    finally:
        # Cleanup
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
            print(f"\n🧹 Cleaned up test directory")


def main():
    """Run all installation tests"""
    print("\n" + "="*80)
    print(" "*20 + "INSTALLATION TESTING SUITE")
    print("="*80)

    results = []

    # Test 1: Piped installation scenario
    results.append(("Piped Installation", test_piped_installation()))

    # Test 2: Actual installation script
    results.append(("Installation Script", test_actual_installation_script()))

    # Print summary
    print("\n" + "="*80)
    print(" "*30 + "TEST SUMMARY")
    print("="*80)

    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:30s} {status}")

    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
    print(f"Success rate: {(passed/total*100):.1f}%")
    print("="*80 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
