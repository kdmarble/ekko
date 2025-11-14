"""
Shared pytest fixtures for ekko tests
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict

import pytest
import pexpect

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def current_version():
    """Returns the current package version dynamically"""
    from ekko import __version__
    return __version__


@pytest.fixture
def test_home(tmp_path):
    """Creates a temporary HOME directory for isolated testing"""
    home = tmp_path / "home"
    home.mkdir()

    # Create config directory structure
    config_dir = home / ".config" / "ekko"
    config_dir.mkdir(parents=True)

    return home


@pytest.fixture
def test_env(test_home):
    """Returns environment dict with test HOME for isolated testing"""
    env = os.environ.copy()

    # Save the original HOME before changing it
    original_home = os.environ.get('HOME', '/root')
    env['HOME'] = str(test_home)

    # Preserve access to user site-packages by setting PYTHONUSERBASE
    # This ensures Python can still find packages installed with --user
    # even though we've changed HOME
    env['PYTHONUSERBASE'] = f"{original_home}/.local"

    return env


@pytest.fixture
def config_path(test_home):
    """Returns the path to the config file"""
    return test_home / ".config" / "ekko" / "config.json"


@pytest.fixture
def write_config(config_path):
    """Returns a function to write config data to the test config file"""
    def _write_config(config_data: Dict[str, Any]):
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        return config_path
    return _write_config


@pytest.fixture
def read_config(config_path):
    """Returns a function to read the current config"""
    def _read_config():
        with open(config_path, 'r') as f:
            return json.load(f)
    return _read_config


@pytest.fixture
def ekko_runner(test_env):
    """
    Returns a function to run ekko CLI commands in isolated environment.

    Usage:
        result = ekko_runner(['--version'])
        assert result.returncode == 0
    """
    def _run_ekko(args: list, env: dict = None, timeout: int = 10):
        if env is None:
            env = test_env

        result = subprocess.run(
            ['ekko'] + args,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result

    return _run_ekko


@pytest.fixture
def pexpect_runner(test_env):
    """
    Returns a function to run interactive ekko CLI commands with pexpect.

    Usage:
        child = pexpect_runner(['--setup'])
        child.expect('Enter choice:')
        child.sendline('1')
        child.close()
    """
    def _run_pexpect(args: list, env: dict = None, timeout: int = 10):
        if env is None:
            env = test_env

        child = pexpect.spawn(
            'ekko',
            args,
            env=env,
            timeout=timeout
        )
        return child

    return _run_pexpect


@pytest.fixture
def sample_config():
    """Returns a basic valid config for testing"""
    return {
        "provider": "ollama",
        "anthropic_api_key": "",
        "anthropic_model": "claude-sonnet-4-5-20250929",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "qwen3-coder",
        "system_prompt": "You are a shell expert. Output ONLY the command to solve the problem. No explanation, no markdown, no backticks - just the raw shell command."
    }


@pytest.fixture
def preconfigured_env(write_config):
    """Sets up environment with both providers configured"""
    config = {
        "provider": "ollama",
        "anthropic_api_key": "sk-ant-test1234567890abcdefghij",
        "anthropic_model": "claude-sonnet-4-5-20250929",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "qwen3-coder",
        "system_prompt": "You are a shell expert. Output ONLY the command."
    }
    write_config(config)
    return config


@pytest.fixture
def v101_ollama_config():
    """Returns a v1.0.1-style config with Ollama only"""
    return {
        "provider": "ollama",
        "anthropic_api_key": "",
        "anthropic_model": "claude-sonnet-4-5-20250929",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "qwen3-coder",
        "system_prompt": "You are a shell expert. Output ONLY the command to solve the problem. No explanation, no markdown, no backticks - just the raw shell command."
    }


@pytest.fixture
def v101_anthropic_config():
    """Returns a v1.0.1-style config with Anthropic only"""
    return {
        "provider": "anthropic",
        "anthropic_api_key": "sk-ant-test123456789",
        "anthropic_model": "claude-sonnet-4-5-20250929",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "qwen3-coder",
        "system_prompt": "You are a shell expert. Output ONLY the command to solve the problem. No explanation, no markdown, no backticks - just the raw shell command."
    }


@pytest.fixture
def v101_both_providers_config():
    """Returns a v1.0.1-style config with both providers configured"""
    return {
        "provider": "ollama",
        "anthropic_api_key": "sk-ant-original-key-123",
        "anthropic_model": "claude-3-opus-20240229",
        "ollama_url": "http://192.168.1.100:11434",
        "ollama_model": "mistral",
        "system_prompt": "You are a shell expert. Output ONLY the command to solve the problem. No explanation, no markdown, no backticks - just the raw shell command."
    }


# Config schema constants
REQUIRED_CONFIG_KEYS = [
    "provider",
    "anthropic_api_key",
    "anthropic_model",
    "ollama_url",
    "ollama_model",
    "system_prompt"
]

VALID_PROVIDERS = ["anthropic", "ollama"]
