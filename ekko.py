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
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.default_config()
    
    def default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "provider": "ollama",  # "anthropic" or "ollama"
            "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "anthropic_model": "claude-sonnet-4-20250514",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "llama3.2",
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
        choice = input("Enter choice [1]: ").strip() or "1"
        
        if choice == "2":
            self.config["provider"] = "anthropic"
            api_key = input("Enter Anthropic API key: ").strip()
            self.config["anthropic_api_key"] = api_key
            
            model = input(f"Model [{self.config['anthropic_model']}]: ").strip()
            if model:
                self.config["anthropic_model"] = model
        else:
            self.config["provider"] = "ollama"
            
            url = input(f"Ollama URL [{self.config['ollama_url']}]: ").strip()
            if url:
                self.config["ollama_url"] = url
            
            model = input(f"Model [{self.config['ollama_model']}]: ").strip()
            if model:
                self.config["ollama_model"] = model
        
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
            return f"Error: {str(e)}"


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
            return f"Error: {str(e)}"


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
            print("ekko v1.0.0")
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
