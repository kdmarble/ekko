#!/usr/bin/env python3
"""
ekko - AI-powered command line assistant
Supports Anthropic API and Ollama
"""
import sys
import os
import json
import subprocess
import re
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import requests
except ImportError:
    print("Error: requests module not found. Install with: pip install requests")
    sys.exit(1)


class Config:
    """Configuration management"""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "ekko"
        self.config_file = self.config_dir / "config.json"
        self.config = self.load_config()

    def _get_input(self, prompt: str) -> str:
        """Get input from TTY/console instead of stdin to handle piped installation scripts"""
        try:
            # Try to open TTY directly (Unix/Linux/macOS/WSL)
            if sys.platform != 'win32':
                with open('/dev/tty', 'r') as tty:
                    # Print to stdout so user sees the prompt
                    print(prompt, end='', flush=True)
                    return tty.readline().strip()
            else:
                # On Windows, try to open CON
                with open('CON', 'r') as con:
                    print(prompt, end='', flush=True)
                    return con.readline().strip()
        except (IOError, OSError, FileNotFoundError):
            # Fall back to regular input if TTY is not available
            return input(prompt).strip()

    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        if not url:
            return False
        # Check if it starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            return False
        # Basic validation that it has a domain/host
        # Remove protocol and check if there's something after it
        without_protocol = url.split('://', 1)[1] if '://' in url else ''
        return bool(without_protocol and len(without_protocol) > 0)

    def _validate_model_name(self, model: str) -> bool:
        """Validate model name is reasonable"""
        if not model:
            return False
        # Check for suspicious content (like bash commands or comments)
        suspicious_patterns = ['#', '$', '&&', '||', ';', '\n', 'echo', 'rm ', 'curl']
        return not any(pattern in model for pattern in suspicious_patterns)

    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key format"""
        if not api_key:
            return False
        # Anthropic API keys typically start with 'sk-ant-'
        # Check for reasonable length and no suspicious content
        suspicious_patterns = ['#', '\n', 'echo', '$', '&&']
        return len(api_key) > 10 and not any(pattern in api_key for pattern in suspicious_patterns)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)

                # Validate the loaded config
                if not self._validate_config(config):
                    print(f"⚠ Warning: Configuration file appears to be corrupted or invalid.")
                    print(f"   Config file: {self.config_file}")
                    print(f"   Please run 'ekko --setup' to reconfigure.\n")
                    sys.exit(1)

                return config
            except json.JSONDecodeError:
                print(f"⚠ Error: Configuration file is not valid JSON.")
                print(f"   Config file: {self.config_file}")
                print(f"   Please run 'ekko --setup' to reconfigure.\n")
                sys.exit(1)
        return self.default_config()

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration structure and content"""
        # Check for required keys
        required_keys = ["provider", "ollama_url", "ollama_model", "anthropic_model", "system_prompt"]
        if not all(key in config for key in required_keys):
            return False

        # Validate provider-specific settings
        provider = config.get("provider", "")
        if provider == "ollama":
            # Validate Ollama URL
            ollama_url = config.get("ollama_url", "")
            if not self._validate_url(ollama_url):
                print(f"⚠ Invalid Ollama URL in config: '{ollama_url}'")
                return False

            # Validate model name
            model = config.get("ollama_model", "")
            if not self._validate_model_name(model):
                print(f"⚠ Invalid Ollama model name in config: '{model}'")
                return False

        elif provider == "anthropic":
            # Validate API key
            api_key = config.get("anthropic_api_key", "")
            if not self._validate_api_key(api_key):
                print(f"⚠ Invalid Anthropic API key in config")
                return False

            # Validate model name
            model = config.get("anthropic_model", "")
            if not self._validate_model_name(model):
                print(f"⚠ Invalid Anthropic model name in config: '{model}'")
                return False
        else:
            print(f"⚠ Invalid provider in config: '{provider}'")
            return False

        return True
    
    def default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "provider": "ollama",  # "anthropic" or "ollama"
            "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "anthropic_model": "claude-sonnet-4-5-20250929",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "qwen3-coder",
            "system_prompt": "You are a shell expert. Output ONLY the command to solve the problem. No explanation, no markdown, no backticks - just the raw shell command."
        }
    
    def save_config(self):
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_wizard(self):
        """Interactive setup wizard"""
        print("🔧 ekko setup wizard\n")

        # Provider selection
        print("Choose your AI provider:")
        print("1. Ollama (local, free)")
        print("2. Anthropic API (requires API key)")
        choice = self._get_input("Enter choice [1]: ") or "1"

        if choice == "2":
            self.config["provider"] = "anthropic"

            # Get and validate API key
            while True:
                api_key = self._get_input("Enter Anthropic API key: ")
                if self._validate_api_key(api_key):
                    self.config["anthropic_api_key"] = api_key
                    break
                else:
                    print("⚠ Invalid API key format. Please enter a valid Anthropic API key.")

            # Get model name (with validation)
            model = self._get_input(f"Model [{self.config['anthropic_model']}]: ")
            if model:
                if self._validate_model_name(model):
                    self.config["anthropic_model"] = model
                else:
                    print(f"⚠ Invalid model name, using default: {self.config['anthropic_model']}")
        else:
            self.config["provider"] = "ollama"

            # Get and validate Ollama URL
            while True:
                url = self._get_input(f"Ollama URL [{self.config['ollama_url']}]: ")
                if not url:
                    # User pressed enter, use default
                    break
                if self._validate_url(url):
                    self.config["ollama_url"] = url
                    break
                else:
                    print("⚠ Invalid URL format. Please enter a valid URL (e.g., http://localhost:11434)")

            # Get and validate model name
            model = self._get_input(f"Model [{self.config['ollama_model']}]: ")
            if model:
                if self._validate_model_name(model):
                    self.config["ollama_model"] = model
                else:
                    print(f"⚠ Invalid model name, using default: {self.config['ollama_model']}")

        self.save_config()
        print(f"\n✓ Configuration saved to {self.config_file}")
        print("\nTo use: ekko find all files over 500MB")


class LLMProvider:
    """Base class for LLM providers"""
    
    def generate(self, prompt: str, system_prompt: str) -> str:
        raise NotImplementedError


class AnthropicProvider(LLMProvider):
    """Anthropic API provider"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    def generate(self, prompt: str, system_prompt: str) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": self.model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Anthropic API: {str(e)}\n"
            error_msg += "Possible fixes:\n"
            error_msg += "  - Check your API key is valid\n"
            error_msg += "  - Verify your internet connection\n"
            error_msg += "  - Run 'ekko --setup' to reconfigure\n"
            print(error_msg)
            sys.exit(1)


class OllamaProvider(LLMProvider):
    """Ollama local provider"""
    
    def __init__(self, url: str, model: str):
        self.url = url.rstrip("/")
        self.model = model
    
    def generate(self, prompt: str, system_prompt: str) -> str:
        api_url = f"{self.url}/api/generate"
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(api_url, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["response"]
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Ollama: {str(e)}\n"
            error_msg += "Possible fixes:\n"
            error_msg += f"  - Check Ollama is running at {self.url}\n"
            error_msg += f"  - Verify the model '{self.model}' is installed: ollama list\n"
            error_msg += f"  - Check the Ollama URL is correct\n"
            error_msg += "  - Run 'ekko --setup' to reconfigure\n"
            print(error_msg)
            sys.exit(1)


class CommandGenerator:
    """Main command generation logic"""
    
    def __init__(self, config: Config):
        self.config = config.config
        self.provider = self._get_provider()
    
    def _get_provider(self) -> LLMProvider:
        """Get the configured LLM provider"""
        provider_type = self.config["provider"]
        
        if provider_type == "anthropic":
            api_key = self.config.get("anthropic_api_key")
            if not api_key:
                print("Error: Anthropic API key not configured. Run: aicmd --setup")
                sys.exit(1)
            return AnthropicProvider(api_key, self.config["anthropic_model"])
        
        elif provider_type == "ollama":
            return OllamaProvider(
                self.config["ollama_url"],
                self.config["ollama_model"]
            )
        
        else:
            print(f"Error: Unknown provider '{provider_type}'")
            sys.exit(1)
    
    def clean_command(self, cmd: str) -> str:
        """Strip markdown and formatting artifacts"""
        # Remove markdown code blocks
        cmd = re.sub(r'```[a-z]*\n?', '', cmd)
        cmd = re.sub(r'```\n?', '', cmd)
        # Remove backticks
        cmd = cmd.strip('`').strip()
        # Get first non-empty line
        lines = [line.strip() for line in cmd.split('\n') if line.strip()]
        return lines[0] if lines else ""
    
    def run(self, original_prompt: str):
        """Main interactive loop"""
        prompt = original_prompt
        system_prompt = self.config["system_prompt"]
        
        while True:
            # Generate command
            response = self.provider.generate(prompt, system_prompt)
            cmd = self.clean_command(response)
            
            if not cmd:
                print("Error: Could not generate valid command")
                return
            
            # Display command
            print(f"\n\033[36m{cmd}\033[0m")
            
            # Get user input
            try:
                user_input = input("\033[90m[enter=run, n=cancel, or describe what's wrong]: \033[0m")
            except (KeyboardInterrupt, EOFError):
                print()
                return
            
            # Handle response
            if not user_input or user_input.lower() in ['y', 'yes']:
                # Run command
                try:
                    subprocess.run(cmd, shell=True)
                except KeyboardInterrupt:
                    print()
                return
            
            elif user_input.lower() in ['n', 'no', 'q', 'quit']:
                # Cancel
                return
            
            else:
                # Correction - loop with feedback
                prompt = f"Original: '{original_prompt}'. Previous: '{cmd}'. Issue: {user_input}. Generate corrected command."
                print("\033[90m↻ revising...\033[0m")


def main():
    """Main entry point"""
    config = Config()
    
    # Handle special commands
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--setup', 'setup', 'config']:
            config.setup_wizard()
            return
        
        if sys.argv[1] in ['--help', '-h', 'help']:
            print("""ekko - AI-powered command line assistant

Usage:
  ekko <prompt>           Generate and run command
  ekko --setup            Run configuration wizard
  ekko --help             Show this help

Examples:
  ekko find all files over 500MB
  ekko compress this folder to tar.gz
  ekko show disk usage sorted by size

Configuration: ~/.config/ekko/config.json""")
            return
        
        if sys.argv[1] in ['--version', '-v']:
            print("ekko v1.0.1")
            return
    
    # Check if configured
    if not config.config.get("anthropic_api_key") and config.config["provider"] == "anthropic":
        print("Not configured. Run: ekko --setup")
        return
    
    # Get prompt from arguments
    if len(sys.argv) < 2:
        print("Usage: ekko <prompt>")
        print("Run 'ekko --help' for more information")
        return
    
    prompt = " ".join(sys.argv[1:])
    
    # Generate and run
    generator = CommandGenerator(config)
    generator.run(prompt)


if __name__ == "__main__":
    main()
